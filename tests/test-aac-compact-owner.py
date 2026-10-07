#!/usr/bin/env python3
"""Retain exact-layout successes and the failed physical qualification."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import run_aac_compact_owner as owner
import run_aac_compact_adapter as adapter
EVIDENCE = ROOT/'tests/results/esp32c3-aac-compact-owner-20261002'
NAMES = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')


class CompactOwnerTests(unittest.TestCase):
    def test_all_guarded_owner_runs(self):
        comparisons = 0
        for name in NAMES:
            p = EVIDENCE/name
            saved = json.loads((p/'result.json').read_text())
            for k, v in owner.parse_log((p/'qemu.log').read_text()).items():
                self.assertEqual(saved[k], v, (name, k))
            self.assertEqual(hashlib.sha256((p/'qemu.log').read_bytes()).hexdigest(),
                             saved['provenance']['qemu_log_sha256'])
            allocation = saved['unguarded_allocator_probe']
            self.assertEqual(allocation['reference_block']-allocation['candidate_block'], 4096)
            self.assertTrue(saved['precision_pass'])
            comparisons += len(saved['runs'])
        self.assertEqual(comparisons, 81)

    def test_adapter_and_reference_pcm(self):
        p = EVIDENCE/'adapter'
        saved = json.loads((p/'result.json').read_text())
        for k, v in adapter.parse_log((p/'qemu.log').read_text()).items():
            self.assertEqual(saved[k], v)
        self.assertEqual(saved['pcm']['max_pcm_error_lsb'], 0)
        self.assertGreater(saved['pcm']['frames'], 0)
        self.assertTrue(saved['known_limitations'])

    def test_lifecycle_evidence_is_required(self):
        log = (EVIDENCE/'adapter/qemu.log').read_text()
        for a, b in (('failures=2', 'failures=1'), ('tasks=2', 'tasks=1'),
                     ('resets=2', 'resets=1'), ('heap=valid', 'heap=corrupt')):
            with self.subTest(a=a), self.assertRaises(ValueError):
                adapter.parse_log(log.replace(a, b))
        log = (EVIDENCE/'synthetic/qemu.log').read_text()
        with self.assertRaises(ValueError):
            owner.parse_log(log.replace('candidate_block=51200', 'candidate_block=55296'))

    def test_exact_implementation_and_saved_firmware(self):
        manifest = json.loads((EVIDENCE/'implementation.json').read_text())
        for name, item in manifest['files'].items():
            self.assertEqual(hashlib.sha256((EVIDENCE/item['snapshot']).read_bytes()).hexdigest(),
                             item['sha256'], name)
        firmware = ROOT/'firmware/development/esp32c3-aac-compact-owner'
        manifest = json.loads((firmware/'manifest.json').read_text())
        for name, item in manifest['files'].items():
            self.assertEqual(hashlib.sha256((firmware/name).read_bytes()).hexdigest(), item['sha256'])
        self.assertEqual(manifest['layout_required_pcm_error_lsb'], 0)

    def test_physical_failures_are_not_promoted(self):
        ota = json.loads((EVIDENCE/'physical/install/report.json').read_text())
        self.assertEqual(ota['cases'][0]['result'], 'PASS')
        for protocol in ('http', 'https'):
            report = json.loads((EVIDENCE/'physical'/protocol/'report.json').read_text())
            cases = {c['name']: c for c in report['cases']}
            self.assertEqual(cases[protocol+':groovesalad-128-aac']['result'], 'PASS')
            self.assertEqual(cases[protocol+':groovesalad-256-mp3']['result'], 'PASS')
            self.assertEqual(cases[protocol+':groovesalad-64-aac']['result'], 'FAIL')
            self.assertEqual(cases['restore']['result'], 'PASS')


if __name__ == '__main__':
    unittest.main()
