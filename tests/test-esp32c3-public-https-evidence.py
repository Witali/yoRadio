"""Validate retained physical failures without mistaking playing status for a pass."""
import json
from collections import Counter
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import check_recovery_heap
from summarize_public import inspect

RESULTS = ROOT/'tests/results/esp32c3-public-https-20261001'


class Evidence(unittest.TestCase):
    def test_exact_image_provenance_and_restoration(self):
        manifest = json.loads((ROOT/'firmware/development/esp32c3-tcp-pcb-pool-fixed/manifest.json').read_text())
        for name in ('load', 'http-comparison', 'http-light'):
            path = RESULTS/name
            report = json.loads((path/'report.json').read_text())
            self.assertEqual(report['image'], manifest['image'])
            restore = next(c for c in report['cases'] if c['name'] == 'restore')
            self.assertEqual(restore['result'], 'PASS')
            self.assertTrue(all(restore['evidence'].values()))
            summary = inspect(path)
            self.assertEqual(summary, json.loads((path/'summary.json').read_text()))
            self.assertFalse(summary['panic_or_capture_errors'])
            self.assertEqual(len(summary['reset_banners']), 1)
            self.assertIn('RTC_SW_CPU_RST', summary['reset_banners'][0]['line'])

    def test_sbr_failure_cannot_be_reported_as_full_rate_playback(self):
        for directory, failed in [('load', 3), ('http-comparison', 2)]:
            summary = inspect(RESULTS/directory)
            failures = [c for c in summary['cases'] if c['playback_result'] == 'FAIL']
            self.assertEqual(len(failures), failed)
            self.assertEqual(len(summary['allocation_failures']), failed)
            self.assertTrue(all('requested=55128 ' in r['line'] for r in summary['allocation_failures']))
            for case in failures:
                self.assertTrue(all(f.startswith('AAC PCM ') for f in case['observed_formats']))
                self.assertIn(case['reference']['profile'], ('HE-AAC', 'HE-AACv2'))

    def test_full_rate_alone_does_not_hide_runtime_starvation(self):
        summary = inspect(RESULTS/'http-light')
        case, = summary['cases']
        self.assertEqual(case['observed_formats'], ['HE-AAC 44.1 kHz stereo'])
        self.assertEqual(case['playback_result'], 'FAIL')
        self.assertLess(case['minimum_free'], 8192)
        self.assertLess(case['minimum_largest'], 4096)
        self.assertTrue(summary['allocation_failures'])
        requests = Counter(int(re.search(r'requested=(\d+)', r['line'])[1])
                           for r in summary['allocation_failures'])
        self.assertEqual(requests, {1700: 61, 1512: 1})
        for directory in ('http-comparison', 'http-light'):
            report = json.loads((RESULTS/directory/'report.json').read_text())
            cases = {c['name']: c for c in report['cases']}
            self.assertEqual(cases['idle:recovery']['result'], 'PASS')
            check_recovery_heap(cases['idle:baseline']['evidence']['samples'],
                                cases['idle:recovery']['evidence']['samples'])


if __name__ == '__main__':
    unittest.main()
