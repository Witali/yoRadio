"""Reject malformed diagnostic evidence rather than interpreting it as silence."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from common import Failure
from production_health import validate_pipeline


class PipelineHealth(unittest.TestCase):
    def setUp(self):
        self.output = dict(available=True, completion_queue_drops=1, write_errors=0)
        self.probe = dict(cpu_mhz=160, sequence=1, phase_drops=[0]*7+[1],
                          events=[[1,100,7,200,300,400,500]])

    def test_clean_numeric_copy(self):
        self.probe['extra'] = 'not retained'
        value = validate_pipeline(self.probe, self.output)
        self.assertNotIn('extra', value)
        value['events'][0][0] = 2
        self.assertEqual(self.probe['events'][0][0], 1)

    def test_counter_wrap_and_partial_retention(self):
        self.probe.update(sequence=0, phase_drops=[2**32-1,1]+[0]*6,
                          events=[[2**32-1,100,0,0,0,0,0],[0,200,1,0,0,0,0]])
        self.output['completion_queue_drops'] = 0
        validate_pipeline(self.probe,self.output)

    def test_invalid_data_fail_closed(self):
        cases = [dict(sequence=True), dict(cpu_mhz=0), dict(events=[]),
                 dict(phase_drops=[0]*8), dict(events=self.probe['events']*17),
                 dict(events=[[2,100,7,0,0,0,0]]), dict(events=[[1,100,8,0,0,0,0]]),
                 dict(events=[[1,100,7,-1,0,0,0]])]
        for change in cases:
            with self.subTest(change=change), self.assertRaises(Failure):
                validate_pipeline(dict(copy.deepcopy(self.probe), **change), self.output)


if __name__ == '__main__':
    unittest.main()
