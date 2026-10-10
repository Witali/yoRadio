import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from tls_path import STAGES, snapshots, summarize


def rows():
    result = []
    for seq in range(1, 5):
        for stage in STAGES:
            result.append(dict(at=seq * 5., line=f'PERF TLS_PATH: seq={seq} at_us={seq*5000000} '
                f'stage={stage} calls={seq*2} elapsed_us={seq*100} max_us=50 requested={seq*16} '
                f'completed={seq*16} ok={seq} zero=0 retry={seq} errors=0 le1024={seq*2} le4096=0 le16384=0 larger=0'))
    return result


class Tests(unittest.TestCase):
    def test_inclusive_deltas(self):
        result = summarize(rows(), 0, 21)
        self.assertEqual(result['observed_seconds'], 15)
        self.assertTrue(result['coverage_complete'])
        for stage in STAGES:
            s = result['stages'][stage]
            self.assertEqual(s['delta']['calls'], 6)
            self.assertEqual(s['mean_call_us'], 50)
            self.assertEqual(s['inclusive_wall_percent'], .002)

    def test_corrupt_or_missing_evidence(self):
        for change in (
            lambda r: r.pop(),
            lambda r: r.pop(6),
            lambda r: r.insert(1, copy.deepcopy(r[0])),
            lambda r: r.__setitem__(3, dict(at=5, line='PERF TLS_PATH: seq=1')),
            lambda r: r.__setitem__(3, dict(at=5, line='serial capture interrupted')),
            lambda r: r[0].update(line=r[0]['line'].replace('ok=1', 'ok=9')),
            lambda r: r[0].update(line=r[0]['line'].replace('le1024=2', 'le1024=9')),
            lambda r: r[0].update(line=r[0]['line'].replace('completed=16', 'completed=100')),
            lambda r: r[0].update(line=r[0]['line'].replace('max_us=50', 'max_us=101')),
            lambda r: r[5].update(line=r[5]['line'].replace('seq=2', 'seq=3')),
            lambda r: r[5].update(line=r[5]['line'].replace('at_us=10000000', 'at_us=1')),
            lambda r: r[0].update(at=float('nan')),
        ):
            with self.subTest(change=change):
                data = rows(); change(data)
                with self.assertRaises(ValueError):
                    snapshots(data)

    def test_insufficient_and_gap(self):
        with self.assertRaises(ValueError):
            summarize(rows(), 14, 21)
        result = summarize(rows(), -20, 21)
        self.assertFalse(result['coverage_complete'])

    def test_counter_reset(self):
        data = rows()
        data[5]['line'] = data[5]['line'].replace('elapsed_us=200', 'elapsed_us=50')
        with self.assertRaises(ValueError):
            snapshots(data)


if __name__ == '__main__':
    unittest.main()
