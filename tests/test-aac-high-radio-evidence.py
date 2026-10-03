"""Preserve physical PC18 failures; never promote numerical/OTA passes alone."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from ota import image_info
from ota_diagnostic import serial_health
from summarize_public_windows import inspect
EVIDENCE = ROOT/'tests/results/esp32c3-aac-high-adapter-20261003'
FIRMWARE = ROOT/'firmware/development/esp32c3-aac-high-history'


def read(path): return json.loads(path.read_text(encoding='utf-8'))


class HighRadio(unittest.TestCase):
    def test_exact_awake_application(self):
        manifest = read(FIRMWARE/'manifest.json')
        self.assertEqual(image_info((FIRMWARE/'app.bin').read_bytes()), manifest['image'])
        for name, item in manifest['files'].items():
            data = (FIRMWARE/name).read_bytes()
            self.assertEqual(len(data), item['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(), item['sha256'])
        config = (FIRMWARE/'sdkconfig').read_text(encoding='utf-8')
        for option in ('YORADIO_AAC_HIGH_HISTORY', 'YORADIO_AAC_COMPACT_SBR', 'YORADIO_AAC_PLUS'):
            self.assertIn('CONFIG_'+option+'=y\n', config)
        for option in ('YORADIO_QEMU', 'YORADIO_DEEP_SLEEP_CLOCK'):
            self.assertNotIn('CONFIG_'+option+'=y\n', config)
        self.assertIn('not a production default', manifest['status'].lower())

    def test_ota_and_saved_settings(self):
        directory = EVIDENCE/'physical/install'
        report = read(directory/'report.json')
        self.assertEqual(report['target_image'], read(FIRMWARE/'manifest.json')['image'])
        case, = report['cases']
        self.assertEqual(case['result'], 'PASS')
        for field in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(case['evidence'][field])
        self.assertEqual(serial_health(read(directory/'performance.json'))['result'], 'PASS')

    def test_full_radio_failures_and_recovery_are_retained(self):
        for protocol in ('http', 'https'):
            directory = EVIDENCE/'physical'/protocol
            report = read(directory/'report.json')
            self.assertEqual(report['image'], read(FIRMWARE/'manifest.json')['image'])
            cases = {c['name']: c for c in report['cases']}
            self.assertEqual(len(cases), 8)
            for rate in (16, 32, 64):
                self.assertEqual(cases[f'{protocol}:groovesalad-{rate}-aac']['result'], 'FAIL')
            for name in ('idle:baseline', 'idle:recovery', 'restore', protocol+':groovesalad-256-mp3'):
                self.assertEqual(cases[name]['result'], 'PASS')
            summary = inspect(directory)
            self.assertEqual(summary, read(directory/'summary.json'))
            self.assertFalse(summary['panic_or_capture_errors'])
            self.assertTrue(any('requested=1700 ' in r['line']
                for c in summary['cases'] for r in c.get('allocation_failures', [])))
        self.assertEqual(cases['https:groovesalad-128-aac']['result'], 'PASS')

    def test_local_formats_and_terminal_status(self):
        for name, count in (('local', 15), ('eof', 3)):
            directory = EVIDENCE/'physical'/name
            report = read(directory/'report.json')
            self.assertEqual(len(report['cases']), count)
            self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
            self.assertEqual(report['board']['app_elf_sha256'], read(FIRMWARE/'manifest.json')['image']['app_elf_sha256'])
            self.assertEqual(serial_health(read(directory/'performance.json'))['result'], 'PASS')
        for case in report['cases'][:2]:
            self.assertTrue(case['evidence']['websocket_stopped'])
            self.assertGreaterEqual(case['evidence']['terminal_samples'], 2)


if __name__ == '__main__': unittest.main()
