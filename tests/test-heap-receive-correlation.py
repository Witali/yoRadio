"""Pair asynchronous telemetry without hiding omissions or inventing RAM owners."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from heap_receive_correlation import paired_metrics, inspect

spec = importlib.util.spec_from_file_location('network_tests', ROOT/'tests/test-esp32c3-network-memory.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def samples():
    rows = []
    for seq, at in enumerate((11., 16., 21., 26.), 1):
        rows.append(helpers.row(at, seq, heap=10000-seq*100, blocks=40+seq))
        rows.append(dict(at=at+5.03, line=f'PERF NET_RX: seq={seq} age_ms=5000 '
                         f'window={5000-seq*100} maximum=5000 refused=100'))
    return rows


class PairedHeapTests(unittest.TestCase):
    def test_same_snapshot_ignores_log_skew_and_refused_overlap(self):
        rows = samples()
        original = copy.deepcopy(rows)
        result = paired_metrics(rows, 10, 30)
        self.assertTrue(result['metrics_available'])
        self.assertAlmostEqual(result['heap_credit_pearson_r'], -1)
        self.assertEqual(result['ranges']['uncredited']['median'], 250)
        self.assertEqual(rows, original)

    def test_missing_duplicate_stale_and_mismatched_samples(self):
        for change in ('missing', 'pair', 'stale', 'gap', 'missed'):
            with self.subTest(change=change):
                rows = samples()
                if change == 'missing': del rows[3]
                if change == 'pair': rows[3]['line'] = rows[3]['line'].replace('age_ms=5000', 'age_ms=4999')
                if change == 'stale':
                    for r in rows[2:4]:
                        r['line'] = r['line'].replace('age_ms=5000', 'age_ms=12000')
                        r['at'] += 7
                if change == 'gap': del rows[2:4]
                if change == 'missed': rows[2]['line'] = rows[2]['line'].replace('missed=0', 'missed=1')
                result = paired_metrics(rows, 10, 30)
                self.assertFalse(result['metrics_available'])
                self.assertNotIn('heap_credit_pearson_r', result)
        rows = samples()
        with self.assertRaises(ValueError): paired_metrics(rows+[rows[0]], 10, 30)

    def test_constant_values_and_malformed_capture(self):
        rows = samples()
        for i in range(1, len(rows), 2):
            rows[i]['line'] = rows[i]['line'].split('window=')[0]+'window=5000 maximum=5000 refused=0'
        self.assertIsNone(paired_metrics(rows, 10, 30)['heap_credit_pearson_r'])
        rows[1]['line'] = rows[1]['line'].replace('refused=0', '')
        with self.assertRaises(ValueError): paired_metrics(rows, 10, 30)

    def test_real_archives_preserve_failure_and_complete_pairing(self):
        root = ROOT/'tests/results/esp32c3-qio80-recheck-20261008/physical'
        for mode in ('dio','qio'):
            result = inspect(root/mode/'hev2-ten-minutes', 'hev2-44100-stereo')
            self.assertTrue(result['paired']['metrics_available'], result['paired']['issues'])
            self.assertGreater(result['paired']['count'], 110)
            self.assertLess(result['paired']['heap_credit_pearson_r'], -.98)
            failed = next(c for c in result['acceptance'] if c['name'].startswith('cpu-under'))
            self.assertEqual(failed['result'], 'FAIL')


if __name__ == '__main__': unittest.main()
