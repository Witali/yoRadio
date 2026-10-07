"""Recompute the physical scheduling comparison and preserve its limits."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'tests/results/esp32c3-output-priority-20261006'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from compare_output_priority import compare
from compare_output_priority_matrix import compare as compare_matrix
from output_priority_matrix import LOAD, SHORT


def read(name):
    return json.loads((EVIDENCE/name).read_text())


class PriorityEvidence(unittest.TestCase):
    def test_integrity(self):
        for name, spec in read('manifest.json').items():
            data = (EVIDENCE/name).read_bytes()
            self.assertEqual(len(data), spec['bytes'], name)
            self.assertEqual(hashlib.sha256(data).hexdigest(), spec['sha256'], name)

    def test_recomputed_comparison(self):
        self.assertEqual(compare(EVIDENCE/'control', EVIDENCE/'board'), read('comparison.json'))

    def test_measured_improvement(self):
        for case in read('comparison.json')['cases']:
            before, after = case['control'], case['candidate']
            for side in (before, after):
                self.assertGreater(side['flow_output']['observed_seconds'], 40)
                self.assertFalse(side['flow_output']['malformed'])
            if case['name'].endswith('lpc32'):
                self.assertLess(after['flow_output']['overruns_per_second'],
                                before['flow_output']['overruns_per_second']/2)
                self.assertGreater(after['decoder']['audio_wall_ratio'],
                                   before['decoder']['audio_wall_ratio'])
                self.assertLess(after['flow_output']['dma']['max_us'],
                                before['flow_output']['dma']['max_us'])

    def test_identity_and_rollback(self):
        build = read('firmware/manifest.json')
        self.assertEqual(build['elf_sha256'], read('board/report.json')['board']['app_elf_sha256'])
        self.assertEqual(build['task_priorities'], dict(stream=5, decoder=7, output=8))
        self.assertFalse(build['production_qualified'])
        boot = [r['line'] for r in read('ota/performance.json') if 'PERF FLOW_CONFIG:' in r['line']]
        self.assertTrue(any('stream_priority=5 decode_priority=7 output_priority=8' in s for s in boot))
        for folder in ('ota', 'restore'):
            case = read(folder+'/report.json')['cases'][0]
            self.assertEqual(case['result'], 'PASS')
            self.assertTrue(case['evidence']['wifi_unchanged'])
            self.assertTrue(case['evidence']['settings_unchanged'])
        restored = read('restore/report.json')['cases'][0]['evidence']['after']['app_elf_sha256']
        self.assertEqual(restored, read('ota/report.json')['board']['app_elf_sha256'])

    def test_matrix_recomputed_and_complete(self):
        self.assertEqual(compare_matrix(EVIDENCE/'matrix-control', EVIDENCE/'matrix-candidate'),
                         read('matrix-comparison.json'))
        expected = ['idle-baseline']
        for name in LOAD:
            expected.extend(prefix+name for prefix in
                            ('cpu-under-http-load:', 'idle-after:', 'stop-recovery:'))
        expected.extend('file-eof:'+name for name in SHORT)
        expected.extend(('stop-play-generation', 'switching-and-heap', 'runtime', 'restore-board'))
        for folder, priority in [('matrix-control', 6), ('matrix-candidate', 8)]:
            report = read(folder+'/report.json')
            self.assertEqual(report['output_priority'], priority)
            self.assertEqual([c['name'] for c in report['cases']], expected)
            self.assertTrue(all(c['result'] in ('PASS', 'FAIL', 'BLOCKED') for c in report['cases']))
        for side in ('control', 'candidate'):
            for case in read('matrix-comparison.json')[side]['cases']:
                self.assertGreater(case['cpu']['observed_seconds'], 20)
                self.assertGreaterEqual(len(case['decoder_windows']), 4)
                self.assertFalse(case['cpu_malformed'])
                self.assertFalse(case['cpu_gaps'])

    def test_profile_off_candidate_identity(self):
        build = read('firmware-off/manifest.json')
        self.assertEqual(build['elf_sha256'], read('matrix-candidate/report.json')['board']['app_elf_sha256'])
        self.assertEqual(build['task_priorities'], dict(stream=5, decoder=7, output=8))
        self.assertFalse(build['pipeline_profile']['enabled'])
        self.assertTrue(build['pipeline_profile']['diagnostic_symbols_absent'])
        self.assertTrue(build['hardware_tested'])
        case = read('ota-candidate/report.json')['cases'][0]
        self.assertEqual(case['result'], 'PASS')
        self.assertTrue(case['evidence']['wifi_unchanged'])
        self.assertTrue(case['evidence']['settings_unchanged'])
        self.assertEqual(case['evidence']['after']['app_elf_sha256'], build['elf_sha256'])
        control = read('firmware-control-off/manifest.json')
        self.assertEqual(control['sections'], build['sections'])
        self.assertEqual(control['app_bytes'], build['app_bytes'])
        self.assertEqual(control['codec_sha256'], build['codec_sha256'])
        self.assertEqual(control['layout_sha256'], build['layout_sha256'])
        self.assertEqual(read('verify-off/matched-control.json')['configuration_delta'],
                         dict(CONFIG_YORADIO_OUTPUT_TASK_FIRST=['unset', 'y']))

    def test_interrupted_run_is_not_a_completed_matrix(self):
        report = read('matrix-control-interrupted/report.json')
        self.assertFalse(read('matrix-control-interrupted/termination.json')['completed'])
        self.assertNotIn('restore-board', [c['name'] for c in report['cases']])
        self.assertEqual(len([c for c in report['cases'] if c['name'].startswith('cpu-under-http-load:')]), 7)


if __name__ == '__main__':
    unittest.main()
