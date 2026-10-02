#!/usr/bin/env python3
"""Cumulative fidelity, saturation, union accounting and retained failures."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import run_aac_combined_storage as runner
import summarize_aac_combined as summary
EVIDENCE = ROOT/'tests/results/esp32c3-aac-combined-storage-20261002'


class CombinedStorageTests(unittest.TestCase):
    def test_all_saved_results(self):
        comparisons = 0
        for name in summary.NAMES:
            p = EVIDENCE/name
            saved = json.loads((p/'result.json').read_text())
            for key, value in runner.parse_log((p/'qemu.log').read_text()).items():
                self.assertEqual(saved[key], value, (name, key))
            self.assertEqual(hashlib.sha256((p/'qemu.log').read_bytes()).hexdigest(),
                             saved['provenance']['qemu_log_sha256'])
            self.assertEqual(saved['ram_saved_bytes'], 0)
            comparisons += len(saved['runs'])
        self.assertEqual(comparisons, 345)

    def test_evidence_hashes_and_summary(self):
        saved = json.loads((EVIDENCE/'summary.json').read_text())
        self.assertEqual(saved, summary.summarize(EVIDENCE))
        self.assertEqual((EVIDENCE/'TABLES.md').read_text(encoding='utf-8'), summary.table(saved))
        for name, item in json.loads((EVIDENCE/'implementation.json').read_text())['files'].items():
            self.assertEqual(hashlib.sha256((EVIDENCE/item['snapshot']).read_bytes()).hexdigest(),
                             item['sha256'], name)
        self.assertTrue(all(not r['production_qualified'] for r in saved['rows']))

    def test_all_16_bit_failure_is_retained(self):
        saved = json.loads((EVIDENCE/'summary.json').read_text())
        full16 = next(r for r in saved['rows'] if r['variant'] == 11)
        self.assertEqual(full16['max_pcm_error_lsb'], 10)
        self.assertFalse(full16['production_precision_pass'])
        # The real captures alone would have missed the synthetic failure.
        self.assertTrue(all(r['max_pcm_error_lsb'] <= 3 for r in full16['per_recording'] if r['input'] != 'synthetic'))

    def test_layout_does_not_add_overlapping_payload_savings(self):
        full18 = summary.memory_model(1)
        self.assertEqual(full18['naive_sum_bytes'], 21504)
        self.assertEqual(full18['estimated_persistent_saving_bytes'], 19308)
        mixed = summary.memory_model(13)
        self.assertEqual((mixed['left_channel_bytes'], mixed['right_channel_bytes']), (16960, 17060))
        self.assertEqual(mixed['right_channel_extra_for_ps_bytes'], 100)
        self.assertEqual(mixed['estimated_owner_bytes'], 34032)
        self.assertEqual(mixed['estimated_persistent_saving_bytes'], 21096)
        self.assertIsNone(mixed['extra_unpack_workspace_bytes'])
        self.assertEqual(mixed['measured_combined_heap_saving_bytes'], 0)

    def test_missing_duplicate_or_falsified_evidence_is_rejected(self):
        log = (EVIDENCE/'synthetic/qemu.log').read_text()
        for marker in ('AACCOMBINED_RESULT', 'AACCOMBINED_AREA', 'AACCOMBINED_PS',
                       'PSSTORAGE_STORAGE', 'AACCOMBINED_WINDOWS'):
            line = next(s for s in log.splitlines(True) if marker+' ' in s)
            for changed in (log.replace(line, '', 1), log+line):
                with self.subTest(marker=marker), self.assertRaises(ValueError):
                    runner.parse_log(changed)
        for old, new in (('saturated=0', 'saturated=1'), ('out_of_int16=0', 'out_of_int16=1'),
                         ('heap_saved=0', 'heap_saved=1000'), ('transform1=0', 'transform1=1')):
            with self.subTest(old=old), self.assertRaises(ValueError):
                runner.parse_log(log.replace(old, new, 1))

    def test_imdct_never_runs_and_controls_are_exact(self):
        for name in summary.NAMES:
            saved = json.loads((EVIDENCE/name/'result.json').read_text())
            self.assertFalse(any(r['calls'] for r in saved['areas'] if r['area'] == 3))
            self.assertFalse(any(r['different'] for r in saved['runs'] if r['variant'] in (0,8)))

    def test_standalone_area_regression(self):
        old = json.loads((ROOT/'tests/results/esp32c3-aac-area-storage-20261002/synthetic/result.json').read_text())
        new = json.loads((EVIDENCE/'area-regression/result.json').read_text())
        keys = ('case','variant','run','samples','max_l','max_r','different',
                'over_one','over_two','over_limit','changed_qmf')
        self.assertEqual([[r[k] for k in keys] for r in old['runs']],
                         [[r[k] for k in keys] for r in new['runs']])
        self.assertEqual(hashlib.sha256((EVIDENCE/'area-regression/qemu.log').read_bytes()).hexdigest(),
                         new['provenance']['qemu_log_sha256'])


if __name__ == '__main__':
    unittest.main()
