"""Prevent idle overruns, damaged captures and counter resets becoming passes."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from staged_dma import parse, summarize


def row(at, overruns, writes=100, written=204800, elapsed=2000, maximum=50, errors=0):
    return dict(at=at, line=f'I (10) audio_output: PERF STAGED_DMA: q_overruns={overruns} '
        f'writes={writes} written_bytes={written} write_us={elapsed} max_write_us={maximum} errors={errors}')


class StagedDma(unittest.TestCase):
    def test_active_delta_excludes_idle_and_keeps_late_service(self):
        rows = [row(0, 100), row(10, 150, 200), row(15, 152, 220), row(20, 155, 240), row(40, 900)]
        value = summarize(rows, 10, 21)
        self.assertEqual(value['delta']['q_overruns'], 5)
        self.assertEqual(value['delta']['writes'], 40)
        self.assertEqual(value['observed_seconds'], 10)
        self.assertTrue(value['coverage_complete'])
        self.assertFalse(value['acoustic_continuity_qualified'])

    def test_missing_intervals_stay_incomplete(self):
        value = summarize([row(10, 0), row(30, 0), row(35, 0)], 10, 35)
        self.assertFalse(value['coverage_complete'])
        self.assertEqual(value['maximum_sample_gap_seconds'], 20)

    def test_reset_duplicate_and_missing_samples_rejected(self):
        for rows in ([row(10, 4), row(15, 1), row(20, 2)],
                     [row(10, 0), row(10, 0), row(20, 0)], [row(10, 0)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                summarize(rows, 10, 20)

    def test_corrupt_rows_are_not_silently_ignored(self):
        valid = row(10, 0)
        for change in ('q_overruns=-1', 'q_overruns=4294967296', 'q_overruns=0 PERF CPU: busy=0'):
            broken = dict(valid, line=valid['line'].replace('q_overruns=0', change))
            with self.subTest(change=change), self.assertRaises(ValueError):
                summarize([broken, row(15, 0), row(20, 0), row(25, 0)], 15, 25)
        with self.assertRaises(ValueError):
            parse(row(float('nan'), 0))
        with self.assertRaises(ValueError):
            parse(row(10, 0, writes=1, errors=2))


if __name__ == '__main__':
    unittest.main()
