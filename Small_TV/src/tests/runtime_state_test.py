"""Verify long-run clock rollover and complete, bounded runtime journals."""
import json
from pathlib import Path
import tempfile
import unittest
from runtime_state import GuestMicroseconds, RuntimeJournal

TEMP_ROOT = Path(__file__).resolve().parents[3] / '.build/runtime-state-unit'
TEMP_ROOT.mkdir(parents=True, exist_ok=True)


class RuntimeStateTests(unittest.TestCase):
    def test_clock_rollover(self):
        clock = GuestMicroseconds()
        raw = (2 ** 32 - 20, 2 ** 32 - 1, 0, 25, 25)
        self.assertEqual([clock.update(value) for value in raw],
                         [2 ** 32 - 20, 2 ** 32 - 1, 2 ** 32, 2 ** 32 + 25, 2 ** 32 + 25])
        self.assertEqual(clock.wraps, 1)

    def test_clock_multiple_rollovers(self):
        clock = GuestMicroseconds()
        for value in (100, 2 ** 32 - 1, 0, 2 ** 32 - 1):
            clock.update(value)
        self.assertEqual(clock.update(10), 2 * 2 ** 32 + 10)

    def test_clock_invalid_samples(self):
        for value in (-1, 2 ** 32, 1.5, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                GuestMicroseconds().update(value)

    def test_complete_stream_and_bounded_summary(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(TEMP_ROOT.resolve()))
            path = Path(directory) / 'events.jsonl'
            journal = RuntimeJournal(path, tail=2)
            for index in range(5):
                journal.append('snapshot', {'label': str(index),
                    'heap': {'free_bytes': 100 - index, 'minimum_free_bytes': 80 - index},
                    'tasks': [{'name': 'worker', 'stack_high_water_free_bytes': 20 - index}]})
            journal.append('http', {'request_count': 2, 'guest_seconds': .25})
            journal.append('outage', {'offline_guest_seconds': 1})
            summary = journal.summary()
            journal.close()
            self.assertEqual(summary['events'], 7)
            self.assertEqual(summary['snapshots'], 5)
            self.assertEqual([row['label'] for row in summary['snapshot_tail']], ['3', '4'])
            self.assertEqual(summary['first_snapshot']['label'], '0')
            self.assertEqual(summary['http_requests'], 2)
            self.assertEqual(summary['minimum_task_stack_fill_bytes_by_name'], {'worker': 16})
            self.assertEqual(summary['minimum_sampled_free_heap_bytes'], 96)
            self.assertEqual(summary['minimum_sdk_sum_of_per_heap_minima_bytes'], 76)
            self.assertEqual(len([json.loads(line) for line in path.read_text().splitlines()]), 7)

    def test_journal_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(TEMP_ROOT.resolve()))
            path = Path(directory) / 'events.jsonl'
            path.write_text('preserve')
            with self.assertRaises(FileExistsError):
                RuntimeJournal(path)
            self.assertEqual(path.read_text(), 'preserve')

    def test_rejected_nonfinite_event_does_not_increment(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(TEMP_ROOT.resolve()))
            journal = RuntimeJournal(Path(directory) / 'events.jsonl')
            try:
                with self.assertRaises(ValueError):
                    journal.append('http', {'guest_seconds': float('nan')})
                self.assertEqual(journal.events, 0)
            finally:
                journal.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
