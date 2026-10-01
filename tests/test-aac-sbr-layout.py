#!/usr/bin/env python3
"""Lossless layout evidence, allocation accounting and fail-closed parsing."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
import run_aac_sbr_layout as layout
import run_aac_bfp16 as common

EVIDENCE = ROOT / 'tests/results/esp32c3-aac-sbr-layout-20261001'
NAMES = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')


class SbrLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logs = {n: (EVIDENCE/n/'qemu.log').read_text() for n in NAMES}
        cls.results = {n: json.loads((EVIDENCE/n/'result.json').read_text()) for n in NAMES}

    def test_reparse_and_provenance(self):
        for name, result in self.results.items():
            with self.subTest(name=name):
                for k, v in layout.parse_log(self.logs[name]).items():
                    self.assertEqual(v, result[k], k)
                self.assertEqual(common.sha256(EVIDENCE/name/'qemu.log'), result['provenance']['qemu_log_sha256'])
                self.assertEqual(common.sha256(EVIDENCE/'sdkconfig'), result['provenance']['sdkconfig_sha256'])
        manifest = json.loads((EVIDENCE/'implementation.json').read_text())
        for path, digest in manifest['files'].items():
            snapshot = manifest.get('snapshots', {}).get(path)
            self.assertEqual(common.sha256(EVIDENCE/snapshot if snapshot else ROOT/path), digest, path)

    def test_complete_lossless_matrix_and_savings(self):
        self.assertEqual(sum(len(r['runs']) for r in self.results.values()), 81)
        for result in self.results.values():
            self.assertTrue(result['precision_pass'])
            self.assertEqual(result['precision_limit_lsb'], 0)
            for m in result['memory']:
                if m['variant'] == 1 and m['calls']:
                    self.assertEqual(m['reference']-m['candidate'], 3532)
                    self.assertEqual(m['physical_reference']-m['physical_candidate'], 2048)
                    self.assertEqual(m['static_test_state'], 144)
            self.assertEqual(result['lifecycle_complete']['segments'], 21)

    def test_active_ps_and_lc_control(self):
        self.assertTrue(all(m['ps_reads'] > 0 for m in self.results['abba64']['memory'] if m['variant']==1))
        self.assertTrue(all(m['allocations']==0 for m in self.results['groovesalad128']['memory']))

    def test_missing_and_duplicate_evidence_rejected(self):
        log = self.logs['abba64']
        for kind in ('RESULT', 'MEMORY', 'STATS', 'HIST', 'EXTERNAL', 'LIFECYCLE_PASS', 'LIFECYCLE_COMPLETE'):
            line = next(s for s in log.splitlines(True) if f'SBRLAYOUT_{kind} ' in s)
            for changed in (log.replace(line, '', 1), log+line):
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    layout.parse_log(changed)

    def test_corrupt_measurements_rejected(self):
        for old, new in (('max_l=0','max_l=1'), ('candidate=51596','candidate=55128'),
                         ('physical_candidate=53248','physical_candidate=55296'),
                         ('guard_bytes=32','guard_bytes=0'), ('static_test_state=144','static_test_state=0'),
                         ('PCM=exact','PCM=changed'), ('cleanup=complete','cleanup=leaked'),
                         ('segments=21','segments=20'), ('ps_reads=30','ps_reads=0')):
            log = self.logs['synthetic']
            self.assertIn(old, log)
            with self.subTest(old=old), self.assertRaises(ValueError):
                layout.parse_log(log.replace(old, new, 1))

    def test_completion_required(self):
        for marker in ('SBRLAYOUT_LAYOUT_PASS','SBRLAYOUT_COUNTER_PASS',
                       'SBRLAYOUT_EXPERIMENT_COMPLETE','QEMU_AAC_FORMAT_PASS','QEMU_SMOKE_PASS'):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                layout.parse_log(self.logs['synthetic'].replace(marker,'REMOVED'))


if __name__ == '__main__':
    unittest.main()
