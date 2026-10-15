"""Independent public gates must retain faults even when another gate fails."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from quiet_acceptance import public_window_checks


class PublicGates(unittest.TestCase):
    def run_checks(self, *, memory_error=False, drops=0, first=3, last=59.8):
        states=[dict(seconds=last,request_ms=50)]
        measured=dict(samples=20,elapsed_ms=44000,completion_queue_drops=drops,write_errors=0)
        with patch('quiet_acceptance.matches',return_value=True), \
             patch('quiet_acceptance.check_playback',return_value=dict(samples=20)), \
             patch('quiet_acceptance.check_memory',side_effect=Failure('Progressive heap loss') if memory_error else None), \
             patch('quiet_acceptance.check_decoder_health',return_value=dict(decoder_failures=0)), \
             patch('quiet_acceptance.output_window',return_value=measured), \
             patch('quiet_acceptance.check_output',side_effect=Failure('Output overflow') if drops else None) as output:
            result=public_window_checks([dict(seconds=first,request_ms=20),*states],[{}]*20,{},60)
            output.assert_called_once()
            return result

    def test_memory_rejection_retains_output_failure_and_measurement(self):
        result=self.run_checks(memory_error=True,drops=36)
        self.assertEqual(result['memory']['result'],'FAIL')
        self.assertEqual(result['output']['result'],'FAIL')
        self.assertEqual(result['output_measurement']['evidence']['completion_queue_drops'],36)

    def test_format_rejection_does_not_skip_remaining_gates(self):
        result=self.run_checks(first=16,drops=2)
        self.assertEqual(result['format']['result'],'FAIL')
        self.assertEqual(result['output']['result'],'FAIL')
        self.assertEqual(result['decoder']['result'],'PASS')

    def test_incomplete_window_is_not_accepted(self):
        self.assertEqual(self.run_checks(last=40)['format']['result'],'FAIL')

    def test_all_pass(self):
        self.assertTrue(all(row['result']=='PASS' for row in self.run_checks().values()))

    def test_provisional_audio_flag_is_not_decoded_format(self):
        with patch('quiet_acceptance.matches',return_value=False):
            result=public_window_checks([dict(seconds=59.8,request_ms=20,audio=True)],[],{},60)
        self.assertEqual(result['format']['result'],'FAIL')
        self.assertIn('matching decoded format',result['format']['reason'])


if __name__=='__main__':unittest.main()
