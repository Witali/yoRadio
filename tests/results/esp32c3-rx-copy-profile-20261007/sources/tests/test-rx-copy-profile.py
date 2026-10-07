from pathlib import Path
import struct
import sys
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from rx_copy_profile import WIRE_FIELDS, analyze, window


def row(at=1, **updates):
    values = dict.fromkeys(WIRE_FIELDS, 0)
    values.update(sequence=1, allocations=10, releases=8, live=2, peak=3,
                  bytes=2100, peak_bytes=3300, max_frame=1080, pbuf_bytes=16, capacity=64,
                  class2_allocations=10, class2_live=2, class2_peak=3)
    values.update(updates)
    words = [values[k] for k in WIRE_FIELDS]
    crc = zlib.crc32(struct.pack('<28I', *words))
    return dict(at=at, line='I (5000) rx_copy: PERF RX_COPY: '+','.join(map(str, words))+f',{crc:08x}\x1b[0m')


class CopyProfileTests(unittest.TestCase):
    def test_balanced_lifetimes_and_window(self):
        rows = [row(), row(at=6, sequence=2, allocations=20, releases=18, class2_allocations=20)]
        result = analyze(rows)
        self.assertTrue(result['sizing_valid'])
        self.assertEqual(result['classes'][2]['live'], 2)
        summary = window(result['snapshots'], 0, 10)
        self.assertTrue(summary['coverage_complete'])
        self.assertEqual(summary['delta']['allocations'], 10)
        self.assertEqual(summary['classes'][2]['arrivals'], 10)
        self.assertEqual(summary['peak_since_boot']['peak'], 3)

    def test_host_oracle_records(self):
        # Actual SDK pbuf/mem host test output, with an independently written C CRC.
        records = ['1,14,14,0,2,0,1632,0,0,0,1601,24,64,4,0,1,3,0,1,3,0,1,3,0,1,1,0,1,1e10e283',
                   '2,4014,4014,0,4,0,4136,0,0,0,1601,24,64,120,0,2,1539,0,4,2351,0,4,3,0,1,1,0,1,483f9e8a']
        result = analyze([dict(at=i*5, line='PERF RX_COPY: '+s) for i, s in enumerate(records)])
        self.assertEqual(result['cumulative_at_last_snapshot']['releases'], 4014)

    def test_bad_record_never_silently_dropped(self):
        original = row()
        for line in [original['line'][:-8], original['line'].replace('1,10,8', '1,10,9'),
                     original['line']+original['line'], original['line'].replace('COPY:', 'COPY'),
                     original['line'].replace('1,10', '4294967296,10'),
                     'serial capture interrupted']:
            with self.subTest(line=line), self.assertRaises(ValueError):
                analyze([original, dict(at=6, line=line)])

    def test_invalid_accounting(self):
        for changes in [dict(lost=1), dict(releases=9), dict(live=4), dict(peak=1),
                        dict(bytes=0), dict(bytes=4000), dict(class2_live=1),
                        dict(class2_peak=4), dict(class2_allocations=11), dict(capacity=32),
                        dict(pbuf_bytes=0), dict(sequence=0), dict(max_frame=65536),
                        dict(rejected=11)]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                analyze([row(**changes)])

    def test_regression_missing_reset_and_nonfinite_time(self):
        for changes in [dict(sequence=1), dict(sequence=3), dict(at=0), dict(at=float('nan')),
                        dict(peak=2, class2_peak=2), dict(max_frame=100), dict(peak_bytes=2200),
                        dict(pbuf_bytes=20), dict(allocations=9, releases=7, class2_allocations=9)]:
            values = dict(at=6, sequence=2); values.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                analyze([row(), row(**values)])
        with self.assertRaises(ValueError):
            analyze([])

    def test_failures_retained_and_invalid_for_sizing(self):
        for changes in [dict(failed=1), dict(rejected=1)]:
            result = analyze([row(**changes)])
            self.assertFalse(result['sizing_valid'])
            self.assertTrue(result['accounting_complete'])
            for key, value in changes.items():
                self.assertEqual(result['faults'][key], value)

    def test_window_coverage_required(self):
        snapshots = analyze([row(), row(at=30, sequence=2)])['snapshots']
        self.assertFalse(window(snapshots, 0, 35)['coverage_complete'])
        self.assertFalse(window(snapshots, 40, 50)['coverage_complete'])
        for bounds in [(1, 1), (2, 1), (0, float('nan'))]:
            with self.assertRaises(ValueError):
                window(snapshots, *bounds)


if __name__ == '__main__':
    unittest.main()
