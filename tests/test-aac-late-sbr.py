"""Evidence and fail-closed acceptance tests for the QEMU controller experiment."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from run_aac_late_sbr import parse_log

EVIDENCE = ROOT/'tests/results/esp32c3-aac-late-sbr-20261004'


class LateSbrEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = (EVIDENCE/'regression-final/qemu.log').read_text()

    def test_byte_exact_evidence(self):
        for directory in (EVIDENCE, ROOT/'tests/results/esp32c3-wifi-recheck-20261004'):
            sums = json.loads((directory/'checksums.json').read_text())
            self.assertTrue(sums)
            for name, expected in sums.items():
                with self.subTest(file=name):
                    self.assertEqual(hashlib.sha256((directory/name).read_bytes()).hexdigest(), expected)

    def test_pass_scope_and_saved_result(self):
        parsed = parse_log(self.log)
        saved = json.loads((EVIDENCE/'regression-final/result.json').read_text())
        for key, value in parsed.items():
            self.assertEqual(saved[key], value, key)
        self.assertEqual(parsed['ordinary_channel_samples'], 887808)
        self.assertTrue(parsed['precision_pass'])
        for key in ('transition_pcm_qualified', 'reverse_transition_qualified', 'production_qualified'):
            self.assertFalse(parsed[key])

    def test_rejects_missing_truncated_or_corrupt_evidence(self):
        changes = (
            ('QEMU_SMOKE_PASS', 'INCOMPLETE'),
            ('case=lc_44100_stereo', 'case=lc_48000_stereo'),
            ('max_error_lsb=0', 'max_error_lsb=1'),
            ('channel_samples=147456', 'channel_samples=147455'),
            ('lc_frames=26', 'lc_frames=13'),
            ('failures=2 tasks=2 resets=2', 'failures=2 tasks=2 resets=0'),
            ('min_free_bytes=2844', 'min_free_bytes=800'),
            ('allocations=290 frees=290', 'allocations=290 frees=289'),
            ('decode_io=1348', 'decode_io=1347'),
            ('negative_cases=10', 'negative_cases=0'),
            ('transition_pcm_quality=unqualified', 'transition_pcm_quality=qualified'),
        )
        for old, new in changes:
            with self.subTest(mutation=old):
                self.assertIn(old, self.log)
                with self.assertRaises(ValueError):
                    parse_log(self.log.replace(old, new, 1))
        for bad in (self.log+self.log, self.log+'\nGuru Meditation'):
            with self.assertRaises(ValueError):
                parse_log(bad)

    def test_failures_remain_failures(self):
        failed = json.loads((EVIDENCE/'initialization-only/result.json').read_text())
        self.assertEqual(failed['process_exit'], 0)
        self.assertFalse(failed['format_pass'])
        with self.assertRaises(ValueError):
            parse_log((EVIDENCE/'initialization-only/qemu.log').read_text())
        board = json.loads((EVIDENCE/'board-baseline/report.json').read_text())
        implicit = next(c for c in board['cases'] if c['name']=='transition:implicit-sbr')
        self.assertEqual(implicit['result'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
