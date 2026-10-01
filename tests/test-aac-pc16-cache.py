"""Validate cache evidence, unchanged PCM, storage accounting and fail-closed parsing."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import run_aac_pc16_cache as cache
from run_aac_reserve import parse_log as owner_log
EVIDENCE=ROOT/'tests/results/esp32c3-aac-pc16-cache-20261001'
BASE=ROOT/'tests/results/esp32c3-aac-pc16-write-20261001'
def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class CacheEvidenceTests(unittest.TestCase):
    def test_saved_pair_matrix_and_fingerprints(self):
        runs=0
        for name in ('synthetic','abba64'):
            report=read(EVIDENCE/name/'result.json');runs+=len(report['runs'])
            for key,value in cache.parse_log((EVIDENCE/name/'qemu.log').read_text()).items():
                self.assertEqual(report[key],value,key)
            self.assertEqual(digest(EVIDENCE/name/'qemu.log'),report['provenance']['qemu_log_sha256'])
            self.assertEqual(digest(EVIDENCE/'sdkconfig'),report['provenance']['sdkconfig_sha256'])
            self.assertIn('CONFIG_YORADIO_AAC_PS_PC16_CACHE=y',(EVIDENCE/'sdkconfig').read_text())
        self.assertEqual(runs,45)
        for path,value in read(EVIDENCE/'implementation.json')['files'].items():
            self.assertEqual(digest(ROOT/path),value,path)

    def test_error_distributions_unchanged(self):
        for name in ('synthetic','abba64'):
            original,current=read(BASE/name/'result.json'),read(EVIDENCE/name/'result.json')
            self.assertEqual(current['precision_pass'],original['precision_pass'])
            self.assertEqual(current['production_precision_pass'],original['production_precision_pass'])
            for a,b in zip(original['runs'],current['runs']):
                for field in ('case','variant','run','frames','samples','max_l','max_r','different','over_one','over_two','over_limit'):
                    self.assertEqual(a[field],b[field],field)
            if name=='abba64':self.assertEqual(original['error_statistics'],current['error_statistics'])

    def test_full_owner_output_is_bit_exact(self):
        report=read(EVIDENCE/'owner/result.json')
        for key,value in owner_log((EVIDENCE/'owner/qemu.log').read_text()).items():
            self.assertEqual(report[key],value,key)
        baseline=read(BASE/'owner/result.json')['pcm']
        for key in ('frames','channels','rate','sample_width','pcm_sha256'):
            self.assertEqual(report['pcm'][key],baseline[key])
        self.assertEqual(report['pcm']['max_pcm_error_lsb'],0)
        for name,key in [('qemu.log','qemu_log_sha256'),('sdkconfig','sdkconfig_sha256')]:
            self.assertEqual(digest(EVIDENCE/'owner'/name),report['provenance'][key])
        self.assertIn('CONFIG_YORADIO_AAC_PS_PC16_CACHE=y',(EVIDENCE/'owner/sdkconfig').read_text())

    def test_cache_memory_and_coverage_cannot_be_faked(self):
        log=(EVIDENCE/'abba64/qemu.log').read_text()
        for old,new in [('cache_bytes=288','cache_bytes=0'),('cache_hits=2221992','cache_hits=0'),
                        ('cache_misses=947928','cache_misses=1'),('heap_saved=0','heap_saved=2156')]:
            self.assertIn(old,log)
            with self.subTest(field=old),self.assertRaises(ValueError):cache.parse_log(log.replace(old,new,1))
        line=next(s for s in log.splitlines(True) if 'PC16WRITE_STORAGE' in s)
        with self.assertRaises(ValueError):cache.parse_log(log.replace(line,'',1))

    def test_recorded_slowdown_not_hidden(self):
        report=read(EVIDENCE/'comparison.json')
        self.assertEqual(report['cache_payload_stack_bytes'],288)
        self.assertEqual(report['decode_function_frame_bytes'],dict(without_cache=128,with_cache=448))
        for row in report['cases']:
            self.assertGreater(row['extra_instructions_vs_pc16_percent'],0)
            self.assertTrue(0<row['cache_hit_percent']<100)

if __name__=='__main__':unittest.main()
