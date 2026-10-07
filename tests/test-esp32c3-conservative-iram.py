"""Check conservative C3 evidence, including failures that block promotion."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'tests/results/esp32c3-conservative-20261001'
IMAGE = ROOT/'firmware/development/esp32c3-iram-safe-wifi16'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import Failure, check_playback, check_recovery_heap, fixtures


def read(path):
    return json.loads(path.read_text())


def config(path):
    return dict(line.split('=', 1) for line in path.read_text().splitlines()
                if line.startswith('CONFIG_'))


class ConservativeEvidence(unittest.TestCase):
    def test_configuration_preserves_flash_critical_paths(self):
        before = config(ROOT/'firmware/development/esp32c3-iram-safe/sdkconfig')
        after = config(IMAGE/'sdkconfig')
        changed = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
        self.assertEqual(changed, {
            'CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM', 'CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM',
            'CONFIG_ESP32_WIFI_DYNAMIC_RX_BUFFER_NUM', 'CONFIG_ESP32_WIFI_DYNAMIC_TX_BUFFER_NUM'})
        for key in changed:
            self.assertEqual((before[key], after[key]), ('6', '16'))
        for key in ('CONFIG_SPI_FLASH_AUTO_SUSPEND', 'CONFIG_YORADIO_DEEP_SLEEP_CLOCK',
                    'CONFIG_YORADIO_QEMU', 'CONFIG_YORADIO_AAC_RELOCATE_PS',
                    'CONFIG_YORADIO_AAC_PS_PC16', 'CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE',
                    'CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE'):
            self.assertNotEqual(after.get(key), 'y', key)
        for key in ('CONFIG_SPI_FLASH_ENABLE_ENCRYPTED_READ_WRITE',
                    'CONFIG_SPI_FLASH_PLACE_FUNCTIONS_IN_IRAM', 'CONFIG_ESP_SYSTEM_IN_IRAM',
                    'CONFIG_ESP_TIMER_IN_IRAM', 'CONFIG_LOG_IN_IRAM',
                    'CONFIG_ESP_ROM_PRINT_IN_IRAM',
                    'CONFIG_YORADIO_AAC_PLUS'):
            self.assertEqual(after.get(key), 'y', key)

    def test_static_gain_is_counted_once(self):
        baseline, safe6, safe16 = read(RESULT/'inventory.json')['builds']
        self.assertEqual(baseline['iram_reserved'], 47104)
        for row in (safe6, safe16):
            self.assertEqual((row['iram_reserved'], row['dram_data'], row['dram_bss']),
                             (43520, 12620, 31368))
            self.assertEqual(row['heap_start_released_vs_baseline'], 3584)
        self.assertEqual(safe6['boundaries'], safe16['boundaries'])

    def test_firmware_and_source_fingerprints(self):
        manifest = read(IMAGE/'manifest.json')
        self.assertTrue(manifest['status'].startswith('Not qualified:'))
        for name, expected in manifest['files'].items():
            data = (IMAGE/name).read_bytes()
            self.assertEqual(len(data), expected['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected['sha256'])
        for report in RESULT.glob('*/report.json'):
            value = read(report)
            for name, expected in value['test_sources_sha256'].items():
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), expected, name)
            if report.parent.name != 'install-ota':
                self.assertEqual(value['board']['app_elf_sha256'], manifest['image']['app_elf_sha256'])
        self.assertEqual(read(RESULT/'ota-repeat/capture.json')['script_sha256'],
                         hashlib.sha256((RESULT/'ota-repeat/run.py').read_bytes()).hexdigest())

    def test_clean_start_full_rate_does_not_replace_switching_gate(self):
        report = read(RESULT/'memory/report.json')
        self.assertEqual([c['result'] for c in report['cases']], ['PASS']*5)
        specs = fixtures()
        for batch in read(RESULT/'memory/status.json'):
            check_playback(batch['samples'], specs[batch['case']])
        summary = read(RESULT/'memory/summary.json')
        self.assertEqual([c['playback_result'] for c in summary['cases']], ['PASS']*3)
        self.assertEqual([c['minimum_largest'] for c in summary['cases']], [65536, 10752, 10752])
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(report['cases'][-1]['evidence'][key])

    def test_switch_failures_and_allocator_geometry_remain_visible(self):
        report = read(RESULT/'switch/report.json')
        self.assertEqual([c['result'] for c in report['cases']], ['FAIL', 'PASS', 'PASS'])
        specs = fixtures()
        failed, passed = [], 0
        for batch in read(RESULT/'switch/status.json'):
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
        switching = read(RESULT/'switch/switching.json')
        self.assertEqual([(c['cycle'], c['fixture']) for c in switching['failures']], failed)
        check_recovery_heap(switching['checkpoints'][0], switching['checkpoints'][-1])
        errors = [row['line'] for row in read(RESULT/'switch/performance.json')
                  if 'allocation failed:' in row['line']]
        self.assertEqual(len(errors), 2)
        for line in errors:
            self.assertIn('requested=55128', line)
            self.assertIn('largest=47104', line)
            self.assertGreater(int(re.search(r'free=(\d+)', line)[1]), 55128)

    def test_ota_from_candidate_covers_both_slots_and_preservation(self):
        cases = read(RESULT/'ota-repeat/report.json')['cases']
        self.assertEqual(len(cases), 15)
        self.assertEqual([c['result'] for c in cases], ['PASS']*15)
        accepted = [c for c in cases if c['name'] in
                    ('ota:roundtrip:1', 'ota:roundtrip:2', 'ota:while-playing', 'ota:slow')]
        self.assertEqual([c['evidence']['partition'] for c in accepted],
                         ['app1', 'app0', 'app1', 'app0'])
        for case in cases:
            for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
                self.assertTrue(case['evidence'][key])
        for case in accepted:
            self.assertTrue(case['evidence']['hash_verified'])
        capture = read(RESULT/'ota-repeat/performance.json')
        self.assertTrue(any('stage=app-start' in row['line'] for row in capture))
        self.assertFalse(any(re.search(r'Guru Meditation|PANIC |CORRUPT HEAP|assert failed|'
                                      r'serial capture interrupted', row['line']) for row in capture))


if __name__ == '__main__':
    unittest.main()
