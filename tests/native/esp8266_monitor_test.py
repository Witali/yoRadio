"""No physical serial access: verify monitor reconnect/reset ownership."""
import pathlib
import runpy
import sys
import types
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / 'tools' / 'monitor_esp8266.py'

class MonitorTests(unittest.TestCase):
    def run_monitor(self, reconnect, reset=False, marker=False):
        clock = [0.0]
        opens, pulses = [], []
        reads = [0]
        stopped = [False]
        class Disconnected(Exception):
            pass
        class Serial:
            def __init__(self, **kwargs):
                self.rts = False
            def __setattr__(self, key, value):
                if key == 'rts' and value:
                    pulses.append(True)
                object.__setattr__(self, key, value)
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def open(self):
                opens.append((self.port, self.dtr, self.rts))
            def read(self, length):
                reads[0] += 1
                if marker:
                    stopped[0] = True
                    return b'stopped\n'
                if reads[0] == 1:
                    raise Disconnected('simulated USB removal')
                clock[0] += 6
                return b'reconnected\n'
        argv = [str(SCRIPT), '--seconds', '5']
        if reconnect:
            argv.append('--reconnect')
        if reset:
            argv.append('--reset')
        if marker:
            argv += ['--stop-file', 'unused-marker']
        # stdout is a real stream because the script deliberately reconfigures
        # its encoding on Windows; suppress only unittest's own exception path.
        with patch.dict(sys.modules, {'serial': types.SimpleNamespace(Serial=Serial, SerialException=Disconnected)}), \
             patch.object(sys, 'argv', argv), \
             patch('time.monotonic', side_effect=lambda: clock[0]), \
             patch('time.sleep', side_effect=lambda amount: clock.__setitem__(0, clock[0]+amount)), \
             patch.object(pathlib.Path, 'exists', side_effect=lambda: stopped[0]):
            if not reconnect and not marker:
                with self.assertRaises(Disconnected):
                    runpy.run_path(str(SCRIPT), run_name='__main__')
            else:
                runpy.run_path(str(SCRIPT), run_name='__main__')
        self.assertTrue(all(port == 'COM8' and not dtr and not rts for port, dtr, rts in opens))
        self.assertEqual(len(pulses), 1 if reset else 0)
        self.assertEqual(len(opens), 2 if reconnect and not marker else 1)

    def test_reconnect_never_resets(self):
        self.run_monitor(True)
    def test_explicit_reset_is_not_repeated_after_reconnect(self):
        self.run_monitor(True, reset=True)
    def test_default_still_fails_on_disconnect(self):
        self.run_monitor(False)
    def test_stop_marker_exits_without_waiting_for_deadline(self):
        self.run_monitor(True, marker=True)

if __name__ == '__main__':
    unittest.main()
