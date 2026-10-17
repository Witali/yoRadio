"""Reject corrupt allocator/task chains before a runtime observer can trust them."""
import copy
import struct
import unittest

from runtime_memory import LISTS, MemorySnapshot


def shape(size, **fields):
    """Describe the explicit synthetic RV32 fixture ABI."""
    return {'size': size, 'fields': {key: {'offset': value[0], 'size': value[1]}
                                   for key, value in fields.items()}}


class MemoryTests(unittest.TestCase):
    def setUp(self):
        """Build two tasks and two capability-separated heaps in synthetic SRAM."""
        self.base = 0x3FCA0000
        self.data = bytearray(32768)
        symbols = {name: {'address': self.base + 0x200 + i * 40, 'size': 20}
                   for i, name in enumerate(LISTS)}
        symbols.update({name: {'address': self.base + 0x100 + i * 4, 'size': 4}
                        for i, name in enumerate(('registered_heaps', 'uxCurrentNumberOfTasks', 'pxCurrentTCBs'))})
        self.layout = {'symbols': symbols, 'structures': {
            'heap_t_': shape(36, caps=(0, 12), start=(12, 4), end=(16, 4), heap=(28, 4), next=(32, 4)),
            'multi_heap_info': shape(20, free_bytes=(4, 4), minimum_free_bytes=(8, 4), pool_size=(12, 4)),
            'tskTaskControlBlock': shape(96, pxStack=(48, 4), pcTaskName=(52, 16), pxEndOfStack=(68, 4)),
            'xLIST': shape(20, uxNumberOfItems=(0, 4), xListEnd=(8, 12)),
            'xLIST_ITEM': shape(20, pxNext=(4, 4), pxPrevious=(8, 4), pvOwner=(12, 4), pxContainer=(16, 4))}}
        self.word(0x100, self.base + 0x1200)
        self.word(0x104, 2)
        self.word(0x108, self.base + 0x800)
        # ORed priority capabilities match 8-bit, while the second heap does not.
        self.put(0x1200, struct.pack('<9I', 1, 4, 0, self.base + 0x6000, self.base + 0x6200,
                                    0, 0, self.base + 0x6000, self.base + 0x1240))
        self.put(0x1240, struct.pack('<9I', 2, 0, 0, self.base + 0x6400, self.base + 0x6600,
                                    0, 0, self.base + 0x6400, 0))
        self.put(0x6000, struct.pack('<5I', 0, 100, 80, 256, 0))
        self.put(0x6400, struct.pack('<5I', 0, 200, 150, 256, 0))
        for symbol in (symbols[name] for name in LISTS):
            off = symbol['address'] - self.base
            self.put(off, struct.pack('<5I', 0, 0, 0xFFFFFFFF, self.base + off + 8, self.base + off + 8))
        for off, stack, label, free in ((0x800, 0x4000, b'clock_ui', 32), (0x900, 0x4200, b'weather_http', 0)):
            self.word(off + 48, self.base + stack)
            self.put(off + 52, label + b'\0')
            self.word(off + 68, self.base + stack + 255)
            self.put(stack, b'\xA5' * free)
        self.attach(0x200, 0x800)
        self.attach(0x228, 0x900)
        self.reader = MemorySnapshot(self.read, self.layout)

    def put(self, offset, data):
        """Write only the host-side synthetic fixture."""
        self.data[offset:offset + len(data)] = data

    def word(self, offset, value):
        """Set a little-endian fixture pointer/count."""
        self.put(offset, struct.pack('<I', value))

    def read(self, address, size):
        """Provide an exact-length bounded synthetic memory reader."""
        off = address - self.base
        return bytes(self.data[off:off + size])

    def attach(self, list_offset, task_offset):
        """Link a single task into an otherwise empty FreeRTOS state list."""
        sentinel = self.base + list_offset + 8
        item = self.base + task_offset + 4
        self.word(list_offset, 1)
        self.word(list_offset + 12, item)
        self.word(list_offset + 16, item)
        self.put(task_offset + 4, struct.pack('<5I', 0, sentinel, sentinel,
                                            self.base + task_offset, self.base + list_offset))

    def test_actual_counts_and_capability_filter(self):
        self.assertEqual(self.reader.heaps()['free_bytes'], 100)
        self.assertEqual(self.reader.heaps()['minimum_free_bytes'], 80)
        self.assertEqual(self.reader.heaps(2)['free_bytes'], 200)

    def test_all_tasks_and_zero_stack_headroom_are_reported(self):
        self.assertEqual(self.reader.tasks(), [
            {'name': 'clock_ui', 'recorded_stack_span_bytes': 256, 'stack_high_water_free_bytes': 32},
            {'name': 'weather_http', 'recorded_stack_span_bytes': 256, 'stack_high_water_free_bytes': 0}])

    def test_heap_cycle(self):
        self.word(0x1240 + 32, self.base + 0x1200)
        with self.assertRaisesRegex(ValueError, 'Cyclic'):
            self.reader.heaps()

    def test_heap_counter_corruption(self):
        self.word(0x6000 + 8, 101)
        with self.assertRaisesRegex(ValueError, 'Inconsistent heap'):
            self.reader.heaps()

    def test_uninitialized_matching_heap_is_not_counted(self):
        self.word(0x1200 + 28, 0)
        with self.assertRaisesRegex(ValueError, 'No initialized heap'):
            self.reader.heaps()

    def test_pool_outside_declared_extent(self):
        self.word(0x1200 + 12, self.base + 0x6100)
        with self.assertRaisesRegex(ValueError, 'Inconsistent heap'):
            self.reader.heaps()

    def test_invalid_memory_pointer(self):
        self.word(0x100, 0x1000)
        with self.assertRaisesRegex(ValueError, 'outside bounded'):
            self.reader.heaps()

    def test_short_transport_read(self):
        with self.assertRaisesRegex(ValueError, 'Short observed'):
            MemorySnapshot(lambda address, size: b'', self.layout).heaps()

    def test_list_cycle_or_incorrect_count(self):
        self.word(0x200, 2)
        self.word(0x804 + 4, self.base + 0x804)
        with self.assertRaisesRegex(ValueError, 'Cyclic or short'):
            self.reader.tasks()

    def test_wrong_list_backlink(self):
        self.word(0x804 + 8, 0)
        with self.assertRaisesRegex(ValueError, 'list links'):
            self.reader.tasks()

    def test_wrong_list_container(self):
        self.word(0x804 + 16, self.base + 0x228)
        with self.assertRaisesRegex(ValueError, 'list links'):
            self.reader.tasks()

    def test_duplicate_task_owner(self):
        self.word(0x904 + 12, self.base + 0x800)
        with self.assertRaisesRegex(ValueError, 'membership'):
            self.reader.tasks()

    def test_missing_task_or_current_pointer(self):
        for off, value in ((0x104, 3), (0x108, 0)):
            with self.subTest(offset=off):
                previous = self.data[off:off + 4]
                self.word(off, value)
                with self.assertRaisesRegex(ValueError, 'membership'):
                    self.reader.tasks()
                self.put(off, previous)

    def test_stack_extent_and_unbounded_fill(self):
        self.word(0x800 + 68, self.base + 0x4000 + 65536)
        with self.assertRaisesRegex(ValueError, 'stack extent'):
            self.reader.tasks()
        self.word(0x800 + 68, self.base + 0x40FF)
        self.put(0x4000, b'\xA5' * 256)
        with self.assertRaisesRegex(ValueError, 'No saved context'):
            self.reader.tasks()

    def test_bad_abi_member_extent(self):
        self.layout = copy.deepcopy(self.layout)
        self.layout['structures']['heap_t_']['fields']['next']['offset'] = 36
        with self.assertRaisesRegex(ValueError, 'field outside'):
            MemorySnapshot(self.read, self.layout).heaps()

    def test_large_stack_respects_debugger_reply_limit(self):
        self.word(0x800 + 68, self.base + 0x4FFF)
        self.word(0x900 + 48, self.base + 0x5000)
        self.word(0x900 + 68, self.base + 0x50FF)
        self.put(0x4000, b'\xA5' * 3500)
        def limited_read(address, size):
            if size > 2048:
                raise ValueError('RSP reply would exceed its packet size')
            return self.read(address, size)
        tasks = MemorySnapshot(limited_read, self.layout).tasks()
        self.assertEqual(tasks[0]['stack_high_water_free_bytes'], 3500)


if __name__ == '__main__':
    unittest.main(verbosity=2)
