"""Keep physical smoothing qualification and its unresolved RAM failures distinct."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from ota import image_info
from ota_diagnostic import serial_health
from summarize_public_windows import inspect

EVIDENCE = ROOT/'tests/results/esp32c3-aac-smoothing-adapter-20261003/physical'
FIRMWARE = ROOT/'firmware/development/esp32c3-aac-smoothing-history'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


class SmoothingRadioTests(unittest.TestCase):
    def test_tested_image_and_build_configuration(self):
        manifest = read(FIRMWARE/'manifest.json')
        self.assertEqual(image_info((FIRMWARE/'app.bin').read_bytes()), manifest['image'])
        for name, item in manifest['files'].items():
            data = (FIRMWARE/name).read_bytes()
            self.assertEqual(len(data), item['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(), item['sha256'])
        config = (FIRMWARE/'sdkconfig').read_text(encoding='utf-8')
        for option in ('YORADIO_AAC_SMOOTHING_HISTORY', 'YORADIO_AAC_HIGH_HISTORY',
                       'YORADIO_AAC_COMPACT_SBR', 'YORADIO_AAC_PLUS'):
            self.assertIn('CONFIG_'+option+'=y\n', config)
        for option in ('YORADIO_QEMU', 'YORADIO_DEEP_SLEEP_CLOCK', 'SPI_FLASH_AUTO_SUSPEND'):
            self.assertNotIn('CONFIG_'+option+'=y\n', config)
        self.assertIn('not a production default', manifest['status'].lower())

    def test_incoming_and_new_image_ota_preserve_settings(self):
        install = read(EVIDENCE/'ota/report.json')
        self.assertEqual(install['target_image'], read(FIRMWARE/'manifest.json')['image'])
        for name in ('ota', 'ota-repeat'):
            folder = EVIDENCE/name
            report = read(folder/'report.json')
            self.assertTrue(report['cases'])
            self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
            self.assertEqual(serial_health(read(folder/'performance.json'))['result'], 'PASS')
            for case in report['cases']:
                for field in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
                    self.assertTrue(case['evidence'][field])
        self.assertEqual({c['name'] for c in report['cases']},
                         {'ota:roundtrip:1', 'ota:roundtrip:2', 'ota:while-playing', 'restore-saved-station'})
        self.assertEqual(report['image'], read(FIRMWARE/'manifest.json')['image'])
        for case in report['cases']:
            if case['name'].startswith('ota:'):
                self.assertTrue(case['evidence']['hash_verified'])
        final = read(EVIDENCE/'final-board.json')
        self.assertEqual(final['board']['app_elf_sha256'], report['image']['app_elf_sha256'])
        self.assertTrue(final['status']['audio'])
        self.assertEqual(final['board']['partition'], report['cases'][2]['evidence']['partition'])

    def test_public_failures_are_not_promoted_to_passes(self):
        for protocol in ('http', 'https'):
            folder = EVIDENCE/protocol
            report = read(folder/'report.json')
            self.assertEqual(report['image'], read(FIRMWARE/'manifest.json')['image'])
            cases = {c['name']: c for c in report['cases']}
            self.assertEqual(len(cases), 8)
            for rate in (16, 32, 64):
                self.assertEqual(cases[f'{protocol}:groovesalad-{rate}-aac']['result'], 'FAIL')
            for name in ('idle:baseline', 'idle:recovery', 'restore',
                         protocol+':groovesalad-128-aac', protocol+':groovesalad-256-mp3'):
                self.assertEqual(cases[name]['result'], 'PASS')
            summary = inspect(folder)
            self.assertEqual(summary, read(folder/'summary.json'))
            self.assertFalse(summary['panic_or_capture_errors'])
            failures = [row for c in summary['cases'] for row in c.get('allocation_failures', [])]
            self.assertTrue(failures)
            self.assertTrue(any('requested=1700 ' in row['line'] for row in failures))

    def test_full_rate_local_matrix_and_stack(self):
        folder = EVIDENCE/'local'
        report = read(folder/'report.json')
        self.assertEqual(len(report['cases']), 15)
        self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
        self.assertEqual(report['board']['app_elf_sha256'], read(FIRMWARE/'manifest.json')['image']['app_elf_sha256'])
        rows = read(folder/'performance.json')
        self.assertEqual(serial_health(rows)['result'], 'PASS')
        self.assertFalse(any(re.search(r'allocation failed|decode (?:error|failed)', r['line']) for r in rows))
        margins = [int(m[1]) for r in rows
                   if (m := re.search(r'PERF STACK: name=audio_decode minimum_free=(\d+)', r['line']))]
        self.assertTrue(margins)
        self.assertGreater(min(margins), 2048)
        cases = {c['name']: c for c in report['cases']}
        for name, rate in (('he-44100-stereo', 44100), ('he-48000-stereo', 48000), ('hev2-44100-stereo', 44100)):
            for hint in ('auto', 'aac'):
                e = cases[f'http:{name}:{hint}']['evidence']
                self.assertEqual((e['rate'], e['channels']), (rate, 2))


if __name__ == '__main__':
    unittest.main()
