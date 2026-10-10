import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from sustained_output import sustained_window, check_output, check_memory


def health(ms=0,drops=9,errors=2):
    return dict(uptime_ms=ms,boot_id='0123456789abcdef',heap=24000,largest=12000,
                allocation_failures=0,task_watchdog_events=0,
                output=dict(available=True,completion_queue_drops=drops,write_errors=errors))


class SustainedTests(unittest.TestCase):
    def test_window_excludes_startup_and_checks_complete_collection(self):
        states=[dict(seconds=s) for s in range(60)]
        rows=[health(s*1000) for s in range(60)]
        steady,measured=sustained_window(states,rows,60)
        self.assertEqual(len(steady),45)
        self.assertEqual(measured[0]['uptime_ms'],15000)
        for s,h in ((states[:-5],rows[:-5]),(states,rows[:-1]),
                    (states[20:],rows[20:]),(states[::2],rows[::2])):
            with self.assertRaises(Failure):sustained_window(s,h,60)
        states[25]['seconds']=24
        with self.assertRaises(Failure):sustained_window(states,rows,60)

    def test_output_gate_keeps_historical_events_but_rejects_new_events(self):
        self.assertEqual(check_output([health(),health(1000)])['completion_queue_drops'],0)
        for row in (health(1000,drops=10),health(1000,errors=3)):
            with self.assertRaises(Failure):check_output([health(),row])

    def test_memory_gate_not_waived_when_output_is_healthy(self):
        rows=[health(s*1000) for s in range(6)]
        self.assertEqual(check_output(rows)['write_errors'],0)
        rows[-1]['largest']=7936
        with self.assertRaises(Failure):check_memory(rows)


if __name__=='__main__':unittest.main()
