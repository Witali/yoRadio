"""Quiet firmware must not pass with absent telemetry, an OOM or a reboot."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from production_health import HealthBoard, NUMERIC, check_health, read_health, output_window


def sample(**updates):
    return dict(dict(schema=1, boot_id='0123456789abcdef', uptime_ms=2000,
        reset_reason=1, heap=120000, largest=110000, minimum_heap=100000,
        tasks=17, allocation_failures=0, task_watchdog_events=0), **updates)


class HealthTests(unittest.TestCase):
    def test_read_filters_unknown_private_fields(self):
        board = Mock()
        board.json.return_value = sample(station='private', password='private')
        self.assertEqual(read_health(board), sample())

    def test_missing_and_invalid_fields_fail(self):
        for key in NUMERIC:
            for value in (None, True, -1, '0'):
                with self.subTest(key=key, value=value), self.assertRaises(Failure):
                    read_health(Mock(json=Mock(return_value=sample(**{key:value}))))
        for update in ({'schema':True}, {'schema':2}, {'boot_id':'short'},
                       {'largest':120001}, {'minimum_heap':120001}, {'tasks':0}):
            with self.subTest(update=update), self.assertRaises(Failure):
                read_health(Mock(json=Mock(return_value=sample(**update))))

    def test_lifetime_fault_and_reset_are_not_hidden_by_playing(self):
        for change in ({'allocation_failures':1}, {'task_watchdog_events':1},
                       {'boot_id':'fedcba9876543210'}, {'uptime_ms':1999}):
            board = HealthBoard('http://unused.invalid')
            with patch('production_health.Board.status', return_value={'audio':True}), \
                 patch('production_health.read_health', side_effect=[sample(), sample(**change)]):
                board.status()
                with self.assertRaises(Failure):
                    board.status()
                self.assertEqual(len(board.health_samples), 2)
                self.assertEqual(board.health_samples[-1].keys() & change.keys(), change.keys())

    def test_quiet_healthy_series(self):
        self.assertEqual(check_health([sample(), sample(uptime_ms=3000)])['samples'], 2)
        with self.assertRaises(Failure):
            check_health([])

    def test_optional_output_filters_extra_fields_and_rejects_invalid_counters(self):
        output = dict(available=True, completion_queue_drops=7, write_errors=2)
        board = Mock(json=Mock(return_value=sample(output=dict(output, private='secret'))))
        self.assertEqual(read_health(board)['output'], output)
        for field in ('completion_queue_drops', 'write_errors'):
            for value in (None, True, -1, 2**32, '0'):
                with self.subTest(field=field, value=value), self.assertRaises(Failure):
                    read_health(Mock(json=Mock(return_value=sample(output=dict(output, **{field:value})))))
        for value in (None, {}, dict(output, available=1)):
            with self.assertRaises(Failure):
                read_health(Mock(json=Mock(return_value=sample(output=value))))

    def test_output_window_excludes_past_events_and_counts_wrap(self):
        def row(ms, drops, errors=2):
            return sample(uptime_ms=ms, output=dict(available=True,
                          completion_queue_drops=drops, write_errors=errors))
        result = output_window([row(2000, 7), row(4000, 7)])
        self.assertEqual(result, dict(samples=2, elapsed_ms=2000,
                                     completion_queue_drops=0, write_errors=0))
        result = output_window([row(2000, 2**32-1), row(3000, 0), row(4000, 2, 3)])
        self.assertEqual(result['completion_queue_drops'], 3)
        self.assertEqual(result['write_errors'], 1)

    def test_output_window_rejects_missing_unavailable_and_rebooted_evidence(self):
        first = sample(output=dict(available=True, completion_queue_drops=0, write_errors=0))
        for last in (sample(uptime_ms=3000),
                     dict(first, uptime_ms=3000, output=dict(first['output'], available=False)),
                     dict(first, uptime_ms=3000, boot_id='fedcba9876543210'), first):
            with self.assertRaises(Failure):
                output_window([first, last])


if __name__ == '__main__':
    unittest.main()
