"""Check retained hardware evidence without equating it to full qualification."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'tests/results/esp32c3-wifi16-20261001'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap, fixtures
from summarize_load import summarize_load


def read(path):
    return json.loads(path.read_text())


def config(name):
    return dict(line.split('=', 1) for line in
                (ROOT/f'firmware/development/{name}/sdkconfig').read_text().splitlines()
                if line.startswith('CONFIG_'))


class WifiBalanceEvidence(unittest.TestCase):
    def test_no_hidden_feature_or_codec_change(self):
        before = config('esp32c3-iram-suspend')
        after = config('esp32c3-iram-wifi16')
        changed = {key for key in before.keys() | after.keys() if before.get(key) != after.get(key)}
        self.assertEqual(changed, {
            'CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM', 'CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM',
            'CONFIG_ESP32_WIFI_DYNAMIC_RX_BUFFER_NUM', 'CONFIG_ESP32_WIFI_DYNAMIC_TX_BUFFER_NUM'})
        for key in changed:
            self.assertEqual((before[key], after[key]), ('6', '16'))
        self.assertEqual(after['CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM'], '6')
        self.assertEqual(after['CONFIG_SPI_FLASH_ENABLE_ENCRYPTED_READ_WRITE'], 'y')
        self.assertNotEqual(after.get('CONFIG_YORADIO_AAC_PS_PC16'), 'y')
        self.assertNotEqual(after.get('CONFIG_YORADIO_DEEP_SLEEP_CLOCK'), 'y')

    def test_no_double_counted_memory_saving(self):
        before, after = read(RESULT/'inventory.json')['builds']
        self.assertEqual(before['boundaries'], after['boundaries'])
        for row in (before, after):
            self.assertEqual((row['iram_reserved'], row['dram_data'], row['dram_bss']),
                             (25600, 10723, 31368))
            self.assertEqual(row['heap_start_released_vs_baseline'], 0)

    def test_firmware_and_test_source_fingerprints(self):
        directory = ROOT/'firmware/development/esp32c3-iram-wifi16'
        manifest = read(directory/'manifest.json')
        for name, expected in manifest['files'].items():
            data = (directory/name).read_bytes()
            self.assertEqual(len(data), expected['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected['sha256'])
        inventory = read(RESULT/'inventory.json')['builds'][1]
        self.assertEqual(manifest['image']['app_elf_sha256'],
                         inventory['fingerprints']['yoradio_esp32c3_oled_native.elf'])
        self.assertEqual(manifest['files']['sdkconfig']['sha256'],
                         inventory['fingerprints']['sdkconfig'])
        for path in RESULT.rglob('report.json'):
            report = read(path)
            for filename, digest in report['test_sources_sha256'].items():
                self.assertEqual(hashlib.sha256((ROOT/filename).read_bytes()).hexdigest(),
                                 digest, str(path)+': '+filename)

    def test_failed_original_control_is_retained(self):
        report = read(RESULT/'bounded6-transport/report.json')
        self.assertEqual([c['result'] for c in report['cases']], ['FAIL']*5)
        self.assertEqual(report['cases'][-1]['name'], 'restore-board')
        self.assertEqual(report['cases'][-1]['reason'], 'TimeoutError')
        spec = fixtures()['flac-level8']
        for condition in report['socket_conditions']:
            self.assertEqual(condition['accepted_nodelay'], [condition['requested_nodelay']])
            event, = condition['events']
            self.assertFalse(event['complete'])
            self.assertLess(event['sent'], len(spec['data']))
            self.assertGreater(event['seconds'], spec['seconds'])

    def test_candidate_delivers_full_file_with_both_socket_options(self):
        spec = fixtures()['flac-level8']
        report = read(RESULT/'wifi16-transport/report.json')
        self.assertEqual(report['fixture_hashes']['flac-level8'], spec['sha256'])
        self.assertEqual([c['result'] for c in report['cases']], ['PASS']*5)
        self.assertEqual([c['requested_nodelay'] for c in report['socket_conditions']], [0, 1, 1, 0])
        for condition in report['socket_conditions']:
            self.assertEqual(condition['accepted_nodelay'], [condition['requested_nodelay']])
            event, = condition['events']
            self.assertTrue(event['complete'])
            self.assertEqual(event['sent'], len(spec['data']))
            self.assertLess(abs(event['seconds']-spec['seconds']/1.02), .1)
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(report['cases'][-1]['evidence'][key])

    def test_matrix_and_repeated_full_rate_switches(self):
        report = read(RESULT/'matrix/report.json')
        self.assertEqual(len(report['cases']), 22)
        self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
        self.assertEqual(sum(c['name'].startswith('http:') for c in report['cases']), 14)
        self.assertEqual(sum(c['name'].startswith('network:') for c in report['cases']), 5)
        switches = read(RESULT/'matrix/switching.json')
        self.assertEqual(switches['failures'], [])
        self.assertEqual(len(switches['checkpoints']), 3)
        check_recovery_heap(switches['checkpoints'][0], switches['checkpoints'][-1])
        batches = [batch for batch in read(RESULT/'matrix/status.json')
                   if batch['case'].startswith('switch:')]
        self.assertEqual(len(batches), 21)
        specs = fixtures()
        for batch in batches:
            check_playback(batch['samples'], specs[batch['case'].split(':', 2)[2]])
        rows = read(RESULT/'matrix/performance.json')
        self.assertFalse(any(re.search(r'allocation failed|decode (?:error|failed)|'
                                      r'assert failed|Guru Meditation|CORRUPT HEAP', row['line'])
                             for row in rows))

    def test_high_bitrate_fixture_provenance(self):
        manifest = read(RESULT/'stress-fixtures.json')
        self.assertEqual(manifest['source_bits'], 16)
        specs = manifest['fixtures']
        self.assertEqual({s['codec'] for s in specs}, {'mp3', 'flac', 'vorbis', 'opus'})
        report = read(RESULT/'load/report.json')
        for spec in specs:
            self.assertEqual((spec['rate'], spec['channels'], spec['bits']), (48000, 2, 16))
            self.assertGreaterEqual(spec['seconds'], 60)
            self.assertEqual(report['fixture_hashes'][spec['name']], spec['sha256'])
            self.assertAlmostEqual(spec['average_kbps'], spec['bytes']*8/spec['seconds']/1000)
        self.assertGreater(next(s['average_kbps'] for s in specs if s['codec'] == 'flac'), 1200)

    def test_load_failures_and_diagnostic_metrics_are_retained(self):
        directory = RESULT/'load'
        report, status, rows = (read(directory/name) for name in
                               ('report.json', 'status.json', 'performance.json'))
        expected = {'cpu-under-http-load:stress-mp3-48000-2ch-16bit-60s':
                    'Progressive heap loss during continuous playback',
                    'cpu-under-http-load:stress-opus-48000-2ch-16bit-60s': 'CPU budget exceeded'}
        self.assertEqual({c['name']: c['reason'] for c in report['cases'] if c['result'] == 'FAIL'},
                         expected)
        self.assertEqual(len(report['cases']), 8)
        summary = summarize_load(report, status, rows)
        self.assertEqual(read(directory/'summary.json'), summary)
        self.assertEqual(len(summary['cases']), 7)
        self.assertEqual({c['name'] for c in summary['cases'] if c['playback_result'] == 'FAIL'},
                         set(expected))
        for case in report['cases']:
            if case['result'] == 'PASS' and case['name'].startswith('cpu-under-http-load:'):
                evidence = case['evidence']
                self.assertLess(evidence['max_http_ms'], 2000)
                self.assertLessEqual(evidence['peak_busy'], 85)
                self.assertGreaterEqual(evidence['minimum_heap'], 8192)
                self.assertGreaterEqual(evidence['minimum_largest'], 4096)
                self.assertTrue(.9 < evidence['audio_wall_ratio'] < 1.1)

    def test_matched_six_buffer_control_reproduces_incomplete_delivery(self):
        report = read(RESULT/'matched6-transport/report.json')
        self.assertEqual(report['board']['app_elf_sha256'],
                         read(ROOT/'firmware/development/esp32c3-iram-suspend/manifest.json')['image']['app_elf_sha256'])
        self.assertEqual([c['result'] for c in report['cases']], ['FAIL', 'FAIL', 'PASS'])
        spec = fixtures()['flac-level8']
        self.assertEqual(report['fixture_hashes']['flac-level8'], spec['sha256'])
        for condition in report['socket_conditions']:
            self.assertEqual(condition['accepted_nodelay'], [condition['requested_nodelay']])
            event, = condition['events']
            self.assertFalse(event['complete'])
            self.assertLess(event['sent'], len(spec['data']))
            self.assertGreater(event['seconds'], spec['seconds'])

    def test_ota_panic_blocks_promotion_despite_prior_pass(self):
        forward = read(RESULT/'matched-to6-ota/report.json')
        self.assertEqual(forward['cases'][0]['result'], 'PASS')
        evidence = forward['cases'][0]['evidence']
        self.assertNotEqual(forward['board']['partition'], evidence['after']['partition'])
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(evidence[key])
        reverse = read(RESULT/'matched-back16-ota/report.json')
        self.assertEqual(reverse['board']['app_elf_sha256'], evidence['after']['app_elf_sha256'])
        self.assertEqual(reverse['cases'][0]['result'], 'FAIL')
        self.assertEqual(reverse['cases'][0]['reason'], 'ConnectionResetError')
        rows = read(RESULT/'matched-back16-ota/performance.json')
        panics = [row for row in rows if 'Guru Meditation' in row['line']]
        self.assertEqual(len(panics), 1)
        self.assertIn('Illegal instruction', panics[0]['line'])
        self.assertTrue(any(row['at'] > panics[0]['at'] and 'stage=app-start' in row['line']
                            for row in rows))
        for variant in ('suspend', 'wifi16'):
            status = read(ROOT/f'firmware/development/esp32c3-iram-{variant}/manifest.json')['status']
            self.assertTrue(status.startswith('Not qualified:'))

    def test_rom_recovery_bounds_and_manual_reset_verification(self):
        directory = RESULT/'rom-recovery'
        initial = read(directory/'recovery.json')
        self.assertEqual(initial['result'], 'FAIL', 'Do not erase reset-verification failure')
        self.assertEqual(initial['steps'], [dict(name='read-partitions', exit_code=0),
                                           dict(name='write-app1', exit_code=0),
                                           dict(name='reset', exit_code=1)])
        self.assertEqual(initial['written_offset'], 0x1e0000)
        self.assertLessEqual(initial['written_bytes'], 0x1d0000)
        self.assertIn('Hash of data verified.', (directory/'write-app1.log').read_text())
        restored = read(directory/'after-manual-reset.json')
        self.assertEqual(restored['result'], 'PASS')
        self.assertEqual(restored['info']['partition'], initial['before']['partition'])
        self.assertEqual(restored['info']['app_elf_sha256'], initial['target']['app_elf_sha256'])
        self.assertEqual(restored['status']['network'], 'client')
        self.assertTrue(restored['status']['audio'])
        self.assertEqual((restored['status']['pcm_sample_rate'], restored['status']['pcm_channels']),
                         (44100, 2))


if __name__ == '__main__':
    unittest.main()
