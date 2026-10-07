"""Validate retained recording statistics; raw music PCM remains local."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from compare_aac_recording_pcm import summarize
from run_aac_late_sbr import parse_log
from save_aac_recording_evidence import CASES
EVIDENCE=ROOT/'tests/results/esp32c3-aac-pc19-recordings-20261004'


class RecordingEvidenceTests(unittest.TestCase):
    def test_complete_exact_evidence(self):
        checksums=json.loads((EVIDENCE/'checksums.json').read_text())
        self.assertEqual(set(checksums),{p.relative_to(EVIDENCE).as_posix() for p in EVIDENCE.rglob('*')
                                       if p.is_file() and p.name!='checksums.json'})
        for name,digest in checksums.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((EVIDENCE/name).read_bytes()).hexdigest(),digest)

    def test_frame_and_channel_histograms_reproduce_error_statistics(self):
        summary=json.loads((EVIDENCE/'summary.json').read_text())
        self.assertEqual([r['case'] for r in summary['cases']],list(CASES))
        self.assertFalse(summary['production_qualified'])
        total=0
        for name in CASES:
            result=json.loads((EVIDENCE/name/'comparison.json').read_text())
            summary_row=next(r for r in summary['cases'] if r['case']==name)
            for key,value in summary_row.items():
                if key in result:self.assertEqual(value,result[key],key)
            frames=Counter();channels=Counter()
            self.assertEqual([r['frame'] for r in result['frames']],list(range(result['frame_count'])))
            for axis,rows in ((frames,result['frames']),(channels,result['per_channel'])):
                for row in rows:
                    hist=Counter({int(k):v for k,v in row['signed_histogram'].items()})
                    self.assertTrue(all(n>=0 for n in hist.values()))
                    for key,value in summarize(hist).items():self.assertEqual(row[key],value)
                    axis.update(hist)
            self.assertEqual(frames,channels)
            for key,value in summarize(frames).items():self.assertEqual(result[key],value)
            self.assertEqual(result['precision_pass'],result['max_error_lsb']<=3)
            self.assertEqual(result['precision_limit_lsb'],3)
            self.assertFalse(result['production_qualified'])
            total+=result['channel_samples']
        self.assertEqual(total,summary['channel_samples'])
        self.assertEqual(summary['max_error_lsb'],max(r['max_error_lsb'] for r in summary['cases']))
        self.assertEqual(summary['precision_pass'],all(r['precision_pass'] for r in summary['cases']))

    def test_inputs_build_roles_and_frame_coverage(self):
        for name in CASES:
            result=json.loads((EVIDENCE/name/'comparison.json').read_text())
            previous=json.loads((ROOT/'tests/results/esp32c3-aac-high-history-20261003/pc18'/name/'result.json').read_text())
            self.assertEqual(result['input_sha256'],previous['provenance']['recording']['sha256'])
            for mode in ('candidate','reference'):
                record=json.loads((EVIDENCE/name/mode/'result.json').read_text())
                self.assertEqual(record['full_precision_history'],mode=='reference')
                self.assertFalse(record['recording_precision_qualified'])
                cap=record['recording_capture']
                self.assertEqual(cap['frames'],result['frame_count'])
                self.assertEqual(cap['channel_samples'],result['channel_samples'])
                self.assertEqual(cap['pcm_sha256'],result[mode+'_pcm_sha256'])
                self.assertEqual((cap['rate'],cap['channels']),(result['rate'],result['channels']))

    def test_sanitized_diagnostics_preserve_validation_without_music_pcm(self):
        for name in CASES:
            result=json.loads((EVIDENCE/name/'comparison.json').read_text())
            for mode in ('candidate','reference'):
                data=gzip.decompress((EVIDENCE/name/mode/'diagnostics.log.gz').read_bytes())
                self.assertNotIn(b'AAC_RECORD_PCM_DATA ',data)
                log=data.decode()
                self.assertEqual(log.count('AAC_RECORD_PASS '),1)
                self.assertEqual(len(re.findall(r'^AAC_RECORD_PCM_FRAME ',log,re.MULTILINE)),result['frame_count'])
                raw=json.loads((EVIDENCE/name/mode/'raw-log.json').read_text())
                self.assertEqual(raw['sha256'],result['log_sha256'][mode])
                self.assertEqual(raw['omitted_recording_pcm_bytes'],result['channel_samples']*2)
                if mode=='candidate':
                    audit=parse_log(log,require_retention=True)
                    self.assertEqual(audit['pointers']['allocations'],audit['pointers']['frees'])


if __name__=='__main__':unittest.main()
