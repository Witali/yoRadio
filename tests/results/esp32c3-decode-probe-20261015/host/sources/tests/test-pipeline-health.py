"""Reject malformed diagnostic evidence rather than interpreting it as silence."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from common import Failure
from production_health import validate_pipeline
from pipeline_probe import analyze_pipeline


class PipelineHealth(unittest.TestCase):
    def setUp(self):
        self.output = dict(available=True, completion_queue_drops=1, write_errors=0)
        self.probe = dict(timer_hz=1_000_000, sequence=1, phase_drops=[0]*7+[1],
                          events=[[1,100,7,200,300,400,500]])

    def test_clean_numeric_copy(self):
        self.probe['extra'] = 'not retained'
        value = validate_pipeline(self.probe, self.output)
        self.assertNotIn('extra', value)
        value['events'][0][0] = 2
        self.assertEqual(self.probe['events'][0][0], 1)

    def v2(self, flags=3, feed=20000, wait=7000, process=1300):
        return dict(copy.deepcopy(self.probe), event_version=2, process_max_us=1500,
                    events=[self.probe['events'][0]+[flags,feed,wait,process]])

    def test_v2_work_fields_are_bounded_and_legacy_stays_compatible(self):
        for flags in range(4):
            probe=self.v2(flags, 20000 if flags & 1 else 0, 7000 if flags & 2 else 0)
            self.assertEqual(validate_pipeline(probe,self.output),probe)
        self.assertEqual(validate_pipeline(self.probe,self.output),self.probe)
        for version in (0,3,True,'2',None):
            with self.subTest(version=version),self.assertRaises(Failure):
                validate_pipeline(dict(self.v2(),event_version=version),self.output)
        bad=[self.v2(4), self.v2(0), self.v2(1), self.v2(2), self.v2(process=1501)]
        for n in (7,8,9,10):
            for value in (-1,2**32,True,None):
                probe=self.v2();probe['events'][0][n]=value;bad.append(probe)
        for value in (-1,2**32,True,None):
            bad.append(dict(self.v2(),process_max_us=value))
        probe=self.v2();del probe['process_max_us'];bad.append(probe)
        bad.extend([dict(self.v2(),events=self.probe['events']),
                    dict(self.probe,events=self.v2()['events'])])
        for probe in bad:
            with self.subTest(probe=probe),self.assertRaises(Failure):
                validate_pipeline(probe,self.output)

    def test_v2_analysis_distinguishes_feed_wait_and_process_wall_times(self):
        def row(probe,ms):
            return dict(boot_id='same',uptime_ms=ms,heap=20000,largest=10000,
                        allocation_failures=0,task_watchdog_events=0,
                        output=dict(self.output,completion_queue_drops=probe['sequence']),pipeline=probe)
        first=row(dict(self.v2(),sequence=0,phase_drops=[0]*8,events=[]),1000)
        last=row(self.v2(),2000)
        summary=analyze_pipeline([first,last])
        self.assertEqual(summary['events'][0]['decoder_work'],dict(feed_active=True,
            pcm_wait_active=True,feed_elapsed_ms=20,pcm_wait_elapsed_ms=7,
            last_completed_batch_process_max_ms=1.3))
        self.assertEqual(summary['process_max_since_boot_ms'],1.5)
        self.assertEqual(summary['events'][0]['ages_ms']['http_read'],0.5)
        self.assertEqual(summary['overwritten_events'],0)
        with self.assertRaises(Failure):
            analyze_pipeline([first,row(self.probe,2000)])

    def test_counter_wrap_and_partial_retention(self):
        self.probe.update(sequence=0, phase_drops=[2**32-1,1]+[0]*6,
                          events=[[2**32-1,100,0,0,0,0,0],[0,200,1,0,0,0,0]])
        self.output['completion_queue_drops'] = 0
        validate_pipeline(self.probe,self.output)

    def test_optional_stream_failure_numeric_copy(self):
        failure = dict(sequence=2**32-1, timestamp_us=2**32-1, http_result=-1,
                       esp_tls_error=32797, tls_code=120, system_errno=104, extra='ignored')
        self.probe['stream_failure'] = failure
        value = validate_pipeline(self.probe, self.output)['stream_failure']
        self.assertNotIn('extra', value)
        self.assertEqual(value['http_result'], -1)
        for change in (dict(sequence=-1), dict(timestamp_us=True), dict(tls_code=2**31),
                       dict(http_result='-1'), dict(system_errno=None)):
            self.probe['stream_failure'] = dict(failure, **change)
            with self.subTest(change=change), self.assertRaises(Failure):
                validate_pipeline(self.probe, self.output)

    def test_invalid_data_fail_closed(self):
        cases = [dict(sequence=True), dict(timer_hz=0), dict(events=[]),
                 dict(phase_drops=[0]*8), dict(events=self.probe['events']*17),
                 dict(events=[[2,100,7,0,0,0,0]]), dict(events=[[1,100,8,0,0,0,0]]),
                 dict(events=[[1,100,7,-1,0,0,0]])]
        for change in cases:
            with self.subTest(change=change), self.assertRaises(Failure):
                validate_pipeline(dict(copy.deepcopy(self.probe), **change), self.output)

    def test_overwritten_events_and_idle_exclusion(self):
        def row(sequence,uptime):
            output=dict(self.output,completion_queue_drops=sequence)
            probe=dict(self.probe,sequence=sequence,phase_drops=[0]*7+[sequence],
                events=[[n,100,7,1000,10000,20000,30000]
                        for n in range(max(1,sequence-15),sequence+1)])
            return dict(boot_id='same',uptime_ms=uptime,heap=20000,largest=10000,
                        allocation_failures=0,task_watchdog_events=0,output=output,pipeline=probe)
        summary=analyze_pipeline([row(100,1000),row(123,2000),row(125,3000)])
        self.assertEqual(summary['output']['completion_queue_drops'],25)
        self.assertEqual(summary['phase_drops'],[0]*7+[25])
        self.assertEqual(summary['retained_events'],18)
        self.assertEqual(summary['overwritten_events'],7)
        self.assertEqual(summary['events'][0]['ages_ms']['output_checkpoint'],1.0)
        self.assertEqual(summary['events'][-1]['sequence'],125)
        broken=row(126,4000);broken['boot_id']='reboot'
        with self.assertRaises(Failure):
            analyze_pipeline([row(125,3000),broken])


if __name__ == '__main__':
    unittest.main()
