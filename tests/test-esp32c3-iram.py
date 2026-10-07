"""Validate retained IRAM measurements and matched-build feature invariants."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
from evidence_sources import historical_source


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'tests/results/esp32c3-iram-20261001'
BUILDS = json.loads((RESULT / 'inventory.json').read_text())['builds']


def read(path):
    return json.loads(path.read_text())


def config(label):
    path = ROOT / f'firmware/development/esp32c3-iram-{label}/sdkconfig'
    return {line.split('=', 1)[0]: line.split('=', 1)[1]
            for line in path.read_text().splitlines() if line.startswith('CONFIG_')}


class IramEvidence(unittest.TestCase):
    def test_profile_source_fingerprints(self):
        evidence = read(RESULT/'implementation.json')
        for path, expected in evidence['files'].items():
            self.assertEqual(hashlib.sha256(historical_source(ROOT, path, expected)).hexdigest(), expected, path)

    def test_actual_artifact_fingerprints(self):
        for build in BUILDS:
            directory = ROOT / ('firmware/development/esp32c3-iram-'+build['label'])
            manifest = read(directory/'manifest.json')
            for name, expected in manifest['files'].items():
                data = (directory/name).read_bytes()
                self.assertEqual(len(data), expected['bytes'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), expected['sha256'])
            self.assertEqual(manifest['files']['sdkconfig']['sha256'],
                             build['fingerprints']['sdkconfig'])
            self.assertEqual(manifest['image']['app_elf_sha256'],
                             build['fingerprints']['yoradio_esp32c3_oled_native.elf'])

    def test_shared_sram_accounting(self):
        expected = {'baseline': (47104, 0), 'safe': (43520, 3584),
                    'suspend': (25600, 23392)}
        base = BUILDS[0]['boundaries']
        for build in BUILDS:
            b = build['boundaries']
            self.assertEqual(b['_iram_end']-b['_data_start'], 0x700000)
            self.assertEqual(sum(s['bytes'] for s in build['iram_sections']),
                             build['iram_reserved'])
            self.assertEqual((build['iram_reserved'], build['heap_start_released_vs_baseline']),
                             expected[build['label']])
            self.assertEqual(build['heap_start_released_vs_baseline'],
                             base['_heap_start']-b['_heap_start'])
            self.assertEqual(sum(a['bytes'] for a in build['iram_archives']),
                             next(s['bytes'] for s in build['iram_sections']
                                  if s['name'] == '.iram0.text'))

    def test_feature_set_preserved(self):
        # Reject a hidden feature deletion being counted as placement savings.
        conservative = {'CONFIG_RINGBUF_PLACE_ISR_FUNCTIONS_INTO_FLASH',
                        'CONFIG_I2C_MASTER_ISR_HANDLER_IN_IRAM',
                        'CONFIG_ESP_EVENT_POST_FROM_IRAM_ISR', 'CONFIG_POST_EVENTS_FROM_IRAM_ISR'}
        suspend = {'CONFIG_ESP_HW_SUPPORT_FUNC_IN_IRAM', 'CONFIG_ESP_ROM_PRINT_IN_IRAM',
                   'CONFIG_ESP_SYSTEM_IN_IRAM', 'CONFIG_ESP_TIMER_IN_IRAM',
                   'CONFIG_FREERTOS_PLACE_ISR_FUNCTIONS_INTO_FLASH', 'CONFIG_LOG_IN_IRAM',
                   'CONFIG_SPI_FLASH_AUTO_SUSPEND', 'CONFIG_SPI_FLASH_PLACE_FUNCTIONS_IN_IRAM'}
        baseline = config('baseline')
        for label, allowed in [('safe', conservative), ('suspend', conservative | suspend)]:
            candidate = config(label)
            changed = {k for k in baseline.keys() | candidate.keys()
                       if baseline.get(k) != candidate.get(k)}
            self.assertEqual(changed, allowed)
            self.assertEqual(candidate['CONFIG_SPI_FLASH_ENABLE_ENCRYPTED_READ_WRITE'], 'y')
            self.assertNotEqual(candidate.get('CONFIG_YORADIO_DEEP_SLEEP_CLOCK'), 'y')
            self.assertNotEqual(candidate.get('CONFIG_YORADIO_AAC_PS_PC16'), 'y')
            self.assertNotEqual(candidate.get('CONFIG_SPI_FLASH_FORCE_ENABLE_XMC_C_SUSPEND'), 'y')
            self.assertNotEqual(candidate.get('CONFIG_SPI_FLASH_ROM_IMPL'), 'y')

    def test_proven_function_placement(self):
        base, safe, suspend = BUILDS
        self.assertFalse(base['functions_moved_to_flash'])
        for build in (safe, suspend):
            names = {s['name'] for s in build['functions_moved_to_flash']}
            self.assertIn('i2c_master_isr_handler_default', names)
            self.assertIn('prvGetItemByteBuf', names)
            self.assertIn('prvReturnItemDefault', names)
        names = {s['name'] for s in suspend['functions_moved_to_flash']}
        self.assertIn('esp_flash_write_encrypted', names)
        self.assertIn('esp_flash_erase_region', names)
        self.assertGreater(len(names), 150)

    def test_failed_control_is_retained(self):
        failures = read(RESULT/'hardware/baseline-switch/switching.json')['failures']
        self.assertEqual(len(failures), 6)
        self.assertEqual({f['fixture'] for f in failures},
                         {'he-48000-stereo', 'hev2-44100-stereo'})
        self.assertEqual({f['cycle'] for f in failures}, {0, 1, 2})
        report = read(RESULT/'hardware/baseline-memory/report.json')
        outcomes = {c['name']: c['result'] for c in report['cases']}
        self.assertEqual(outcomes['memory-playback:lc-48000-stereo'], 'PASS')
        self.assertEqual(outcomes['memory-playback:he-48000-stereo'], 'FAIL')
        self.assertEqual(outcomes['memory-playback:hev2-44100-stereo'], 'FAIL')

    def test_physical_memory_gain_and_full_aac(self):
        boot_free, fixture_hashes = [], []
        sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
        from summarize_memory import summarize
        for label in ('baseline', 'suspend'):
            directory = RESULT/'hardware'/(label+'-memory')
            report, status, performance = (read(directory/name) for name in
                ('report.json', 'status.json', 'performance.json'))
            self.assertEqual(read(directory/'summary.json'), summarize(report, status, performance))
            starts = [int(m[1]) for row in performance
                      if (m := re.search(r'PERF RAM: stage=app-start free=(\d+)', row['line']))]
            self.assertEqual(len(starts), 1)
            boot_free.extend(starts)
            fixture_hashes.append(report['fixture_hashes'])
            manifest = read(ROOT/f'firmware/development/esp32c3-iram-{label}/manifest.json')
            self.assertEqual(report['board']['app_elf_sha256'], manifest['image']['app_elf_sha256'])
            if label == 'suspend':
                self.assertTrue(all(case['result'] == 'PASS' for case in report['cases']))
                self.assertEqual(len([case for case in report['cases']
                                      if case['name'].startswith('memory-playback:')]), 3)
                self.assertFalse(any('allocation failed' in row['line'] for row in performance))
        self.assertEqual(boot_free[1]-boot_free[0], 23392)
        self.assertEqual(fixture_hashes[0], fixture_hashes[1])

    def test_mixed_matrix_failure_is_not_promoted(self):
        directory = RESULT/'hardware/suspend-matrix'
        report = read(directory/'report.json')
        failures = {c['name'] for c in report['cases'] if c['result'] == 'FAIL'}
        self.assertEqual(failures, {'http:flac-level8:auto', 'http:flac-level8:flac',
                                    'switching-and-heap'})
        switches = read(directory/'switching.json')
        self.assertEqual(len(switches['failures']), 2)
        self.assertEqual({c['fixture'] for c in switches['failures']}, {'flac-level8'})
        self.assertEqual(len(switches['checkpoints']), 3)
        states = read(directory/'status.json')
        he = [batch for batch in states if batch['case'].startswith('switch:')
              and any(name in batch['case'] for name in ('he-48000', 'hev2-44100'))]
        self.assertEqual(len(he), 6)
        for batch in he:
            rate = 44100 if 'hev2' in batch['case'] else 48000
            stable = [row for row in batch['samples'] if row['seconds'] >= 2]
            self.assertGreaterEqual(len(stable), 5)
            self.assertTrue(all(row['audio'] and row['pcm_sample_rate'] == rate
                                and row['pcm_channels'] == 2 for row in stable))

    def test_ota_from_flash_exec_image_and_restore(self):
        report = read(RESULT/'hardware/suspend-to-baseline-ota/report.json')
        case, = report['cases']
        self.assertEqual(case['result'], 'PASS')
        evidence = case['evidence']
        self.assertGreaterEqual(evidence['playing_before_upload']['samples'], 5)
        self.assertNotEqual(report['board']['partition'], evidence['after']['partition'])
        self.assertEqual(report['board']['app_elf_sha256'], report['current_image']['app_elf_sha256'])
        self.assertEqual(evidence['after']['app_elf_sha256'], report['target_image']['app_elf_sha256'])
        restore = read(RESULT/'hardware/restore-ota.json')
        initial = read(RESULT/'hardware/baseline-ota.json')
        self.assertEqual(restore['after']['app_elf_sha256'], initial['before']['app_elf_sha256'])
        for result in (evidence, restore, initial, read(RESULT/'hardware/suspend-ota.json')):
            for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
                self.assertTrue(result[key])

    def test_flac_control_does_not_hide_latency_gap(self):
        report = read(RESULT/'hardware/baseline-flac/report.json')
        results = {c['name']: c['result'] for c in report['cases']}
        self.assertEqual(results['http:flac-level8:auto'], 'FAIL')
        self.assertEqual(results['http:flac-level8:flac'], 'FAIL')
        self.assertEqual(results['switching-and-heap'], 'PASS')
        self.assertEqual(read(RESULT/'hardware/baseline-flac/switching.json')['failures'], [])
        candidate = read(RESULT/'hardware/suspend-matrix/report.json')
        self.assertEqual(report['fixture_hashes']['flac-level8'],
                         candidate['fixture_hashes']['flac-level8'])


if __name__ == '__main__':
    unittest.main()
