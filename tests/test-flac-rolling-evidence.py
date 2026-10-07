"""Validate lossless rolling LPC evidence and retain failed general LPC gates."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/results/esp32c3-flac-rolling-20261006'
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from summarize_sustained import summarize


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RollingEvidence(unittest.TestCase):
    def test_integrity_and_sources(self):
        manifest = read(DATA / 'manifest.json')
        self.assertEqual(set(manifest), {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                        if p.is_file() and p != DATA / 'manifest.json'})
        for name, info in manifest.items():
            path = DATA / name
            self.assertEqual((path.stat().st_size, sha(path)), (info['bytes'], info['sha256']), name)
        build = read(DATA / 'verify/build.json')
        core = 'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'
        for folder in ('final-bounds', 'final-contiguous', 'matrix', 'dense-host', 'irregular-host', 'real24-large'):
            report = read(DATA / folder / 'report.json')
            for name, digest in report['sources'].items():
                self.assertEqual(sha(DATA / folder / 'sources' / name), digest)
            self.assertEqual(report['sources'][core], build['source_sha256'][core])

    def test_exact_pcm_and_wide_endpoints(self):
        total = 0
        for folder in ('matrix', 'dense-host', 'irregular-host', 'real24-large'):
            report = read(DATA / folder / 'report.json')
            self.assertTrue(report['passed'] and report['sanitizers'])
            for case in report['cases']:
                self.assertTrue(case['reference']['known_pcm_identical'])
                for variant in case['variants'].values():
                    self.assertEqual(variant['result'], 'PASS')
                    self.assertEqual(variant['sha256'], case['reference']['sha256'])
                    total += 1
        self.assertEqual(total, 378)
        for folder in ('final-bounds', 'final-contiguous'):
            report = read(DATA / folder / 'report.json')
            self.assertTrue(report['passed'] and report['reference']['identical'])
            self.assertEqual(report['edge_cases'], 'PASS')
            self.assertEqual(report['prediction_cases'], 'PASS')
            self.assertIn('predictor_cases=4492', (DATA / folder / 'prediction.log').read_text())

    def test_build_and_matching_board_inputs(self):
        before = read(ROOT / 'firmware/development/esp32c3-flac-spans/manifest.json')
        after = read(DATA / 'verify/build.json')
        artifact = ROOT / 'firmware/development/esp32c3-flac-rolling'
        self.assertEqual(sha(artifact / 'app.bin'), after['app_sha256'])
        self.assertEqual(sha(artifact / 'sdkconfig'), before['sdkconfig_sha256'])
        self.assertEqual(after['app_bytes'] - before['app_bytes'], 2400)
        for name in ('.iram0.text', '.dram0.data', '.dram0.bss', '.rtc.data'):
            self.assertEqual(after['sections'][name], before['sections'][name])
        self.assertFalse(read(artifact / 'manifest.json')['production_qualified'])
        current = read(DATA / 'after/report.json')
        self.assertEqual(current['board']['app_elf_sha256'], after['elf_sha256'])
        for folder in ('irregular-before', 'irregular-before-repeat'):
            report = read(DATA / folder / 'report.json')
            self.assertEqual(report['board']['app_elf_sha256'], before['elf_sha256'])
            self.assertEqual(report['config'], current['config'])
            for name, digest in report['fixture_hashes'].items():
                self.assertEqual(digest, current['fixture_hashes'][name])
        ota = read(DATA / 'ota/report.json')['cases'][0]
        self.assertEqual(ota['result'], 'PASS')
        self.assertEqual(ota['evidence']['after']['app_elf_sha256'], after['elf_sha256'])
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(ota['evidence'][key])

    def test_failed_and_incomplete_outcomes_are_preserved(self):
        for folder in ('irregular-before', 'irregular-before-repeat', 'after'):
            summary = summarize(DATA / folder)
            self.assertEqual(summary, read(DATA / folder / 'summary.json'))
            for case in summary['cases']:
                original = next(c for c in read(DATA / folder / 'report.json')['cases']
                                if c['name'] == 'cpu-under-http-load:' + case['name'])
                self.assertEqual(case['original'], original)
            for case in read(DATA / folder / 'report.json')['cases']:
                if case['name'].startswith(('load-idle-recovery:', 'restore-board')):
                    self.assertEqual(case['result'], 'PASS')
        first = read(DATA / 'irregular-before/summary.json')['cases'][0]
        self.assertEqual(first['original']['reason'], 'Incomplete CPU/heap evidence')
        self.assertTrue(first['full_window']['malformed'])


if __name__ == '__main__':
    unittest.main()
