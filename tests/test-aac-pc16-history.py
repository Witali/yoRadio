#!/usr/bin/env python3
"""Validate PC16 decoder measurements and protect both accuracy gates."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
import run_aac_pc16_history as experiment
from run_aac_bfp16 import sha256

EVIDENCE = ROOT / 'tests/results/esp32c3-aac-pc16-history-20261001'
NAMES = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')


class Pc16HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logs = {n: (EVIDENCE/n/'qemu.log').read_text() for n in NAMES}
        cls.data = {n: json.loads((EVIDENCE/n/'result.json').read_text()) for n in NAMES}

    def test_all_201_comparisons_reparse_and_match_hashes(self):
        for name in NAMES:
            parsed = experiment.parse_log(self.logs[name])
            for k,v in parsed.items(): self.assertEqual(v,self.data[name][k], (name,k))
            self.assertEqual(sha256(EVIDENCE/name/'qemu.log'),self.data[name]['provenance']['qemu_log_sha256'])
        self.assertEqual(sum(len(d['runs']) for d in self.data.values()),201)

    def test_development_passes_but_two_lsb_gate_still_fails(self):
        for name,d in self.data.items():
            self.assertTrue(d['precision_pass'])
            self.assertEqual(d['production_precision_pass'],name not in ('synthetic','abba64','groovesalad16'))
            self.assertEqual(d['ram_saved_bytes'],0)
            self.assertEqual(d['theoretical_history_payload_saving_bytes_hev2'],4188)
        for name,count in (('synthetic',1),('abba64',96),('groovesalad16',34)):
            s=next(s for s in self.data[name]['summaries'] if s['variant']==3 and (name!='synthetic' or s['case'].startswith('hev2')))
            self.assertEqual(s['max_pcm_error_lsb'],3)
            self.assertEqual(s['over_two_per_run'],[count]*3)

    def test_block_and_scalar_coverage_and_zero_saturation(self):
        for d in self.data.values():
            for q in d['quantization']:
                self.assertEqual(q['saturated'],0)
                self.assertEqual(q['zero_to_nonzero'],0)
            for b in d['block_coverage']:
                if b['variant']<=3:self.assertEqual(b['scalar_pairs'],0)
                else:self.assertEqual(b['blocks8'],0)
        self.assertGreater(sum(b['blocks8'] for b in self.data['abba64']['block_coverage']),0)
        self.assertGreater(sum(b['tail_pairs'] for b in self.data['abba64']['block_coverage']),0)
        self.assertGreater(sum(h['ps_frames'] for h in self.data['abba64']['history']),0)

    def test_controls_and_inactive_histories_are_distinguished(self):
        for name in ('groovesalad32','groovesalad64','groovesalad128'):
            self.assertFalse(self.data[name]['quantization_exercised'])
        for d in self.data.values():
            for r in d['runs']:
                if r['variant'] in (0,7):self.assertEqual(r['different'],0)

    def test_missing_duplicate_or_fake_block_coverage_is_rejected(self):
        log=self.logs['abba64']
        line=next(l for l in log.splitlines(True) if 'PCX16_BLOCKS' in l)
        for corrupt in (log.replace(line,'',1),log+line,re.sub(r'blocks8=[1-9]\d*','blocks8=0',log,count=1)):
            with self.assertRaises(ValueError):experiment.parse_log(corrupt)

    def test_arithmetic_completion_and_format_identity_required(self):
        for marker in ('PCX16_ARITHMETIC_PASS','PCX16_EXPERIMENT_COMPLETE','QEMU_AAC_FORMAT_PASS'):
            with self.assertRaises(ValueError):experiment.parse_log(self.logs['synthetic'].replace(marker,'MISSING'))
        with self.assertRaises(ValueError):experiment.parse_log(self.logs['synthetic'].replace('PCX16_','PCX14_'))

    def test_falsified_two_lsb_count_is_rejected(self):
        with self.assertRaises(ValueError):
            experiment.parse_log(re.sub(r'over_two=[1-9]\d*','over_two=0',self.logs['abba64'],count=1))


if __name__=='__main__':unittest.main()
