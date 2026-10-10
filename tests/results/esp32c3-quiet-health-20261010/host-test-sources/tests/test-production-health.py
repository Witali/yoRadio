"""Quiet firmware must not pass with absent telemetry, an OOM or a reboot."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from production_health import HealthBoard, NUMERIC, check_health, read_health


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


if __name__ == '__main__':
    unittest.main()
