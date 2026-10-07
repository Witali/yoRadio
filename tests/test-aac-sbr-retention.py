"""Retained SBR state, raw transition PCM and native-branch provenance checks."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import patch_aac_late_sbr as patch
import compare_aac_late_sbr_pcm as pcm
from run_aac_late_sbr import parse_log
EVIDENCE=ROOT/'tests/results/esp32c3-aac-sbr-retention-20261004'
TOOLCHAIN=None


def sha(data):return hashlib.sha256(data).hexdigest()
def read(name):return json.loads((EVIDENCE/name).read_text())


class RetentionTests(unittest.TestCase):
    def test_exact_evidence(self):
        for name,expected in read('checksums.json').items():
            with self.subTest(file=name):self.assertEqual(sha((EVIDENCE/name).read_bytes()),expected)

    def test_faad_retains_established_extensions(self):
        phases=[]
        for mode in ('float','fixed'):
            rows=[list(map(int,line.split())) for line in (EVIDENCE/f'faad/{mode}.frames').read_text().splitlines()]
            self.assertEqual(len(rows),41)
            self.assertTrue(all(r[2:]==[44100,2,1,1] for r in rows[13:]))
            phases.append(rows)
        self.assertEqual(phases[0],phases[1])
        self.assertEqual(read('faad/provenance.json')['pristine_source_files_verified'],129)

    def test_retention_and_output_bounds(self):
        log=pcm.read_log(EVIDENCE/'candidate/qemu.log.gz')
        parsed=parse_log(log,require_retention=True)
        self.assertTrue(parsed['retention_format_pass'])
        self.assertTrue(parsed['output_poison_independent'])
        self.assertFalse(parsed['production_qualified'])
        with self.assertRaises(ValueError):parse_log(log.replace('missing_frames=13','missing_frames=12',1),require_retention=True)

    def test_exact_pcm_against_full_precision_history(self):
        result,left,right=pcm.compare(pcm.read_log(EVIDENCE/'reference/qemu.log.gz'),pcm.read_log(EVIDENCE/'candidate/qemu.log.gz'))
        saved=read('pcm/comparison.json')
        for key,value in result.items():self.assertEqual(saved[key],value,key)
        self.assertEqual(result['channel_samples'],189440)
        self.assertTrue(result['precision_pass'])
        self.assertLessEqual(result['max_error_lsb'],3)
        self.assertEqual(gzip.decompress((EVIDENCE/'pcm/reference.pcm.gz').read_bytes()),left)
        self.assertEqual(gzip.decompress((EVIDENCE/'pcm/candidate.pcm.gz').read_bytes()),right)

    def test_incomplete_or_malformed_capture_is_rejected(self):
        log=pcm.read_log(EVIDENCE/'candidate/qemu.log.gz')
        for before,after in [('frame=1 offset=0','frame=1 offset=256'),('channels=1 bytes=2048','channels=2 bytes=2048'),
                             ('QEMU_SMOKE_PASS','INCOMPLETE'),('poison_patterns=2','poison_patterns=1')]:
            with self.subTest(before=before):
                self.assertIn(before,log)
                with self.assertRaises(ValueError):pcm.parse_capture(log.replace(before,after,1))
        with self.assertRaises(ValueError):pcm.parse_capture(log+'\nGuru Meditation')

    def test_patch_changes_only_one_native_instruction(self):
        for variant in ('candidate','reference'):
            folder=EVIDENCE/variant
            before=(folder/'late-sbr-input.o').read_bytes()
            after=(folder/'pvmp4audiodecoderframe.c.obj').read_bytes()
            audit=json.loads((folder/'late-sbr-audit.json').read_text())
            _,code,_,_,_,branch,disable,active=patch.locate(before)
            changed=ELFFile(io.BytesIO(after)).get_section_by_name(patch.SECTION).data()
            self.assertEqual(code.data()[:branch],changed[:branch])
            self.assertEqual(code.data()[branch+4:],changed[branch+4:])
            self.assertEqual(changed[branch:branch+4],bytes.fromhex('6f000000'))
            self.assertEqual((audit['branch_offset'],audit['disable_offset'],audit['active_offset']),(branch,disable,active))
            self.assertEqual(audit['input_sha256'],sha(before));self.assertEqual(audit['output_sha256'],sha(after))
            self.assertFalse(audit['structure_offsets_changed'])
            with self.assertRaises(ValueError):patch.locate(after)

    def test_wrong_native_instructions_and_relocations_rejected(self):
        original=(EVIDENCE/'candidate/late-sbr-input.o').read_bytes()
        _,code,_,rels,index,branch,_,_=patch.locate(original)
        for offset in (code['sh_offset']+branch-4,code['sh_offset']+branch,code['sh_offset']+branch+4):
            changed=bytearray(original);changed[offset]^=1
            with self.subTest(offset=offset),self.assertRaises(ValueError):patch.locate(changed)
        changed=bytearray(original)
        entry=rels['sh_offset']+index*rels['sh_entsize']+4
        info=struct.unpack_from('<I',changed,entry)[0]
        struct.pack_into('<I',changed,entry,(info&~255)|patch.R_RISCV_JAL)
        with self.assertRaises(ValueError):patch.locate(changed)

    def test_fresh_bridge_build_and_full_input_hash_gate(self):
        if TOOLCHAIN is None:self.skipTest('Pass --toolchain for fresh native bridge checks')
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory);native=directory/'native.o'
            original=(EVIDENCE/'candidate/late-sbr-input.o').read_bytes()
            native.write_bytes(original)
            (directory/'audit.json').write_bytes((EVIDENCE/'candidate/audit.json').read_bytes())
            tool=lambda name:TOOLCHAIN/('riscv32-esp-elf-'+name+'.exe')
            bridge=ROOT/'idf/esp32c3-oled-native/main/aac_late_sbr_bridge.S'
            result=patch.build(native,bridge,tool('gcc'),tool('ld'),tool('objcopy'))
            self.assertEqual(result['changed_native_bytes'],4)
            modified=bytearray(original);modified[-1]^=1;native.write_bytes(modified)
            with self.assertRaisesRegex(ValueError,'pinned compact-layout audit'):
                patch.build(native,bridge,tool('gcc'),tool('ld'),tool('objcopy'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--toolchain',type=Path)
    args,rest=parser.parse_known_args();TOOLCHAIN=args.toolchain
    unittest.main(argv=[sys.argv[0],*rest])
