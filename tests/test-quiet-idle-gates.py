"""A transport failure must remain a failure, not a heap leak or false recovery."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Blocked, Failure
from quiet_acceptance import idle_checkpoint, idle_recovery


class IdleGateTests(unittest.TestCase):
    def setup_case(self, rows=3, playing=False, error=False):
        old = dict(heap=10000, largest=8000, tasks=16)
        fresh = dict(heap=9900, largest=8000, tasks=16)
        board = SimpleNamespace(health_samples=[old]*3, stop=Mock())
        data = dict(idle=dict(initial=[old]*3, websocket=[old]*3))
        def observe(*args, **kwargs):
            board.health_samples.extend([fresh]*rows)
            if error:
                raise TimeoutError()
            return [dict(audio=playing)]*3
        suite = SimpleNamespace(observe=Mock(side_effect=observe))
        return board, suite, data, fresh

    def test_complete_checkpoint_uses_only_new_rows(self):
        board, suite, data, fresh = self.setup_case()
        idle_checkpoint(board, suite, data, 'websocket')
        self.assertEqual(data['idle']['websocket'], [fresh]*3)
        self.assertEqual(idle_recovery(data, 'websocket')['compared_with'], 'initial')

    def test_partial_failure_retained_but_cannot_become_baseline(self):
        board, suite, data, fresh = self.setup_case(rows=4, error=True)
        with patch('quiet_acceptance.capture_failure_snapshot', return_value={'diagnostic': True}) as capture:
            with self.assertRaises(TimeoutError):
                idle_checkpoint(board, suite, data, 'websocket')
        capture.assert_called_once_with(board)
        self.assertEqual(data['idle_failures']['websocket']['partial_health'], [fresh]*4)
        self.assertNotIn('websocket', data['idle'])
        with self.assertRaisesRegex(Blocked, 'Incomplete idle checkpoint: websocket'):
            idle_recovery(data, 'websocket')

    def test_old_health_cannot_fill_missing_samples(self):
        board, suite, data, _ = self.setup_case(rows=1)
        with patch('quiet_acceptance.capture_failure_snapshot', return_value={}):
            with self.assertRaisesRegex(Failure, 'fresh idle health'):
                idle_checkpoint(board, suite, data, 'websocket')
        self.assertNotIn('websocket', data['idle'])

    def test_playing_cannot_pass_as_idle(self):
        board, suite, data, _ = self.setup_case(playing=True)
        with patch('quiet_acceptance.capture_failure_snapshot', return_value={}):
            with self.assertRaisesRegex(Failure, 'confirmed idle'):
                idle_checkpoint(board, suite, data, 'websocket')

    def test_failed_stop_preserves_error_and_blocks_recovery(self):
        board, suite, data, _ = self.setup_case()
        board.stop.side_effect = OSError()
        with patch('quiet_acceptance.capture_failure_snapshot', return_value={}):
            with self.assertRaises(OSError):
                idle_checkpoint(board, suite, data, 'websocket')
        suite.observe.assert_not_called()
        self.assertEqual(data['idle_failures']['websocket']['partial_health'], [])
        with self.assertRaises(Blocked):
            idle_recovery(data, 'websocket')

    def test_missing_initial_baseline_is_explicitly_blocked(self):
        with self.assertRaisesRegex(Blocked, 'initial'):
            idle_recovery(dict(idle=dict(websocket=[])), 'websocket')


if __name__ == '__main__':
    unittest.main()
