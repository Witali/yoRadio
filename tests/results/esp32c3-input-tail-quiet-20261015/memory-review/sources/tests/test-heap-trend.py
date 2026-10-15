"""Exercise phase aliasing and genuine losses independently of board results."""
import sys
import json
import copy
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from heap_trend import heap_trend
from sustained_output import check_memory
from review_finite_memory import review


def samples(values):
    return [dict(uptime_ms=i*500, heap=v, largest=32768) for i,v in enumerate(values)]


class HeapTrendTests(unittest.TestCase):
    def test_periodic_phase_is_not_a_progressive_loss(self):
        values=([70000]*6+[61000]*3)*11
        result=heap_trend(samples(values))['fields']['heap']
        self.assertEqual(result['endpoint_loss'],9000)
        self.assertFalse(result['loss_detected'])

    def test_slope_and_loss_on_top_of_periodic_allocations(self):
        for values in ([70000-100*i for i in range(99)],
                       [70000-(9000 if i%9>=6 else 0)-(4000 if i>=66 else 0) for i in range(99)]):
            self.assertTrue(heap_trend(samples(values))['fields']['heap']['loss_detected'])

    def test_late_fall_below_initial_range_is_not_diluted(self):
        result=heap_trend(samples([70000]*96+[67000]*3))['fields']['heap']
        self.assertEqual(result['median_loss'],0)
        self.assertTrue(result['loss_detected'])

    def test_short_window_and_exact_tolerances(self):
        for loss in (2048,2049):
            result=heap_trend(samples([70000]*3+[70000-loss]*3))['fields']['heap']
            self.assertEqual(result['loss_detected'],loss>2048)

    def test_fragmentation_and_recovery(self):
        rows=samples([70000]*99)
        for row in rows[66:]:row['largest']-=5000
        self.assertTrue(heap_trend(rows)['fields']['largest']['loss_detected'])
        values=[70000]*33+[60000]*33+[70000]*33
        self.assertFalse(heap_trend(samples(values))['fields']['heap']['loss_detected'])

    def test_reject_sparse_invalid_or_repeated_times(self):
        for rows in (samples([70000]*5),samples([70000]*5+[-1]),samples([70000]*5+[True])):
            with self.assertRaises(Failure):heap_trend(rows)
        rows=samples([70000]*6);rows[-1]['uptime_ms']=rows[-2]['uptime_ms']
        with self.assertRaises(Failure):heap_trend(rows)

    def test_real_flac_retains_original_failures_and_independent_gates(self):
        directory=Path(__file__).resolve().parent/'results/esp32c3-input-tail-quiet-20261015/public-files/public-files'
        result=review(directory)
        failed=[c['name'] for c in result['original_cases'] if c['result']=='FAIL']
        self.assertEqual(failed,['https:flac:auto','https:flac:flac'])
        self.assertEqual(len(result['files']),6)
        for case in result['files']:
            self.assertTrue(all(c['result']=='PASS' for c in case['checks'].values()),case['case'])
        all_health=json.loads((directory/'health.json').read_text())
        for case in result['files'][:2]:
            window=case['window']
            rows=[h for h in all_health if window['first_at']<=h['at']<=window['last_at']]
            self.assertGreater(check_memory(rows)['trend']['fields']['heap']['endpoint_loss'],8000)
            for key,loss in (('heap',4096),('largest',8192)):
                damaged=copy.deepcopy(rows)
                for row in damaged[-len(rows)//3:]:row[key]-=loss
                with self.subTest(case=case['case'],key=key),self.assertRaises(Failure):
                    check_memory(damaged)


if __name__=='__main__':unittest.main()
