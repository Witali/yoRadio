#!/usr/bin/env python3
"""Validate retained address-audit evidence and fail-closed report parsing."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import run_aac_pointer_audit as runner

EVIDENCE = ROOT/'tests/results/esp32c3-aac-pointer-audit-20261003'
RUNS = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')
BOUNDARIES = ROOT/'tests/results/esp32c3-aac-pointer-boundaries-20261003'


class PointerAuditTests(unittest.TestCase):
    def test_all_retained_runs_and_pcm_controls(self):
        configs = hashlib.sha256((EVIDENCE/'sdkconfig').read_bytes()).hexdigest()
        elfs = set()
        for name in RUNS:
            with self.subTest(name=name):
                raw = EVIDENCE/name/'qemu.log'
                saved = json.loads((EVIDENCE/name/'result.json').read_text(encoding='utf-8'))
                for key, value in runner.parse_log(raw.read_text(encoding='utf-8')).items():
                    self.assertEqual(saved[key], value)
                self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), saved['provenance']['qemu_log_sha256'])
                self.assertEqual(configs, saved['provenance']['sdkconfig_sha256'])
                elfs.add(saved['provenance']['elf_sha256'])
                self.assertTrue(saved['precision_pass'])
                self.assertEqual(saved['pcm_without_audit']['different'], 0)
                self.assertEqual(saved['pcm_without_audit']['samples'], 657540)
                if name != 'synthetic':
                    capture = saved['capture']
                    source = saved['provenance']['recording']
                    self.assertEqual(capture['bytes'], source['bytes'])
                    self.assertEqual(capture['rate'], int(source['ffprobe']['streams'][0]['sample_rate']))
                    self.assertEqual(capture['channels'], source['ffprobe']['streams'][0]['channels'])
                    self.assertGreater(capture['samples'], 1000000)
        self.assertEqual(len(elfs), 1)

    def test_totals_and_allocation_cleanup(self):
        summary = json.loads((EVIDENCE/'summary.json').read_text(encoding='utf-8'))
        for key, total in (('checks', 'total_checks'), ('copies', 'total_copies'),
                           ('allocations', 'total_allocations'), ('frees', 'total_frees')):
            self.assertEqual(sum(item['pointers'][key] for item in summary['runs'].values()), summary[total])
        self.assertGreater(summary['total_checks'], 2000000)
        self.assertEqual(summary['total_allocations'], summary['total_frees'])

    def test_missing_coverage_leaks_duplicates_and_error_diagnostics_rejected(self):
        log = (EVIDENCE/'synthetic/qemu.log').read_text(encoding='utf-8')
        marker = re.search(r'AAC_POINTER_PASS[^\r\n]*', log).group()
        for changed in (log.replace('AAC_POINTER_PASS', 'DISABLED_POINTERS'),
                        log.replace('negative_cases=10', 'negative_cases=9'),
                        log.replace('frees=145', 'frees=144'),
                        re.sub(r'copies=\d+', 'copies=0', log),
                        log+'\n'+marker, log+'\naac_pointer: field=wrong_address\n'):
            with self.assertRaises(ValueError):
                runner.parse_log(changed)

    def test_captured_stream_requires_nonempty_measurements(self):
        log = (EVIDENCE/'abba64/qemu.log').read_text(encoding='utf-8')
        marker = re.search(r'AAC_POINTER_CAPTURE[^\r\n]*', log).group()
        with self.assertRaises(ValueError):
            runner.parse_log(log+'\n'+marker)
        with self.assertRaises(ValueError):
            runner.parse_log(log.replace(marker, re.sub(r'samples=\d+', 'samples=0', marker)))

    def test_immutable_source_snapshots(self):
        saved = json.loads((EVIDENCE/'implementation.json').read_text(encoding='utf-8'))
        for path, record in saved['files'].items():
            self.assertEqual(hashlib.sha256((EVIDENCE/record['snapshot']).read_bytes()).hexdigest(),
                             record['sha256'], path)

    def test_ps_coverage_uses_execution_not_ffprobe_label(self):
        followup = ROOT/'tests/results/esp32c3-aac-ps-coverage-20261003'
        reference = json.loads((followup/'result.json').read_text(encoding='utf-8'))
        native = json.loads((EVIDENCE/'groovesalad16/result.json').read_text(encoding='utf-8'))
        baseline = json.loads((EVIDENCE/'synthetic/result.json').read_text(encoding='utf-8'))
        positive = json.loads((EVIDENCE/'abba64/result.json').read_text(encoding='utf-8'))
        self.assertEqual(reference['input_sha256'], native['provenance']['recording']['sha256'])
        self.assertEqual(reference['gdb_elf_sha256'], native['provenance']['elf_sha256'])
        self.assertEqual(reference['ffprobe']['result']['streams'][0]['profile'], 'HE-AACv2')
        for mode in ('fixed', 'float'):
            decoded = json.loads((followup/f'faad-{mode}.log').read_text(encoding='utf-8'))
            self.assertEqual(decoded, reference['faad'][mode]['result'])
            self.assertEqual((decoded['rate'], decoded['channels'], decoded['ps_frames']),
                             (32000, 1, 0))
            self.assertEqual(decoded['frames'], native['capture']['frames'])
        self.assertEqual(reference['ffmpeg']['samples'], native['capture']['samples'])
        self.assertEqual(reference['ffmpeg']['different_lr'], 0)
        self.assertEqual(native['pointers']['ps'], baseline['pointers']['ps'])
        self.assertGreater(positive['pointers']['ps'], baseline['pointers']['ps'])


class PointerBoundaryTests(unittest.TestCase):
    def test_all_current_runs_require_boundary_checks(self):
        elfs = set()
        for name in RUNS:
            with self.subTest(name=name):
                log = BOUNDARIES/name/'qemu.log'
                saved = json.loads((BOUNDARIES/name/'result.json').read_text(encoding='utf-8'))
                for key, value in runner.parse_log(log.read_text(encoding='utf-8'), require_boundaries=True).items():
                    self.assertEqual(saved[key], value)
                self.assertEqual(hashlib.sha256(log.read_bytes()).hexdigest(), saved['provenance']['qemu_log_sha256'])
                self.assertEqual(hashlib.sha256((BOUNDARIES/'sdkconfig').read_bytes()).hexdigest(),
                                 saved['provenance']['sdkconfig_sha256'])
                elfs.add(saved['provenance']['elf_sha256'])
                self.assertTrue(saved['precision_pass'])
                self.assertEqual(saved['pcm_without_audit']['different'], 0)
                self.assertEqual(saved['pointers']['allocations'], saved['pointers']['frees'])
                self.assertEqual(saved['pointer_boundaries']['decode_io'], saved['pointers']['frames'])
                self.assertEqual(saved['stack']['concurrent_peak'], 2)
        self.assertEqual(len(elfs), 1)

    def test_full_recordings_match_previous_hash_and_length(self):
        for name in RUNS[1:]:
            current = json.loads((BOUNDARIES/name/'result.json').read_text(encoding='utf-8'))
            previous = json.loads((EVIDENCE/name/'result.json').read_text(encoding='utf-8'))
            for key in ('bytes', 'rate', 'channels', 'samples', 'frames', 'pcm_hash'):
                self.assertEqual(current['capture'][key], previous['capture'][key], (name, key))
            self.assertEqual(current['provenance']['recording']['sha256'],
                             previous['provenance']['recording']['sha256'])

    def test_missing_duplicate_partial_and_wrong_count_rejected(self):
        log = (BOUNDARIES/'synthetic/qemu.log').read_text(encoding='utf-8')
        marker = re.search(r'AAC_POINTER_BOUNDARY_PASS[^\r\n]*', log).group()
        for changed in (log.replace(marker, ''), log+'\n'+marker,
                        log.replace('release_negative_cases=6', 'release_negative_cases=5'),
                        log.replace('boundary_negative_cases=5', 'boundary_negative_cases=4'),
                        re.sub(r'ps_bits=\d+', 'ps_bits=0', log),
                        re.sub(r'decode_io=\d+', 'decode_io=1', log),
                        log+'\nassert failed: release_allowed(p,state)\n'):
            with self.assertRaises(ValueError):
                runner.parse_log(changed, require_boundaries=True)

    def test_legacy_log_cannot_claim_extended_coverage(self):
        log = (EVIDENCE/'synthetic/qemu.log').read_text(encoding='utf-8')
        self.assertNotIn('pointer_boundaries', runner.parse_log(log))
        with self.assertRaises(ValueError):
            runner.parse_log(log, require_boundaries=True)

    def test_snapshots_and_summary(self):
        saved = json.loads((BOUNDARIES/'implementation.json').read_text(encoding='utf-8'))
        for path, record in saved['files'].items():
            self.assertEqual(hashlib.sha256((BOUNDARIES/record['snapshot']).read_bytes()).hexdigest(),
                             record['sha256'], path)
        summary = json.loads((BOUNDARIES/'summary.json').read_text(encoding='utf-8'))
        for group in ('pointers', 'pointer_boundaries'):
            for key, total in summary['totals'][group].items():
                self.assertEqual(sum(row[group][key] for row in summary['runs'].values()), total)
        self.assertGreater(summary['totals']['pointers']['checks'], 2400000)
        self.assertTrue(summary['all_capture_hashes_match'])


if __name__ == '__main__':
    unittest.main()
