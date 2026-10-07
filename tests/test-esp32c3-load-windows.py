"""Failed and interrupted load cases must not inherit the next codec's metrics."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from load_windows import summarize


def cpu(at, heap=9000):
    return dict(at=at, line=f'PERF CPU: busy=65.0% idle=35.0% heap={heap} largest=4096')


def report():
    return dict(cases=[dict(name='cpu-under-http-load:one', result='FAIL', reason='TimeoutError')])


def batch(start=10, end=12):
    return dict(case='load:one', started_at=start, ended_at=end, samples=[])


class LoadWindowsTests(unittest.TestCase):
    def test_failed_short_case_does_not_borrow_later_samples(self):
        data = report()
        original = copy.deepcopy(data)
        case = summarize(data, [batch()], [cpu(9), cpu(11), cpu(12, 8000), cpu(20, 7000)])['cases'][0]
        self.assertEqual(case['cpu']['ranges']['heap']['min'], 9000)
        self.assertEqual(len(case['cpu']['samples']), 1)
        self.assertEqual(case['acceptance']['result'], 'FAIL')
        self.assertFalse(case['receive']['available'])
        self.assertEqual(data, original)

    def test_missing_timestamps_cannot_be_reconstructed(self):
        case = summarize(report(), [dict(case='load:one', samples=[])], [cpu(11)])['cases'][0]
        self.assertNotIn('cpu', case)
        self.assertTrue(case['issues'])

    def test_incomplete_cpu_is_visible_without_discarding_other_samples(self):
        rows = [cpu(11), dict(at=12, line='PERF CPU: busy=65.0% idle=35.0%')]
        case = summarize(report(), [batch(end=14)], rows)['cases'][0]
        self.assertEqual(len(case['cpu']['samples']), 1)
        self.assertIn('Incomplete', case['issues'][0])

    def test_delayed_receive_snapshot_is_selected_by_sample_time(self):
        rows = [dict(at=16, line='PERF NET_RX: seq=1 age_ms=5000 window=10000 maximum=23040 refused=0'),
                dict(at=18, line='PERF NET_RX: seq=2 age_ms=5000 window=9000 maximum=23040 refused=0')]
        case = summarize(report(), [batch()], rows)['cases'][0]
        self.assertEqual([s['seq'] for s in case['receive']['samples']], [1])
        self.assertEqual(case['receive']['ranges']['uncredited']['min'],13040)
        self.assertIn('unmatched snapshot', case['issues'][0])

    def test_bins_use_half_open_boundaries(self):
        case = summarize(report(), [batch(end=71)], [cpu(t) for t in (10,39,40,69,70,71)])['cases'][0]
        self.assertEqual([b['count'] for b in case['cpu']['bins']],[2,2,1])

    def test_overlapping_windows_are_rejected(self):
        data = report()
        data['cases'].append(dict(name='cpu-under-http-load:two', result='PASS'))
        with self.assertRaises(ValueError):
            summarize(data,[batch(),dict(batch(start=11,end=14),case='load:two')],[])


if __name__ == '__main__':
    unittest.main()
