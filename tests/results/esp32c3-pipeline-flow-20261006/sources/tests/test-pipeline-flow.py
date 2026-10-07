"""Queue profiling controls and complete-window statistics."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from pipeline_flow import flow_summary


def row(at, us, count, window=5_000_000):
    return dict(at=at, line=f'PERF FLOW_DEC: gen=2 codec=FLAC window_us={window} '
        f'input_us={us} input_n={count} input_timeouts=0 input_max={us} '
        'pcm_us=0 pcm_n=0 pcm_timeouts=0 pcm_max=0')


class Flow(unittest.TestCase):
    def test_full_intervals_and_weighted_wait(self):
        result = flow_summary([row(5, 100, 1), row(10, 1000, 1),
                               row(20, 2000, 2, 10_000_000), row(25, 1, 1)], 5, 20, 'DEC')
        self.assertEqual(result['observed_seconds'], 15)
        self.assertEqual(result['input']['count'], 3)
        self.assertEqual(result['input']['us'], 3000)
        self.assertEqual(result['input']['mean_us'], 1000)
        self.assertAlmostEqual(result['input']['wall_percent'], .02)

    def test_missing_and_malformed_are_not_zero_wait(self):
        broken = row(10, 100, 1)
        broken['line'] = broken['line'].replace('pcm_max=0', 'pcm_max=')
        result = flow_summary([broken, row(15, 6_000_000, 1)], 0, 20, 'DEC')
        self.assertEqual(len(result['malformed']), 2)
        self.assertNotIn('input', result)

    def test_observed_zero_is_preserved(self):
        result = flow_summary([row(10, 0, 0)], 0, 10, 'DEC')
        self.assertEqual(result['input']['wall_percent'], 0)
        self.assertEqual(result['input']['count'], 0)


if __name__ == '__main__':
    unittest.main()
