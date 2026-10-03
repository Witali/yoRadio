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


if __name__ == '__main__':
    unittest.main()
