"""Check calendar-pixel polling with independent host and guest clock schedules."""
import argparse
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import time_qemu as clock


class DateCaptureTest(unittest.TestCase):
    """Model slow, stalled and wrapped VM clocks without waiting in real time."""

    def capture(self, speed=1, ready=2, initial=0, corrupt=False, fail_capture=False):
        """Exercise the real polling loop and pixel comparison with a fake display source."""
        host=[0.0]
        commands=[]
        expected=clock.text_pixels('2025/9/19',240,0,0xffff)
        def read(_,address,size):
            value=(initial+round(host[0]*speed*1e6))&0xffffffff if address==0x6004d000 else 0
            return value.to_bytes(size,'little')
        def sleep(seconds):host[0]+=seconds
        def capture(_,path):
            if fail_capture:raise OSError('Display capture failed')
            path.with_suffix('.ppm').touch()
        def pixels(_):
            if host[0]*speed<ready:return bytes(len(expected))
            return bytes([expected[0]^1])+expected[1:] if corrupt else expected
        def save(path,data):path.write_text(json.dumps(data))
        qmp=SimpleNamespace(execute=lambda command:commands.append(command))
        vm=SimpleNamespace(capture_png=capture,ppm_pixels=pixels,save_json=save)
        temp_root=clock.ROOT/'.build/small-tv-parity/date-capture-unit-temp'
        temp_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as directory:
            folder=Path(directory)
            with patch.object(clock,'read_bytes',side_effect=read), \
                 patch.object(clock,'snapshot',return_value={'synced':False}), \
                 patch.object(clock,'region',side_effect=lambda pixels,_:pixels), \
                 patch.object(clock,'vm',vm,create=True), \
                 patch.object(clock.time,'monotonic',side_effect=lambda:host[0]), \
                 patch.object(clock.time,'sleep',side_effect=sleep):
                try:
                    row=clock.date_capture(qmp,folder,'reconstructed',{},'2025/9/19')
                    error=None
                except (AssertionError,OSError) as failure:
                    error=failure
                    saved=folder/'failed-date-observation.json'
                    row=json.loads(saved.read_text()) if saved.exists() else None
        self.assertTrue(commands)
        self.assertEqual(commands[-1],'cont')
        self.assertEqual(commands.count('stop'),commands.count('cont'))
        return row,error

    def test_slow_guest_can_finish_startup_after_thirty_host_seconds(self):
        """A valid frame at 18.1 guest seconds must survive slower host execution."""
        row,error=self.capture(speed=.25,ready=18.1)
        self.assertIsNone(error)
        self.assertGreater(row['host_seconds'],30)
        self.assertGreaterEqual(row['guest_seconds'],18.1)
        self.assertLess(row['guest_seconds'],30)
        self.assertEqual(row['different_bytes'],0)

    def test_guest_deadline_rejects_a_clock_that_never_draws(self):
        """Fast emulation still fails after the unchanged thirty-guest-second budget."""
        row,error=self.capture(speed=2,ready=1000)
        self.assertIsInstance(error,AssertionError)
        self.assertGreaterEqual(row['guest_seconds'],30)
        self.assertLess(row['host_seconds'],30)

    def test_host_deadline_rejects_a_stalled_guest(self):
        """A stopped virtual clock cannot turn observation into an infinite wait."""
        row,error=self.capture(speed=0,ready=1000)
        self.assertIsInstance(error,AssertionError)
        self.assertGreaterEqual(row['host_seconds'],90)
        self.assertEqual(row['guest_seconds'],0)

    def test_one_wrong_pixel_is_not_accepted_after_startup(self):
        """Additional host time must not weaken exact date-band comparison."""
        row,error=self.capture(corrupt=True)
        self.assertIsInstance(error,AssertionError)
        self.assertEqual(row['different_bytes'],1)

    def test_microsecond_counter_wrap_preserves_elapsed_time(self):
        """Crossing the exposed 32-bit counter boundary is a short positive wait."""
        row,error=self.capture(initial=0xfffff000)
        self.assertIsNone(error)
        self.assertGreaterEqual(row['guest_seconds'],2)
        self.assertLess(row['guest_seconds'],3)

    def test_capture_failure_resumes_the_owned_vm(self):
        """An observation exception must still release the QMP stop."""
        _,error=self.capture(fail_capture=True)
        self.assertIsInstance(error,OSError)


def run_tests():
    """Return a report suitable for the mandatory full-QEMU gate."""
    output=io.StringIO()
    result=unittest.TextTestRunner(stream=output).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(DateCaptureTest))
    return {'passed':result.wasSuccessful(),'tests':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),
            'output':output.getvalue(),
            'scope':__doc__}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=run_tests()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['output'],end='')
    raise SystemExit(0 if result['passed'] else 1)
