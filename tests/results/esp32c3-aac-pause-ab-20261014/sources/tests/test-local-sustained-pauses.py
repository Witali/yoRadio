import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from local_sustained import check_delivery_pauses
from common import Failure


class PauseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.schedule=((100,.25),(200,.5))
        self.events=[dict(fixture='aac',pacing_ratio=1.,
            pause_schedule=[dict(after_bytes=n,seconds=s) for n,s in self.schedule],
            pauses=[dict(after_bytes=n,requested_seconds=s,completed=True,elapsed_seconds=s+.001)
                    for n,s in self.schedule])]

    def test_complete_schedule(self):
        self.assertEqual(len(check_delivery_pauses(self.events,'aac',self.schedule)['pauses']),2)

    def test_missing_duplicate_wrong_or_interrupted_pause(self):
        variants=[]
        for field,value in (('after_bytes',201),('requested_seconds',.25),('completed',False)):
            changed=copy.deepcopy(self.events);changed[0]['pauses'][1][field]=value;variants.append(changed)
        changed=copy.deepcopy(self.events);changed[0]['pauses'].pop();variants.append(changed)
        variants += [[],self.events*2]
        for events in variants:
            with self.subTest(events=events),self.assertRaises(Failure):
                check_delivery_pauses(events,'aac',self.schedule)

    def test_bad_timing_and_schedule_fail(self):
        for elapsed in (.1,.7,float('nan')):
            changed=copy.deepcopy(self.events);changed[0]['pauses'][1]['elapsed_seconds']=elapsed
            with self.assertRaises(Failure):check_delivery_pauses(changed,'aac',self.schedule)
        changed=copy.deepcopy(self.events);changed[0]['pause_schedule'].reverse()
        with self.assertRaises(Failure):check_delivery_pauses(changed,'aac',self.schedule)


if __name__=='__main__':unittest.main()
