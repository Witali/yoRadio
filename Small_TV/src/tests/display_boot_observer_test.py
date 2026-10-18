"""Test exact-frame decisions; real PPM parsing is the existing display module's job."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from display_boot_observer import observe_frame

TEMP=None
EXPECTED=bytes([1,2,3])*(240*240)


class ExactFrameTests(unittest.TestCase):
    def observe(self,frames,host_step=.1,guest_step=100000,initial=0,stale=False,short=False):
        """Replace only the transport/clock; read every captured byte from a real file."""
        with tempfile.TemporaryDirectory(dir=TEMP) as directory:
            folder=Path(directory)
            if stale:(folder/'display.ppm').write_bytes(EXPECTED)
            class Clock:
                now=0
                def monotonic(self):return self.now
                def sleep(self,ignored):self.now+=host_step
            class Qmp:
                tick=-1
                captures=0
                def virtual_us(self):
                    self.tick+=1;return (initial+self.tick*guest_step)&0xffffffff
                def execute(self,command,**arguments):
                    if command!='screendump':raise AssertionError('Non-display observation')
                    if stale:return
                    value=frames[min(self.captures,len(frames)-1)]
                    Path(arguments['filename']).write_bytes(value[:-1] if short else value)
                    self.captures+=1
            qmp=Qmp()
            with patch('display_boot_observer.time',Clock()):
                result=observe_frame(qmp,folder,qmp.virtual_us,Path.read_bytes,EXPECTED)
            self.assertFalse((folder/'uart.log').exists())
            return result

    def test_exact_frame(self):
        self.assertTrue(self.observe([EXPECTED])['passed'])

    def test_transient_clear_and_partial_frame(self):
        result=self.observe([bytes(len(EXPECTED)),EXPECTED[:1000]+bytes(len(EXPECTED)-1000),EXPECTED])
        self.assertTrue(result['passed']);self.assertEqual(len(result['samples']),3)

    def test_fully_lit_wrong_image(self):
        self.assertFalse(self.observe([bytes([255])*len(EXPECTED)],guest_step=1000000)['passed'])

    def test_one_wrong_pixel_is_not_ready(self):
        self.assertFalse(self.observe([b'\x02'+EXPECTED[1:]],guest_step=1000000)['passed'])

    def test_black_screen(self):
        self.assertFalse(self.observe([bytes(len(EXPECTED))],guest_step=1000000)['passed'])

    def test_stalled_guest_host_bound(self):
        self.assertFalse(self.observe([bytes(len(EXPECTED))],guest_step=0,host_step=30)['passed'])

    def test_guest_deadline_not_extended_by_readiness(self):
        self.assertFalse(self.observe([bytes(len(EXPECTED)),EXPECTED],guest_step=5000000)['passed'])

    def test_host_deadline_not_extended_by_readiness(self):
        self.assertFalse(self.observe([bytes(len(EXPECTED)),EXPECTED],guest_step=0,host_step=90)['passed'])

    def test_clock_wrap(self):
        self.assertTrue(self.observe([EXPECTED],initial=0xffffff00,guest_step=512)['passed'])

    def test_stale_screenshot_is_not_fresh_evidence(self):
        with self.assertRaises(FileNotFoundError):self.observe([EXPECTED],stale=True)

    def test_short_raster(self):
        with self.assertRaisesRegex(ValueError,'Short LCD'):self.observe([EXPECTED],short=True)

    def test_no_uart_or_network_flags_required(self):
        result=self.observe([EXPECTED]);self.assertEqual(result['differing_rgb_bytes'],0)


def main():
    """Write actual unittest results to a new independent report."""
    global TEMP
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--temp-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.temp_root.mkdir(parents=True,exist_ok=True);TEMP=args.temp_root
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ExactFrameTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    report=dict(passed=result.wasSuccessful(),tests=result.testsRun,
        test_source_sha256=sha(Path(__file__)),observer_source_sha256=sha(Path(__file__).with_name('display_boot_observer.py')),
        failures=[str(case) for case,_ in result.failures],errors=[str(case) for case,_ in result.errors])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    return not report['passed']


if __name__=='__main__':raise SystemExit(main())
