"""Test TCP attribution with native types and actual private ROM allocations."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import unittest

from runtime_heap_topology import HeapTopology
from runtime_tcp_allocations import AllocationIndex
from runtime_tcp_fixture import TcpFixture
from runtime_tcp_gate import tcp_gate_layout
from runtime_tcp_journal import TcpCoverage
from runtime_tcp_layout import FIELDS, tcp_layout, validate_layout
from runtime_tcp_snapshot import TcpSnapshot

OPTIONS = TOPOLOGY = LAYOUT = GATE_LAYOUT = None


class TcpTests(unittest.TestCase):
    """Distinguish packet sharing, list corruption and unclassified heap capacity."""
    def setUp(self):
        """Keep each ROM allocator fixture independent; native layouts are immutable."""
        self.fixture = TcpFixture(OPTIONS.rom, TOPOLOGY, LAYOUT, GATE_LAYOUT)
        self.observer = TcpSnapshot(OPTIONS.elf, LAYOUT, GATE_LAYOUT)

    def sample(self, read=None):
        """Pair each observation with its exact actual-ROM allocation snapshot."""
        frame = self.fixture.frame()
        frame['tcp_topology'] = self.observer.sample(read or self.fixture.read, frame, TOPOLOGY)
        return frame

    def test_native_abi_and_enum(self):
        self.assertEqual([LAYOUT['structures'][name]['size'] for name in FIELDS], [208, 76, 16, 16])
        self.assertEqual(LAYOUT['states']['TIME_WAIT'], 10)
        self.assertEqual(LAYOUT['structures']['pbuf']['fields']['ref']['size'], 1)

    def test_all_four_lists_and_unclassified_allocation_balance(self):
        for role in ('bound', 'listen', 'active', 'time_wait'):
            self.fixture.pcb(role)
        self.fixture.allocate(64)
        row = self.sample()['tcp_topology']
        self.assertEqual(row['list_counts'], dict.fromkeys(('bound', 'listen', 'active', 'time_wait'), 1))
        self.assertEqual(row['unregistered_pcbs'], 0)
        allocation = row['attribution']
        self.assertEqual(allocation['attributed_capacity_bytes'], 3 * 208 + 76)
        self.assertEqual(allocation['attributed_header_bytes'], 16)
        self.assertEqual(allocation['unclassified_capacity_bytes'], 64)
        self.assertEqual(allocation['unclassified_header_bytes'], 4)

    def test_json_replay_binds_every_counter_and_read(self):
        self.fixture.pcb('time_wait')
        frame = json.loads(json.dumps(self.sample()))
        self.observer.validate(frame, TOPOLOGY)
        frame['tcp_topology']['attribution']['attributed_capacity_bytes'] += 4
        with self.assertRaisesRegex(ValueError, 'replay'):
            self.observer.validate(frame, TOPOLOGY)

    def test_cyclic_pcb_list(self):
        pointer = self.fixture.pcb()
        self.fixture.field('tcp_pcb', pointer, 'next', pointer)
        with self.assertRaisesRegex(ValueError, 'PCB list'):
            self.sample()

    def test_pcb_cannot_belong_to_two_lists(self):
        pointer = self.fixture.pcb('bound')
        self.fixture.symbol('tcp_active_pcbs', pointer)
        with self.assertRaisesRegex(ValueError, 'PCB list'):
            self.sample()

    def test_state_must_match_list(self):
        self.fixture.pcb('active', 'TIME_WAIT')
        with self.assertRaisesRegex(ValueError, 'state does not match'):
            self.sample()

    def test_counter_cannot_be_smaller_than_registered_pcbs(self):
        self.fixture.pcb()
        self.fixture.symbol('num_tcp_pcb', 0)
        with self.assertRaisesRegex(ValueError, 'counter'):
            self.sample()

    def test_unregistered_closed_pcbs_are_not_invented_or_lost(self):
        self.fixture.pcb()
        self.fixture.symbol('num_tcp_pcb', 3)
        row = self.sample()['tcp_topology']
        self.assertEqual(row['unregistered_pcbs'], 2)
        self.assertEqual(len(row['pcbs']), 1)

    def test_timer_wrap_and_future_timer(self):
        pointer = self.fixture.pcb('time_wait')
        self.fixture.symbol('tcp_ticks', 1)
        self.fixture.field('tcp_pcb', pointer, 'tmr', 0xFFFFFFFE)
        self.assertEqual(self.sample()['tcp_topology']['pcbs'][0]['age_ticks'], 3)
        self.fixture.field('tcp_pcb', pointer, 'tmr', 2)
        with self.assertRaisesRegex(ValueError, 'timer is ahead'):
            self.sample()

    def test_contiguous_packet_accounts_one_allocation(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf()
        self.fixture.segment(pcb, packet)
        row = self.sample()['tcp_topology']
        self.assertEqual(row['attribution']['attributed_blocks'], 3)
        self.assertEqual(row['pbufs'][0]['payload_allocation'], packet)
        allocation = next(part for part in row['attribution']['allocations'] if part['pointer'] == packet)
        self.assertEqual({claim['kind'] for claim in allocation['claims']}, {'pbuf', 'pbuf-data'})

    def test_shared_packet_is_not_double_counted(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf(ref=2)
        self.fixture.segment(pcb, packet, 'unsent')
        self.fixture.segment(pcb, packet, 'unacked')
        row = self.sample()['tcp_topology']
        self.assertEqual(row['attribution']['attributed_blocks'], 4)
        self.assertEqual(len(row['pbufs']), 1)
        self.assertEqual(row['pbufs'][0]['references_observed'], 2)
        self.observer.validate(self.sample(), TOPOLOGY)

    def test_refcount_covers_all_observed_shared_owners(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf(ref=1)
        self.fixture.segment(pcb, packet, 'unsent')
        self.fixture.segment(pcb, packet, 'unacked')
        with self.assertRaisesRegex(ValueError, 'refcount'):
            self.sample()

    def test_zero_reference_count(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf(ref=0)
        self.fixture.segment(pcb, packet)
        with self.assertRaisesRegex(ValueError, 'reference count'):
            self.sample()

    def test_cyclic_pbuf_chain(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf()
        self.fixture.segment(pcb, packet)
        self.fixture.field('pbuf', packet, 'next', packet)
        with self.assertRaisesRegex(ValueError, 'pbuf chain'):
            self.sample()

    def test_segment_cycle_or_multiple_ownership(self):
        for duplicate in (False, True):
            self.setUp()
            pcb, packet = self.fixture.pcb(), self.fixture.pbuf()
            segment = self.fixture.segment(pcb, packet)
            if duplicate:
                self.fixture.field('tcp_pcb', pcb, 'unsent', segment)
            else:
                self.fixture.field('tcp_seg', segment, 'next', segment)
            with self.subTest(duplicate=duplicate), self.assertRaisesRegex(ValueError, 'segment list'):
                self.sample()

    def test_invalid_or_truncated_pbuf_total(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf(total=25)
        self.fixture.segment(pcb, packet, length=24)
        with self.assertRaisesRegex(ValueError, 'Truncated pbuf'):
            self.sample()

    def test_packet_queue_boundary_is_allowed(self):
        pcb, tail = self.fixture.pcb(), self.fixture.pbuf(10)
        head = self.fixture.pbuf(20, next_pointer=tail, total=20)
        self.fixture.segment(pcb, head, length=20)
        row = self.sample()['tcp_topology']
        self.assertEqual(len(row['pbufs']), 2)
        self.assertEqual(row['segments'][0]['pbuf_chain'], [head, tail])

    def test_external_rom_payload_is_never_read(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf(payload=0x3C010000)
        self.fixture.segment(pcb, packet)
        self.fixture.calls.clear()
        row = self.sample()['tcp_topology']
        self.assertIsNone(row['pbufs'][0]['payload_allocation'])
        self.assertFalse(any(address <= 0x3C010000 < address + size for address, size in self.fixture.calls))

    def test_separate_ram_payload_is_attributed_once(self):
        pcb, payload = self.fixture.pcb(), self.fixture.allocate(24)
        packet = self.fixture.pbuf(payload=payload)
        self.fixture.segment(pcb, packet)
        row = self.sample()['tcp_topology']
        self.assertEqual(row['pbufs'][0]['payload_allocation'], payload)
        self.assertEqual(row['attribution']['attributed_blocks'], 4)

    def test_freed_payload_is_rejected_without_dereferencing_it(self):
        pcb, payload = self.fixture.pcb(), self.fixture.allocate(24)
        packet = self.fixture.pbuf(payload=payload)
        self.fixture.segment(pcb, packet)
        self.fixture.image.call('multi_heap_free_impl', self.fixture.heap, payload)
        self.fixture.calls.clear()
        with self.assertRaisesRegex(ValueError, 'not in a live'):
            self.sample()
        self.assertFalse(any(address < payload + 24 and payload < address + size for address, size in self.fixture.calls))

    def test_contiguous_payload_must_share_its_pbuf_allocation(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf(payload=0x3C010000)
        self.fixture.field('pbuf', packet, 'type_internal', 0x80)
        self.fixture.segment(pcb, packet)
        with self.assertRaisesRegex(ValueError, 'Contiguous pbuf'):
            self.sample()

    def test_pcb_link_into_packet_payload_is_rejected_before_read(self):
        pcb, payload = self.fixture.pcb(), self.fixture.allocate(256)
        packet = self.fixture.pbuf(payload=payload)
        self.fixture.segment(pcb, packet)
        self.fixture.field('tcp_pcb', pcb, 'next', payload)
        self.fixture.calls.clear()
        with self.assertRaisesRegex(ValueError, 'aliases'):
            self.sample()
        self.assertFalse(any(payload <= address < payload + 256 for address, size in self.fixture.calls))

    def test_metadata_must_start_at_qualified_live_allocation(self):
        pcb = self.fixture.pcb()
        self.fixture.symbol('tcp_active_pcbs', pcb + 4)
        with self.assertRaisesRegex(ValueError, 'allocation'):
            self.sample()

    def test_payload_cannot_cross_allocation_end(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf()
        self.fixture.field('pbuf', packet, 'len', 1000)
        self.fixture.field('pbuf', packet, 'tot_len', 1000)
        self.fixture.segment(pcb, packet)
        with self.assertRaisesRegex(ValueError, 'crosses'):
            self.sample()

    def test_send_queue_length_must_count_real_chain_nodes(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf()
        self.fixture.segment(pcb, packet)
        self.fixture.field('tcp_pcb', pcb, 'snd_queuelen', 2)
        with self.assertRaisesRegex(ValueError, 'queue length'):
            self.sample()

    def test_short_selected_field_transport(self):
        pcb = self.fixture.pcb()
        address = pcb + LAYOUT['structures']['tcp_pcb']['fields']['state']['offset']

        def read(pointer, size):
            """Truncate a real selected field, after pointer/extent qualification."""
            return b'\x04' if pointer == address else self.fixture.read(pointer, size)

        with self.assertRaisesRegex(ValueError, 'Short TCP'):
            self.sample(read)

    def test_busy_actor_skips_tcp_globals_and_inventory(self):
        self.fixture.mailbox.symbol('pxCurrentTCBs', self.fixture.mailbox.task)
        row = self.sample()['tcp_topology']
        self.assertFalse(row['observed'])
        self.assertEqual(row['reads'], [])
        self.assertNotIn('attribution', row)
        self.observer.validate(self.sample(), TOPOLOGY)

    def test_journal_partitions_consumed_heap_without_losing_unclassified_bytes(self):
        self.fixture.pcb('listen')
        self.fixture.allocate(64)
        coverage = TcpCoverage(TOPOLOGY, self.observer)
        coverage(self.sample())
        row = coverage.series[0]
        self.assertEqual(row['tcp_consumed_bytes'], 76 + 4)
        self.assertEqual(row['unclassified_consumed_bytes'], 64 + 4)
        self.assertEqual(coverage.summary()['maximum_pcbs'], 1)

    def test_journal_keeps_busy_samples_out_of_numeric_attribution(self):
        self.fixture.mailbox.symbol('pxCurrentTCBs', self.fixture.mailbox.task)
        coverage = TcpCoverage(TOPOLOGY, self.observer)
        coverage(self.sample())
        self.assertEqual(coverage.summary()['observed'], 0)
        self.assertEqual(coverage.summary()['busy_reasons'], {'tcpip-running': 1})
        self.assertNotIn('tcp_consumed_bytes', coverage.series[0])

    def test_missing_unused_or_retyped_reads_do_not_replay(self):
        self.fixture.pcb()
        frame = self.sample()
        for case in ('missing', 'unused', 'retyped', 'different-stop'):
            changed = copy.deepcopy(frame)
            reads = changed['tcp_topology']['reads']
            if case == 'missing': reads.pop()
            elif case == 'unused': reads.append(reads[-1])
            elif case == 'retyped': reads[0][1] = float(reads[0][1])
            else: changed['tcp_topology']['guest_seconds'] += 1
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.observer.validate(changed, TOPOLOGY)

    def test_only_selected_scalar_fields_and_gate_metadata_are_read(self):
        pcb, packet = self.fixture.pcb(), self.fixture.pbuf()
        self.fixture.segment(pcb, packet)
        frame = self.fixture.frame()
        gate = self.fixture.mailbox.sample()
        allowed = {(row[0], row[1]) for row in gate['reads']}
        allowed |= {(row['address'], row['size']) for row in LAYOUT['symbols'].values()}
        for pointer, kind in self.fixture.objects.items():
            allowed |= {(pointer + row['offset'], row['size']) for row in LAYOUT['structures'][kind]['fields'].values()}

        def read(address, size):
            """Fail at the attempted transport boundary, including IP/packet reads."""
            self.assertIn((address, size), allowed)
            return self.fixture.read(address, size)

        row = self.observer.sample(read, frame, TOPOLOGY)
        self.assertTrue(row['observed'])

    def test_external_range_cannot_overlap_observed_heap(self):
        index = AllocationIndex(TOPOLOGY, self.fixture.frame())
        with self.assertRaisesRegex(ValueError, 'not in a live'):
            index.containing(self.fixture.base - 4, 8, optional=True)

    def test_layout_cannot_reinterpret_members_or_states(self):
        for case in ('ref-width', 'offset', 'enum', 'prefix'):
            layout = copy.deepcopy(LAYOUT)
            if case == 'ref-width': layout['structures']['pbuf']['fields']['ref']['size'] = 2
            elif case == 'offset': layout['structures']['tcp_pcb']['fields']['next']['offset'] = 60
            elif case == 'enum': layout['states']['TIME_WAIT'] = layout['states']['LISTEN']
            else: layout['metadata_allocation_offset'] = 4
            with self.subTest(case=case), self.assertRaises(ValueError):
                validate_layout(layout)


def main():
    """Save actual test outcomes and exact native/ROM/source identities."""
    global OPTIONS, TOPOLOGY, LAYOUT, GATE_LAYOUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    OPTIONS = parser.parse_args()
    OPTIONS.output.mkdir(parents=True, exist_ok=False)
    names = ('runtime_tcp_snapshot_test.py', 'runtime_tcp_fixture.py', 'runtime_tcp_snapshot.py',
             'runtime_tcp_layout.py', 'runtime_tcp_allocations.py', 'runtime_tcp_gate.py', 'runtime_tcp_gate_test.py',
             'runtime_tcp_journal.py',
             'runtime_memory.py', 'runtime_heap_topology.py', 'runtime_tlsf_instructions.py',
             'runtime_instruction_image.py', 'runtime_heap_rom.py')
    files = [Path(__file__).with_name(name) for name in names] + [OPTIONS.rom, OPTIONS.elf]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    pins = {str(path.resolve()): sha(path) for path in files}
    TOPOLOGY = HeapTopology(OPTIONS.rom, OPTIONS.elf)
    LAYOUT, GATE_LAYOUT = tcp_layout(OPTIONS.elf), tcp_gate_layout(OPTIONS.elf)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TcpTests))
    unchanged = pins == {str(path.resolve()): sha(path) for path in files}
    report = dict(passed=result.wasSuccessful() and unchanged, tests=result.testsRun,
                  inputs_unchanged=unchanged, inputs_sha256=pins, layout=LAYOUT,
                  no_vm_or_hardware_access=True, all_functionality_verified=False,
                  failures=[str(case) for case, _ in result.failures], errors=[str(case) for case, _ in result.errors])
    (OPTIONS.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
