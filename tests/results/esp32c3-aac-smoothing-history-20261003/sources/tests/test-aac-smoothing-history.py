#!/usr/bin/env python3
"""Verify retained four-row FIR/PCM evidence and reject incomplete qualification."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import compact_sbr_tables as base
import compact_smoothing_history as patch
import run_aac_smoothing_history as runner
import summarize_aac_smoothing_history as summary

EVIDENCE=ROOT/'tests/results/esp32c3-aac-smoothing-history-20261003'
PREVIOUS=ROOT/'tests/results/esp32c3-aac-high-history-20261003/pc18'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class SmoothingHistoryTests(unittest.TestCase):
    def test_all_inputs_precision_lifecycle_and_real_owner_saving(self):
        comparisons=0
        for name in summary.NAMES:
            folder=EVIDENCE/name;saved=read(folder/'result.json')
            result=runner.parse_log((folder/'qemu.log').read_text(encoding='utf-8'))
            for k,v in result.items():self.assertEqual(saved[k],v,(name,k))
            self.assertEqual(digest(folder/'qemu.log'),saved['provenance']['qemu_log_sha256'])
            self.assertEqual(digest(EVIDENCE/'sdkconfig'),saved['provenance']['sdkconfig_sha256'])
            self.assertTrue(result['precision_pass'])
            self.assertLessEqual(result['max_pcm_error_lsb'],2)
            self.assertEqual((result['allocator']['candidate_request'],result['allocator']['candidate_block']),(45932,47104))
            self.assertEqual(result['measured_owner_block_saving_bytes'],8192)
            self.assertFalse(result['production_qualified'])
            comparisons+=len(result['runs'])
        self.assertEqual(comparisons,81)

    def test_direct_fir_and_coverage_cannot_be_omitted_or_corrupted(self):
        log=(EVIDENCE/'synthetic/qemu.log').read_text(encoding='utf-8')
        for marker in ('SMOOTHING_HISTORY_FIR_PASS','HIGHHISTORY_RESET','HIGHHISTORY_MEMORY','SBRLAYOUT_ALLOCATOR'):
            line=next(s for s in log.splitlines(True) if marker+' ' in s)
            for changed in (log.replace(line,'',1),log+line):
                with self.subTest(marker=marker),self.assertRaises(ValueError):runner.parse_log(changed)
        for old,new in (('retained_rows=4','retained_rows=5'),('taps=5','taps=4'),
                        ('scratch_bytes=1024','scratch_bytes=0'),('guards=pass','guards=corrupt'),
                        ('candidate_request=45932','candidate_request=47980')):
            self.assertIn(old,log)
            with self.subTest(old=old),self.assertRaises(ValueError):runner.parse_log(log.replace(old,new))

    def test_all_91_patches_reconstruct_original_instructions(self):
        prior=base.PATCH_SPECS
        try:
            base.PATCH_SPECS=patch.SPECS
            fields=base.read_layout((EVIDENCE/'layout.o').read_bytes())
            self.assertEqual(fields,read(EVIDENCE/'audit.json')['compiler_layout'])
            self.assertEqual(fields['matrix_size'],[1280,1024])
            patches=base.resolve_patches({k:[v[0],v[0]] for k,v in fields.items()})
            self.assertEqual(sum(map(len,patches.values())),91)
            for function,items in patches.items():
                for offset,word,value,meaning in items:
                    self.assertEqual(base.immediate(int(word,16),len(word)//2,value),int(word,16),
                                     (function,offset,meaning))
        finally:base.PATCH_SPECS=prior
        self.assertEqual(read(EVIDENCE/'audit.json')['envelope_calls'],['0x23c','0xc3a'])

    def test_summary_keeps_stack_cost_and_previous_error_counts(self):
        result=summary.summarize(EVIDENCE,PREVIOUS)
        self.assertEqual(result,read(EVIDENCE/'summary.json'))
        self.assertEqual(summary.table(result),(EVIDENCE/'TABLES.md').read_text(encoding='utf-8'))
        self.assertTrue(result['error_counts_match_previous'])
        self.assertEqual(result['owner_block_saving_vs_previous_bytes'],2048)
        self.assertEqual(result['temporary_stack_payload_bytes'],1024)
        self.assertEqual(result['compiled_complex_wrapper_stack_frame_bytes'],1184)

    def test_failed_real_only_trial_is_retained(self):
        failed=read(EVIDENCE/'rejected/failure.json')
        log=EVIDENCE/'rejected/real-only-null-tables.log'
        self.assertEqual(digest(log),failed['qemu_log_sha256'])
        self.assertIn('Load access fault',log.read_text(encoding='utf-8'))
        with self.assertRaises(ValueError):runner.parse_log(log.read_text(encoding='utf-8'))

    def test_source_and_build_snapshots(self):
        saved=read(EVIDENCE/'implementation.json')
        for name,item in saved['files'].items():
            self.assertEqual(digest(EVIDENCE/item['snapshot']),item['sha256'],name)
        for name,expected in saved['build_evidence'].items():
            self.assertEqual(digest(EVIDENCE/name),expected,name)

if __name__=='__main__':unittest.main()
