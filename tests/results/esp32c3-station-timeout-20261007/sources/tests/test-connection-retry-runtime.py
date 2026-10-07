"""Only the requested persistence-test software reboot may bypass the reboot gate."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from connection_retry import check_runtime
from common import Failure


class RetryRuntime(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(at=1, line='PERF CPU: busy=50.0%'),
                     dict(at=3, line='ESP-ROM:esp32c3-api1-20210207'),
                     dict(at=3, line='rst:0xc (RTC_SW_CPU_RST),boot:0xc (SPI_FAST_FLASH_BOOT)'),
                     dict(at=8, line='PERF CPU: busy=50.0%')]
        self.reboots = [dict(start=2, end=7)]

    def test_requested_software_reset_only(self):
        self.assertEqual(check_runtime(self.rows, self.reboots), dict(planned_software_reboots=1))
        with self.assertRaises(Failure): check_runtime(self.rows, [])
        with self.assertRaises(Failure): check_runtime(self.rows[0:2]+self.rows[3:], self.reboots)
        wrong = list(self.rows)
        wrong[2] = dict(at=3,line='rst:0x8 (TG1WDT_SYS_RST),boot:0xc (SPI_FAST_FLASH_BOOT)')
        with self.assertRaises(Failure): check_runtime(wrong, self.reboots)

    def test_fault_during_expected_reboot_is_not_hidden(self):
        for line in ('assert failed: owner', 'Runtime watchdog timeout: task_watchdog=true',
                     'allocation failed', 'decode error', 'serial capture interrupted',
                     'waiting for download', 'ESP-ROM:esp32c3'):
            with self.subTest(line=line), self.assertRaises(Failure):
                check_runtime(self.rows+[dict(at=4,line=line)], self.reboots)
        with self.assertRaises(Failure):
            check_runtime(self.rows+[dict(at=10,line='rst:0xc')], self.reboots)


if __name__ == '__main__':
    unittest.main()
