#!/usr/bin/env python3
"""Retained integration evidence and rejection gates for temporary FIR rows."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import run_aac_smoothing_adapter as runner

EVIDENCE = ROOT/'tests/results/esp32c3-aac-smoothing-adapter-20261003'


class SmoothingAdapterTests(unittest.TestCase):
    def setUp(self):
        self.log = (EVIDENCE/'adapter/qemu.log').read_text(encoding='utf-8')

    def test_retained_evidence(self):
        saved = json.loads((EVIDENCE/'adapter/result.json').read_text(encoding='utf-8'))
        for key, value in runner.parse_log(self.log).items():
            self.assertEqual(saved[key], value)
        for path, key in ((EVIDENCE/'adapter/qemu.log', 'qemu_log_sha256'),
                          (EVIDENCE/'adapter-sdkconfig', 'sdkconfig_sha256')):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), saved['provenance'][key])
        self.assertTrue(saved['precision_pass'])
        self.assertGreater(saved['pcm']['samples'], 600000)
        self.assertLessEqual(saved['pcm']['max_pcm_error_lsb'], 3)
        self.assertEqual(saved['pcm_vs_previous_pc18']['different'], 0)

    def test_missing_or_weak_stack_evidence_rejected(self):
        for before, after in (('min_free_bytes=4956', 'min_free_bytes=1023'),
                              ('concurrent_peak=2', 'concurrent_peak=1'),
                              ('AACSMOOTHING_STACK', 'DISABLED_STACK')):
            with self.subTest(after=after), self.assertRaises(ValueError):
                runner.parse_log(self.log.replace(before, after))

    def test_wrong_owner_rejected(self):
        for before, after in (('owner_bytes=45932', 'owner_bytes=47980'),
                              ('block_bytes=47092', 'block_bytes=49140')):
            with self.subTest(after=after), self.assertRaises(ValueError):
                runner.parse_log(self.log.replace(before, after))

    def test_failed_run_cannot_qualify(self):
        with self.assertRaises(ValueError):
            runner.parse_log((EVIDENCE/'rejected-stack4096/qemu.log').read_text(encoding='utf-8'))

    def test_source_snapshots(self):
        manifest = json.loads((EVIDENCE/'implementation.json').read_text(encoding='utf-8'))
        for name, record in manifest['files'].items():
            self.assertEqual(hashlib.sha256((EVIDENCE/record['snapshot']).read_bytes()).hexdigest(),
                             record['sha256'], name)


if __name__ == '__main__':
    unittest.main()
