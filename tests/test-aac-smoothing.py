#!/usr/bin/env python3
"""Replay compact smoothing evidence; reject missing coverage and ABI changes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import run_aac_smoothing as runner

EVIDENCE=ROOT/'tests/results/esp32c3-aac-smoothing-20261001'
# Replay the exact patcher used to produce this historical evidence. Current
# compiler-derived patches are checked independently by test-aac-abi.py.
spec=importlib.util.spec_from_file_location('smoothing_snapshot_patcher',EVIDENCE/'implementation-snapshots/compact_sbr_tables.py')
patch=importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
NAMES=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class SmoothingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logs={name:(EVIDENCE/name/'qemu.log').read_text() for name in NAMES}
        cls.results={name:json.loads((EVIDENCE/name/'result.json').read_text()) for name in NAMES}

    def test_reparse_and_hashes(self):
        for name,result in self.results.items():
            with self.subTest(name=name):
                for key,value in runner.parse_log(self.logs[name]).items():self.assertEqual(value,result[key])
                self.assertEqual(sha(EVIDENCE/name/'qemu.log'),result['provenance']['qemu_log_sha256'])
                self.assertEqual(sha(EVIDENCE/'sdkconfig'),result['provenance']['sdkconfig_sha256'])
        manifest=json.loads((EVIDENCE/'implementation.json').read_text())
        for name,entry in manifest['files'].items():
            self.assertEqual(sha(EVIDENCE/entry['snapshot']),entry['sha256'],name)
        self.assertEqual(sha(EVIDENCE/'audit.json'),manifest['audit_sha256'])

    def test_pcm_and_memory_are_separate(self):
        self.assertEqual(sum(len(r['runs']) for r in self.results.values()),81)
        self.assertEqual(sum(r['variant']==1 for x in self.results.values() for r in x['runs']),24)
        self.assertEqual(sum(r['samples'] for x in self.results.values() for r in x['runs'] if r['variant']==1),38596608)
        for result in self.results.values():
            self.assertTrue(result['precision_pass'])
            self.assertEqual(result['precision_limit_lsb'],0)
            probe=result['unguarded_allocator_probe']
            self.assertEqual(probe['reference_block']-probe['candidate_block'],2048)
            for row in result['memory']:
                if row['variant']==1 and row['calls']:
                    self.assertEqual(row['reference']-row['candidate'],1888)
                    # Guards cross a bin boundary; do not fabricate a saving.
                    self.assertEqual(row['physical_reference']-row['physical_candidate'],0)

    def test_lifecycle_and_active_ps(self):
        for result in self.results.values():
            self.assertEqual(result['lifecycle_complete'],dict(samples=1102848,segments=21,failure_paths=2))
        self.assertTrue(all(m['ps_reads']>0 for m in self.results['abba64']['memory'] if m['variant']==1))
        self.assertTrue(all(m['allocations']==0 for m in self.results['groovesalad128']['memory']))

    def test_missing_or_duplicate_evidence_rejected(self):
        log=self.logs['abba64']
        for kind in ('RESULT','MEMORY','EXTERNAL','STATS','HIST','ALLOCATOR','FIR_PASS','LIFECYCLE_PASS'):
            line=next(s for s in log.splitlines(True) if f'SBRLAYOUT_{kind} ' in s)
            for changed in (log.replace(line,'',1),log+line):
                with self.subTest(kind=kind),self.assertRaises(ValueError):runner.parse_log(changed)

    def test_false_precision_memory_and_coverage_rejected(self):
        log=self.logs['synthetic']
        for old,new in (('max_l=0','max_l=1'),('candidate=53240','candidate=55128'),
                        ('candidate_block=53248','candidate_block=55296'),('guard_bytes=32','guard_bytes=0'),
                        ('cases=24','cases=12'),('frames=3 max_index=4','frames=1 max_index=4'),
                        ('PS=checked','PS=skipped'),('qmf_equal=1','qmf_equal=0'),
                        ('smoothing_modes=2','smoothing_modes=0'),('cleanup=complete','cleanup=leaked')):
            self.assertIn(old,log)
            with self.subTest(old=old),self.assertRaises(ValueError):runner.parse_log(log.replace(old,new,1))
        with self.assertRaises(ValueError):runner.parse_log(log+'\nGuru Meditation\n')

    def test_audited_machine_changes_are_immediates_only(self):
        audit=json.loads((EVIDENCE/'audit.json').read_text())
        self.assertEqual(audit['codec_sha256'],patch.PIN)
        self.assertEqual(audit['compact_owner'],patch.SIZE)
        self.assertEqual(set(audit['functions']),set(patch.PATCHES))
        for symbol,info in audit['functions'].items():
            expected=patch.PATCHES[symbol]
            self.assertEqual(len(info['patches']),len(expected))
            self.assertEqual(len({x[0] for x in expected}),len(expected))
            for actual,(offset,old,value,meaning) in zip(info['patches'],expected):
                self.assertEqual(actual['offset'],hex(offset))
                self.assertEqual(actual['meaning'],meaning)
                width=len(old)//2;before=int(old,16);after=int(actual['replacement'],16)
                self.assertEqual(after,patch.immediate(before,width,value))
                mask=0x107c if width==2 else (0xfe000f80 if before&127==0x23 else 0xfff00000)
                self.assertEqual((before^after)&~mask,0)
        # Regression: pointer stored at +0x1d0 and the initializer cursor must
        # BOTH move. Leaving the cursor unchanged caused the first PS fault.
        offsets={x[0] for x in patch.PATCHES['ps_allocate_decoder']}
        self.assertTrue({0xa2,0x102}.issubset(offsets))

    def test_wrong_archive_and_immediate_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'wrong.a';path.write_bytes(b'not the audited archive')
            with self.assertRaisesRegex(ValueError,'SHA differs'):
                patch.build(path,Path(folder)/'out',Path('unused-ar'),Path('unused-objcopy'))
        for word,width,value in ((0x8082,2,12),(0x1117a023,4,2048),(0x00000097,4,1)):
            with self.assertRaises(ValueError):patch.immediate(word,width,value)


if __name__=='__main__':unittest.main()
