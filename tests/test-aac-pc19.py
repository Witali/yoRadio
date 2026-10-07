"""Replay PC19 precision, allocation, ownership and work-count evidence."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
import compare_aac_sbr_gap_pcm as gaps
import compare_aac_late_sbr_pcm as late
import summarize_aac_pc19 as work
from run_aac_late_sbr import parse_log

EVIDENCE = ROOT / 'tests/results/esp32c3-aac-pc19-20261004'
OLD = ROOT / 'tests/results/esp32c3-aac-sbr-gaps-20261004'


class PC19Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logs = {name: gaps.read_log(EVIDENCE / name / 'qemu.log.gz')
                    for name in ('baseline', 'reference', 'inline', 'candidate')}

    def test_exact_evidence(self):
        checksums = json.loads((EVIDENCE / 'checksums.json').read_text())
        self.assertEqual(set(checksums), {p.relative_to(EVIDENCE).as_posix()
                         for p in EVIDENCE.rglob('*') if p.is_file() and p.name != 'checksums.json'})
        for name, digest in checksums.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest(), digest)

    def test_precision_and_raw_pcm(self):
        for directory, compare in (('pcm', gaps.compare), ('previous-pcm', late.compare)):
            result, left, right = compare(self.logs['reference'], self.logs['candidate'])
            saved = json.loads((EVIDENCE / directory / 'comparison.json').read_text())
            for key, value in result.items():
                self.assertEqual(saved[key], value, key)
            self.assertTrue(result['precision_pass'])
            self.assertLessEqual(result['max_error_lsb'], 3)
            self.assertEqual(result['over_three'], 0)
            self.assertFalse(result['production_qualified'])
            for name, data in (('reference', left), ('candidate', right)):
                self.assertEqual(gzip.decompress((EVIDENCE / directory / (name + '.pcm.gz')).read_bytes()), data)

    def test_pc19_layouts_decode_identically(self):
        for compare in (gaps.compare, late.compare):
            result, left, right = compare(self.logs['inline'], self.logs['candidate'])
            self.assertEqual(left, right)
            self.assertEqual(result['max_error_lsb'], 0)

    def test_new_instrumentation_preserves_reference_and_pc18_pcm(self):
        for new, old in (('reference', 'reference'), ('baseline', 'candidate')):
            old_log = gaps.read_log(OLD / old / 'qemu.log.gz')
            for compare in (gaps.compare, late.compare):
                result, left, right = compare(old_log, self.logs[new])
                self.assertEqual(left, right)
                self.assertEqual(result['max_error_lsb'], 0)
        rejected, _, _ = gaps.compare(self.logs['reference'], self.logs['baseline'])
        self.assertFalse(rejected['precision_pass'])
        self.assertEqual(rejected['max_error_lsb'], 5)
        self.assertEqual(rejected['over_three'], 41)

    def test_allocation_and_instruction_evidence(self):
        result = work.compare_work(self.logs['baseline'], self.logs['candidate'])
        saved = json.loads((EVIDENCE / 'work.json').read_text())
        for key, value in result.items():
            self.assertEqual(saved[key], value, key)
        inline, reference = map(work.parse_work, (self.logs['inline'], self.logs['reference']))
        base, candidate = result['baseline'], result['candidate']
        self.assertEqual(inline['owner_allocated'] - base['owner_allocated'], 2048)
        self.assertEqual(candidate['owner_allocated'], base['owner_allocated'])
        self.assertEqual(result['extra_owner_and_adapter_bytes'], 144)
        self.assertEqual(reference['owner_allocated'], 51188)
        self.assertFalse(result['physical_cpu_qualified'])

    def test_incomplete_or_mismatched_work_is_rejected(self):
        log = self.logs['candidate']
        row = re.search(r'^AAC_GAP_WORK .+$', log, re.MULTILINE)[0]
        for bad in (log.replace(row, '', 1), log.replace(row, row + '\n' + row, 1),
                    log.replace('nop1024=1025', 'nop1024=1024', 1),
                    log.replace('AAC_GAP_ADAPTER_MEMORY', 'LOST_ADAPTER_MEMORY', 1)):
            with self.assertRaises(ValueError):
                work.parse_work(bad)
        calls = re.search(r'calls=(\d+)', row)[1]
        bad = log.replace(row, row.replace('calls=' + calls, 'calls=' + str(int(calls) + 1)), 1)
        with self.assertRaises(ValueError):
            work.compare_work(self.logs['baseline'], bad)

    def test_pointer_and_history_lifetime(self):
        for name in ('baseline', 'inline', 'candidate'):
            result = parse_log(self.logs[name], require_retention=True)
            self.assertEqual(result['pointers']['allocations'], result['pointers']['frees'])
            self.assertGreater(result['pointers']['checks'], 900000)
            self.assertGreaterEqual(result['stack_min_free_bytes'], 2048)
        marker = ('AAC_PC19_REOPEN_PASS channels=distinct channel_cursor=preserved '
                  'sbr_open=zero ps_overlay=preserved')
        self.assertEqual(self.logs['candidate'].count(marker), 1)

    def test_host_arithmetic_and_sanitizer_regression(self):
        record = json.loads((EVIDENCE / 'host/result.json').read_text())
        self.assertEqual(record['exit_code'], 0)
        self.assertIn('exact_pairs=524288 random_pairs=1000000', record['stdout'])
        self.assertIn('split_neighbors=33792', record['stdout'])
        self.assertEqual((EVIDENCE / 'host/test.log').read_text().strip(), record['stdout'].strip())
        for name, digest in record['hashes'].items():
            self.assertEqual(hashlib.sha256((EVIDENCE / 'sources' / Path(name)).read_bytes()).hexdigest(), digest)
        self.assertIn('cannot be represented', (EVIDENCE / 'unsigned-mask-failure/test.log').read_text())


if __name__ == '__main__':
    unittest.main()
