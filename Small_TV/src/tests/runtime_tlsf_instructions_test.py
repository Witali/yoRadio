"""Check heap accounting against real C2 ROM allocation/free/realloc instructions."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import struct
import unittest

from runtime_instruction_image import InstructionImage
from runtime_tlsf_instructions import TlsfInstructionWalker

OPTIONS = None


class RomPool:
    """Build a single-threaded private host heap using the ROM's own public API."""
    def __init__(self, size=32768):
        self.image = InstructionImage(OPTIONS.rom)
        self.size = size
        self.heap = self.image.call('multi_heap_register_impl', 0x3FCB0000, size)
        if self.heap != 0x3FCB0000:
            raise ValueError('ROM fixture registration failed')
        self.initial = self.header()[1]

    def header(self):
        """Read scalar fixture counters, independently maintained by ROM operations."""
        return struct.unpack('<5I', self.image.cpu.mem_read(self.heap, 20))

    def allocate(self, size):
        """Allocate only in the host fixture, never in a QEMU or physical device."""
        return self.image.call('multi_heap_malloc_impl', self.heap, size)

    def free(self, pointer):
        """Use actual ROM coalescing and its counter update."""
        self.image.call('multi_heap_free_impl', self.heap, pointer)

    def inspect(self, walker, linked=True, read=None):
        """Supply the independent heap header and a metadata-only read callback."""
        header = self.header()
        read = read or (lambda address, size: bytes(self.image.cpu.mem_read(address, size)))
        return walker.inspect(read, header[4], header[3], header[1],
                              (self.heap, self.heap + self.size), linked)


class InstructionTests(unittest.TestCase):
    def setUp(self):
        """Use fresh instruction images so one negative control cannot affect another."""
        self.pool = RomPool()
        self.walker = TlsfInstructionWalker(OPTIONS.rom, OPTIONS.elf)

    def test_exact_accounting_and_json_replay(self):
        self.pool.allocate(33)
        result = self.pool.inspect(self.walker)
        self.assertEqual(result['allocated_capacity_bytes'], 36)
        self.assertEqual(result['allocated_header_bytes'], 4)
        self.assertEqual(self.walker.replay(json.loads(json.dumps(result['record']))), result)

    def test_rom_and_linked_patch_agree_for_continuing_callback(self):
        pointers = [self.pool.allocate(n) for n in (1, 20, 513, 1024)]
        self.pool.free(pointers[1])
        original = self.pool.inspect(self.walker, False)
        patched = self.pool.inspect(self.walker, True)
        for key in ('allocated_blocks', 'allocated_capacity_bytes', 'allocated_header_bytes',
                    'free_blocks', 'free_capacity_bytes', 'largest_free_capacity_bytes',
                    'allocated_capacity_histogram', 'free_capacity_histogram'):
            self.assertEqual(original[key], patched[key])
        self.assertEqual(original['record']['metadata_words'], patched['record']['metadata_words'])

    def test_alloc_free_realloc_series(self):
        randomizer, pointers = random.Random(731), []
        for _ in range(180):
            action = randomizer.randrange(3)
            if pointers and action == 0:
                self.pool.free(pointers.pop(randomizer.randrange(len(pointers))))
            elif pointers and action == 1:
                index = randomizer.randrange(len(pointers))
                result = self.pool.image.call('multi_heap_realloc_impl', self.pool.heap,
                                              pointers[index], randomizer.randrange(1, 2049))
                if result:
                    pointers[index] = result
            else:
                result = self.pool.allocate(randomizer.randrange(1, 2049))
                if result:
                    pointers.append(result)
            result = self.pool.inspect(self.walker)
            self.assertEqual(result['allocated_blocks'], len(pointers))
        for pointer in pointers:
            self.pool.free(pointer)
        self.assertEqual(self.pool.header()[1], self.pool.initial)
        self.assertEqual(self.pool.inspect(self.walker)['free_blocks'], 1)

    def test_same_live_requests_can_retain_twelve_more_capacity_bytes(self):
        """Prove a concrete allocator-padding control, not the cause of the old soak."""
        clean, fragmented = self.pool, RomPool()
        clean_pointers = [clean.allocate(n) for n in (20, 32, 32)]
        fragmented_pointers = [fragmented.allocate(32) for _ in range(3)]
        fragmented.free(fragmented_pointers[0])
        fragmented_pointers[0] = fragmented.allocate(20)
        a, b = clean.inspect(self.walker), fragmented.inspect(self.walker)
        self.assertEqual(a['allocated_blocks'], b['allocated_blocks'])
        self.assertEqual(b['allocated_capacity_bytes'] - a['allocated_capacity_bytes'], 12)
        self.assertEqual(clean.header()[1] - fragmented.header()[1], 12)
        for pool, pointers in ((clean, clean_pointers), (fragmented, fragmented_pointers)):
            for pointer in pointers:
                pool.free(pointer)
            self.assertEqual(pool.header()[1], pool.initial)

    def test_payload_is_never_read(self):
        pointer = self.pool.allocate(256)
        calls = []
        def read(address, size):
            """Fail even if the observer attempts to fetch one payload byte."""
            self.assertFalse(address < pointer + 256 and pointer < address + size)
            calls.append((address, size))
            return bytes(self.pool.image.cpu.mem_read(address, size))
        result = self.pool.inspect(self.walker, read=read)
        self.assertTrue(calls)
        self.assertTrue(all(size == 4 for _, size in calls))
        self.assertEqual(len(calls), len(result['record']['metadata_words']))

    def test_false_free_counter(self):
        self.pool.allocate(32)
        header = self.pool.header()
        with self.assertRaisesRegex(ValueError, 'free counter'):
            self.walker.inspect(lambda address, size: bytes(self.pool.image.cpu.mem_read(address, size)),
                                header[4], header[3], header[1] + 4,
                                (self.pool.heap, self.pool.heap + self.pool.size))

    def test_missing_duplicate_and_unused_transcript_words(self):
        record = self.pool.inspect(self.walker)['record']
        for case in ('missing', 'duplicate', 'unused'):
            changed = copy.deepcopy(record)
            if case == 'missing': changed['metadata_words'].pop()
            elif case == 'duplicate': changed['metadata_words'].append(changed['metadata_words'][0])
            else: changed['metadata_words'].insert(0, [4, 123])
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.walker.replay(changed)

    def test_corrupt_chain_cannot_escape_pool(self):
        record = self.pool.inspect(self.walker)['record']
        record['metadata_words'][0][1] = 0x100000
        with self.assertRaises(ValueError):
            self.walker.replay(record)

    def test_replay_cannot_write_heap(self):
        # Deliberately unsafe host-only callback: sw zero,0(a0), then ret.
        self.walker.image.cpu.mem_write(self.walker.image.CALLBACK, bytes.fromhex('2320050067800000'))
        with self.assertRaisesRegex(ValueError, 'heap write'):
            self.pool.inspect(self.walker)

    def test_replay_cannot_read_payload(self):
        # Deliberately unsafe host-only callback: lw a0,0(a0), then ret.
        self.walker.image.cpu.mem_write(self.walker.image.CALLBACK, bytes.fromhex('0325050067800000'))
        with self.assertRaisesRegex(ValueError, 'allocator payload'):
            self.pool.inspect(self.walker)

    def test_short_metadata_transport(self):
        with self.assertRaisesRegex(ValueError, 'Short TLSF'):
            self.pool.inspect(self.walker, read=lambda address, size: b'')


def main():
    """Preserve actual ROM/app/source identities and every failing test result."""
    global OPTIONS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    OPTIONS = parser.parse_args()
    OPTIONS.output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), Path(__file__).with_name('runtime_instruction_image.py'),
               Path(__file__).with_name('runtime_tlsf_instructions.py'), OPTIONS.rom, OPTIONS.elf]
    pins = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(InstructionTests))
    unchanged = pins == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    report = dict(passed=result.wasSuccessful() and unchanged, tests=result.testsRun,
                  inputs_sha256=pins, inputs_unchanged=unchanged, no_vm_or_hardware_access=True,
                  all_functionality_verified=False, failures=[str(case) for case, _ in result.failures],
                  errors=[str(case) for case, _ in result.errors],
                  scope='Real C2 ROM host-only allocator fixtures and exact linked/ROM metadata walkers; no production leak conclusion.')
    (OPTIONS.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
