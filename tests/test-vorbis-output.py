"""Negative controls for independent Ogg accounting and complete PCM capture."""
import gzip
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import run_vorbis_output as output
from vorbis_packets import packets

class OutputChecks(unittest.TestCase):
    def test_packet_count_and_crc(self):
        data=(ROOT/'tests/fixtures/esp32c3_calibration/vorbis-q10.ogg').read_bytes()
        values=packets(data)
        self.assertEqual(len(values)-3,535)
        self.assertEqual(values[-1]['granule'],528000)
        self.assertTrue(values[-1]['eos'])
        self.assertEqual(values[3]['data'],b'\0') # Valid tiny first audio packet.
        damaged=bytearray(data);damaged[-1]^=1
        for invalid in (b'',data[:20],data[:-1],damaged):
            with self.assertRaises(ValueError):packets(invalid)

    def test_pcm_capture_rejects_missing_or_duplicate_chunks(self):
        valid='VPCM run=1 offset=0 data=0001\nVPCM run=1 offset=2 data=0203\n'
        self.assertEqual(output.pcm_from_log(valid),bytes(range(4)))
        for wrong in (valid+valid,valid.replace('offset=2','offset=3'),valid.replace('run=1','run=2')):
            with self.assertRaises(ValueError):output.pcm_from_log(wrong)

    def test_retained_final_matrix(self):
        folder=ROOT/'tests/results/esp32c3-vorbis-output-20261005/final'
        if not folder.exists():self.skipTest('Retained run not saved yet')
        report=json.loads((folder/'report.json').read_text())
        self.assertTrue(report['full_matrix'] and report['all_passed'])
        self.assertEqual({c['name'] for c in report['cases']},set(output.CASES))
        reference=report['cases'][0]['rows'][0]
        self.assertEqual(reference['pcm'],528000*2*2)
        for case in report['cases']:
            log=gzip.decompress((folder/(case['name']+'.log.gz')).read_bytes()).decode()
            checked,pcm=output.assess(log,case['options'],reference)
            self.assertTrue(checked['passed'],case['name'])
            self.assertEqual(pcm,gzip.decompress((folder/(case['name']+'.pcm.gz')).read_bytes()))
            if case['name']!='resize-oom':
                self.assertEqual(checked['output'][0]['synthesis'],535)

if __name__=='__main__':unittest.main()
