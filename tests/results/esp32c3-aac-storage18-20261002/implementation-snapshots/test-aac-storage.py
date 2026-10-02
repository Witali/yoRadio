#!/usr/bin/env python3
"""Reparse QMF/PS storage evidence and reject incomplete or contradictory results."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
import run_aac_bfp16 as common
import run_aac_qmf_storage as qmf
import run_aac_ps_storage as ps

EVIDENCE = ROOT / 'tests/results/esp32c3-aac-storage-20261002'
NAMES = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')
PARSERS = {'qmf': qmf.parse_log, 'ps': ps.parse_log}


class StorageTests(unittest.TestCase):
    evidence = EVIDENCE
    expected_runs = {'qmf':129, 'ps':153}
    payloads = {'1':2780, '2':3088, '3':2964, '4':3088}

    @classmethod
    def setUpClass(cls):
        cls.logs = {(kind, name): (cls.evidence / kind / name / 'qemu.log').read_text()
                    for kind in PARSERS for name in NAMES}
        cls.results = {(kind, name): json.loads((cls.evidence / kind / name / 'result.json').read_text())
                       for kind in PARSERS for name in NAMES}

    def test_results_and_provenance(self):
        for (kind, name), result in self.results.items():
            with self.subTest(kind=kind, name=name):
                parsed = PARSERS[kind](self.logs[kind, name])
                for key, value in parsed.items():
                    self.assertEqual(value, result[key], key)
                self.assertEqual(common.sha256(self.evidence / kind / name / 'qemu.log'),
                                 result['provenance']['qemu_log_sha256'])
                self.assertEqual(common.sha256(self.evidence / kind / 'sdkconfig'),
                                 result['provenance']['sdkconfig_sha256'])
        for kind,count in self.expected_runs.items():
            self.assertEqual(sum(len(r['runs']) for (k,n),r in self.results.items() if k==kind), count)
        manifest = json.loads((self.evidence / 'implementation.json').read_text())
        for path, digest in manifest['files'].items():
            self.assertEqual(common.sha256(self.evidence / manifest['snapshots'][path]), digest, path)

    def test_no_heap_saving_or_unexercised_quality_claim(self):
        for (kind, name), result in self.results.items():
            self.assertEqual(result['ram_saved_bytes'], 0)
            active = name != 'groovesalad128' if kind == 'qmf' else name in ('synthetic', 'abba64')
            self.assertEqual(result['quantization_exercised'], active)
            self.assertTrue(result['precision_pass'])
            self.assertEqual(result['production_precision_pass'],
                             name == 'groovesalad128' if kind == 'qmf' else name != 'abba64')
            self.assertTrue(all(s['saturations'] == 0 for s in result['storage']))
            if kind == 'ps':
                self.assertEqual(result['ps_delay_packed_payload_bytes'],
                                 self.payloads)

    def test_controls_are_bit_exact(self):
        for result in self.results.values():
            for r in result['runs']:
                if r['variant'] in (0, 7):
                    self.assertEqual(r['different'], 0)

    def test_completion_markers_required(self):
        for kind, parse in PARSERS.items():
            label = kind.upper() + 'STORAGE'
            for marker in (label+'_STORAGE_ARITHMETIC_PASS', label+'_COUNTER_PASS',
                           label+'_EXPERIMENT_COMPLETE', 'QEMU_AAC_FORMAT_PASS', 'QEMU_SMOKE_PASS'):
                with self.subTest(kind=kind, marker=marker), self.assertRaises(ValueError):
                    parse(self.logs[kind, 'synthetic'].replace(marker, 'REMOVED'))

    def test_missing_duplicate_records_rejected(self):
        for kind, parse in PARSERS.items():
            log = self.logs[kind, 'abba64']
            for record in ('RESULT', 'STORAGE', 'STATS', 'HIST', 'EXTERNAL'):
                line = next(s for s in log.splitlines(True) if kind.upper()+'STORAGE_'+record+' ' in s)
                for altered in (log.replace(line, '', 1), log+line):
                    with self.subTest(kind=kind, record=record), self.assertRaises(ValueError):
                        parse(altered)

    def test_false_precision_and_clipping_rejected(self):
        for kind, parse in PARSERS.items():
            log = self.logs[kind, 'abba64']
            for pattern, replacement in ((r'over_two=[1-9]\d*', 'over_two=0'),
                                         (r'saturations=0', 'saturations=-1'),
                                         (r'precision=PASS', 'precision=FAIL')):
                changed = re.sub(pattern, replacement, log, count=1)
                self.assertNotEqual(changed, log)
                with self.subTest(kind=kind, pattern=pattern), self.assertRaises(ValueError):
                    parse(changed)

    def test_false_ps_payload_and_heap_saving_rejected(self):
        log = self.logs['ps', 'abba64']
        for old, new in (('heap_saved=0','heap_saved=1848'), ('packed_payload=3088','packed_payload=2780'),
                         ('pairs=617','pairs=616'), ('guards=617','guards=616')):
            self.assertIn(old, log)
            with self.subTest(old=old), self.assertRaises(ValueError):
                ps.parse_log(log.replace(old, new, 1))


if __name__ == '__main__':
    unittest.main()
