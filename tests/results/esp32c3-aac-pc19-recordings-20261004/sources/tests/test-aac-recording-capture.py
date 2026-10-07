"""Reject lost ADTS/PCM frames and enforce the three-LSB recording gate."""
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from compare_aac_late_sbr_pcm import read_log
from run_aac_recording_capture import adts_core_rates,parse_recording
from compare_aac_recording_pcm import compare


class RecordingParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prefix=read_log(ROOT/'tests/results/esp32c3-aac-pc19-20261004/candidate/qemu.log.gz')
        data=(ROOT/'tests/fixtures/aac_stream_format/lc-44100-stereo.aac').read_bytes()
        size=((data[3]&3)<<11)|(data[4]<<3)|(data[5]>>5)
        cls.data=data[:size]
        # Deliberately constructed parser data, not claimed as decoded audio.
        cls.pcm=struct.pack('<2048h',*range(2048))

    def capture(self,pcm=None):
        pcm=self.pcm if pcm is None else pcm
        rows=[self.prefix,f'AAC_RECORD_BEGIN bytes={len(self.data)} rate=44100 channels=2',
              'AAC_RECORD_PCM_FRAME frame=0 rate=44100 channels=2 bytes=4096']
        rows += [f'AAC_RECORD_PCM_DATA frame=0 offset={i} hex={pcm[i:i+256].hex()}' for i in range(0,4096,256)]
        rows += [f'AAC_RECORD_PASS consumed={len(self.data)} frames=1 channel_samples=2048 calls=1 poison_patterns=2 heap=valid']
        return '\n'.join(rows)+'\n'

    def test_complete_frame_and_capture(self):
        self.assertEqual(adts_core_rates(self.data),[44100])
        info,rows=parse_recording(self.capture(),self.data)
        self.assertEqual(info['frames'],1);self.assertEqual(bytes(rows[0]['pcm']),self.pcm)
        self.assertEqual(parse_recording(self.capture().replace('\n','\r\n'),self.data)[0],info)

    def test_partial_input_and_unsupported_framing_fail_closed(self):
        for bad in (b'',self.data[:6],self.data[:-1],b'\0'+self.data,self.data+b'\xff'):
            with self.assertRaises(ValueError):adts_core_rates(bad)
        bad=bytearray(self.data);bad[6]|=1
        with self.assertRaises(ValueError):adts_core_rates(bad)

    def test_missing_reordered_or_duplicate_pcm_rejected(self):
        log=self.capture()
        for old,new in [('frame=0 offset=0','frame=0 offset=256'),
                        ('AAC_RECORD_PCM_FRAME frame=0','AAC_RECORD_PCM_FRAME frame=1'),
                        ('channel_samples=2048','channel_samples=2047'),
                        ('AAC_RECORD_PASS','LOST_RECORD_PASS')]:
            with self.subTest(old=old),self.assertRaises(ValueError):
                parse_recording(log.replace(old,new,1),self.data)
        chunk=next(s for s in log.splitlines() if s.startswith('AAC_RECORD_PCM_DATA'))
        for bad in (log.replace(chunk,'',1),log.replace(chunk,chunk+'\n'+chunk,1)):
            with self.assertRaises(ValueError):parse_recording(bad,self.data)

    def test_missing_decoded_frame_or_wrong_rate_rejected(self):
        with self.assertRaises(ValueError):parse_recording(self.capture(),self.data+self.data)
        with self.assertRaises(ValueError):parse_recording(self.capture().replace('rate=44100','rate=48000'),self.data)

    def test_three_lsb_pass_four_lsb_fail_and_channel_accounting(self):
        for delta in (0,3,4):
            changed=struct.pack('<h',delta)+self.pcm[2:]
            result=compare(self.capture(),self.capture(changed),self.data)
            self.assertEqual(result['max_error_lsb'],delta)
            self.assertEqual(result['precision_pass'],delta<=3)
            self.assertEqual(result['over_three'],int(delta>3))
            self.assertEqual(result['per_channel'][0]['max_error_lsb'],delta)
            self.assertEqual(result['per_channel'][1]['max_error_lsb'],0)
            self.assertFalse(result['production_qualified'])


if __name__=='__main__':unittest.main()
