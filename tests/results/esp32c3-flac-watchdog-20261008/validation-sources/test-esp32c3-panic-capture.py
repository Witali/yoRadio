"""Panic diagnostics must retain code evidence without raw private memory."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from diagnostic import filter_line
from ota_diagnostic import serial_health
from common import TLS_CERTIFICATE_REJECTED
from common import check_file_runtime, Failure


class PanicFilter(unittest.TestCase):
    def test_watchdog_counter_replay_without_isr_output(self):
        raw = 'E (123) cpu_profile: PERF watchdog: task_timeouts=2 private-secret'
        result = filter_line(raw)
        self.assertEqual(result, 'Runtime watchdog timeout: task_watchdog=true events=2')
        for line in (raw, result):
            rows = [dict(at=1, line=line)]
            self.assertEqual(serial_health(rows)['result'], 'FAIL')
            with self.assertRaises(Failure):
                check_file_runtime(rows)
        zero = [dict(at=1, line='PERF watchdog: task_timeouts=0')]
        check_file_runtime(zero)
        self.assertEqual(serial_health(zero)['result'], 'PASS')

    def test_watchdog_context_survives_lost_caption_and_fails_runtime(self):
        cases = {
            ' - IDLE0 (CPU 0)': 'phase=starved cpu=0 task=IDLE0',
            ' - radio_stream (CPU 0/1)': 'phase=starved cpu=0/1 task=radio_stream',
            'CPU 0: tcpip': 'phase=running cpu=0 task=tcpip',
            'CPU 1: audio_decode': 'phase=running cpu=1 task=audio_decode',
            'Tasks currently running:': 'phase=current-tasks',
            'Print CPU 0 (current core) backtrace': 'phase=backtrace cpu=0',
            'Print CPU 0 (current core) registers': 'phase=registers cpu=0',
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                result = filter_line('\x1b[0;31mE (123) task_wdt: '+source+'\x1b[0m')
                self.assertEqual(result, 'Runtime watchdog timeout: task_watchdog=true '+expected)
                rows = [dict(at=1, line=result)]
                self.assertEqual(serial_health(rows)['result'], 'FAIL')
                with self.assertRaises(Failure):
                    check_file_runtime(rows)

    def test_watchdog_unknown_names_are_redacted(self):
        for source, phase in [(' - private-secret (CPU 0)', 'starved'),
                              ('CPU 0: private-secret', 'running'),
                              ('CPU 0: tcpip private-secret', 'running')]:
            with self.subTest(source=source):
                result = filter_line('E (123) task_wdt: '+source)
                self.assertEqual(result, 'Runtime watchdog timeout: task_watchdog=true '
                                 'phase='+phase+' cpu=0 task=redacted')
        self.assertIsNone(filter_line('E (123) unrelated: CPU 0: tcpip'))
        self.assertIsNone(filter_line('E (123) task_wdt: Tasks currently running: private-secret'))

    def test_tls_reserve_retains_only_numeric_counters(self):
        counters = ('TLS_RESERVE capacity=17058 minimum=16384 allocations=10 '
                    'releases=9 busy_fallbacks=0 oversize=0 busy=1 used=16749')
        self.assertEqual(filter_line('I (12) tls_reserve: '+counters+' private-secret'), counters)
        self.assertIsNone(filter_line('I (12) tls_reserve: private-secret'))

    def test_adaptive_input_retains_only_numeric_counters(self):
        counters = ('TLS_INPUT released=4 retries=0 request=16749 resident=4 '
                    'minimum=4 target=8 occupied=2 capacity=8240')
        self.assertEqual(filter_line('I (12) tls_input: '+counters+' private-secret'), counters)
        self.assertIsNone(filter_line('I (12) tls_input: private-secret'))
        fault = 'allocation failed '+counters
        self.assertEqual(filter_line(fault), fault)

    def test_watchdog_without_register_dump_is_failure(self):
        line=filter_line('\x1b[0;31mE (123) task_wdt: Task watchdog got triggered. '
                         'The following tasks/users did not reset the watchdog in time:')
        self.assertEqual(line,'Runtime watchdog timeout: task_watchdog=true')
        self.assertEqual(serial_health([dict(at=1,line=line)])['result'],'FAIL')
        self.assertIsNone(filter_line('E (123) task_wdt: private task data'))

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

    def test_tls_errors_are_retained_without_private_message_text(self):
        self.assertEqual(filter_line('E (12) Dynamic Impl: alloc(16432 bytes) failed'),
                         'TLS failure: component=Dynamic Impl allocation_bytes=16432')
        for tag in ('esp-tls', 'esp-tls-mbedtls', 'esp-x509-crt-bundle',
                    'SSL TLS', 'SSL client', 'SSL Server'):
            with self.subTest(tag=tag):
                self.assertEqual(filter_line('\x1b[0;31mE (12) '+tag+
                    ': certificate/URL private-secret allocation failed\x1b[0m'),
                    'TLS failure: component='+tag)
        self.assertIsNone(filter_line('I (12) esp-tls: private-secret'))

    def test_only_fixed_certificate_verification_message_proves_rejection(self):
        self.assertEqual(filter_line('\x1b[0;31mE (12) esp-x509-crt-bundle: '
            'Failed to verify certificate\x1b[0m'), TLS_CERTIFICATE_REJECTED)
        for text in ('No certificates in bundle', 'Failed to allocate memory',
                     'Failed to verify certificate for private-subject'):
            self.assertEqual(filter_line('E (12) esp-x509-crt-bundle: '+text),
                             'TLS failure: component=esp-x509-crt-bundle')


if __name__ == '__main__':
    unittest.main()
