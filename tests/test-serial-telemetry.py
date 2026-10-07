"""Exercise real capture loops with fragmented, bursty and interrupted input."""
from collections import deque
from pathlib import Path
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from run import Capture
from diagnostic import DiagnosticCapture
from transport import DiagnosticCapture as TransportCapture


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


if __name__ == '__main__': unittest.main()
