"""HTTP success cannot hide an OTA panic and automatic reboot into the same image."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from ota_diagnostic import serial_health


class SerialHealth(unittest.TestCase):
    def test_expected_restart_is_allowed(self):
        rows = [dict(at=1, line='ESP-ROM:esp32c3'), dict(at=2, line='rst:0xc'),
                dict(at=3, line='PERF RAM: stage=app-start free=288880')]
        self.assertEqual(serial_health(rows)['result'], 'PASS')

    def test_fault_survives_later_successful_boot(self):
        for marker in ('assert failed: TCP PCB is allocated', 'Guru Meditation Error',
                       'PANIC registers: MEPC=0x40386b58', 'CORRUPT HEAP:',
                       'PERF TCP_POOL: action=invalid-free', 'serial capture interrupted'):
            rows = [dict(at=1, line=marker), dict(at=2, line='ESP-ROM:esp32c3'),
                    dict(at=3, line='PERF RAM: stage=app-start free=288880')]
            health = serial_health(rows)
            self.assertEqual(health['result'], 'FAIL', marker)
            self.assertEqual(health['evidence']['faults'], rows[:1])

    def test_absent_capture_is_not_a_pass(self):
        self.assertEqual(serial_health([])['result'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
