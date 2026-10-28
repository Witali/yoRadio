"""Reject misleading topology evidence using real ROM heaps and linked DWARF."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import unittest

import runtime_tlsf_instructions_test as fixtures
from runtime_heap_topology import HeapTopology
from runtime_memory import MemorySnapshot

OPTIONS = None


class TopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Resolve the real native ABI once; fixture payloads remain private host data."""
        cls.topology = HeapTopology(OPTIONS.rom, OPTIONS.elf)

    def setUp(self):
        """Register a typed synthetic heap and the exact expected patched dispatch."""
        self.pool = fixtures.RomPool()
        self.pool.allocate(128)
        topology = self.topology
        self.layout = topology.layout
        dispatch = topology.dispatch_layout
        patch = dispatch['symbols']['heap_tlsf_patch_table_ptr']['address']
        self.pool.image.cpu.mem_write(patch, topology.expected_dispatch)
        self.pool.image.cpu.mem_write(dispatch['symbols']['heap_tlsf_table_ptr']['address'], patch.to_bytes(4, 'little'))
        registry = 0x3FCA9000
        structure = self.layout['structures']['heap_t_']
        data = bytearray(structure['size'])
        for name, value in (('caps', 4), ('start', self.pool.heap),
                            ('end', self.pool.heap + self.pool.size), ('heap', self.pool.heap), ('next', 0)):
            offset = structure['fields'][name]['offset']
            data[offset:offset + 4] = value.to_bytes(4, 'little')
        self.pool.image.cpu.mem_write(registry, bytes(data))
        self.pool.image.cpu.mem_write(self.layout['symbols']['registered_heaps']['address'], registry.to_bytes(4, 'little'))
        self.reader = MemorySnapshot(lambda address, size: bytes(self.pool.image.cpu.mem_read(address, size)),
                                     self.layout, topology.counters.validate)
        aggregate = self.reader.heaps()
        self.row = {'heap': aggregate, 'heap_topology': topology.sample(self.reader, aggregate)}

    def test_saved_metadata_replays_after_json_roundtrip(self):
        self.topology.validate(json.loads(json.dumps(self.row)))

    def test_reserved_rom_slots_remain_zero(self):
        dispatch = self.topology.dispatch_layout
        table = bytes.fromhex(self.row['heap_topology']['dispatch_hex'])
        for name in ('tlsf_size', 'tlsf_align_size'):
            offset = dispatch['fields'][name]
            self.assertEqual(table[offset:offset + 4], bytes(4))
        self.topology.validate(self.row)

    def test_dispatch_cannot_substitute_another_walker(self):
        row = copy.deepcopy(self.row)
        table = bytearray.fromhex(row['heap_topology']['dispatch_hex'])
        offset = self.topology.dispatch_layout['fields']['tlsf_walk_pool']
        table[offset:offset + 4] = self.topology.walker.image.functions['tlsf_walk_pool']['address'].to_bytes(4, 'little')
        row['heap_topology']['dispatch_hex'] = table.hex()
        with self.assertRaisesRegex(ValueError, 'dispatch target'):
            self.topology.validate(row)

    def test_same_totals_do_not_permit_original_rom_instead_of_actual_patch(self):
        row = copy.deepcopy(self.row)
        part = row['heap_topology']['heaps'][0]
        header = self.pool.header()
        part['inventory'] = self.topology.walker.inspect(
            lambda address, size: bytes(self.pool.image.cpu.mem_read(address, size)),
            header[4], header[3], header[1], (self.pool.heap, self.pool.heap + self.pool.size), False)
        with self.assertRaisesRegex(ValueError, 'geometry differs'):
            self.topology.validate(row)

    def test_changed_counter_even_after_rehashing_all_scalar_summaries(self):
        row = copy.deepcopy(self.row)
        part = row['heap_topology']['heaps'][0]
        row['heap']['free_bytes'] += 4
        row['heap']['heaps'][0]['free_bytes'] += 4
        part['summary']['free_bytes'] += 4
        header = bytearray.fromhex(part['header_hex'])
        offset = self.layout['structures']['multi_heap_info']['fields']['free_bytes']['offset']
        header[offset:offset + 4] = part['summary']['free_bytes'].to_bytes(4, 'little')
        part['header_hex'] = header.hex()
        part['inventory']['record']['free_counter'] += 4
        with self.assertRaisesRegex(ValueError, 'free counter'):
            self.topology.validate(row)

    def test_reported_header_overhead_cannot_hide_loss(self):
        row = copy.deepcopy(self.row)
        row['heap_topology']['heaps'][0]['inventory']['allocated_header_bytes'] = 0
        with self.assertRaisesRegex(ValueError, 'instruction replay'):
            self.topology.validate(row)

    def test_missing_heap_is_not_accepted(self):
        row = copy.deepcopy(self.row)
        row['heap_topology']['heaps'] = []
        with self.assertRaises(ValueError):
            self.topology.validate(row)

    def test_aggregate_total_is_independently_checked(self):
        row = copy.deepcopy(self.row)
        row['heap']['free_bytes'] += 4
        with self.assertRaises(ValueError):
            self.topology.validate(row)


def main():
    """Preserve identities and negative controls without touching any live VM."""
    global OPTIONS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    OPTIONS = parser.parse_args(); fixtures.OPTIONS = OPTIONS
    OPTIONS.output.mkdir(parents=True, exist_ok=False)
    names = ('runtime_heap_topology_test.py', 'runtime_heap_topology.py', 'runtime_tlsf_instructions_test.py',
             'runtime_tlsf_instructions.py', 'runtime_instruction_image.py', 'runtime_memory.py', 'runtime_heap_rom.py')
    paths = [Path(__file__).with_name(name) for name in names] + [OPTIONS.rom, OPTIONS.elf]
    pins = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TopologyTests))
    unchanged = pins == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    report = dict(passed=result.wasSuccessful() and unchanged, tests=result.testsRun, inputs_unchanged=unchanged,
                  inputs_sha256=pins, no_vm_or_hardware_access=True, all_functionality_verified=False,
                  failures=[str(case) for case, _ in result.failures], errors=[str(case) for case, _ in result.errors])
    (OPTIONS.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
