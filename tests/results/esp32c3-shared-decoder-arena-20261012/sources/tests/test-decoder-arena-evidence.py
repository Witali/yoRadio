"""Keep private-arena exhaustion and retained owners visible in experiment reports."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from common import Board, Failure
from decoder_arena_experiment import ArenaBoard, arena_check, check_transition_memory

class Evidence(unittest.TestCase):
    def test_transition_growth_keeps_absolute_headroom_gate(self):
        rows = [dict(boot_id='0123456789abcdef', uptime_ms=i*1000, heap=free,
                     largest=free-1000, minimum_heap=20000, allocation_failures=0,
                     task_watchdog_events=0) for i,free in enumerate((80000,60000,24000))]
        self.assertEqual(check_transition_memory(rows)['minimum_heap'], 24000)
        rows[-1]['largest'] = 8191
        with self.assertRaises(Failure): check_transition_memory(rows)

    def test_health_and_arena_share_one_response(self):
        calls = []
        arena = dict(capacity=100, live=10, peak=10, blocks=1, free=80, largest=80, failures=0)
        def response(board, path, data=None, timeout=5):
            calls.append(path)
            if path == '/api/native/status':
                return dict(firmware='esp32c3-oled-native', audio=True)
            return dict(schema=1, boot_id='0123456789abcdef', uptime_ms=100,
                reset_reason=1, heap=65536, largest=32768, minimum_heap=60000,
                tasks=16, allocation_failures=0, task_watchdog_events=0, decoder_arena=arena)
        with patch.object(Board, 'json', response):
            board = ArenaBoard('http://test.invalid')
            board.status()
        self.assertEqual(calls, ['/api/native/status', '/api/native/health'])
        self.assertEqual(board.arenas, [arena])
        self.assertEqual(len(board.health_samples), 1)

    def test_reuse_after_previous_case_failure(self):
        active = [dict(live=100, peak=200, blocks=1, failures=1)]
        idle = [dict(live=0, peak=200, blocks=0, failures=1)] * 3
        self.assertEqual(arena_check(active, idle, 1)['maximum_live'], 100)
        with self.assertRaises(Failure): arena_check(active, idle, 0)

    def test_missing_or_unrouted(self):
        idle = [dict(live=0, peak=0, blocks=0, failures=0)] * 3
        for active in ([], [None], idle):
            with self.assertRaises(Failure): arena_check(active, idle)

    def test_failure_at_stop_and_retained_owner(self):
        active = [dict(live=100, peak=100, blocks=1, failures=0)]
        for idle in ([dict(live=0, blocks=0, failures=1)] * 3,
                     [dict(live=12, blocks=1, failures=0)] * 3):
            with self.assertRaises(Failure): arena_check(active, idle)

if __name__ == '__main__':
    unittest.main()
