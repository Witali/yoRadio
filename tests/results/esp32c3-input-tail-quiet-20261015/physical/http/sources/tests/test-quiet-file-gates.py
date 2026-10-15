"""A stopped/error status or decoder fault must not pass a positive file test."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure, check_natural_eof
from run import Suite, check_file_output


class QuietFileTests(unittest.TestCase):
    def test_eof_requires_three_final_natural_terminal_observations(self):
        end = dict(audio=False, format='stream ended')
        self.assertFalse(check_natural_eof([dict(audio=True), end, end, end])['explicit_stop'])
        for rows in ([end], [end, end], [end, end, dict(audio=True, format='stream ended')],
                     [end, end, dict(audio=False, format='stopped')],
                     [end, end, dict(audio=False, format='stream read failed')]):
            with self.assertRaises(Failure):
                check_natural_eof(rows)

    def run_file(self, terminal='stream ended', fault=0, missing=False, start_error=False, output_fault=False):
        events = []
        board = SimpleNamespace(health_samples=[], stop=Mock(side_effect=lambda: events.append('stop')))
        with tempfile.TemporaryDirectory() as directory:
            suite = Suite(board, 'http://unused.invalid', {'fixture': {'seconds': 11}},
                          SimpleNamespace(port=None, since=lambda _: []), directory)
            suite.start = Mock(side_effect=OSError() if start_error else None)
            def observe(seconds, name):
                row = {} if missing else dict(decoder_failure=dict(sequence=fault))
                board.health_samples.extend([row]*3)
                return [dict(audio=False, format=terminal)]*3
            suite.observe = Mock(side_effect=observe)
            def snapshot(_):
                events.append('snapshot')
                return dict(before_stop=True)
            with patch('run.check_playback', return_value={}), \
                 patch('run.check_file_output', side_effect=Failure('output fault') if output_fault else None,
                       return_value={'completion_queue_drops':0,'write_errors':0}) as output_check, \
                 patch('run.capture_failure_snapshot', side_effect=snapshot):
                try:
                    result = suite.file('fixture')
                    self.assertEqual(output_check.call_args[0][1], board.health_samples[:3])
                    error = None
                except Exception as caught:
                    result, error = None, caught
            return result, error, events, suite.file_failure_snapshots

    def test_positive_eof_and_health_pass_before_cleanup(self):
        result, error, events, failures = self.run_file()
        self.assertIsNone(error)
        self.assertEqual(result['eof']['format'], 'stream ended')
        self.assertEqual(result['decoder_health']['decoder_failures'], 0)
        self.assertEqual(events, ['stop'])
        self.assertEqual(failures, [])

    def test_stream_error_is_not_eof_and_snapshot_precedes_stop(self):
        result, error, events, failures = self.run_file(terminal='stream read failed')
        self.assertIsInstance(error, Failure)
        self.assertEqual(events, ['snapshot', 'stop'])
        self.assertTrue(failures[0]['snapshot']['before_stop'])

    def test_decoder_fault_or_missing_telemetry_cannot_hide_behind_eof(self):
        for kwargs in ({'fault': 1}, {'missing': True}):
            _, error, events, _ = self.run_file(**kwargs)
            self.assertIsInstance(error, Failure)
            self.assertEqual(events, ['snapshot', 'stop'])

    def test_start_request_failure_is_retained_before_cleanup(self):
        _, error, events, _ = self.run_file(start_error=True)
        self.assertIsInstance(error, OSError)
        self.assertEqual(events, ['snapshot', 'stop'])

    def test_output_failure_cannot_hide_behind_successful_eof(self):
        _, error, events, failures = self.run_file(output_fault=True)
        self.assertIsInstance(error, Failure)
        self.assertEqual(events, ['snapshot', 'stop'])
        self.assertTrue(failures[0]['snapshot']['before_stop'])

    def test_output_gate_uses_paired_active_window_without_eof_idle_events(self):
        states=[dict(seconds=s,audio=True,pcm_sample_rate=48000,pcm_channels=2) for s in range(8)]
        health=[dict(uptime_ms=s*1000,boot_id='0123456789abcdef',heap=24000,largest=12000,
            allocation_failures=0,task_watchdog_events=0,
            output=dict(available=True,completion_queue_drops=9 if s<2 else 12,write_errors=0)) for s in range(8)]
        result=check_file_output(states,health)
        self.assertEqual(result['completion_queue_drops'],0)
        self.assertEqual((result['first_seconds'],result['last_seconds']),(2,7))
        for counter in ('completion_queue_drops','write_errors'):
            health[-1]['output'][counter]+=1
            with self.assertRaises(Failure):check_file_output(states,health)
            health[-1]['output'][counter]-=1
        for broken in (health[:-1],health[:4]):
            with self.assertRaises(Failure):check_file_output(states,broken)
        with self.assertRaises(Failure):check_file_output(states[:4],health[:4])
        for field,value in (('audio',False),('pcm_sample_rate',0),('pcm_channels',0),('seconds',3)):
            old=states[4][field];states[4][field]=value
            with self.assertRaises(Failure):check_file_output(states,health)
            states[4][field]=old
        health[-1]['boot_id']='another-boot'
        with self.assertRaises(Failure):check_file_output(states,health)


if __name__ == '__main__':
    unittest.main()
