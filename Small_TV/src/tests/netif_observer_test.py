"""Reject corrupt netif pointers, ambiguous roles and unsupported factory layouts."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

import netif_observer as observer


class NetifObserverTest(unittest.TestCase):
    """Exercise independent malformed guest-memory fixtures without a live VM."""
    def setUp(self):
        """Create one bounded RAM list with a public key in read-only DROM."""
        self.base = observer.RAM[0]
        self.memory = bytearray(1024)
        self.layout = {'head': self.base, 'head_first': 0, 'node_size': 8,
                       'node_netif': 0, 'node_next': 4, 'if_key': 92}
        self.put(0, self.base + 16)
        self.put(16, self.base + 128)
        self.put(128 + 92, observer.DROM[0] + 32)

    def put(self, offset, value):
        """Change one fixture pointer; guest execution is never involved."""
        struct.pack_into('<I', self.memory, offset, value)

    def read(self, address, size):
        """Expose only the fixture's allocated RAM and one immutable public key."""
        if address == observer.DROM[0] + 32:
            return b'WIFI_STA_DEF\0'.ljust(size, b'\0')
        if self.base <= address < self.base + len(self.memory):
            return bytes(self.memory[address - self.base:address - self.base + size])
        raise AssertionError('Observer attempted an unapproved memory read')

    def test_single_station(self):
        """Recognize exactly the station role and reject it as an AP role."""
        rows = observer.read_netifs(self.read, self.layout)
        observer.require_role(rows, True)
        with self.assertRaisesRegex(ValueError, 'Unexpected interfaces'):
            observer.require_role(rows, False)

    def test_cycle(self):
        """Reject a self-referential list instead of looping or counting it twice."""
        self.put(20, self.base + 16)
        with self.assertRaisesRegex(ValueError, 'Cyclic'):
            observer.read_netifs(self.read, self.layout)

    def test_node_pointer_guards(self):
        """Reject null-object, unaligned and peripheral pointers before dereference."""
        for pointer in (0, self.base + 1, 0x60000000, observer.RAM[1] - 4):
            with self.subTest(pointer=pointer):
                self.put(16, pointer)
                with self.assertRaisesRegex(ValueError, 'pointer outside'):
                    observer.read_netifs(self.read, self.layout)

    def test_key_pointer_guard(self):
        """Prevent a bogus if_key from reading MMIO or past DROM."""
        for pointer in (0, 0x60000000, observer.DROM[1] - 4):
            with self.subTest(pointer=pointer):
                self.put(128 + 92, pointer)
                with self.assertRaisesRegex(ValueError, 'key outside'):
                    observer.read_netifs(self.read, self.layout)

    def test_short_and_unterminated_reads(self):
        """Reject a failed memory read and a plausible key without a terminator."""
        with self.assertRaisesRegex(ValueError, 'Truncated'):
            observer.read_netifs(lambda address, size: b'\0', self.layout)
        for key in (b'WIFI_STA_DEFxxxx', b'OTHER\0'.ljust(16, b'\0')):
            with self.subTest(key=key):
                def read(address, size):
                    return key if address == observer.DROM[0] + 32 else self.read(address, size)
                with self.assertRaises(ValueError):
                    observer.read_netifs(read, self.layout)

    def test_missing_or_duplicate_roles(self):
        """Reject empty lists, duplicates and an idle second interface."""
        for keys in ([], ['WIFI_AP_DEF', 'WIFI_AP_DEF'], ['WIFI_AP_DEF', 'WIFI_STA_DEF']):
            with self.subTest(keys=keys):
                with self.assertRaisesRegex(ValueError, 'Unexpected interfaces'):
                    observer.require_role([{'key': key} for key in keys], False)

    def test_factory_identity(self):
        """Refuse to apply fixed factory addresses to another image."""
        temporary_root = Path(__file__).resolve().parents[3] / '.build/netif-observer-unit'
        temporary_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as folder:
            path = Path(folder) / 'other.bin'
            path.write_bytes(b'unknown firmware')
            with self.assertRaisesRegex(ValueError, 'Unknown factory'):
                observer.factory_layout(path)


def run_tests():
    """Return a compact acceptance record for the host/QEMU suite."""
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(NetifObserverTest))
    return {'passed': result.wasSuccessful(), 'tests': result.testsRun}


if __name__ == '__main__':
    report = run_tests()
    print(json.dumps(report))
    raise SystemExit(0 if report['passed'] else 1)
