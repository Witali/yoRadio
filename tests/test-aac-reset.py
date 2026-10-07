#!/usr/bin/env python3
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import run_aac_reset as reset
import run_aac_bfp16 as common
EVIDENCE=ROOT/'tests/results/esp32c3-aac-reset-20261001'


class ResetTests(unittest.TestCase):
    def setUp(self):
        self.log=(EVIDENCE/'qemu.log').read_text()

    def test_evidence_and_hashes(self):
        result=json.loads((EVIDENCE/'result.json').read_text())
        for k,v in reset.parse_log(self.log).items():self.assertEqual(result[k],v)
        self.assertEqual(common.sha256(EVIDENCE/'qemu.log'),result['provenance']['qemu_log_sha256'])
        self.assertEqual(common.sha256(EVIDENCE/'sdkconfig'),result['provenance']['sdkconfig_sha256'])
        manifest=json.loads((EVIDENCE/'implementation.json').read_text())
        for path,digest in manifest['files'].items():
            snapshot=manifest.get('snapshots',{}).get(path)
            self.assertEqual(common.sha256(EVIDENCE/snapshot if snapshot else ROOT/path),digest,path)

    def test_rejected_padding_run_is_not_a_pass(self):
        log=(EVIDENCE/'rejected-paired-padding.log').read_text()
        self.assertIn('Disable AAC-Plus for memory not enough',log)
        with self.assertRaises(ValueError):reset.parse_log(log)

    def test_bad_evidence_rejected(self):
        for old,new in (('baseline_oob_writes=6','baseline_oob_writes=0'),
                        ('paired_reset_calls=24','paired_reset_calls=22'),
                        ('PCM=exact','PCM=changed'),('guards=pass','guards=fail'),
                        ('cleanup=complete','cleanup=leaked'),('samples=184320','samples=0'),
                        ('QEMU_SMOKE_PASS','REMOVED')):
            with self.subTest(old=old),self.assertRaises(ValueError):reset.parse_log(self.log.replace(old,new,1))
        line=next(s for s in self.log.splitlines(True) if 'AACRESET_PASS' in s)
        for log in (self.log+line,self.log.replace(line,'',1)):
            with self.assertRaises(ValueError):reset.parse_log(log)


if __name__=='__main__':unittest.main()
