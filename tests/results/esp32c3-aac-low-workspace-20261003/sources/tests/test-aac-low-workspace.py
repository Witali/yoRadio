#!/usr/bin/env python3
"""Retained RV32 address, lifetime, PCM and allocation evidence for low-QMF reuse."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import sys
import unittest
import wave
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import compact_sbr_tables as base
import compact_low_workspace as patch
import run_aac_low_workspace as runner
import run_aac_pointer_audit as pointer_runner

EVIDENCE=ROOT/'tests/results/esp32c3-aac-low-workspace-20261003'
BASELINE=ROOT/'tests/results/esp32c3-aac-pointer-boundaries-20261003'
RUNS=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class LowWorkspaceTests(unittest.TestCase):
    def test_retained_runs_preserve_controls_and_captures(self):
        elfs=set()
        for name in RUNS:
            with self.subTest(name=name):
                folder=EVIDENCE/name
                saved=read(folder/'result.json')
                for key,value in runner.parse_log((folder/'qemu.log').read_text(encoding='utf-8')).items():
                    self.assertEqual(saved[key],value,key)
                self.assertEqual(saved['provenance']['qemu_log_sha256'],sha(folder/'qemu.log'))
                self.assertEqual(saved['provenance']['sdkconfig_sha256'],sha(EVIDENCE/'sdkconfig'))
                self.assertEqual(saved['baseline_sha256'],sha(BASELINE/name/'result.json'))
                elfs.add(saved['provenance']['elf_sha256'])
                self.assertTrue(saved['precision_pass'])
                self.assertFalse(saved['production_qualified'])
                self.assertEqual(saved['pcm_vs_previous']['different'],0)
                self.assertEqual(saved['pcm_vs_previous']['samples'],657540)
                self.assertEqual(saved['pointers']['allocations'],saved['pointers']['frees'])
                self.assertEqual(saved['low_pointer_bindings']*2,saved['pointers']['frames'])
                self.assertEqual(saved['low_pointer_negative_cases'],6)
                if name!='synthetic':
                    prior=read(BASELINE/name/'result.json')
                    self.assertTrue(saved['capture_identical'])
                    for key in ('bytes','rate','channels','samples','frames','pcm_hash'):
                        self.assertEqual(saved['capture'][key],prior['capture'][key],key)
                    self.assertEqual(saved['provenance']['recording']['sha256'],
                                     prior['provenance']['recording']['sha256'])
        self.assertEqual(len(elfs),1)

    def test_control_pcm_is_recomputed_from_retained_wav(self):
        audio={}
        for name in ('previous','candidate'):
            wav=gzip.decompress((EVIDENCE/f'control-{name}.wav.gz').read_bytes())
            with wave.open(io.BytesIO(wav)) as stream:
                self.assertEqual((stream.getnchannels(),stream.getsampwidth(),stream.getframerate()),(2,2,48000))
                audio[name]=stream.readframes(stream.getnframes())
            if name=='previous':
                self.assertEqual(hashlib.sha256(wav).hexdigest(),
                                 read(EVIDENCE/'synthetic/result.json')['pcm_vs_previous']['reference_wav_sha256'])
        self.assertEqual(audio['previous'],audio['candidate'])
        self.assertEqual(len(audio['candidate'])//2,657540)
        for name in RUNS:
            saved=read(EVIDENCE/name/'result.json')['pcm_vs_previous']
            self.assertEqual(hashlib.sha256(audio['candidate']).hexdigest(),saved['pcm_sha256'])
            self.assertEqual((saved['different'],saved['max_pcm_error_lsb'],saved['rms_error_lsb']),(0,0,0))

    def test_missing_duplicate_wrong_storage_and_lifetime_reports_rejected(self):
        log=(EVIDENCE/'synthetic/qemu.log').read_text(encoding='utf-8')
        for marker in ('AAC_LOW_WORKSPACE_PASS','AAC_LOW_POINTER_PASS','AAC_POINTER_BOUNDARY_PASS'):
            line=re.search(marker+r'[^\r\n]*',log).group()
            for bad in (log.replace(line,''),log+'\n'+line):
                with self.subTest(marker=marker),self.assertRaises(ValueError):runner.parse_log(bad)
        for old,new in (('work_bytes=10240','work_bytes=10236'),('stored_bytes=4096','stored_bytes=4092'),
                        ('owner_bytes=35900','owner_bytes=45932'),('task_stack_bytes=16384','task_stack_bytes=8192'),
                        ('negative_cases=6','negative_cases=5')):
            self.assertIn(old,log)
            with self.subTest(old=old),self.assertRaises(ValueError):runner.parse_log(log.replace(old,new))
        for bad in (re.sub(r'bindings=\d+','bindings=1',log),re.sub(r'calls=\d+','calls=1',log),
                    log+'\naac_pointer: field=wrong_low_matrix\n',log+'\nassert failed: LOW_WORK_GUARD\n'):
            with self.assertRaises(ValueError):runner.parse_log(bad)

    def test_all_164_address_immediates_reconstruct_original_words(self):
        previous=base.PATCH_SPECS
        try:
            base.PATCH_SPECS=patch.SPECS
            fields=base.read_layout((EVIDENCE/'layout.o').read_bytes())
            self.assertEqual(fields,read(EVIDENCE/'audit.json')['compiler_layout'])
            patches=base.resolve_patches({key:[value[0],value[0]] for key,value in fields.items()})
            self.assertEqual(sum(map(len,patches.values())),164)
            for function,items in patches.items():
                offsets=[offset for offset,_,_,_ in items]
                self.assertEqual(len(offsets),len(set(offsets)),function)
                for offset,word,value,meaning in items:
                    self.assertEqual(base.immediate(int(word,16),len(word)//2,value),int(word,16),
                                     (function,offset,meaning))
            self.assertEqual(fields['left_sample_mode'],[212,220])
            self.assertIn((0x89c,'0d4da703','lo:left_sample_mode','low workspace: lo:left_sample_mode'),
                          patch.SPECS['PVMP4AudioDecodeFrame'])
        finally:base.PATCH_SPECS=previous

    def original_low_bases(self):
        patched=(EVIDENCE/'sbr_dec.c.obj').read_bytes()
        section=ELFFile(io.BytesIO(patched)).get_section_by_name('.text.sbr_dec')
        original=bytearray(patched)
        for sites in patch.LOW_BASES.values():
            for offset,word in sites:
                struct.pack_into('<I',original,section['sh_offset']+offset,int(word,16))
        return bytes(original),section['sh_offset']

    def test_exactly_14_low_bases_become_scoped_loads_and_nothing_else_changes(self):
        original,start=self.original_low_bases()
        slots=patch.read_slots((EVIDENCE/'layout.o').read_bytes())
        self.assertEqual(slots,{'real':-8,'imag':-4})
        changed,records=patch.bind_low_bases(original,slots)
        self.assertEqual(len(records),14)
        self.assertEqual(changed,(EVIDENCE/'sbr_dec.c.obj').read_bytes())
        covered=set()
        for part,sites in patch.LOW_BASES.items():
            for offset,word in sites:
                covered.update(range(start+offset,start+offset+4))
                inst=struct.unpack_from('<I',changed,start+offset)[0]
                self.assertEqual(inst&0x707f,0x2003)  # LW
                self.assertEqual((inst>>15)&31,19)  # frame register s3
                self.assertEqual((inst>>7)&31,(int(word,16)>>7)&31)
                self.assertEqual((inst>>20)-4096,slots[part])
        self.assertTrue(all(a==b or index in covered for index,(a,b) in enumerate(zip(original,changed))))
        self.assertEqual(sha(EVIDENCE/'sbr_dec.c.obj'),read(EVIDENCE/'audit.json')['functions']['sbr_dec']['output_sha256'])

    def test_wrong_opcode_missing_descriptor_and_invalid_slots_rejected(self):
        original,start=self.original_low_bases()
        offset=patch.LOW_BASES['real'][0][0]
        broken=bytearray(original);broken[start+offset]^=1
        with self.assertRaises(ValueError):patch.bind_low_bases(bytes(broken),{'real':-8,'imag':-4})
        with self.assertRaises(ValueError):patch.read_slots((EVIDENCE/'sbr_dec.c.obj').read_bytes())
        for slots in ({'real':-7,'imag':-3},{'real':-8,'imag':0},{'real':-4,'imag':-8},
                      {'real':-12,'imag':-4},{'real':-4096,'imag':-4092},{'real':-8}):
            with self.subTest(slots=slots),self.assertRaises(ValueError):patch.bind_low_bases(original,slots)

    def test_rejected_prefix_revision_does_not_qualify(self):
        folder=EVIDENCE/'rejected-prefix'
        failed=read(folder/'failure.json')
        self.assertEqual(failed['qemu_log_sha256'],sha(folder/'qemu.log'))
        log=(folder/'qemu.log').read_text(encoding='utf-8')
        self.assertIn('assert failed: check_fixture',log)
        with self.assertRaises(ValueError):runner.parse_log(log)
        old=read(folder/'audit.json')['functions']['PVMP4AudioDecodeFrame']['patches']
        new=read(EVIDENCE/'audit.json')['functions']['PVMP4AudioDecodeFrame']['patches']
        self.assertFalse(any(int(row['offset'],16)==0x89c for row in old))
        self.assertTrue(any(int(row['offset'],16)==0x89c for row in new))

    def test_memory_and_audit_totals_keep_stack_cost_visible(self):
        saved=read(EVIDENCE/'summary.json')
        runs=[read(EVIDENCE/name/'result.json') for name in RUNS]
        self.assertEqual(saved['owner_request_bytes'],35900)
        self.assertEqual(saved['owner_block_saving_bytes'],10240)
        self.assertEqual(saved['temporary_stack_payload_bytes'],10240)
        self.assertEqual(saved['decoder_task_stack_bytes'],16384)
        self.assertEqual(saved['minimum_test_stack_free_bytes'],min(row['stack']['min_free_bytes'] for row in runs))
        self.assertGreaterEqual(saved['minimum_test_stack_free_bytes'],1024)
        self.assertEqual(saved['low_workspace_calls'],sum(row['low_workspace']['calls'] for row in runs))
        for key,value in saved['pointers'].items():
            self.assertEqual(value,sum(row['pointers'][key] for row in runs))
        self.assertEqual(saved['capture_samples'],sum(row.get('capture',{}).get('samples',0) for row in runs))
        self.assertEqual(saved['pointers']['allocations'],saved['pointers']['frees'])
        self.assertFalse(saved['production_qualified'])

    def test_scope_sources_and_binary_evidence_are_retained_exactly(self):
        config=(EVIDENCE/'sdkconfig').read_text(encoding='utf-8')
        for flag in ('YORADIO_QEMU','YORADIO_QEMU_AAC_POINTER_AUDIT','YORADIO_QEMU_AAC_LOW_WORKSPACE'):
            self.assertIn('CONFIG_'+flag+'=y\n',config)
        self.assertNotIn('CONFIG_YORADIO_QEMU_AAC_LOW_LIFETIME=y\n',config)
        manifest=read(EVIDENCE/'implementation.json')
        for path,record in manifest['files'].items():
            self.assertEqual(sha(EVIDENCE/record['snapshot']),record['sha256'],path)
        for path,expected in manifest['build_evidence'].items():
            self.assertEqual(sha(EVIDENCE/path),expected,path)

    def test_flag_off_rebuild_preserves_previous_adapter(self):
        folder=EVIDENCE/'flag-off'
        saved=read(folder/'result.json')
        log=(folder/'qemu.log').read_text(encoding='utf-8')
        for key,value in pointer_runner.parse_log(log,require_boundaries=True).items():
            self.assertEqual(saved[key],value,key)
        self.assertNotIn('AAC_LOW_WORKSPACE_PASS',log)
        self.assertNotIn('CONFIG_YORADIO_QEMU_AAC_LOW_WORKSPACE=y\n',
                         (folder/'sdkconfig').read_text(encoding='utf-8'))
        self.assertTrue(saved['precision_pass'])
        self.assertEqual(saved['pcm_without_audit']['different'],0)
        self.assertEqual(saved['pcm_without_audit']['samples'],657540)
        self.assertEqual(saved['memory']['owner_bytes'],45932)
        self.assertEqual(saved['provenance']['qemu_log_sha256'],sha(folder/'qemu.log'))
        self.assertEqual(saved['provenance']['sdkconfig_sha256'],sha(folder/'sdkconfig'))


if __name__=='__main__':unittest.main()
