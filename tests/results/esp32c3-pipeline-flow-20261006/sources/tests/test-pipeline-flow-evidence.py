"""Check retained evidence without treating known load failures as success."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'tests/results/esp32c3-pipeline-flow-20261006'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from pipeline_flow import summarize


def read(path):
    return json.loads(path.read_text())


class Evidence(unittest.TestCase):
    def test_integrity(self):
        for name, spec in read(RESULT/'manifest.json').items():
            data = (RESULT/name).read_bytes()
            self.assertEqual(len(data), spec['bytes'], name)
            self.assertEqual(hashlib.sha256(data).hexdigest(), spec['sha256'], name)
        self.assertFalse(list(RESULT.rglob('*.bin')) + list(RESULT.rglob('*.flac')))

    def test_recompute(self):
        for folder in ('board', 'board-off'):
            self.assertEqual(summarize(RESULT/folder), read(RESULT/folder/'summary.json'))

    def test_control_and_original_failure_retained(self):
        report = read(RESULT/'board/report.json')
        cases = {c['name']: c for c in report['cases']}
        self.assertEqual(cases['load:radio-groovesalad-lpc12']['result'], 'FAIL')
        self.assertIn('heap', cases['load:radio-groovesalad-lpc12']['reason'])
        self.assertEqual(cases['control:input-jitter']['result'], 'PASS')
        summary = read(RESULT/'board/summary.json')['cases']
        for case in summary:
            self.assertFalse(case['flow_decoder']['malformed'])
            self.assertFalse(case['flow_output']['malformed'])
        control = summary[-1]
        self.assertGreater(control['flow_decoder']['input']['timeouts'], 0)
        self.assertGreater(control['flow_decoder']['input']['wall_percent'], 50)
        for name in ('radio-groovesalad', 'radio-indiepop'):
            pair = {c['name']: c for c in summary}
            low, high = pair['load:'+name+'-lpc12'], pair['load:'+name+'-lpc32']
            self.assertGreater(high['flow_output']['overruns'], low['flow_output']['overruns'])
            self.assertLess(high['decoder']['audio_wall_ratio'], low['decoder']['audio_wall_ratio'])
            self.assertEqual(high['flow_decoder']['pcm']['timeouts'], 0)

    def test_images_and_exact_pcm(self):
        for suffix in ('', '-off'):
            build = read(RESULT/('firmware'+suffix)/'manifest.json')
            board = read(RESULT/('board'+suffix)/'report.json')['board']
            self.assertEqual(build['elf_sha256'], board['app_elf_sha256'])
            self.assertFalse(build['production_qualified'])
        host = read(RESULT/'host-dma-profile/report.json')
        self.assertTrue(host['profile_pcm_identical'] and host['profile_metadata_identical'])
        self.assertEqual(host['variants']['staged'], host['variants']['dma-profile'])
        for folder in ('ota', 'ota-off'):
            self.assertEqual(read(RESULT/folder/'report.json')['cases'][0]['result'], 'PASS')


if __name__ == '__main__':
    unittest.main()
