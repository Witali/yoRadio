"""Long playback must not pass with valid PCM status and a runtime fault."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from run import Suite


class SustainedRuntimeTests(unittest.TestCase):
    def exercise(self, records, origin=None):
        board = Mock()
        capture = Mock(port=object())
        capture.since.return_value = [dict(at=0, line=line) for line in records]
        spec = dict(codec='flac', seconds=65, rate=48000, channels=2,
                    bits=16, label='FLAC')
        samples = [dict(seconds=i, request_ms=10, audio=True,
                        pcm_sample_rate=48000, pcm_channels=2,
                        bits_per_sample=16, format='FLAC 48 kHz stereo')
                   for i in range(60)]
        # Observation is supplied in memory; the output directory is irrelevant.
        with patch('run.Path.mkdir'):
            suite = Suite(board, 'http://fixture.invalid', {'fixture': spec},
                          capture, 'unused-sustained-output')
            suite.observe = Mock(return_value=samples)
            with patch('run.time.sleep'):
                try:
                    result = suite.sustained(60, 'fixture', origin=origin)
                    self.assertTrue(result['serial_capture_enabled'])
                    return board
                finally:
                    # Initial stop plus cleanup, including failed acceptance.
                    self.assertEqual(board.stop.call_count, 2)

    def test_runtime_faults_fail_even_with_valid_playback_and_without_cpu_gate(self):
        for line in ('PANIC registers: MCAUSE=0xdeadc0de',
                     'Runtime watchdog timeout: task_watchdog=true events=1',
                     'PERF watchdog: task_timeouts=1',
                     'E (12) audio: allocation failed',
                     'rst:0x1 (POWERON_RESET)',
                     'serial capture interrupted'):
            with self.subTest(line=line), self.assertRaisesRegex(Failure, 'Runtime failure'):
                self.exercise([line])

    def test_default_http_and_explicit_https_origins(self):
        board = self.exercise(['PERF PCM: audio 5000 ms'])
        board.play.assert_called_once_with('http://fixture.invalid/file/fixture', 'flac')
        board = self.exercise([], origin='https://secure-fixture.invalid')
        board.play.assert_called_once_with('https://secure-fixture.invalid/file/fixture', 'flac')


if __name__ == '__main__':
    unittest.main()
