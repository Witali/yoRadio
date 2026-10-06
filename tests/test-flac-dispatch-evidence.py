"""Replay the exact PCM and board results for the separated FLAC predictor."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/results/esp32c3-flac-dispatch-20261006'
BASELINE = ROOT / 'tests/results/esp32c3-flac-rolling-20261006'
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from summarize_sustained import summarize


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DispatchEvidence(unittest.TestCase):
    def test_integrity_and_compiled_source(self):
        manifest = read(DATA / 'manifest.json')
        self.assertEqual(set(manifest), {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                        if p.is_file() and p != DATA / 'manifest.json'})
        for name, info in manifest.items():
            path = DATA / name
            self.assertEqual((path.stat().st_size, sha(path)), (info['bytes'], info['sha256']), name)
        build = read(DATA / 'verify/build.json')
        core = 'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'
        for folder in ('bounds', 'contiguous', 'matrix', 'long-host', 'real24-large', 'physical-host'):
            report = read(DATA / folder / 'report.json')
            for name, digest in report['sources'].items():
                self.assertEqual(sha(DATA / folder / 'sources' / name), digest)
            self.assertEqual(report['sources'][core], build['source_sha256'][core])

    def test_exact_pcm_and_incomplete_invocation(self):
        total = 0
        for folder in ('matrix', 'long-host', 'real24-large'):
            report = read(DATA / folder / 'report.json')
            self.assertTrue(report['passed'] and report['sanitizers'])
            for case in report['cases']:
                self.assertTrue(case['reference']['known_pcm_identical'])
                for variant in case['variants'].values():
                    self.assertEqual(variant['result'], 'PASS')
                    self.assertEqual(variant['sha256'], case['reference']['sha256'])
                    total += 1
        self.assertEqual(total, 378)
        for folder in ('bounds', 'contiguous'):
            report = read(DATA / folder / 'report.json')
            self.assertTrue(report['passed'] and report['reference']['identical'])
            self.assertEqual(report['edge_cases'], 'PASS')
            self.assertEqual(report['prediction_cases'], 'PASS')
            self.assertIn('predictor_cases=4492', (DATA / folder / 'prediction.log').read_text())
        # The initial mixed-manifest invocation never finished; don't count its
        # duplicate LPC comparisons as another complete successful suite.
        self.assertEqual(read(DATA / 'physical-host/attempt.json')['result'], 'ERROR')
        self.assertNotIn('passed', read(DATA / 'physical-host/report.json'))

    def test_build_identity_and_ota(self):
        before = read(ROOT / 'firmware/development/esp32c3-flac-rolling/manifest.json')
        after = read(DATA / 'verify/build.json')
        artifact = ROOT / 'firmware/development/esp32c3-flac-dispatch'
        self.assertEqual(sha(artifact / 'app.bin'), after['app_sha256'])
        self.assertEqual(sha(artifact / 'sdkconfig'), before['sdkconfig_sha256'])
        self.assertEqual(after['app_bytes'] - before['app_bytes'], -976)
        for name in ('.iram0.text', '.dram0.data', '.dram0.bss', '.rtc.data'):
            self.assertEqual(after['sections'][name], before['sections'][name])
        self.assertFalse(read(artifact / 'manifest.json')['production_qualified'])
        current = read(DATA / 'after/report.json')
        self.assertEqual(current['board']['app_elf_sha256'], after['elf_sha256'])
        repeated = read(DATA / 'repeat/report.json')
        self.assertEqual(repeated['board']['app_elf_sha256'], after['elf_sha256'])
        self.assertEqual(repeated['config'], current['config'])
        for name, digest in repeated['fixture_hashes'].items():
            self.assertEqual(digest, current['fixture_hashes'][name])
        prior = read(BASELINE / 'after/report.json')
        self.assertEqual(current['config'], prior['config'])
        self.assertEqual(current['fixture_hashes'], prior['fixture_hashes'])
        ota = read(DATA / 'ota/report.json')['cases'][0]
        self.assertEqual(ota['result'], 'PASS')
        self.assertEqual(ota['evidence']['after']['app_elf_sha256'], after['elf_sha256'])
        for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
            self.assertTrue(ota['evidence'][key])

    def test_original_load_failures_are_preserved(self):
        for folder in ('after', 'repeat'):
            summary = summarize(DATA / folder)
            self.assertEqual(summary, read(DATA / folder / 'summary.json'))
            cases = read(DATA / folder / 'report.json')['cases']
            for case in summary['cases']:
                original = next(c for c in cases if c['name'] == 'cpu-under-http-load:' + case['name'])
                self.assertEqual(case['original'], original)
            for case in cases:
                if case['name'].startswith(('load-idle-recovery:', 'restore-board')):
                    self.assertEqual(case['result'], 'PASS')


if __name__ == '__main__':
    unittest.main()
