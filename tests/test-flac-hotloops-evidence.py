"""Validate retained exactness, host timing and RV32 code-size evidence."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-flac-hotloops-20261008'
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from compare_flac_hotloops import summarize


def read(name):
    return json.loads((DATA/name).read_text())


class HotLoopEvidence(unittest.TestCase):
    def test_archive_and_source_identity(self):
        index = read('index.json')
        files = {p.relative_to(DATA).as_posix() for p in DATA.rglob('*') if p.is_file()}
        self.assertEqual(set(index), files-{'index.json'})
        for name, record in index.items():
            data = (DATA/name).read_bytes()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()),
                             (record['bytes'], record['sha256']), name)
            self.assertNotIn(Path(name).suffix, {'.pcm', '.flac', '.aac', '.obj', '.bin'})
        for folder in ('baseline', 'rice-profile', 'compare', 'matrix', 'radio-asan',
                       'bounds', 'bounds-contiguous', 'rice-parent', 'rice-agent'):
            report = read(folder+'/report.json')
            self.assertTrue(report['passed'])
            for name, digest in report['sources'].items():
                self.assertEqual(hashlib.sha256((DATA/folder/'sources'/name).read_bytes()).hexdigest(), digest)

    def test_reader_state_and_malformed_input(self):
        for folder in ('rice-agent', 'rice-parent'):
            report = read(folder+'/report.json')
            self.assertEqual(report['sanitizers'], ['address', 'undefined'])
            self.assertFalse(report['physical_timing'])
            self.assertTrue(report['identical'])
            for variant in report['variants'].values():
                self.assertEqual(variant, dict(passed=True, cases=294888, reads=941077))
        for folder in ('bounds', 'bounds-contiguous'):
            report = read(folder+'/report.json')
            self.assertTrue(report['sanitizers'] and report['reference']['identical'])
            self.assertEqual(len(report['cases']), 16)
            self.assertTrue(all(c['result'] == 'PASS' for c in report['cases'].values()))
            self.assertEqual(report['edge_cases'], 'PASS')
            self.assertIn('predictor_cases=4492', (DATA/folder/'prediction.log').read_text())

    def test_complete_pcm_and_allocation_recovery(self):
        count = 0
        for folder, expected in (('matrix', 120), ('radio-asan', 20)):
            report = read(folder+'/report.json')
            self.assertEqual(len(report['cases']), expected)
            self.assertTrue(report['sanitizers'])
            self.assertEqual(report['defines'], ['FLAC_BYTEWISE_RICE=1', 'FLAC_LPC_NO_AUTO_UNROLL=1'])
            self.assertEqual(report['failures'], 0)
            for case in report['cases']:
                self.assertTrue(case['reference']['known_pcm_identical'])
                self.assertEqual(set(case['variants']), {'segmented', 'contiguous', 'adapter'})
                for variant in case['variants'].values():
                    self.assertTrue(variant['identical'])
                    self.assertEqual(variant['result'], 'PASS')
                    self.assertEqual(variant['sha256'], case['reference']['sha256'])
                    self.assertEqual(variant['bytes'], case['reference']['bytes'])
                    count += 1
                if folder == 'matrix':
                    self.assertEqual(case['allocation_failures']['result'], 'PASS')
                    self.assertIn('recovery_cases=', case['allocation_failures']['output'])
        self.assertEqual(count, 420)

    def test_hot_stages_and_speed_comparison_are_host_only(self):
        baseline = read('baseline/report.json')
        candidate = read('rice-profile/report.json')
        self.assertEqual(len(baseline['cases']), 20)
        self.assertEqual(len(candidate['cases']), 20)
        self.assertEqual(candidate['defines'], ['FLAC_BYTEWISE_RICE=1'])
        reference = {c['name']: c['reference']['sha256'] for c in read('radio-asan/report.json')['cases']}
        for report in (baseline, candidate):
            self.assertIn('not ESP32-C3 timing', report['platform'])
            self.assertEqual(report['clock'], 'CLOCK_THREAD_CPUTIME_ID')
            for case in report['cases']:
                for variant in case['variants'].values():
                    self.assertTrue(variant['identical'])
                    self.assertEqual(variant['pcm_sha256'], reference[case['name']])
                stage = case['variants']['profile']['stages']
                self.assertEqual(set(stage), {'frame_and_pcm', 'stereo', 'subframe', 'residual', 'prediction'})
                self.assertTrue(all(s['cpu_ns'] > 0 and s['calls'] > 0 for s in stage.values()))
                self.assertLess(sum(s['cpu_ns'] for s in stage.values()), case['variants']['profile']['decode_ns'])
        report = read('compare/report.json')
        self.assertEqual(len(report['rows']), 64)
        self.assertEqual(report['summary'], summarize(report['rows']))
        self.assertEqual(len({(r['name'], r['round'], r['variant']) for r in report['rows']}), 64)
        for row in report['rows']:
            self.assertTrue(row['identical'])
            self.assertEqual(row['pcm_sha256'], reference[row['name']])
        for row in report['summary']:
            self.assertLess(row['change_percent']['rice'], 0)
            # Preserve the adverse LPC32 measurements, not just favorable rows.
            if row['name'].endswith('lpc32'):
                self.assertGreater(row['change_percent']['lpc'], 0)

    def test_parent_target_review_and_rejected_experiment(self):
        report = read('parent-review/report.json')
        for key in ('passed', 'default_alloc_sections_identical',
                    'bounded_shift_alloc_sections_identical', 'non_code_alloc_sections_unchanged'):
            self.assertTrue(report[key])
        sections = report['sections']
        self.assertEqual(sections['original'], sections['default'])
        self.assertEqual({r['variant']: r['text_bytes'] for r in read('rv32/text-comparison.json')},
            {'default': 13592, 'no-auto-unroll': 12886, 'bytewise-rice': 13118, 'combined': 12412})
        for name, rows in sections.items():
            self.assertEqual({k:v for k,v in rows.items() if not k.startswith('.text')},
                             {k:v for k,v in sections['original'].items() if not k.startswith('.text')})
        for directory in ('rv32', 'rejected-shift'):
            for record in read(directory+'/input-hashes.json'):
                name = record['Path'].replace('\\', '/').split('/')[-1]
                if name.endswith('.exe'): continue
                self.assertEqual(hashlib.sha256((DATA/directory/'inputs'/name).read_bytes()).hexdigest(), record['Hash'].lower())
        left = gzip.decompress((DATA/'rejected-shift/default.disassembly.txt.gz').read_bytes()).decode().splitlines()[3:]
        right = gzip.decompress((DATA/'rejected-shift/bounded-shift.disassembly.txt.gz').read_bytes()).decode().splitlines()[3:]
        self.assertEqual(left, right)


if __name__ == '__main__':
    unittest.main()
