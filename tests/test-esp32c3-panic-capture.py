"""Panic diagnostics must retain code evidence without raw private memory."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from diagnostic import filter_line


class PanicFilter(unittest.TestCase):
    def test_measured_code_and_cause_survive(self):
        self.assertEqual(filter_line('MEPC    : 0x42012344  RA      : 0x40381234  SP : 0x3fc91200'),
                         'PANIC registers: MEPC=0x42012344 RA=0x40381234')
        self.assertEqual(filter_line('MCAUSE  : 0x00000002  MTVAL : 0xdeadbeef'),
                         'PANIC registers: MCAUSE=0x00000002')

    def test_stack_retains_only_possible_code_addresses(self):
        result = filter_line('3fc91200: 0x42012344 0x73656372 0x65742121 0x3fc91300 0x40381234')
        self.assertEqual(result, 'PANIC stack code candidates: 0x42012344 0x40381234')
        self.assertIsNone(filter_line('3fc91200: 0x73656372 0x65742121 0x3fc91300'))
        self.assertIsNone(filter_line('network: ssid=private password=private'))
        self.assertIsNone(filter_line('station: https://private.invalid/token'))

    def test_runtime_failure_and_boot_evidence_survive(self):
        for line in ('Guru Meditation Error: Illegal instruction',
                     'I (45) cpu_profile: PERF RAM: stage=app-start free=100',
                     'E (12) audio: allocation failed', 'rst:0x1 (POWERON_RESET)'):
            self.assertEqual(filter_line(line), line)


if __name__ == '__main__':
    unittest.main()
