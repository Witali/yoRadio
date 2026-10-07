"""Replay the full HEv2 duration while preserving the memory failure."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tests/results/esp32c3-hev2-soak-20261005'
sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
from summarize_sustained import read,summarize


class HEv2Evidence(unittest.TestCase):
    def test_manifest(self):
        manifest=read(DATA,'manifest.json')
        actual={p.relative_to(DATA).as_posix() for p in DATA.rglob('*') if p.is_file() and p!=DATA/'manifest.json'}
        self.assertEqual(actual,set(manifest))
        for name,identity in manifest.items():
            data=(DATA/name).read_bytes()
            self.assertEqual((len(data),hashlib.sha256(data).hexdigest()),(identity['bytes'],identity['sha256']))

    def test_full_replay(self):
        result=summarize(DATA)
        self.assertEqual(result,read(DATA,'summary.json'))
        self.assertEqual(len(result['cases']),1)
        case=result['cases'][0]
        self.assertEqual(case['original']['result'],'FAIL')
        self.assertEqual(case['original']['reason'],'Progressive heap loss during continuous playback')
        self.assertEqual(case['runtime']['result'],'PASS')
        full=case['full_window'];self.assertGreaterEqual(full['seconds'],1790)
        self.assertFalse(full['malformed']);self.assertEqual(full['cpu_samples'],354)
        self.assertEqual(full['decoder_windows'],358)
        self.assertEqual([w['strict']['result'] for w in case['subwindows']],['FAIL','PASS','PASS','PASS','PASS','FAIL'])
        metrics=full['diagnostic']
        self.assertLess(metrics['peak_busy'],85)
        self.assertGreater(metrics['minimum_heap'],8192)
        self.assertGreater(metrics['minimum_largest'],4096)
        self.assertTrue(.99<metrics['audio_wall_ratio']<1.01)
        self.assertLess(case['max_http_ms'],2000)

    def test_idle_recovery_and_identity(self):
        report=read(DATA,'report.json')
        before,load,after,restore=report['cases']
        self.assertEqual([c['result'] for c in report['cases']],['PASS','FAIL','PASS','PASS'])
        self.assertGreaterEqual(load['seconds'],1800)
        for c,heap in ((before,148256),(after,147980)):
            self.assertEqual(c['evidence']['samples'],[dict(heap=heap,largest=114688,tasks=17)]*2)
        artifact=ROOT/'firmware/development/esp32c3-flac-bounds'
        self.assertEqual((artifact/'app.bin').read_bytes()[176:208].hex(),report['board']['app_elf_sha256'])
        self.assertEqual(hashlib.sha256((artifact/'sdkconfig').read_bytes()).hexdigest(),report['config']['sha256'])


if __name__=='__main__':unittest.main()
