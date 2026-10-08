"""A valid format and natural EOF must not mask a recorded runtime failure."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from run import Suite


class FileRuntimeTests(unittest.TestCase):
    def playback(self, line=None, serial=True):
        spec = dict(codec='aac', label='HE-AACv2 ', rate=44100, channels=2,
                    bits=16, seconds=12)
        state = dict(audio=True, format='HE-AACv2 44.1 kHz stereo',
                     pcm_sample_rate=44100, pcm_channels=2, bits_per_sample=16)
        samples = [dict(state, seconds=i) for i in range(2, 9)]
        board = Mock()
        capture = Mock(port=object() if serial else None)
        capture.since.return_value = [] if line is None else [dict(at=1, line=line)]
        with tempfile.TemporaryDirectory() as output, patch('run.time.sleep'):
            suite = Suite(board, 'http://127.0.0.1', {'sample':spec}, capture, output)
            suite.observe = Mock(side_effect=[samples, [dict(audio=False)]])
            try:
                return suite.file('sample')
            finally:
                # Failure must still stop the board and release its connection.
                self.assertEqual(board.stop.call_count, 2)

    def test_valid_format_and_eof(self):
        self.assertTrue(self.playback()['serial_capture_enabled'])

    def test_no_serial_is_explicit(self):
        self.assertFalse(self.playback(serial=False)['serial_capture_enabled'])

    def test_valid_pcm_does_not_mask_runtime_fault(self):
        for line in (
            'PERF allocation failed: requested=1700',
            'AAC decode error', 'OGG decode failed',
            'TLS failure: component=esp-tls-mbedtls',
            'assert failed: owner', 'Guru Meditation Error', 'CORRUPT HEAP',
            'PANIC registers: MEPC=0x42000000', 'serial capture interrupted',
            'E (1000) task_wdt: Task watchdog got triggered.',
            'Runtime watchdog timeout: task_watchdog=true',
            'ESP-ROM:esp32c3-api1', 'rst:0x1', 'waiting for download',
        ):
            with self.subTest(line=line), self.assertRaisesRegex(Failure, 'Runtime failure'):
                self.playback(line)


if __name__ == '__main__':
    unittest.main()
