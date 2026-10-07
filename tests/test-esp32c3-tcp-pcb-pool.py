"""Retain TCP pool playback gains and reject hidden OTA panics."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'tests/results/esp32c3-tcp-pcb-pool-20261001'
IMAGE = ROOT/'firmware/development/esp32c3-tcp-pcb-pool'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap, fixtures
from ota_diagnostic import serial_health


def read(path):
    return json.loads(path.read_text())


def config(path):
    return dict(line.split('=', 1) for line in path.read_text().splitlines()
                if line.startswith('CONFIG_'))


class PoolEvidence(unittest.TestCase):
    def test_artifact_and_original_source_fingerprints(self):
        for folder in sorted(IMAGE.parent.glob('esp32c3-tcp-pcb-pool*')):
            manifest = read(folder/'manifest.json')
            for name, expected in manifest['files'].items():
                data = (folder/name).read_bytes()
                self.assertEqual(len(data), expected['bytes'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), expected['sha256'])
            for name, expected in manifest['source_sha256'].items():
                snapshot = manifest.get('source_snapshots', {}).get(name)
                data = (ROOT/snapshot).read_bytes() if snapshot else subprocess.check_output(
                    ['git', 'show', manifest['source_commit']+':'+name], cwd=ROOT)
                self.assertEqual(hashlib.sha256(data).hexdigest(), expected, name)
        self.assertTrue(read(IMAGE/'manifest.json')['status'].startswith('Not qualified:'))

    def test_matched_configuration_and_reservation_cost(self):
        before = config(ROOT/'firmware/development/esp32c3-iram-safe-wifi16/sdkconfig')
        after = config(IMAGE/'sdkconfig')
        self.assertEqual({k for k in before.keys() | after.keys() if before.get(k) != after.get(k)},
                         {'CONFIG_YORADIO_TCP_PCB_POOL'})
        self.assertEqual(after['CONFIG_YORADIO_TCP_PCB_POOL'], 'y')
        before, after = read(RESULT/'inventory.json')['builds']
        self.assertEqual(after['iram_reserved'], before['iram_reserved'])
        self.assertEqual(after['dram_data'], before['dram_data'])
        self.assertEqual(after['dram_bss']-before['dram_bss'], 16)
        placement = read(IMAGE/'manifest.json')['placement']
        self.assertEqual(placement['s_pcbs']['bytes'], 2688)
        self.assertEqual(placement['s_pcbs']['section'], '.rtc.data')

    def test_all_21_switches_full_rate_and_heap_recovery(self):
        report = read(RESULT/'switch/report.json')
        self.assertEqual([c['result'] for c in report['cases']], ['PASS']*3)
        specs = fixtures()
        batches = [b for b in read(RESULT/'switch/status.json') if b['case'].startswith('switch:')]
        self.assertEqual(len(batches), 21)
        for batch in batches:
            check_playback(batch['samples'], specs[batch['case'].split(':')[2]])
        value = read(RESULT/'switch/switching.json')
        self.assertEqual(value['failures'], [])
        check_recovery_heap(value['checkpoints'][0], value['checkpoints'][-1])
        self.assertEqual(serial_health(read(RESULT/'switch/performance.json'))['result'], 'PASS')

    def test_clean_start_memory_survey_is_not_ota_qualification(self):
        report = read(RESULT/'memory/report.json')
        self.assertEqual([c['result'] for c in report['cases']], ['PASS']*5)
        summary = read(RESULT/'memory/summary.json')
        self.assertEqual([c['playback_result'] for c in summary['cases']], ['PASS']*3)
        self.assertTrue(all(c['decode_mean'] < c['busy_mean'] < 60 for c in summary['cases']))
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(report['cases'][-1]['evidence'][key])
        self.assertEqual(serial_health(read(RESULT/'memory/performance.json'))['result'], 'PASS')

    def test_15_http_passes_do_not_hide_two_panics(self):
        report = read(RESULT/'ota-repeat/report.json')
        self.assertEqual([c['result'] for c in report['cases']], ['PASS']*15)
        rows = read(RESULT/'ota-repeat/performance.json')
        self.assertEqual(sum('assert failed:' in r['line'] for r in rows), 2)
        health = serial_health(rows)
        self.assertEqual(health, read(RESULT/'ota-repeat/serial-health.json'))
        self.assertEqual(health['result'], 'FAIL')
        accepted = [c for c in report['cases'] if c['name'] in
                    ('ota:roundtrip:1', 'ota:roundtrip:2', 'ota:while-playing', 'ota:slow')]
        self.assertEqual([c['evidence']['partition'] for c in accepted], ['app0','app1','app0','app1'])
        for case in report['cases']:
            for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
                self.assertTrue(case['evidence'][key])

    def test_verbose_diagnostic_pass_is_a_different_image(self):
        report = read(RESULT/'trace-negative-ota/report.json')
        self.assertEqual([c['result'] for c in report['cases']], ['PASS']*11)
        self.assertNotEqual(report['board']['app_elf_sha256'], read(IMAGE/'manifest.json')['image']['app_elf_sha256'])
        health = serial_health(read(RESULT/'trace-negative-ota/performance.json'))
        self.assertEqual(health, read(RESULT/'trace-negative-ota/serial-health.json'))
        self.assertEqual(health['result'], 'PASS')

    def test_sleep_link_footprint_is_not_a_hardware_wake_claim(self):
        manifest = read(IMAGE.with_name('esp32c3-tcp-pcb-pool-sleep')/'manifest.json')
        self.assertIn('not flashed', manifest['status'])
        symbols = manifest['rtc_symbols']
        remaining = int(symbols['_rtc_reserved_start']['address'],16)-int(symbols['_rtc_force_slow_end']['address'],16)
        self.assertEqual(remaining, 1796)
        self.assertEqual(symbols['s_pcbs']['bytes'], 2688)
        self.assertEqual(symbols['g_rtc_clock']['bytes'], 1064)

    def test_bounded_history_retains_double_release_sequence(self):
        rows = read(RESULT/'history-negative-ota/performance.json')
        events = []
        for row in rows:
            match = re.search(r'PERF TCP_POOL: sequence=(\d+) action=([\w-]+) slot=(\d+) state=(\d+) owned=(\d+)', row['line'])
            if match:
                events.append((int(match[1]), match[2], int(match[3]), int(match[4]), int(match[5])))
        self.assertEqual([e[0] for e in events], list(range(62)))
        self.assertEqual(events[-2:], [(60,'free',3,0,1), (61,'invalid-free',3,0,0)])
        self.assertEqual(events[58], (58,'alloc',3,0,1))
        self.assertEqual(serial_health(rows), read(RESULT/'history-negative-ota/serial-health.json'))
        self.assertEqual(serial_health(rows)['result'], 'FAIL')
        cases = read(RESULT/'history-negative-ota/report.json')['cases']
        self.assertEqual([c['result'] for c in cases], ['PASS']*3+['FAIL']*8)

    def test_board_was_restored_to_awake_control(self):
        expected = read(ROOT/'firmware/development/esp32c3-iram-safe-wifi16/manifest.json')['image']['app_elf_sha256']
        report = read(RESULT/'restore-control/report.json')
        case = report['cases'][0]
        self.assertEqual(case['result'], 'PASS')
        self.assertEqual(case['evidence']['after']['app_elf_sha256'], expected)
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(case['evidence'][key])
        final = read(RESULT/'final-board.json')
        self.assertEqual(final['board']['app_elf_sha256'], expected)
        self.assertEqual(final['restore_serial_health'], 'PASS')
        self.assertTrue(final['status']['audio'])
        self.assertEqual((final['status']['pcm_sample_rate'], final['status']['pcm_channels']), (44100, 2))


if __name__ == '__main__':
    unittest.main()
