"""Validate the fixed image's retained OTA/playback evidence, without broad qualification."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'tests/results/esp32c3-lwip-half-close-20261001'
IMAGE = ROOT/'firmware/development/esp32c3-tcp-pcb-pool-fixed'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap, fixtures
from ota_diagnostic import serial_health


def read(path):
    return json.loads(path.read_text())


class BoardEvidence(unittest.TestCase):
    def test_exact_artifact_sources_and_awake_configuration(self):
        manifest = read(IMAGE/'manifest.json')
        for name, expected in manifest['files'].items():
            data = (IMAGE/name).read_bytes()
            self.assertEqual(len(data), expected['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected['sha256'])
        for name, expected in manifest['source_sha256'].items():
            data = subprocess.check_output(['git', 'show', manifest['source_commit']+':'+name], cwd=ROOT)
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected)
        config = (IMAGE/'sdkconfig').read_text()
        for flag in ('SPI_FLASH_AUTO_SUSPEND', 'YORADIO_DEEP_SLEEP_CLOCK', 'YORADIO_QEMU',
                     'YORADIO_TCP_PCB_POOL_DIAGNOSTICS'):
            self.assertNotIn('CONFIG_'+flag+'=y', config)
        for flag in ('YORADIO_TCP_PCB_POOL', 'YORADIO_AAC_PLUS'):
            self.assertIn('CONFIG_'+flag+'=y', config)
        control, fixed = read(RESULT/'inventory.json')['builds']
        self.assertEqual(fixed['iram_reserved'], control['iram_reserved'])
        self.assertEqual(fixed['dram_data'], control['dram_data'])
        self.assertEqual(fixed['dram_bss']-control['dram_bss'], 16)

    def test_install_and_15_repeat_ota_checks_include_serial_health(self):
        digest = read(IMAGE/'manifest.json')['image']['app_elf_sha256']
        install = read(RESULT/'install-ota/report.json')
        self.assertEqual(install['target_image']['app_elf_sha256'], digest)
        self.assertEqual(install['cases'][0]['result'], 'PASS')
        report = read(RESULT/'ota-repeat/report.json')
        self.assertEqual(report['board']['app_elf_sha256'], digest)
        self.assertEqual(len(report['cases']), 15)
        self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
        for case in install['cases']+report['cases']:
            for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
                self.assertTrue(case['evidence'][key])
        for suite in ('install-ota', 'ota-repeat'):
            health = serial_health(read(RESULT/suite/'performance.json'))
            self.assertEqual(health['result'], 'PASS')
        self.assertEqual(serial_health(read(RESULT/'ota-repeat/performance.json')),
                         read(RESULT/'ota-repeat/serial-health.json'))
        resets = [r['line'] for r in read(RESULT/'ota-repeat/performance.json')
                  if r['line'].startswith('rst:')]
        # Four accepted updates plus the explicit final station restoration.
        self.assertEqual(len(resets), 5)
        self.assertTrue(all('RTC_SW_CPU_RST' in line for line in resets))

    def test_21_mixed_switches_require_full_sbr_ps_and_heap_recovery(self):
        report = read(RESULT/'switch/report.json')
        self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
        self.assertEqual(report['board']['app_elf_sha256'], read(IMAGE/'manifest.json')['image']['app_elf_sha256'])
        batches = [b for b in read(RESULT/'switch/status.json') if b['case'].startswith('switch:')]
        self.assertEqual(len(batches), 21)
        specs = fixtures()
        for batch in batches:
            check_playback(batch['samples'], specs[batch['case'].split(':')[2]])
        switching = read(RESULT/'switch/switching.json')
        self.assertEqual(switching['failures'], [])
        check_recovery_heap(switching['checkpoints'][0], switching['checkpoints'][-1])
        self.assertEqual(serial_health(read(RESULT/'switch/performance.json'))['result'], 'PASS')

    def test_aac_cpu_survey_and_preserved_settings(self):
        report = read(RESULT/'memory/report.json')
        self.assertEqual([c['result'] for c in report['cases']], ['PASS']*5)
        summary = read(RESULT/'memory/summary.json')
        baseline = read(ROOT/'tests/results/esp32c3-tcp-pcb-pool-20261001/memory/summary.json')
        self.assertEqual(len(summary['cases']), 3)
        for before, after in zip(baseline['cases'], summary['cases']):
            self.assertEqual(before['name'], after['name'])
            self.assertEqual(after['playback_result'], 'PASS')
            # Short CPU surveys tolerate measurement noise; not an IRQ/soak guarantee.
            self.assertLessEqual(after['decode_mean'], before['decode_mean']*1.05+0.5)
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(report['cases'][-1]['evidence'][key])
        self.assertEqual(serial_health(read(RESULT/'memory/performance.json'))['result'], 'PASS')


if __name__ == '__main__':
    unittest.main()
