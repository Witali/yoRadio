"""Keep diagnostic transport/file failures from replacing the original error."""
import io
from contextlib import nullcontext
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from gdb_observer_deadline_test import peer
from runtime_failure_capture import DeadlineStream, FailureCapture, qmp_read


class FailureCaptureTests(unittest.TestCase):
    """Exercise the exceptional path without running or modifying guest code."""
    def recorder(self, folder, result):
        """Construct an unused transport; individual tests provide explicit records."""
        return FailureCapture(None, None, None, None, folder, result, {})

    def test_normal_exit_does_not_capture(self):
        """A successful workload does not gain extra pauses or output files."""
        with tempfile.TemporaryDirectory() as folder:
            recorder = self.recorder(Path(folder), {})
            recorder.capture = Mock(side_effect=AssertionError('Unexpected capture'))
            with recorder:
                pass
            recorder.capture.assert_not_called()
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_capture_error_preserves_original_exception(self):
        """A broken debugger must not mask the original HTTP timeout."""
        with tempfile.TemporaryDirectory() as folder:
            result = {}; recorder = self.recorder(Path(folder), result)
            recorder.capture = Mock(side_effect=ConnectionError('Debugger disconnected'))
            error = TimeoutError('Original HTTP failure')
            with self.assertRaises(TimeoutError) as observed:
                with recorder:
                    raise error
            self.assertIs(observed.exception, error)
            self.assertEqual(result['failure_capture']['status'], 'unavailable')

    def test_existing_artifact_is_never_overwritten(self):
        """Preserve earlier observations if an output path is unexpectedly reused."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'failure-state.json'; path.write_bytes(b'preserved')
            result = {}; recorder = self.recorder(Path(folder), result)
            recorder.capture = Mock(return_value={'status': 'captured'})
            with self.assertRaises(TimeoutError), recorder:
                raise TimeoutError('Original failure')
            self.assertEqual(path.read_bytes(), b'preserved')
            self.assertEqual(result['failure_capture']['status'], 'unavailable')

    def test_oversized_artifact_is_rejected(self):
        """A diagnostic cannot export an arbitrary large payload as metadata."""
        with tempfile.TemporaryDirectory() as folder:
            result = {}; recorder = self.recorder(Path(folder), result)
            recorder.capture = Mock(return_value={'status': 'captured', 'data': 'x' * 65536})
            with self.assertRaises(TimeoutError), recorder:
                raise TimeoutError('Original failure')
            self.assertFalse((Path(folder) / 'failure-state.json').exists())
            self.assertEqual(result['failure_capture']['status'], 'unavailable')

    def test_qmp_does_not_accept_state_changes(self):
        """Do not add an arbitrary HMP command or QMP write route to capture."""
        for command, args in (('stop', {}), ('qom-set', {}),
                              ('human-monitor-command', {'command-line': 'system_reset'})):
            with self.subTest(command=command), self.assertRaises(ValueError):
                qmp_read(None, time.monotonic() + 1, command, **args)

    def test_partial_qmp_line_has_total_deadline(self):
        """Continuously arriving non-newline bytes cannot delay cleanup forever."""
        with peer(drip=.03) as (observer, _):
            observer.resume()
            with observer.socket.makefile('rwb') as stream:
                bounded = DeadlineStream(stream, observer.socket, time.monotonic() + .12)
                started = time.monotonic()
                with self.assertRaises(TimeoutError):
                    bounded.readline()
                self.assertLess(time.monotonic() - started, .8)

    def test_qmp_response_byte_limit(self):
        """Reject an oversized stream before accepting a trailing newline."""
        bounded = DeadlineStream(io.BytesIO(b'x' * 65537 + b'\n'), Mock(), time.monotonic() + 2)
        with self.assertRaises(ValueError):
            bounded.readline()

    def test_large_usernet_does_not_displace_other_metadata(self):
        """Reject a large component while restoring the existing owner's stream."""
        qmp = Mock()
        original = qmp.file
        qmp.sock.gettimeout.return_value = 5
        qmp.execute.return_value = '\x01' * 4096  # Escaped JSON exceeds 16 KiB.
        with self.assertRaises(ValueError):
            qmp_read(qmp, time.monotonic() + 1, 'human-monitor-command', **{'command-line': 'info usernet'})
        self.assertIs(qmp.file, original)
        qmp.sock.settimeout.assert_called_with(5)

    def stress_reads(self, size):
        """Drive the real capture budget past its limit through a declared fake heap."""
        calls = []
        observer = Mock()
        observer.time_limit.return_value = nullcontext()
        observer.register.side_effect = lambda number: number
        observer.memory.side_effect = lambda address, count: calls.append(count) or b'\0' * count

        class Reader:
            """Request real callback reads without needing a fabricated linked ABI."""
            def __init__(self, read, layout):
                self.memory = read

            def heaps(self):
                for index in range(250):
                    self.memory(0x3fca1000 + index * size, size)

        result = dict(app_sha256='a' * 64, native_elf_sha256='b' * 64,
                      qemu_sha256='c' * 64, completed_cycles=0)
        layout = {'symbols': {'connected': {'address': 0x3fca0000}}}
        capture = FailureCapture(observer, None, layout, {}, None, result, {'name': 'owned-fixture'})
        capture.photo_state, capture.tasks = Mock(return_value={}), Mock(return_value={})
        with patch('runtime_failure_capture.MemorySnapshot', Reader), \
                patch('runtime_failure_capture.qmp_read', return_value={'running': False}):
            record = capture.capture('TimeoutError')
        self.assertEqual(record['status'], 'partial')
        self.assertEqual(record['errors'], {'heap': 'TimeoutError'})
        self.assertEqual(record['memory_reads'], len(calls))
        self.assertEqual(record['memory_requested_bytes'], sum(calls))
        return calls, record

    def test_capture_request_count_is_bounded(self):
        """Stop before issuing a 193rd target-memory request."""
        calls, record = self.stress_reads(4)
        self.assertEqual(len(calls), 192)
        self.assertLessEqual(record['memory_requested_bytes'], 32768)

    def test_capture_target_byte_budget_is_bounded(self):
        """Reject the next bounded block before crossing the 32-KiB byte cap."""
        calls, record = self.stress_reads(4096)
        self.assertEqual(len(calls), 8)  # One connection flag plus seven 4-KiB blocks.
        self.assertLessEqual(record['memory_requested_bytes'], 32768)


if __name__ == '__main__':
    unittest.main()
