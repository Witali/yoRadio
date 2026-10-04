"""Recompute retained network/heap measurements; a recorded FAIL stays FAIL."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from network_memory import inspect as network_inspect
from summarize_public_windows import inspect as cpu_inspect
from ota import image_info
from public_streams import no_runtime_faults

EVIDENCE = ROOT/'tests/results/esp32c3-network-memory-20261004'
FIRMWARE = ROOT/'firmware/development/esp32c3-aac-network-memory'


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


class NetworkMemoryEvidenceTests(unittest.TestCase):
    def test_checksums_and_exact_runner_sources(self):
        for name, digest in read(EVIDENCE/'checksums.json').items():
            self.assertEqual(sha(EVIDENCE/name), digest, name)
        for suite in ('baseline-http32', 'ota-transition', 'candidate-http32', 'candidate-https64'):
            report = read(EVIDENCE/suite/'report.json')
            for name, digest in report['test_sources_sha256'].items():
                self.assertEqual(sha(EVIDENCE/'sources'/name), digest, (suite, name))

    def test_firmware_config_and_unchanged_aac_patch(self):
        manifest = read(FIRMWARE/'manifest.json')
        self.assertEqual(image_info((FIRMWARE/'app.bin').read_bytes()), manifest['image'])
        for name, value in manifest['files'].items():
            self.assertEqual(sha(FIRMWARE/name), value['sha256'])
        build = read(EVIDENCE/'build-verification.json')
        self.assertEqual(build['elf_sha256'], manifest['image']['app_elf_sha256'])
        self.assertEqual(build['config_changes'], {'CONFIG_YORADIO_NETWORK_HEAP_PROFILE': [None, 'y']})
        self.assertEqual(build['section_deltas']['.dram0.bss'], 96)
        self.assertEqual(build['section_deltas']['.iram0.text'], 0)
        previous = read(ROOT/'tests/results/esp32c3-aac-asymmetric-production-20261004/physical-patch-audit.json')
        current = read(EVIDENCE/'physical-patch-audit.json')
        for key in ('functions', 'compiler_layout'):
            self.assertEqual(current[key], previous[key])

    def test_initial_signal_measurement(self):
        data = read(EVIDENCE/'wifi-signal-check.json')
        good = [s for s in data['samples'] if s['ok']]
        self.assertEqual((len(data['samples']), len(good)), (30, 30))
        levels = [s['rssi'] for s in good]
        self.assertEqual(data['summary']['rssi_dbm'], dict(min=min(levels), median=statistics.median(levels), max=max(levels)))
        self.assertEqual(data['summary']['response_ms']['median'], statistics.median(s['request_ms'] for s in good))
        self.assertEqual(data['summary']['response_ms']['max'], max(s['request_ms'] for s in good))
        self.assertEqual(data['summary']['audio_active_samples'], 0)

    def test_summaries_and_original_baseline_failure(self):
        for suite in ('baseline-http32', 'candidate-http32', 'candidate-https64'):
            folder = EVIDENCE/suite
            self.assertEqual(network_inspect(folder), read(folder/'network-summary.json'))
            self.assertEqual(cpu_inspect(folder), read(folder/'summary.json'))
        baseline = read(EVIDENCE/'baseline-http32/report.json')
        failures = {c['name']: c['reason'] for c in baseline['cases'] if c['result'] == 'FAIL'}
        self.assertEqual(failures, {'http:groovesalad-32-aac': 'Progressive heap loss during continuous playback',
                                   'restore': 'Saved station did not resume after reboot'})
        self.assertFalse(read(EVIDENCE/'baseline-http32/network-summary.json')['cases'][0]['metrics_available'])

    def test_candidate_snapshots_and_fault_windows(self):
        target = read(FIRMWARE/'manifest.json')['image']
        for suite in ('candidate-http32', 'candidate-https64'):
            folder = EVIDENCE/suite
            report, rows = read(folder/'report.json'), read(folder/'performance.json')
            self.assertEqual(report['image'], target)
            case = read(folder/'network-summary.json')['cases'][0]
            self.assertTrue(case['metrics_available'], case.get('issues'))
            self.assertGreaterEqual(len(case['samples']), 50)
            self.assertEqual(case['ranges']['listen']['min'], 1)
            for sample in case['samples']:
                self.assertLessEqual(sample['active']+sample['tw']+sample['bound'], 16)
            start, end = case['window']['start'], case['window']['end']
            no_runtime_faults([r for r in rows if start <= r['at'] < end])

    def test_ota_identity_and_settings(self):
        report = read(EVIDENCE/'ota-transition/report.json')
        case = report['cases'][0]
        self.assertEqual(case['result'], 'PASS')
        for key in ('wifi_unchanged', 'settings_unchanged', 'playlist_unchanged'):
            self.assertTrue(case['evidence'][key])
        self.assertEqual(case['evidence']['after']['app_elf_sha256'],
                         read(FIRMWARE/'manifest.json')['image']['app_elf_sha256'])
        final = read(EVIDENCE/'final-board.json')
        self.assertEqual(final['info']['app_elf_sha256'], report['target_image']['app_elf_sha256'])
        self.assertTrue(final['status']['audio'])


if __name__ == '__main__':
    unittest.main()
