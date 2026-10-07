"""Verify the complete, intentionally failing original Vorbis qualification run."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'tests/results/esp32c3-vorbis-lifecycle-20261004'
# Importing the frozen runner must not add a __pycache__ to retained evidence.
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
import run_vorbis_lifecycle as runner
import save_vorbis_lifecycle as saver


class RetainedLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((EVIDENCE / 'report.json').read_text())
        cls.summary = json.loads((EVIDENCE / 'summary.json').read_text())
        cls.symbols = runner.symbol_table((EVIDENCE / 'symbols.txt').read_text())

    def test_manifest_covers_every_retained_byte(self):
        manifest = json.loads((EVIDENCE / 'manifest.json').read_text())
        files = {p.relative_to(EVIDENCE).as_posix() for p in EVIDENCE.rglob('*')
                 if p.is_file() and p.name != 'manifest.json'}
        self.assertEqual(set(manifest), files)
        for name, identity in manifest.items():
            with self.subTest(file=name):
                path = EVIDENCE / name
                self.assertEqual(path.stat().st_size, identity['bytes'])
                self.assertEqual(runner.sha(path), identity['sha256'])

    def test_exact_run_and_validator_provenance(self):
        for name, digest in self.report['source_sha256'].items():
            self.assertEqual(runner.sha(EVIDENCE / 'sources' / name), digest, name)
        for filename, key in [('run_vorbis_lifecycle.py', 'classifier_sha256'),
                              ('save_vorbis_lifecycle.py', 'saver_sha256')]:
            self.assertEqual(runner.sha(EVIDENCE / 'validation_sources' / filename),
                             self.summary[key])
        self.assertEqual(runner.sha(EVIDENCE / 'sdkconfig'), self.report['config_sha256'])
        self.assertEqual(runner.sha(EVIDENCE / 'build/yoradio_esp32c3_oled_native.bin'),
                         self.report['app_sha256'])
        self.assertEqual(self.report['archive_sha256'], runner.ARCHIVES)
        fixture = self.report['fixture']
        self.assertEqual(runner.sha(ROOT / 'tests/fixtures/esp32c3_calibration' / fixture['file']),
                         fixture['sha256'])

    def test_saver_rejects_rebuilt_images_or_changed_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            build = folder / 'build'
            source = folder / 'sources/harness.c'
            build.mkdir()
            source.parent.mkdir()
            source.write_bytes(b'original source')
            report = {'source_sha256': {'harness.c': runner.sha(source)}}
            for name, key in [('sdkconfig', 'config_sha256'),
                              ('yoradio_esp32c3_oled_native.bin', 'app_sha256'),
                              ('yoradio_esp32c3_oled_native.elf', 'elf_sha256')]:
                (build / name).write_bytes(name.encode())
                report[key] = runner.sha(build / name)
            (folder / 'report.json').write_text(json.dumps(report))
            saver.verify_artifacts(folder, build)
            source.write_bytes(b'changed source')
            with self.assertRaisesRegex(ValueError, 'Source snapshot changed'):
                saver.verify_artifacts(folder, build)
            source.write_bytes(b'original source')
            (build / 'yoradio_esp32c3_oled_native.bin').write_bytes(b'rebuilt app')
            with self.assertRaisesRegex(ValueError, 'Build changed'):
                saver.verify_artifacts(folder, build)

    def test_recompute_every_outcome_and_peak_from_raw_logs(self):
        expected = {k: v for k, v in self.summary.items()
                    if k not in ('classifier_sha256', 'saver_sha256')}
        self.assertEqual(saver.summarize(EVIDENCE), expected)
        self.assertEqual(self.summary['cycles'], 100)
        self.assertEqual(self.summary['allocation_failure_cases'], 198)
        self.assertEqual(self.summary['malformed_cases'], 4)
        self.assertEqual(self.summary['oom_counts'],
                         {'CRASH': 189, 'HANDLED': 6, 'UNSAFE_RETURN': 3})
        self.assertFalse(self.report['decoder_gate_pass'])
        self.assertFalse(self.summary['decoder_fixed'])
        self.assertFalse(self.summary['hardware_tested'])

    def test_both_historical_and_ordered_ledgers_are_reproducible(self):
        # The executed runner grouped events by kind. Keep its exact hashes;
        # ordered ledgers used for ownership replay were derived afterwards.
        spec = importlib.util.spec_from_file_location(
            'historical_vorbis_runner',
            EVIDENCE / 'sources/tools/codec_benchmark/run_vorbis_lifecycle.py')
        historical = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(historical)
        for case in self.report['cases']:
            with self.subTest(case=case['name']):
                _, log = saver.read_log(EVIDENCE, case['name'])
                ledger_file = EVIDENCE / (case['name'] + '-allocations.json.gz')
                self.assertEqual(json.loads(gzip.decompress(ledger_file.read_bytes())),
                                 runner.allocation_ledger(log, self.symbols))
                old = historical.allocation_ledger(log, self.symbols)
                # Original Path.write_text() ran on Windows and wrote CRLF.
                payload = (json.dumps(old, indent=2) + '\n').replace('\n', '\r\n').encode()
                self.assertEqual(hashlib.sha256(payload).hexdigest(),
                                 case['allocation_ledger_sha256'])

    def test_silent_loss_remains_a_decoder_failure(self):
        cases = {c['name']: c for c in self.summary['outcomes']}
        self.assertEqual({name for name, case in cases.items()
                          if case['status'] == 'UNSAFE_RETURN'},
                         {'oom-0003', 'oom-0004', 'oom-0198'})
        for name in ('oom-0003', 'oom-0004'):
            self.assertEqual(cases[name]['result']['pcm'], 0)
            self.assertEqual(cases[name]['result']['result'], 0)
        truncated = cases['oom-0198']['result']
        self.assertEqual(truncated['result'], 0)
        self.assertEqual(self.summary['baseline_reference']['pcm'] - truncated['pcm'], 3584)
        self.assertNotEqual(truncated['sha256'], self.summary['baseline_reference']['sha256'])


if __name__ == '__main__':
    unittest.main()
