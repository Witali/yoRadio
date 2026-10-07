"""Validate retained heap/TCP evidence, incomplete captures and failed HE starts."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'tests/results/esp32c3-heap-layout-20261001'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import Failure, check_playback, fixtures

spec = importlib.util.spec_from_file_location('heap_analysis', RESULT/'analyze.py')
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def read(path):
    return json.loads(path.read_text())


class HeapEvidence(unittest.TestCase):
    def test_image_config_and_source_fingerprints(self):
        for variant in ('esp32c3-heap-layout', 'esp32c3-heap-tcp'):
            folder = ROOT/'firmware/development'/variant
            manifest = read(folder/'manifest.json')
            for name, expected in manifest['files'].items():
                data = (folder/name).read_bytes()
                self.assertEqual(len(data), expected['bytes'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), expected['sha256'])
            for name, expected in manifest['source_sha256'].items():
                source = manifest.get('source_snapshots', {}).get(name, name)
                self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(), expected, name)
        for name in ('inventory.json', 'tcp-inventory.json'):
            for row in read(RESULT/name)['builds']:
                self.assertEqual((row['iram_reserved'], row['dram_data'], row['dram_bss']),
                                 (43520, 12620, 31368))

    def test_raw_analysis_reproduces_with_incomplete_snapshots_excluded(self):
        for run, count, tcp_count in (('switch', 40, 0), ('tcp-switch', 36, 946)):
            value = analysis.summarize(RESULT/run/'performance.json')
            self.assertEqual(value, read(RESULT/run/'topology.json'))
            self.assertEqual(len(value['snapshots']), count)
            self.assertEqual(len(value['tcp_events']), tcp_count)
            incomplete = [s for s in value['snapshots'] if not s['selection_complete']]
            self.assertEqual(len(incomplete), 1)
            self.assertLess(incomplete[0]['received'], incomplete[0]['selected'])
            self.assertIsNone(incomplete[0]['raw_largest_free'])
            self.assertEqual(incomplete[0]['dividers'], [])

    def test_tcp_lifetime_confirms_divider_not_just_size(self):
        value = read(RESULT/'tcp-switch/topology.json')
        matches = [d for s in value['snapshots'] for d in s['dividers']
                   if d['block']['address'] == '0x3fcc6d74' and d['tcp_free_seen']]
        self.assertTrue(matches)
        for d in matches:
            self.assertEqual(d['block']['bytes'], 168)
            self.assertEqual(d['next_tcp_event']['state'], 10)
            self.assertEqual(d['next_tcp_event']['operation'], 'free')
        control = read(RESULT/'switch/topology.json')
        self.assertFalse(any(d['tcp_free_seen'] for s in control['snapshots'] for d in s['dividers']))

    def test_first_cycle_failures_are_preserved(self):
        specs = fixtures()
        for run in ('switch', 'tcp-switch'):
            failed, passed = [], 0
            for batch in read(RESULT/run/'status.json'):
                if not batch['case'].startswith('switch:'):
                    continue
                _, cycle, name = batch['case'].split(':')
                try:
                    check_playback(batch['samples'], specs[name])
                    passed += 1
                except Failure:
                    failed.append((int(cycle), name))
            self.assertEqual(passed, 19)
            self.assertEqual(failed, [(0, 'he-48000-stereo'), (0, 'hev2-44100-stereo')])
            cases = read(RESULT/run/'report.json')['cases']
            self.assertEqual(cases[0]['result'], 'FAIL')
            self.assertTrue(all(c['result'] == 'PASS' for c in cases[1:]))
            self.assertTrue(cases[-1]['evidence']['rebooted'])


if __name__ == '__main__':
    unittest.main()
