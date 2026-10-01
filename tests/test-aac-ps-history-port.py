#!/usr/bin/env python3
"""Validate current-decoder PS write-port evidence and fail-closed parsing."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
import run_aac_ps_history_port as port
import run_aac_bfp16 as common

EVIDENCE = ROOT / 'tests/results/esp32c3-aac-ps-port-20261001'
NAMES = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')


class PsWritePortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logs = {n: (EVIDENCE / n / 'qemu.log').read_text() for n in NAMES}
        cls.results = {n: json.loads((EVIDENCE / n / 'result.json').read_text()) for n in NAMES}

    def test_saved_results_reparse_and_hashes_match(self):
        for name, result in self.results.items():
            with self.subTest(name=name):
                for k, v in port.parse_log(self.logs[name]).items():
                    self.assertEqual(v, result[k], k)
                self.assertEqual(common.sha256(EVIDENCE / name / 'qemu.log'),
                                 result['provenance']['qemu_log_sha256'])
                self.assertEqual(common.sha256(EVIDENCE / 'sdkconfig'),
                                 result['provenance']['sdkconfig_sha256'])
        self.assertEqual(sum(len(r['runs']) for r in self.results.values()), 81)
        manifest = json.loads((EVIDENCE / 'implementation.json').read_text())
        for path, digest in manifest['files'].items():
            snapshot = manifest.get('snapshots', {}).get(path)
            self.assertEqual(common.sha256(EVIDENCE / snapshot if snapshot else ROOT / path), digest, path)

    def test_native_source_and_bypass_are_bit_exact(self):
        for result in self.results.values():
            for r in result['runs']:
                if r['variant'] in (0, 7):
                    self.assertEqual(r['different'], 0)
                    self.assertEqual(r['max_l'], 0)
                    self.assertEqual(r['max_r'], 0)

    def test_development_pass_does_not_hide_final_precision_failure(self):
        for name, result in self.results.items():
            self.assertTrue(result['precision_pass'])
            self.assertEqual(result['production_precision_pass'], name not in ('synthetic', 'abba64'))
        self.assertEqual(max(r['max_pcm_error_lsb'] for r in self.results['synthetic']['summaries']), 3)
        abba = next(r for r in self.results['abba64']['summaries'] if r['variant'] == 1)
        self.assertEqual(abba['over_two_per_run'], [2542]*3)
        self.assertEqual(abba['over_limit_per_run'], [0]*3)

    def test_actual_ps_writes_and_unused_imaginary_storage(self):
        for name, result in self.results.items():
            self.assertEqual(result['ram_saved_bytes'], 0)
            self.assertEqual(result['ps_delay_native_payload_bytes'], 4936)
            self.assertEqual(result['ps_delay_packed_payload_bytes'], 2468)
            self.assertEqual(result['quantization_exercised'], name in ('synthetic', 'abba64'))
            for s in result['storage']:
                self.assertEqual(s['pairs'], 617*s['allocations'])
                self.assertGreaterEqual(s['guards'], s['pairs'])
                if s['allocations']:
                    self.assertGreater(s['stores'], s['pairs'])
                    self.assertGreater(s['calls'], 0)

    def test_completion_markers_required(self):
        for marker in ('PSPORT_LIMIT', 'PSPORT_ARITHMETIC_PASS', 'PSPORT_COUNTER_PASS',
                       'PSPORT_EXPERIMENT_COMPLETE', 'QEMU_AAC_FORMAT_PASS', 'QEMU_SMOKE_PASS'):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                port.parse_log(self.logs['synthetic'].replace(marker, 'REMOVED'))

    def test_missing_or_duplicate_records_rejected(self):
        for kind in ('RESULT', 'STORAGE', 'STATS', 'HIST', 'EXTERNAL'):
            log = self.logs['abba64']
            line = next(s for s in log.splitlines(True) if f'PSPORT_{kind} ' in s)
            for changed in (log.replace(line, '', 1), log + line):
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    port.parse_log(changed)

    def test_false_memory_saving_and_lost_guards_rejected(self):
        log = self.logs['abba64']
        for old, new in (('heap_saved=0', 'heap_saved=2468'), ('guards=617', 'guards=616'),
                         ('pairs=617', 'pairs=616'), ('packed_payload=2468', 'packed_payload=0')):
            self.assertIn(old, log)
            with self.subTest(old=old), self.assertRaises(ValueError):
                port.parse_log(log.replace(old, new, 1))

    def test_corrupt_precision_and_native_controls_rejected(self):
        log = self.logs['abba64']
        for pattern, replacement in ((r'over_two=[1-9]\d*', 'over_two=0'),
                                     (r'max_l=0', 'max_l=1'),
                                     (r'changed_qmf=[1-9]\d*', 'changed_qmf=0'),
                                     (r'precision=PASS', 'precision=FAIL')):
            changed = re.sub(pattern, replacement, log, count=1)
            self.assertNotEqual(changed, log)
            with self.subTest(pattern=pattern), self.assertRaises(ValueError):
                port.parse_log(changed)


if __name__ == '__main__':
    unittest.main()
