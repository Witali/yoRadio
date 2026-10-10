"""Exercise real capture loops with fragmented, bursty and interrupted input."""
from collections import deque
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch
import itertools

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from run import Capture
from diagnostic import DiagnosticCapture
from transport import DiagnosticCapture as TransportCapture
from serial_lines import serial_lines


class Port:
    def __init__(self, chunks, closed):
        self.chunks = deque(chunks)
        self.closed = closed
        self.read_sizes = []

    @property
    def in_waiting(self):
        return len(self.chunks[0]) if self.chunks else 0

    def read(self, size):
        self.read_sizes.append(size)
        if not self.chunks:
            self.closed.set()
            return b''
        result = self.chunks.popleft()
        if len(result) > size:
            self.chunks.appendleft(result[size:])
        return result[:size]


class SerialTelemetry(unittest.TestCase):
    def capture(self, cls, chunks):
        cap = cls.__new__(cls)
        cap.rows, cap.closed = [], threading.Event()
        cap.port = Port(chunks, cap.closed)
        cap.read()
        return cap

    def test_timeouts_bursts_and_filtering(self):
        for cls in (Capture, DiagnosticCapture, TransportCapture):
            cap = self.capture(cls, [b'ignored private text\nI: PERF RX_', b'',
                b'OWNER: seq=1\r', b'', b'\n' + b'I: PERF RX_BLOCK: id=1\n' * 1000])
            self.assertEqual([r['line'] for r in cap.rows],
                ['I: PERF RX_OWNER: seq=1'] + ['I: PERF RX_BLOCK: id=1'] * 1000)
            self.assertIn(4096, cap.port.read_sizes)

    def test_incomplete_and_overlong_lines_fail_closed(self):
        for cls in (Capture, DiagnosticCapture, TransportCapture):
            for chunks in ([b'PERF incomplete'], [b'x' * 70000]):
                cap = self.capture(cls, chunks)
                self.assertEqual(len(cap.rows), 1)
                self.assertTrue(cap.rows[0]['line'].startswith('serial capture interrupted:'))

    def test_tls_numeric_detail_survives_fragmented_capture(self):
        for cls in (Capture, DiagnosticCapture):
            cap = self.capture(cls, [b'E (123) Dynamic Impl: mbedtls_ssl_fetch_', b'',
                b'input error=80\r\nE (124) esp-tls-mbedtls: read error :-0x0050\n',
                b'E (125) esp-tls-mbedtls: private.example detail\n'])
            self.assertEqual([r['line'] for r in cap.rows], [
                'TLS failure: component=Dynamic Impl operation=fetch_input mbedtls_return=-80',
                'TLS failure: component=esp-tls-mbedtls operation=read mbedtls_return=-80',
                'TLS failure: component=esp-tls-mbedtls'])

    def test_os_error_is_visible(self):
        cap = Capture.__new__(Capture)
        cap.rows, cap.closed = [], threading.Event()
        class Broken:
            def read(self, size): raise AssertionError('Read must not be reached')
            @property
            def in_waiting(self): raise OSError('test-only detail must not escape')
        cap.port = Broken()
        cap.read()
        self.assertEqual(cap.rows[0]['line'], 'serial capture interrupted')

    def test_requested_shutdown_finishes_only_the_current_line(self):
        closed = threading.Event()
        class ClosingPort(Port):
            def read(self, size):
                data = super().read(size)
                closed.set()
                return data
        port = ClosingPort([b'PERF caf\xc3', b'\xa9\nnext private line\n'], closed)
        self.assertEqual(list(serial_lines(port, closed)), ['PERF caf\u00e9'])
        self.assertEqual(b''.join(port.chunks), b'next private line\n')
        self.assertTrue(all(size == 1 for size in port.read_sizes[1:]))

    def test_requested_shutdown_without_newline_still_fails(self):
        closed = threading.Event()
        port = Port([b'PERF partial'], closed)
        with patch('serial_lines.time.monotonic', side_effect=itertools.count(0, .1)):
            self.assertEqual(list(serial_lines(port, closed)),
                             ['serial capture interrupted: incomplete final line'])
        self.assertLess(len(port.read_sizes), 10)

    def test_closed_empty_capture_does_not_read(self):
        closed = threading.Event(); closed.set()
        port = Port([b'unread'], closed)
        self.assertEqual(list(serial_lines(port, closed)), [])
        self.assertEqual(port.read_sizes, [])

    def test_shutdown_read_error_remains_visible(self):
        closed = threading.Event()
        class BrokenOnClose(Port):
            def read(self, size):
                if closed.is_set(): raise OSError('private device detail')
                data = super().read(size); closed.set(); return data
        self.assertEqual(list(serial_lines(BrokenOnClose([b'PERF partial'], closed), closed)),
                         ['serial capture interrupted'])


if __name__ == '__main__': unittest.main()
