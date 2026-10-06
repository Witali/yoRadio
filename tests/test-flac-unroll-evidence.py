"""Replay LPC group optimization evidence without hiding saturated-CPU failures."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/results/esp32c3-flac-unroll-20261006'
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from summarize_sustained import summarize


def read(path):
    return json.loads(path.read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


class UnrollEvidence(unittest.TestCase):
    def test_integrity(self):
        manifest = read(DATA / 'manifest.json')
        self.assertEqual(set(manifest), {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                        if p.is_file() and p != DATA / 'manifest.json'})
        for name, info in manifest.items():
            data = (DATA / name).read_bytes()
            self.assertEqual((len(data), sha(data)), (info['bytes'], info['sha256']), name)
        for folder in ('expanded-bounds', 'expanded-contiguous', 'matrix', 'dense-host', 'real24-large'):
            for name, digest in read(DATA / folder / 'report.json')['sources'].items():
                self.assertEqual(sha((DATA / folder / 'sources' / name).read_bytes()), digest)

    def test_exact_pcm_and_all_shifts(self):
        total = 0
        for folder in ('matrix', 'dense-host', 'real24-large'):
            report = read(DATA / folder / 'report.json')
            self.assertTrue(report['passed'] and report['sanitizers'])
            for case in report['cases']:
                self.assertTrue(case['reference']['known_pcm_identical'])
                for variant in case['variants'].values():
                    self.assertEqual(variant['result'], 'PASS')
                    self.assertEqual(variant['sha256'], case['reference']['sha256'])
                    total += 1
        self.assertEqual(total, 375)
        for folder in ('expanded-bounds', 'expanded-contiguous'):
            report = read(DATA / folder / 'report.json')
            self.assertTrue(report['passed'] and report['reference']['identical'])
            self.assertEqual(report['prediction_cases'], 'PASS')
            self.assertIn('predictor_cases=1222 orders=0..32 shifts=0..15',
                          (DATA / folder / 'prediction.log').read_text())

    def test_build_and_board_identity(self):
        before = read(ROOT / 'firmware/development/esp32c3-flac-predictor/manifest.json')
        after = read(DATA / 'verify/build.json')
        artifact = ROOT / 'firmware/development/esp32c3-flac-unroll'
        self.assertEqual(sha((artifact / 'app.bin').read_bytes()), after['app_sha256'])
        self.assertEqual(sha((artifact / 'sdkconfig').read_bytes()), before['sdkconfig_sha256'])
        self.assertEqual(after['app_bytes'] - before['app_bytes'], 1056)
        for name in ('.iram0.text', '.dram0.data', '.dram0.bss', '.rtc.data'):
            self.assertEqual(after['sections'][name], before['sections'][name])
        self.assertFalse(read(artifact / 'manifest.json')['production_qualified'])
        for name in ('before', 'after', 'regression', 'load16'):
            report = read(DATA / name / 'report.json')
            expected = before if name == 'before' else after
            self.assertEqual(report['board']['app_elf_sha256'], expected['elf_sha256'])
            self.assertEqual(report['config']['sha256'], after['sdkconfig_sha256'])
        core = 'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'
        self.assertEqual(after['source_sha256'][core], read(DATA / 'matrix/report.json')['sources'][core])

    def test_physical_failures_are_preserved(self):
        for name in ('before', 'after', 'regression', 'load16'):
            summary = summarize(DATA / name)
            self.assertEqual(summary, read(DATA / name / 'summary.json'))
            for case in summary['cases']:
                dense = 'lpc32dense' in case['name']
                self.assertEqual(case['original']['result'], 'FAIL' if dense else 'PASS')
                if dense:
                    self.assertEqual(case['full_window']['strict']['result'], 'FAIL')
                else:
                    self.assertEqual(case['runtime']['result'], 'PASS')
            cases = read(DATA / name / 'report.json')['cases']
            for case in cases:
                if case['name'].startswith(('load-idle-recovery:', 'restore-board')):
                    self.assertEqual(case['result'], 'PASS')

    def test_ota_kept_settings(self):
        result = read(DATA / 'ota/report.json')['cases'][0]
        self.assertEqual(result['result'], 'PASS')
        for name in ('wifi_unchanged', 'settings_unchanged', 'playlist_unchanged'):
            self.assertTrue(result['evidence'][name])


if __name__ == '__main__':
    unittest.main()
