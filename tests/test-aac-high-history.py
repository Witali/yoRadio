#!/usr/bin/env python3
"""Check persistent QMF precision, actual allocation and fail-closed ABI patches."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import compact_sbr_tables as base
import compact_high_history as patch
import run_aac_high_history as runner
import summarize_aac_high_history as summary
import run_aac_compact_owner as lossless

EVIDENCE=ROOT/'tests/results/esp32c3-aac-high-history-20261003'
NAMES=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class HighHistoryTests(unittest.TestCase):
    def test_all_saved_pcm_and_allocation_results(self):
        comparisons=0
        for variant in ('pc18','pc16'):
            for name in NAMES:
                folder=EVIDENCE/variant/name
                saved=read(folder/'result.json')
                for k,v in runner.parse_log((folder/'qemu.log').read_text(encoding='utf-8')).items():
                    self.assertEqual(saved[k],v,(variant,name,k))
                self.assertEqual(digest(folder/'qemu.log'),saved['provenance']['qemu_log_sha256'])
                self.assertEqual(digest(EVIDENCE/variant/'sdkconfig'),saved['provenance']['sdkconfig_sha256'])
                self.assertEqual(saved['measured_owner_block_saving_bytes'],6144)
                self.assertFalse(saved['production_qualified'])
                comparisons+=len(saved['runs'])
        self.assertEqual(comparisons,162)

    def test_original_layout_recovers_every_native_instruction(self):
        previous=base.PATCH_SPECS
        try:
            base.PATCH_SPECS=patch.SPECS
            for variant in ('pc18','pc16'):
                fields=base.read_layout((EVIDENCE/variant/'layout.o').read_bytes())
                self.assertEqual(fields,read(EVIDENCE/variant/'audit.json')['compiler_layout'])
                original={k:[v[0],v[0]] for k,v in fields.items()}
                instructions=base.resolve_patches(original)
                self.assertEqual(sum(map(len,instructions.values())),87)
                for function,items in instructions.items():
                    for offset,word,value,meaning in items:
                        self.assertEqual(base.immediate(int(word,16),len(word)//2,value),int(word,16),
                                         (variant,function,offset,meaning))
        finally:base.PATCH_SPECS=previous

    def test_both_layouts_fit_ps_and_same_allocator_bin(self):
        for variant,channel,request in (('pc18',23984,47980),('pc16',23840,47692)):
            a=read(EVIDENCE/variant/'audit.json')
            self.assertEqual(a['compact_channel'],channel)
            self.assertEqual(set(a['history_copy_calls']),{hex(n) for n in set(patch.HISTORY_CALLS)|patch.OTHER_MEMMOVES})
            self.assertEqual(sum(v!='forward unchanged' for v in a['history_copy_calls'].values()),6)
            p=read(EVIDENCE/variant/'synthetic/result.json')['allocator']
            self.assertEqual((p['candidate_request'],p['candidate_block']),(request,49152))

    def test_missing_coverage_or_corruption_is_rejected(self):
        log=(EVIDENCE/'pc18/synthetic/qemu.log').read_text(encoding='utf-8')
        for marker in ('HIGHHISTORY_MEMORY','HIGHHISTORY_RESET','HIGHHISTORY_LIFECYCLE','SBRLAYOUT_RESULT','SBRLAYOUT_ALLOCATOR'):
            line=next(s for s in log.splitlines(True) if marker+' ' in s)
            for changed in (log.replace(line,'',1),log+line):
                with self.subTest(marker=marker),self.assertRaises(ValueError):runner.parse_log(changed)
        for old,new in (('saturations=0','saturations=1'),('state_bytes=44','state_bytes=0'),
                        ('candidate_block=49152','candidate_block=55296'),
                        ('segments=21','segments=20'),('guards=pass','guards=corrupt')):
            self.assertIn(old,log)
            with self.subTest(old=old),self.assertRaises(ValueError):runner.parse_log(log.replace(old,new))

    def test_reset_and_lifecycle_error_are_part_of_precision_gate(self):
        log=(EVIDENCE/'pc18/synthetic/qemu.log').read_text(encoding='utf-8')
        changed=log.replace('HIGHHISTORY_RESET case=he44 max_error=1','HIGHHISTORY_RESET case=he44 max_error=4')
        self.assertNotEqual(changed,log)
        result=runner.parse_log(changed)
        self.assertEqual(result['max_pcm_error_lsb'],4)
        self.assertFalse(result['precision_pass'])

    def test_saved_sources_and_build_evidence(self):
        manifest=read(EVIDENCE/'implementation.json')
        for name,item in manifest['files'].items():
            self.assertEqual(digest(EVIDENCE/item['snapshot']),item['sha256'],name)
        for name,sha in manifest['build_evidence'].items():
            self.assertEqual(digest(EVIDENCE/name),sha,name)

    def test_shared_eighteen_passes_current_accuracy_gate(self):
        results=[read(EVIDENCE/'pc18'/name/'result.json') for name in NAMES]
        self.assertTrue(all(r['precision_pass'] for r in results))
        self.assertEqual(max(r['max_pcm_error_lsb'] for r in results),2)
        synthetic=results[0]
        for mode in ('real_frames','complex_frames'):
            self.assertGreater(sum(h[mode] for h in synthetic['history']),0)

    def test_summary_preserves_accuracy_and_measured_memory(self):
        saved=read(EVIDENCE/'summary.json')
        self.assertEqual(saved,summary.summarize(EVIDENCE))
        self.assertEqual((EVIDENCE/'TABLES.md').read_text(encoding='utf-8'),summary.table(saved))
        for variant,peak in (('pc18',2),('pc16',3)):
            rows=[r for r in saved['rows'] if r['format']==variant]
            self.assertEqual(max(r['max_decode_error_lsb'] for r in rows),peak)
            self.assertTrue(all(r['production_precision_pass'] and not r['production_qualified'] for r in rows))

    def test_original_lossless_profile_stays_bit_exact(self):
        folder=EVIDENCE/'lossless-regression'
        saved=read(folder/'result.json')
        for k,v in lossless.parse_log((folder/'qemu.log').read_text(encoding='utf-8')).items():
            self.assertEqual(saved[k],v,k)
        self.assertEqual(digest(folder/'qemu.log'),saved['provenance']['qemu_log_sha256'])
        self.assertEqual(digest(folder/'sdkconfig'),saved['provenance']['sdkconfig_sha256'])
        self.assertTrue(saved['precision_pass'])
        self.assertEqual(saved['precision_limit_lsb'],0)

if __name__=='__main__':unittest.main()
