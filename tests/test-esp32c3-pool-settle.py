"""Lifecycle tests for the planned pool-settling diagnostic; no board access."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
import pool_settle
from common import Failure


class PoolSettleLifecycle(unittest.TestCase):
    def run_diagnostic(self, failures):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'result'
            board = Mock()
            board.info.return_value = dict(app_elf_sha256='identity', partition='app0')
            capture = Mock(rows=[])
            suite = Mock()
            suite.idle_heap.return_value = [dict(heap=100000, largest=65536, tasks=17)]*2
            suite.observe.return_value = [dict(request_ms=100)]*250
            server = Mock(events=[])
            private = dict(wifi=b'private-sentinel-not-for-report')
            arguments = ['pool_settle.py', '--board', 'http://unused.invalid', '--host', '127.0.0.1',
                         '--serial-port', 'unused', '--fixture-manifest', 'unused.json',
                         '--case', 'mp3', '--output', str(output)]
            with patch.object(sys, 'argv', arguments), \
                 patch.object(pool_settle, 'fixtures', return_value={'mp3': dict(seconds=180, codec='mp3', sha256='digest')}), \
                 patch.object(pool_settle, 'Board', return_value=board), \
                 patch.object(pool_settle, 'Capture', return_value=capture), \
                 patch.object(pool_settle, 'Suite', return_value=suite), \
                 patch.object(pool_settle, 'Server') as server_class, \
                 patch.object(pool_settle, 'snapshot', return_value=private), \
                 patch.object(pool_settle, 'verify_snapshot', return_value={'settings_unchanged': True}) as verify, \
                 patch.object(pool_settle, 'wait_ready'), \
                 patch.object(pool_settle, 'check_playback', side_effect=lambda *a, **k: {}), \
                 patch.object(pool_settle, 'check_cpu', side_effect=failures):
                server_class.return_value.__enter__.return_value = server
                result = pool_settle.main()
            self.assertEqual(suite.start.call_count, 1, 'Must not restart between load phases')
            self.assertEqual(suite.observe.call_count, 2)
            self.assertEqual(suite.idle_heap.call_count, 2)
            board.reboot.assert_called_once()
            capture.close.assert_called_once()
            verify.assert_called_once_with(board, private)
            text = (output/'report.json').read_text()
            self.assertNotIn('private-sentinel', text)
            report = json.loads(text)
            self.assertEqual(len(report['windows']), 2)
            return result, {case['name']: case['result'] for case in report['cases']}

    def test_initial_failure_is_not_erased_by_settled_success(self):
        code, outcomes = self.run_diagnostic([Failure('initial heap growth'), {}])
        self.assertEqual(code, 1)
        self.assertEqual(outcomes['initial-load'], 'FAIL')
        self.assertEqual(outcomes['settled-load'], 'PASS')
        self.assertEqual(outcomes['settled-idle-recovery'], 'PASS')
        self.assertEqual(outcomes['restore-board'], 'PASS')

    def test_settled_failure_still_restores_saved_station(self):
        code, outcomes = self.run_diagnostic([{}, Failure('continuing heap loss')])
        self.assertEqual(code, 1)
        self.assertEqual(outcomes['initial-load'], 'PASS')
        self.assertEqual(outcomes['settled-load'], 'FAIL')
        self.assertEqual(outcomes['restore-board'], 'PASS')


if __name__ == '__main__':
    unittest.main()
