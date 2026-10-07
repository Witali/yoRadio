"""Regression tests for delayed network snapshots and unchanged acceptance."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from network_memory import FIELDS, parse_snapshot, parse_receive_snapshot, summarize


def row(sample_at, sequence, age_ms=5000, **changes):
    values = dict(seq=sequence, age_ms=age_ms, heap=10000, largest=4096, used=5000,
                  blocks=40, free_blocks=5, active=2, tw=10, bound=0, listen=1,
                  tx_segments=1, tx_bytes=100, rx_segments=0, rx_bytes=0, missed=0, walk_us=60)
    values.update(changes)
    return dict(at=sample_at+age_ms/1000,
                line='I (12345) net_heap: PERF NET_HEAP: '+' '.join(f'{k}={values[k]}' for k in FIELDS))


def report():
    return dict(cases=[dict(name='http:stream', result='FAIL', reason='Progressive heap loss')],
                windows={'stream':dict(start=10, end=30)})


class NetworkMemoryTests(unittest.TestCase):
    def test_receive_credit_is_optional_delayed_and_not_added_to_refused(self):
        self.assertIsNone(parse_receive_snapshot(row(12, 1)))
        value = parse_receive_snapshot(dict(at=17,
            line='PERF NET_RX: seq=1 age_ms=5000 window=15000 maximum=23040 refused=1440'))
        self.assertEqual(value['sample_at'], 12)
        self.assertEqual(value['uncredited'], 8040)
        self.assertEqual(value['refused'], 1440)

    def test_invalid_receive_credit_is_rejected(self):
        good = 'PERF NET_RX: seq=1 age_ms=5000 window=10000 maximum=23040 refused=0'
        for line in (good.replace(' refused=0',''), good.replace('window=10000','window=99999'),
                     good.replace('seq=1','seq=0'), good.replace('refused=0','refused=-1'),
                     good.replace('refused=0','maximum=0'), good.replace('maximum=23040',f'maximum={2**32}')):
            with self.subTest(line=line), self.assertRaises(ValueError):
                parse_receive_snapshot(dict(at=17, line=line))

    def test_delayed_sample_and_failed_acceptance_preserved(self):
        data = report()
        original = copy.deepcopy(data)
        result = summarize(data, [], [row(8, 1), row(12, 2), row(17, 3), row(22, 4), row(27, 5), row(32, 6)])
        case = result['cases'][0]
        self.assertEqual([s['seq'] for s in case['samples']], [2, 3, 4, 5])
        self.assertTrue(case['metrics_available'])
        self.assertEqual(case['acceptance'], original['cases'][0])
        self.assertEqual(data, original)
        self.assertEqual(case['ranges']['heap']['median'], 10000)

    def test_sequence_gap_and_missed_callback_are_visible(self):
        case = summarize(report(), [], [row(12, 2), row(17, 4, missed=1), row(27, 5, missed=1)])['cases'][0]
        self.assertFalse(case['metrics_available'])
        self.assertIn('Nonconsecutive snapshot sequence', case['issues'])
        self.assertIn('Missed-callback counter changed', case['issues'])

    def test_wait_warning_without_ready_snapshot(self):
        rows = [row(12, 2), row(17, 3), row(27, 4), dict(at=20, line='PERF NET_HEAP_WAIT: pending=1 missed=1')]
        self.assertFalse(summarize(report(), [], rows)['cases'][0]['metrics_available'])

    def test_stale_snapshot_and_large_interval(self):
        case = summarize(report(), [], [row(12, 2, age_ms=12000), row(25, 3), row(29, 4)])['cases'][0]
        self.assertIn('Stale network heap sample', case['issues'])
        self.assertIn('Missing or unordered sample interval', case['issues'])

    def test_incomplete_duplicate_negative_and_invalid_counters_rejected(self):
        good = row(12, 1)
        for line in (good['line'].replace(' tw=10', ''), good['line'].replace('tw=10', 'active=10'),
                     good['line'].replace('tw=10', 'tw=-1')):
            with self.subTest(line=line), self.assertRaises(ValueError):
                parse_snapshot(dict(at=17, line=line))
        for change in (dict(largest=10001), dict(seq=0), dict(blocks=2**32)):
            with self.subTest(change=change), self.assertRaises(ValueError):
                parse_snapshot(row(12, 1, **change))

    def test_missing_metrics_do_not_change_acceptance(self):
        case = summarize(report(), [], [])['cases'][0]
        self.assertFalse(case['metrics_available'])
        self.assertEqual(case['acceptance']['result'], 'FAIL')

    def test_overlapping_windows_rejected(self):
        data = report()
        data['cases'].append(dict(name='https:second', result='PASS'))
        data['windows']['second'] = dict(start=29, end=40)
        with self.assertRaises(ValueError):
            summarize(data, [], [])

    def test_bin_boundaries_and_webui_ranges(self):
        data = report()
        data['windows']['stream']['end'] = 70
        states = [dict(case='stream', samples=[dict(rssi=-60, request_ms=40, audio=True), dict(rssi=-70, request_ms=80, audio=False)])]
        case = summarize(data, states, [row(s, i+1) for i, s in enumerate(range(10, 70, 5))])['cases'][0]
        self.assertTrue(case['metrics_available'])
        self.assertEqual([b['count'] for b in case['bins']], [6, 6])
        self.assertEqual(case['webui']['rssi']['rssi']['median'], -65)
        self.assertEqual(case['webui']['audio_active'], 1)


if __name__ == '__main__':
    unittest.main()
