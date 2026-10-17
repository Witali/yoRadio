"""Reject torn weather-cache reads and distinguish cached data from refreshes."""
from copy import deepcopy
import unittest

from runtime_weather import WeatherSnapshot


class WeatherObserverTests(unittest.TestCase):
    def setUp(self):
        """Expose only four numeric fields; any payload/string read fails the test."""
        self.layout = {'address': 0x3fca1000, 'size': 24, 'request_state_address': 0x3fca2000,
                       'fields': {'valid': 0, 'humidity': 8, 'generation': 16}, 'elf_sha256': 'matched'}
        self.objects = {'cached_weather': {'address': 0x3fca1000, 'size': 24},
                        'request_state': {'address': 0x3fca2000, 'size': 4}}
        self.values = {0x3fca1000: b'\1', 0x3fca1008: (67).to_bytes(4, 'little'),
                       0x3fca1010: (1).to_bytes(4, 'little'), 0x3fca2000: bytes(4)}
        self.reads = []
        def read(address, size):
            self.reads.append((address, size))
            value = self.values[address]
            self.assertEqual(len(value), size)
            return value
        self.read = read
        self.observer = WeatherSnapshot(read, self.layout, self.objects, 'matched')

    def test_only_numeric_cache_fields_leave_the_reader(self):
        self.assertEqual(self.observer.sample(10), {'worker_state': 0, 'valid': True, 'generation': 1, 'humidity': 67})
        self.assertEqual(sum(size for _, size in self.reads), 13)
        self.assertEqual(set(self.reads), {(0x3fca1000, 1), (0x3fca1008, 4), (0x3fca1010, 4), (0x3fca2000, 4)})

    def test_busy_and_pending_states_never_read_a_partial_cache(self):
        for state in (1, 2, 3):
            with self.subTest(state=state):
                self.values[0x3fca2000] = state.to_bytes(4, 'little')
                self.reads.clear()
                self.assertEqual(self.observer.sample(20), {'worker_state': state})
                self.assertEqual(self.reads, [(0x3fca2000, 4)])

    def test_invalidated_cache_is_not_a_successful_response(self):
        self.values[0x3fca1000] = b'\0'
        self.assertEqual(self.observer.sample(10), {'worker_state': 0, 'valid': False, 'generation': 1})
        self.assertEqual(self.observer.summary()['valid_samples'], 0)
        self.assertNotIn((0x3fca1008, 4), self.reads)

    def test_old_valid_samples_do_not_masquerade_as_new_publications(self):
        self.observer.sample(10)
        self.observer.sample(20)
        self.values[0x3fca1010] = (2).to_bytes(4, 'little')
        self.observer.sample(30)
        self.assertEqual(self.observer.summary(), {'snapshots': 3, 'quiescent_samples': 3, 'valid_samples': 3,
            'distinct_valid_generations': 2, 'first_fresh_guest_seconds': 10, 'last_fresh_guest_seconds': 30,
            'maximum_fresh_gap_guest_seconds': 20})

    def test_wrong_humidity_flags_and_zero_success_generation_reject(self):
        for address, raw in [(0x3fca1008, (41).to_bytes(4, 'little')), (0x3fca1000, b'\2'),
                             (0x3fca1010, bytes(4)), (0x3fca2000, (4).to_bytes(4, 'little'))]:
            with self.subTest(address=address):
                saved = self.values[address]
                self.values[address] = raw
                with self.assertRaises(ValueError):
                    WeatherSnapshot(self.read, self.layout, self.objects, 'matched').sample(10)
                self.values[address] = saved

    def test_generation_regression_is_not_silent_recovery(self):
        self.observer.sample(10)
        self.values[0x3fca1010] = bytes(4)
        self.values[0x3fca1000] = b'\0'
        with self.assertRaisesRegex(ValueError, 'regressed'):
            self.observer.sample(20)

    def test_wrong_elf_object_extent_and_overlapping_fields_reject(self):
        with self.assertRaisesRegex(ValueError, 'ELF differs'):
            WeatherSnapshot(self.read, self.layout, self.objects, 'other ELF')
        for key, value in [('valid', -1), ('humidity', 0), ('generation', 21), ('generation', 3)]:
            with self.subTest(key=key, value=value):
                layout = deepcopy(self.layout)
                layout['fields'][key] = value
                with self.assertRaises(ValueError):
                    WeatherSnapshot(self.read, layout, self.objects, 'matched')
        objects = deepcopy(self.objects)
        objects['request_state']['size'] = 1
        with self.assertRaisesRegex(ValueError, 'ABI differs'):
            WeatherSnapshot(self.read, self.layout, objects, 'matched')

    def test_short_memory_read_cannot_invent_a_valid_idle_worker(self):
        reader = WeatherSnapshot(lambda _, size: bytes(size - 1), self.layout, self.objects, 'matched')
        with self.assertRaisesRegex(ValueError, 'Short'):
            reader.sample(10)


if __name__ == '__main__':
    unittest.main()
