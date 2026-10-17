"""Check the exact ROM getters, including an intentionally wrong decoder ABI."""
import argparse
from pathlib import Path
import struct
import sys
import unittest

from runtime_heap_rom import RomHeapCounters

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dependency-root', type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.dependency_root / '.build/small-tv-parity/oracle-deps'))
ROM = args.dependency_root / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'


class RomCounterTests(unittest.TestCase):
    def setUp(self):
        """Load the pinned ROM code for an independent counter evaluation."""
        self.rom = RomHeapCounters(ROM)
        self.header = struct.pack('<5I', 0, 78900, 65432, 200000, 0)

    def test_real_counters(self):
        self.assertEqual(self.rom.value('multi_heap_free_size_impl', self.header), 78900)
        self.assertEqual(self.rom.value('multi_heap_minimum_free_size_impl', self.header), 65432)
        self.rom.validate(self.header, 78900, 65432)
        self.assertEqual(self.rom.checks, 2)

    def test_null_heap(self):
        for name in self.rom.functions:
            self.assertEqual(self.rom.value(name, self.header, null=True), 0)

    def test_counter_values_are_not_constants(self):
        for free, minimum in ((0, 0), (1, 1), (0xFFFFFFFF, 2), (34567, 12345)):
            with self.subTest(free=free):
                self.rom.validate(struct.pack('<5I', 0, free, minimum, 0, 0), free, minimum)

    def test_wrong_decoder_field_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'disagree'):
            self.rom.validate(self.header, 200000, 65432)
        with self.assertRaisesRegex(ValueError, 'disagree'):
            self.rom.validate(self.header, 78900, 78900)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]], verbosity=2)
