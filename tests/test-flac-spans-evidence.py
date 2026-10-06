"""Verify exact reconstruction and replay the measured span-loop outcomes."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/results/esp32c3-flac-spans-20261006'
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from summarize_sustained import summarize


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SpanEvidence(unittest.TestCase):
    def test_integrity_and_compiled_source(self):
        manifest = read(DATA / 'manifest.json')
        self.assertEqual(set(manifest), {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                        if p.is_file() and p != DATA / 'manifest.json'})
        for name, info in manifest.items():
            path = DATA / name
            self.assertEqual((path.stat().st_size, sha(path)), (info['bytes'], info['sha256']), name)
        build = read(DATA / 'verify/build.json')
        core = 'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'
        for folder in ('bounds', 'contiguous', 'matrix', 'dense-host', 'real24-large'):
            report = read(DATA / folder / 'report.json')
            for name, digest in report['sources'].items():
                self.assertEqual(sha(DATA / folder / 'sources' / name), digest)
            self.assertEqual(report['sources'][core], build['source_sha256'][core])
        self.assertIn('<_Z23restoreLinearPredictionhh.part.0>:',
                      (DATA / 'verify/predictor.asm').read_text())

    def test_exact_pcm_and_sanitizers(self):
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
        for folder in ('bounds', 'contiguous'):
            report = read(DATA / folder / 'report.json')
            self.assertTrue(report['passed'] and report['reference']['identical'])
            self.assertEqual(report['edge_cases'], 'PASS')
            self.assertEqual(report['prediction_cases'], 'PASS')
            self.assertIn('predictor_cases=1222', (DATA / folder / 'prediction.log').read_text())

    def test_build_identity_and_memory(self):
        before = read(ROOT / 'firmware/development/esp32c3-flac-unroll/manifest.json')
        after = read(DATA / 'verify/build.json')
        artifact = ROOT / 'firmware/development/esp32c3-flac-spans'
        self.assertEqual(sha(artifact / 'app.bin'), after['app_sha256'])
        self.assertEqual(sha(artifact / 'sdkconfig'), before['sdkconfig_sha256'])
        self.assertEqual(after['app_bytes'] - before['app_bytes'], 96)
        for name in ('.iram0.text', '.dram0.data', '.dram0.bss', '.rtc.data'):
            self.assertEqual(after['sections'][name], before['sections'][name])
        self.assertFalse(read(artifact / 'manifest.json')['production_qualified'])
        for folder in ('after', 'load16'):
            report = read(DATA / folder / 'report.json')
            self.assertEqual(report['board']['app_elf_sha256'], after['elf_sha256'])
            self.assertEqual(report['config']['sha256'], after['sdkconfig_sha256'])
        ota = read(DATA / 'ota/report.json')['cases'][0]
        self.assertEqual(ota['result'], 'PASS')
        self.assertEqual(ota['evidence']['after']['app_elf_sha256'], after['elf_sha256'])
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(ota['evidence'][key])

    def test_runtime_outcomes_are_not_overridden(self):
        for folder in ('after', 'load16'):
            summary = summarize(DATA / folder)
            self.assertEqual(summary, read(DATA / folder / 'summary.json'))
            for case in summary['cases']:
                dense = 'lpc32dense' in case['name']
                self.assertEqual(case['original']['result'], 'FAIL' if dense else 'PASS')
                if dense:
                    self.assertEqual(case['full_window']['strict']['result'], 'FAIL')
                else:
                    self.assertEqual(case['runtime']['result'], 'PASS')
            for case in read(DATA / folder / 'report.json')['cases']:
                if case['name'].startswith(('load-idle-recovery:', 'restore-board')):
                    self.assertEqual(case['result'], 'PASS')


if __name__ == '__main__':
    unittest.main()
