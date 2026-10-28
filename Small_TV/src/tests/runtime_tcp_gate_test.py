"""Exercise native mailbox ABI and reject falsely quiet TCP/IP observations."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import unittest

from runtime_tcp_gate import QUALIFIED_ELF, TcpMailboxGate, tcp_gate_layout


OPTIONS = LAYOUT = None


class MailboxFixture:
    """Place synthetic metadata at the actual linked globals in private host memory."""
    def __init__(self):
        self.layout = copy.deepcopy(LAYOUT)
        self.gate = TcpMailboxGate(self.layout)
        self.data, self.calls = {}, []
        self.task, self.mailbox, self.other = 0x3FCA1000, 0x3FCA2000, 0x3FCA3000
        self.queue = self.mailbox + self.offset('sys_mbox_s', 'os_mbox')
        self.waiting = self.queue + self.offset('QueueDefinition', 'xTasksWaitingToReceive')
        self.event = self.task + self.offset('tskTaskControlBlock', 'xEventListItem')
        self.sentinel = self.waiting + self.offset('xLIST', 'xListEnd')
        for name, value in (('lwip_task', self.task), ('tcpip_mbox', self.mailbox), ('pxCurrentTCBs', self.other)):
            self.symbol(name, value)
        self.field('QueueDefinition', self.queue, 'uxMessagesWaiting', 0)
        self.field('xLIST', self.waiting, 'uxNumberOfItems', 1)
        for key in ('pxNext', 'pxPrevious'):
            self.field('xLIST_ITEM', self.sentinel, key, self.event)
            self.field('xLIST_ITEM', self.event, key, self.sentinel)
        self.field('xLIST_ITEM', self.event, 'pxContainer', self.waiting)
        self.field('xLIST_ITEM', self.event, 'pvOwner', self.task)

    def offset(self, name, key):
        """Use the compiled field location even for adversarial host fixtures."""
        return self.layout['structures'][name]['fields'][key]['offset']

    def put(self, address, size, value):
        """Populate only a private dictionary; no emulator or hardware is accessed."""
        for index, byte in enumerate(value.to_bytes(size, 'little')):
            self.data[address + index] = byte

    def symbol(self, name, value):
        """Assign a host-only fixture scalar at its native global address."""
        row = self.layout['symbols'][name]
        self.put(row['address'], row['size'], value)

    def field(self, name, address, key, value):
        """Assign one compiled member without inventing its offset or width."""
        row = self.layout['structures'][name]['fields'][key]
        self.put(address + row['offset'], row['size'], value)

    def read(self, address, size):
        """Record each metadata request, including deliberately damaged fixtures."""
        self.calls.append((address, size))
        return bytes(self.data.get(address + index, 0) for index in range(size))

    def sample(self):
        """Exercise the same decoder that a paused diagnostic VM will use."""
        return self.gate.sample(self.read)


class GateTests(unittest.TestCase):
    """A quiet flag needs real list ownership, an empty queue and a blocked actor."""
    def setUp(self):
        self.fixture = MailboxFixture()

    def test_native_abi_and_static_task_identity(self):
        self.assertEqual(LAYOUT['elf_sha256'], QUALIFIED_ELF)
        self.assertEqual(LAYOUT['structures']['QueueDefinition']['size'], 84)
        self.assertEqual(LAYOUT['structures']['tskTaskControlBlock']['size'], 96)
        self.assertEqual(LAYOUT['symbols']['lwip_task']['address'], 0x3FCB6850)

    def test_quiet_requires_actual_receive_list_and_replays(self):
        row = self.fixture.sample()
        self.assertTrue(row['quiet'])
        self.assertEqual(self.fixture.gate.replay(json.loads(json.dumps(row))), row)

    def test_current_tcpip_task_is_busy(self):
        self.fixture.symbol('pxCurrentTCBs', self.fixture.task)
        self.assertEqual(self.fixture.sample()['reason'], 'tcpip-running')

    def test_waiting_on_another_resource_is_busy(self):
        self.fixture.field('xLIST_ITEM', self.fixture.event, 'pxContainer', self.fixture.waiting + 20)
        row = self.fixture.sample()
        self.assertFalse(row['quiet'])
        self.assertEqual(row['reason'], 'tcpip-not-waiting-on-mailbox')

    def test_pending_work_is_busy_even_with_stale_receive_membership(self):
        self.fixture.field('QueueDefinition', self.fixture.queue, 'uxMessagesWaiting', 1)
        row = self.fixture.sample()
        self.assertFalse(row['quiet'])
        self.assertEqual(row['reason'], 'mailbox-has-work')

    def test_not_initialized_does_not_read_task_or_queue(self):
        self.fixture.symbol('lwip_task', 0)
        row = self.fixture.sample()
        self.assertEqual(row['reason'], 'not-initialized')
        self.assertEqual(len(self.fixture.calls), 3)

    def test_invalid_pointers_never_reach_transport(self):
        for bad in (self.fixture.task + 1, 0x1000, 0x3FCDFFF0):
            with self.subTest(address=bad):
                self.fixture.symbol('lwip_task', bad)
                with self.assertRaises(ValueError):
                    self.fixture.sample()
                self.assertNotIn((bad, 96), self.fixture.calls)

    def test_broken_link_cannot_prove_quiet(self):
        self.fixture.field('xLIST_ITEM', self.fixture.event, 'pxPrevious', self.fixture.event)
        with self.assertRaisesRegex(ValueError, 'list links'):
            self.fixture.sample()

    def test_wrong_waiting_owner_cannot_prove_quiet(self):
        self.fixture.field('xLIST_ITEM', self.fixture.event, 'pvOwner', self.fixture.other)
        with self.assertRaisesRegex(ValueError, 'different owner'):
            self.fixture.sample()

    def test_other_event_item_with_same_owner_is_rejected(self):
        f, substitute = self.fixture, 0x3FCA4000
        for key in ('pxNext', 'pxPrevious'):
            f.field('xLIST_ITEM', f.sentinel, key, substitute)
            f.field('xLIST_ITEM', substitute, key, f.sentinel)
        f.field('xLIST_ITEM', substitute, 'pvOwner', f.task)
        f.field('xLIST_ITEM', substitute, 'pxContainer', f.waiting)
        with self.assertRaisesRegex(ValueError, 'different event item'):
            f.sample()

    def test_missing_extra_and_false_quiet_transcripts_are_rejected(self):
        row = self.fixture.sample()
        for mode in ('missing', 'extra', 'false-quiet'):
            changed = copy.deepcopy(row)
            if mode == 'missing':
                changed['reads'].pop()
            elif mode == 'extra':
                changed['reads'].append(changed['reads'][-1])
            else:
                changed['quiet'] = False
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.fixture.gate.replay(changed)

    def test_queue_storage_tcb_context_and_packet_payload_are_not_read(self):
        f = self.fixture
        allowed = {(row['address'], row['size']) for row in f.layout['symbols'].values()}
        allowed |= {(f.waiting, f.layout['structures']['xLIST']['size']),
                    (f.event, f.layout['structures']['xLIST_ITEM']['size']),
                    (f.event + f.offset('xLIST_ITEM', 'pxContainer'), 4),
                    (f.queue + f.offset('QueueDefinition', 'uxMessagesWaiting'), 4)}

        def read(address, size):
            """Fail at the attempted transport boundary, not just on saved output."""
            self.assertIn((address, size), allowed)
            return f.read(address, size)

        self.assertTrue(f.gate.sample(read)['quiet'])

    def test_unknown_elf_and_policy_are_rejected(self):
        for key, value in (('elf_sha256', '00' * 32), ('synchronization', 'unknown')):
            layout = copy.deepcopy(LAYOUT)
            layout[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                TcpMailboxGate(layout)

    def test_overlapping_or_outside_abi_is_rejected(self):
        for offset in (36, 1000):
            layout = copy.deepcopy(LAYOUT)
            layout['structures']['QueueDefinition']['fields']['uxMessagesWaiting']['offset'] = offset
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                TcpMailboxGate(layout)

    def test_short_metadata_transport_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Short mailbox'):
            self.fixture.gate.sample(lambda address, size: b'')


def main():
    """Preserve the qualified native layout, source identities and actual failures."""
    global OPTIONS, LAYOUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    OPTIONS = parser.parse_args()
    OPTIONS.output.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__), Path(__file__).with_name('runtime_tcp_gate.py'),
             Path(__file__).with_name('runtime_memory.py'), OPTIONS.elf]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    pins = {str(path.resolve()): sha(path) for path in files}
    LAYOUT = tcp_gate_layout(OPTIONS.elf)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GateTests))
    unchanged = pins == {str(path.resolve()): sha(path) for path in files}
    report = dict(passed=result.wasSuccessful() and unchanged, tests=result.testsRun,
                  inputs_unchanged=unchanged, inputs_sha256=pins, layout=LAYOUT,
                  no_vm_or_hardware_access=True, all_functionality_verified=False,
                  scope='Host-only mailbox quiescence gate; no actual TCP inventory or leak conclusion.',
                  failures=[str(case) for case, _ in result.failures], errors=[str(case) for case, _ in result.errors])
    (OPTIONS.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
