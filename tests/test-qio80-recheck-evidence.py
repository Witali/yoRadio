"""Replay the retained DIO/QIO comparison, including unsuccessful outcomes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/results/esp32c3-qio80-recheck-20261008'
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from flash_mode import validate


def read(name):
    return json.loads((DATA / name).read_text())


class RecheckEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('qio_recheck_summary', DATA / 'summarize.py')
        cls.replay = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.replay)

    def test_archive_identity_and_private_data_exclusion(self):
        index = read('index.json')
        actual = {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(actual - {'index.json'}, set(index))
        for name, record in index.items():
            data = (DATA / name).read_bytes()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()),
                             (record['bytes'], record['sha256']), name)
            self.assertNotIn('private', Path(name).parts)
            self.assertNotIn(Path(name).suffix, {'.bin', '.elf', '.key', '.pem', '.pcm', '.flac', '.aac'})
            self.assertNotRegex(data, rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----')
        for name, digest in read('source-index.json').items():
            self.assertEqual(hashlib.sha256((DATA / 'sources' / name).read_bytes()).hexdigest(), digest)

    def test_actual_mode_images_and_mapped_reads(self):
        for mode in ('dio', 'qio'):
            artifact = ROOT / f'firmware/development/esp32c3-idf-6.1-r9a97-flash-{mode}80'
            manifest = read(f'artifacts/{mode}/manifest.json')
            app = (artifact / 'app.bin').read_bytes()
            self.assertEqual(hashlib.sha256(app).hexdigest(), manifest['image']['sha256'])
            self.assertEqual(hashlib.sha256((artifact / 'bootloader.bin').read_bytes()).hexdigest(),
                             manifest['bootloader_sha256'])
            self.assertEqual(hashlib.sha256((DATA / f'artifacts/{mode}/sdkconfig').read_bytes()).hexdigest(),
                             manifest['sdkconfig_sha256'])
            for boot in (1, 2):
                name = f'physical/{mode}-boot-{boot}'
                result = validate((DATA / (name + '.log')).read_text(), app, mode)
                saved = read(name + '.json')
                self.assertEqual(result, {k: v for k, v in saved.items() if k != 'identity'})
                self.assertEqual(saved['identity']['app_elf_sha256'], manifest['image']['app_elf_sha256'])
                with self.assertRaises(ValueError):
                    validate((DATA / (name + '.log')).read_text(), app,
                             'qio' if mode == 'dio' else 'dio')
        sections = read('section-comparison.json')
        for section in sections.values():
            self.assertEqual(section['dio'], section['qio'])

    def test_replay_preserves_outcomes_and_restoration(self):
        result = self.replay.summarize(DATA)
        self.assertEqual(result, read('summary.json'))
        self.assertTrue(result['complete'])
        self.assertTrue(result['phases_complete'])
        self.assertTrue(result['restored'])
        self.assertFalse(result['acoustic_continuity_qualified'])
        initial = read('physical/initial.json')
        final = read('physical/final-board.json')
        self.assertEqual(final['identity']['app_elf_sha256'],
                         initial['identity']['app_elf_sha256'])
        self.assertTrue(all(read('physical/flash-restoration.json').values()))
        self.assertTrue(all(final['persistence'].values()))
        self.assertEqual(len(final['status']), 3)
        self.assertTrue(all(s['audio'] == initial['status']['audio']
                            for s in final['status']))
        flash_status = read('physical/flash-status-restoration.json')
        self.assertEqual(flash_status['before'], flash_status['after'])
        recovery = read('physical/restoration-recovery.json')
        self.assertEqual(recovery['initial_controller_exit_code'], 1)
        self.assertEqual(recovery['retry_http_status'], 200)
        self.assertFalse(final['post_retry_snapshot_compared'])
        self.assertFalse(result['all_gates_passed'])
        for mode, variant in result['variants'].items():
            self.assertTrue(variant['matrix_complete'])
            expected = read(f'artifacts/{mode}/manifest.json')['image']['app_elf_sha256']
            for report in variant['reports'].values():
                self.assertEqual(report['board']['app_elf_sha256'], expected)
            self.assertEqual(variant['original_gates_passed'], not variant['failures'])
            for case in variant['performance']:
                if case['runtime_acceptance']['result'] != 'PASS':
                    self.assertFalse(case['acceptance_passed'])
                    self.assertFalse(result['all_gates_passed'])

    def test_missing_case_and_telemetry_cannot_be_accepted(self):
        original = Path.read_text
        target = DATA / 'physical/dio/matrix/report.json'
        def missing_case(path, *args, **kwargs):
            data = original(path, *args, **kwargs)
            if path == target:
                value = json.loads(data)
                value['cases'] = value['cases'][1:]
                return json.dumps(value)
            return data
        with patch.object(Path, 'read_text', missing_case):
            result = self.replay.summarize(DATA)
        self.assertFalse(result['complete'])
        self.assertFalse(result['variants']['dio']['matrix_complete'])
        self.assertFalse(result['all_gates_passed'])

        target = DATA / 'physical/qio/heavy-flac/performance.json'
        def missing_cpu(path, *args, **kwargs):
            data = original(path, *args, **kwargs)
            if path == target:
                return json.dumps([r for r in json.loads(data) if 'PERF CPU:' not in r['line']])
            return data
        with patch.object(Path, 'read_text', missing_cpu):
            result = self.replay.summarize(DATA)
        case = next(c for c in result['variants']['qio']['performance'] if c['case'] == 'heavy-flac')
        self.assertFalse(case['telemetry_complete'])
        self.assertFalse(case['acceptance_passed'])
        self.assertFalse(result['all_gates_passed'])


if __name__ == '__main__':
    unittest.main()
