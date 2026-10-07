#!/usr/bin/env python3
"""Retain measured failures and reject false/incomplete per-area PCM evidence."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
import run_aac_area_storage as experiment
import run_aac_bfp16 as common

EVIDENCE = ROOT / 'tests/results/esp32c3-aac-area-storage-20261002'
NAMES = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')


class AreaStorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logs = {n: (EVIDENCE/n/'qemu.log').read_text() for n in NAMES}
        cls.results = {n: json.loads((EVIDENCE/n/'result.json').read_text()) for n in NAMES}

    def test_saved_evidence_and_provenance(self):
        for n, result in self.results.items():
            for k, value in experiment.parse_log(self.logs[n]).items():
                self.assertEqual(value, result[k], (n, k))
            self.assertEqual(common.sha256(EVIDENCE/n/'qemu.log'), result['provenance']['qemu_log_sha256'])
            self.assertEqual(common.sha256(EVIDENCE/'sdkconfig'), result['provenance']['sdkconfig_sha256'])
            if n != 'synthetic':
                previous = json.loads((ROOT/'tests/results/esp32c3-aac-storage18-20261002/qmf'/n/'result.json').read_text())
                self.assertEqual(result['provenance']['recording']['sha256'], previous['provenance']['recording']['sha256'])
        self.assertEqual(sum(len(d['runs']) for d in self.results.values()), 330)
        manifest = json.loads((EVIDENCE/'implementation.json').read_text())
        for path, digest in manifest['files'].items():
            self.assertEqual(common.sha256(EVIDENCE/manifest['snapshots'][path]), digest, path)

    def test_negative_imdct_result_is_preserved(self):
        d = self.results['synthetic']
        self.assertFalse(d['precision_pass'])
        for case, maximum in (('he44100_stereo', 2838), ('he48000_stereo', 2364), ('hev2_44100_stereo', 1350)):
            row = next(r for r in d['summaries'] if r['case']==case and r['variant']==3)
            self.assertEqual(row['max_pcm_error_lsb'], maximum)
            self.assertGreater(row['over_limit_per_run'], 0)
        self.assertTrue(all(d['precision_pass'] for n,d in self.results.items() if n!='synthetic'))

    def test_exact_controls_and_exponents(self):
        for d in self.results.values():
            self.assertEqual(d['ram_saved_bytes'], 0)
            self.assertTrue(d['exponent_int16_range_pass'])
            for r in d['runs']:
                if r['variant'] in (0, 5, 9):
                    self.assertEqual(r['different'], 0)
            self.assertTrue(all(a['saturated']==0 for a in d['areas']))
        values = [a for d in self.results.values() for a in d['areas']
                  if a['variant']==5 and a['area']==5 and a['run']==1 and a['calls']]
        self.assertEqual(min(a['minimum'] for a in values), -50)
        self.assertEqual(max(a['maximum'] for a in values), 16)

    def test_all_window_sequences_and_both_transforms(self):
        for w in self.results['synthetic']['windows']:
            if w['variant'] != 3:
                continue
            self.assertEqual(w['mask'], 15)
            self.assertGreater(w['transform2'] if w['case'].startswith('lc') else w['transform1'], 0)

    def test_isolation_and_real_input_coverage(self):
        d = self.results['abba64']
        for v in experiment.AREAS:
            r = next(s for s in d['summaries'] if s['variant']==v)
            self.assertEqual(r['coverage'], 'exercised')
        for a in self.results['groovesalad128']['areas']:
            if a['area'] != 3:
                self.assertEqual(a['calls'], 0)

    def test_missing_duplicate_completion_rejected(self):
        log = self.logs['synthetic']
        result_line = next(l for l in log.splitlines() if 'AREASTORAGE_RESULT ' in l)
        area_line = next(l for l in log.splitlines() if 'AREASTORAGE_AREA ' in l)
        for bad in (log.replace(result_line, ''), log+'\n'+result_line,
                    log.replace(area_line, ''), log+'\n'+area_line,
                    log.replace('AREASTORAGE_EXPERIMENT_COMPLETE', 'INCOMPLETE')):
            with self.assertRaises(ValueError):
                experiment.parse_log(bad)

    def test_false_precision_and_cross_area_writes_rejected(self):
        log = self.logs['synthetic']
        bad_verdict = log.replace('precision=FAIL', 'precision=PASS')
        line = next(l for l in log.splitlines() if 'AREASTORAGE_AREA ' in l and 'variant=1 run=1 area=2 ' in l)
        bad_area = log.replace(line, line.replace('calls=0 pairs=0', 'calls=1 pairs=12'))
        for bad in (bad_verdict, bad_area):
            with self.assertRaises(ValueError):
                experiment.parse_log(bad)

    def test_missing_histogram_or_false_moments_rejected(self):
        log = self.logs['abba64']
        line = next(l for l in log.splitlines() if 'AREASTORAGE_HIST ' in l)
        stats = next(l for l in log.splitlines() if 'AREASTORAGE_STATS ' in l)
        for bad in (log.replace(line, ''), log.replace(stats, re.sub(r'square_sum=\d+', 'square_sum=9999999999999', stats))):
            with self.assertRaises(ValueError):
                experiment.parse_log(bad)


if __name__ == '__main__':
    unittest.main()
