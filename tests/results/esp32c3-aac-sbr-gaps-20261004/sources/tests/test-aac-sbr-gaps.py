"""Verify genuine SBR removal, native lifecycle results and strict PCM evidence."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import generate_aac_sbr_gaps as gen
import compare_aac_sbr_gap_pcm as pcm
from run_aac_late_sbr import parse_log

FIXTURES=ROOT/'tests/fixtures/aac_sbr_gap'
EVIDENCE=ROOT/'tests/results/esp32c3-aac-sbr-gaps-20261004'


class GapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=pcm.verified_manifest()
        cls.reference=pcm.read_log(EVIDENCE/'reference/qemu.log.gz')
        cls.candidate=pcm.read_log(EVIDENCE/'candidate/qemu.log.gz')

    def test_exact_saved_evidence(self):
        for name,digest in json.loads((EVIDENCE/'checksums.json').read_text()).items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((EVIDENCE/name).read_bytes()).hexdigest(),digest)

    def test_rebuild_all_missing_sbr_frames_from_parser_spans(self):
        count=0
        for name,meta in self.manifest['cases'].items():
            data=(FIXTURES/('source-'+name+'.aac')).read_bytes();trace=(FIXTURES/(name+'.trace')).read_bytes()
            self.assertEqual(hashlib.sha256(trace).hexdigest(),meta['trace_sha256'])
            spans={}
            for line in trace.decode().splitlines():
                if line.startswith('FIL '):
                    index,*span=map(int,line.split()[1:]);spans.setdefault(index,[]).append(span)
            outputs=[]
            for index,frame in enumerate(gen.adts_frames(data)):
                sbr=[s for s in spans[index] if s[-2] in gen.SBR_TYPES]
                self.assertEqual(len(sbr),1);span=sbr[0]
                outputs.append(gen.remove_sbr(frame,span,[s for s in spans[index] if s[0]>=span[2]]))
                count+=1
            self.assertEqual(b''.join(outputs),(FIXTURES/('missing-'+name+'.aac')).read_bytes())
        self.assertEqual(count,55)

    def test_wrong_syntax_or_trace_is_rejected(self):
        # Frame 1 has no trailing fill, only SBR then ID_END/alignment.
        frame=gen.adts_frames((FIXTURES/'source-he-44100-stereo.aac').read_bytes())[1]
        row=next(s for s in (FIXTURES/'he-44100-stereo.trace').read_text().splitlines() if s.startswith('FIL 1 '))
        span=list(map(int,row.split()[2:]));gen.remove_sbr(frame,span)
        for field in range(len(span)):
            invalid=span.copy();invalid[field]+=1
            with self.subTest(field=field),self.assertRaises(ValueError):gen.remove_sbr(frame,invalid)
        for bit in (span[0],span[1],span[2],len(frame)*8-1):
            bad=bytearray(frame);bad[bit//8]^=1<<(7-bit%8)
            with self.subTest(bit=bit),self.assertRaises(ValueError):gen.remove_sbr(bytes(bad),span)
        for field,mask in ((1,1),(6,1)):
            bad=bytearray(frame);bad[field]^=mask
            with self.assertRaises(ValueError):gen.adts_frames(bytes(bad))
        with self.assertRaises(ValueError):gen.adts_frames(frame[:-1])

    def test_faad_float_and_fixed_keep_sbr_and_ps(self):
        record=json.loads((EVIDENCE/'faad/result.json').read_text())
        self.assertEqual(len(record['cases']),8)
        for name,meta in self.manifest['cases'].items():
            for mode in ('float','fixed'):
                rows=[list(map(int,s.split())) for s in (EVIDENCE/f'faad/{name}-{mode}.frames').read_text().splitlines()]
                self.assertEqual(len(rows),3*meta['frames'])
                for i,row in enumerate(rows):
                    self.assertEqual(row[1:],[(0 if i==0 else 2048*meta['channels']),meta['rate'],meta['channels'],1,int(meta['aot']==29)])

    def test_native_lifecycle_and_no_new_pointer_failure(self):
        for log in (self.reference,self.candidate):
            self.assertEqual(len(pcm.parse_gaps(log)),165)
        report=parse_log(self.candidate,require_retention=True)
        self.assertEqual(report['pointers']['allocations'],report['pointers']['frees'])
        self.assertGreater(report['pointers']['resets'],4)
        self.assertFalse(report['production_qualified'])

    def test_raw_precision_result_is_reproducible(self):
        result,left,right=pcm.compare(self.reference,self.candidate)
        saved=json.loads((EVIDENCE/'pcm/comparison.json').read_text())
        for key,value in result.items():self.assertEqual(saved[key],value,key)
        self.assertEqual(result['channel_samples'],675840)
        # This immutable record is a rejected candidate. Reproducing its
        # result is not qualification: the live comparator exits 2 (>3 LSB).
        self.assertFalse(result['precision_pass'])
        self.assertEqual(result['max_error_lsb'],5)
        self.assertEqual(result['over_three'],41)
        for name,data in (('reference',left),('candidate',right)):
            self.assertEqual(gzip.decompress((EVIDENCE/f'pcm/{name}.pcm.gz').read_bytes()),data)

    def test_partial_or_changed_capture_is_rejected(self):
        for old,new in [('AAC_GAP_PCM_DATA offset=0','AAC_GAP_PCM_DATA offset=256'),
                        ('partial_close=9','partial_close=8'),
                        ('duplicated_pairs=exact','duplicated_pairs=unknown'),
                        ('AAC_GAP_PCM_FRAME case=he_44100_stereo phase=0 frame=0',
                         'AAC_GAP_PCM_FRAME case=he_44100_stereo phase=0 frame=1')]:
            with self.subTest(old=old):
                self.assertIn(old,self.candidate)
                with self.assertRaises(ValueError):pcm.parse_gaps(self.candidate.replace(old,new,1))

    def test_four_lsb_is_a_failure(self):
        match=re.search(r'AAC_GAP_PCM_DATA offset=0 hex=([0-9a-f]{4})',self.reference)
        self.assertIsNotNone(match)
        sample=struct.unpack('<h',bytes.fromhex(match[1]))[0]
        changed=struct.pack('<h',sample+4 if sample<32764 else sample-4).hex()
        log=self.reference[:match.start(1)]+changed+self.reference[match.end(1):]
        result,_,_=pcm.compare(self.reference,log)
        self.assertEqual(result['max_error_lsb'],4);self.assertFalse(result['precision_pass'])


if __name__=='__main__':unittest.main()
