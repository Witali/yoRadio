"""Fail-closed checks for late growth and uninterrupted quiet TLS observations."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from quiet_tls_records import check_record_window, check_format, check_response


def observation():
    writes = [dict(phase='body-'+mode,plaintext_bytes=size,at=at)
              for mode,size,at in [('small',1024,1),('small',1024,2),('large',16384,31),('large',16384,33)]]
    records = [dict(phase=w['phase'],wire_payload_bytes=w['plaintext_bytes']+24,type=23,at=w['at']) for w in writes]
    return dict(captured_at=34,events=[dict(mode='grow',version='TLSv1.2',cipher='ECDHE-RSA-AES128-GCM-SHA256',
        records=records,writes=writes,dropped_records=0,dropped_writes=0,fixture_sha256='abc',
        pacing_ratio=1.0,target_audio_bytes_per_second=8192,audio_bytes=34816)])


class QuietRecordTests(unittest.TestCase):
    def test_growth_after_pcm_and_continuing_delivery(self):
        obs = observation()
        self.assertEqual(check_record_window(obs,'grow',dict(sha256='abc'),5,34)['audio_bytes'],34816)
        for first,end in ((32,34),(5,40),(5,32)):
            with self.subTest(first=first,end=end),self.assertRaises(Failure):
                check_record_window(obs,'grow',dict(sha256='abc'),first,end)

    def test_reject_ended_retried_incomplete_or_wrong_stream(self):
        for key,value in [('error','OSError'),('ended_at',33),('fixture_sha256','def'),
                          ('pacing_ratio',1.02),('audio_bytes',1024),('dropped_writes',1)]:
            obs=observation();obs['events'][0][key]=value
            with self.subTest(key=key),self.assertRaises(Failure):
                check_record_window(obs,'grow',dict(sha256='abc'),5,34)
        obs=observation();obs['events'].append(copy.deepcopy(obs['events'][0]))
        with self.assertRaises(Failure):check_record_window(obs,'grow',dict(sha256='abc'),5,34)

    def test_startup_timeout_and_response_threshold(self):
        with self.assertRaises(Failure):check_format([],dict(),75)
        spec=dict(rate=44100,channels=2,bits=16,label='HE-AAC ')
        states=[dict(seconds=s,audio=True,pcm_sample_rate=44100,pcm_channels=2,
                     bits_per_sample=16,format='HE-AAC test') for s in range(5,75)]
        self.assertEqual(check_format(states,spec,75)['first_full_pcm_seconds'],5)
        with self.assertRaises(Failure):check_format(states[11:],spec,75)
        states[30]['audio']=False
        with self.assertRaises(Failure):check_format(states,spec,75)
        self.assertEqual(check_response([dict(request_ms=1999)])['maximum_ms'],1999)
        with self.assertRaises(Failure):check_response([dict(request_ms=2000)])


if __name__ == '__main__':unittest.main()
