#!/usr/bin/env python3
"""The production gate is three PCM units, with historical evidence preserved."""
import json
import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import aac_precision as policy
import assess_aac_precision as assessment
import run_aac_qmf_storage as qmf
import run_aac_ps_storage as ps
import run_aac_area_storage as areas


class PrecisionPolicyTests(unittest.TestCase):
    def test_three_units_not_three_bits(self):
        self.assertEqual((policy.PRODUCTION_LIMIT, policy.DEVELOPMENT_LIMIT), (3, 5))
        self.assertTrue(policy.passes([dict(max_l=3, max_r=3)], policy.PRODUCTION_LIMIT))
        for error in (4, 5, 7):
            self.assertFalse(policy.passes([dict(max_l=0, max_r=error)], policy.PRODUCTION_LIMIT))

    def test_new_and_historical_headers(self):
        for value in (2, 3):
            self.assertEqual(policy.log_limits(f'X_LIMIT development=5 production={value}', 'X')['production'], value)
        for bad in ('', 'X_LIMIT development=5 production=4', 'X_LIMIT development=6 production=3',
                    'X_LIMIT development=5 production=3\nX_LIMIT development=5 production=3'):
            with self.assertRaises(ValueError):
                policy.log_limits(bad, 'X')

    def test_new_log_gate_uses_maximum(self):
        for kind, parser, label in (('qmf', qmf.parse_log, 'QMFSTORAGE'), ('ps', ps.parse_log, 'PSSTORAGE')):
            log = (ROOT/'tests/results/esp32c3-aac-storage18-20261002'/kind/'abba64/qemu.log').read_text()
            self.assertFalse(parser(log)['production_precision_pass'])
            if 'production=2' in log:
                current = log.replace('production=2', 'production=3')
            else:
                current = f'{label}_LIMIT development=5 production=3\n'+log
            result = parser(current)
            self.assertEqual(result['production_precision_limit_lsb'], 3)
            self.assertTrue(result['production_precision_pass'])
            self.assertTrue(any(r['over_two'] for r in result['runs']))

    def test_imdct_failure_remains_failure(self):
        log = (ROOT/'tests/results/esp32c3-aac-area-storage-20261002/synthetic/qemu.log').read_text()
        result = areas.parse_log(log.replace('production=2', 'production=3'))
        self.assertEqual(result['production_precision_limit_lsb'], 3)
        self.assertFalse(result['production_precision_pass'])
        self.assertFalse(result['precision_pass'])

    def test_actual_current_firmware_run(self):
        evidence = ROOT/'tests/results/esp32c3-aac-precision-20261002'
        log_path = evidence/'synthetic/qemu.log'
        result = json.loads((evidence/'synthetic/result.json').read_text())
        parsed = areas.parse_log(log_path.read_text())
        self.assertEqual(result['production_precision_limit_lsb'], 3)
        self.assertEqual(result['provenance']['qemu_log_sha256'],
                         hashlib.sha256(log_path.read_bytes()).hexdigest())
        for key, value in parsed.items():
            self.assertEqual(result[key], value, key)
        old = json.loads((ROOT/'tests/results/esp32c3-aac-area-storage-20261002/synthetic/result.json').read_text())
        # The gate changed; measured PCM errors and coverage did not.
        keys = ('case', 'variant', 'run', 'samples', 'max_l', 'max_r', 'over_two', 'over_limit')
        self.assertEqual([[row[k] for k in keys] for row in result['runs']],
                         [[row[k] for k in keys] for row in old['runs']])
        for name, item in json.loads((evidence/'implementation.json').read_text())['files'].items():
            self.assertEqual(hashlib.sha256((evidence/item['snapshot']).read_bytes()).hexdigest(),
                             item['sha256'], name)

    def test_reassessment_is_reproducible_and_not_release_approval(self):
        result = assessment.assess()
        saved = json.loads((ROOT/'tests/results/esp32c3-aac-precision-20261002/summary.json').read_text())
        self.assertEqual(result, saved)
        self.assertEqual(len(result['rows']), 18)
        rejected = [(r['kind'], r['name']) for r in result['rows'] if not r['production_precision_pass']]
        self.assertEqual(rejected, [('other_arrays', 'imdct_overlap')])
        self.assertTrue(all(not r['production_qualified'] for r in result['rows']))


if __name__ == '__main__':
    unittest.main()
