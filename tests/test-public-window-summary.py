import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from summarize_public_windows import summarize


class Windows(unittest.TestCase):
    def inputs(self):
        report = dict(board={}, cases=[dict(name='http:short', result='FAIL'), dict(name='http:next', result='PASS')],
                      windows=dict(short=dict(start=0, end=7), next=dict(start=8, end=50)))
        rows = [dict(at=t, line='Memory after first AAC') for t in (1, 9)]
        rows += [dict(at=t, line='PERF CPU: busy=40.0% decode=20.0% heap=12345 largest=8192')
                 for t in (6, 14, 19, 24, 29, 34, 39)]
        return report, [], rows

    def test_early_failure_never_uses_next_station(self):
        short, following = summarize(*self.inputs())['cases']
        self.assertFalse(short['metrics_available'])
        self.assertIsNone(short['busy_mean'])
        self.assertEqual([r['at'] for r in short['samples']], [6])
        self.assertTrue(following['metrics_available'])
        self.assertEqual(following['busy_mean'], 40)

    def test_reject_ambiguous_order_and_unproven_pass(self):
        report, status, rows = self.inputs()
        report['windows']['next']['start'] = 6
        with self.assertRaises(ValueError): summarize(report, status, rows)
        report, status, rows = self.inputs()
        report['cases'][0]['result'] = 'PASS'
        with self.assertRaises(ValueError): summarize(report, status, rows)

    def test_no_checkpoint_does_not_borrow_one(self):
        report, status, rows = self.inputs()
        report['cases'][1]['result'] = 'FAIL'
        out = summarize(report, status, [r for r in rows if r['at'] != 9])
        self.assertFalse(out['cases'][1]['metrics_available'])


if __name__ == '__main__': unittest.main()
