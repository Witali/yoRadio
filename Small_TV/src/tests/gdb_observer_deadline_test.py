"""Exercise shared diagnostic deadlines against real slow local RSP sockets."""
from contextlib import contextmanager
import socket
import threading
import time
import unittest

from gdb_observer import Observer


@contextmanager
def peer(delay=0, drip=0, timeout=1.5):
    """Run only a local register-read responder; never connect to a VM."""
    # Windows' socketpair fallback can wait without a deadline in connect/accept.
    # Use the same explicit bounded IPv4 loopback transport as the real observer.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.settimeout(2)
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        client = socket.create_connection(listener.getsockname(), 2)
        try:
            server, _ = listener.accept()
        except BaseException:
            client.close()
            raise
    client.settimeout(timeout); server.settimeout(.1)
    observer = Observer.__new__(Observer)
    observer.socket, observer._deadline, observer.breakpoints = client, None, set()
    stopped = threading.Event()
    commands, errors = [], []

    def serve():
        """Send valid packets slowly enough to expose per-read timeout resets."""
        try:
            while not stopped.is_set():
                try:
                    first = server.recv(1)
                except TimeoutError:
                    continue
                if not first:
                    return
                if first == b'+':
                    continue
                if first != b'$':
                    raise AssertionError('Unexpected client framing')
                command = bytearray()
                while True:
                    byte = server.recv(1)
                    if byte == b'#':
                        break
                    if not byte:
                        return
                    command += byte
                checksum = server.recv(2)
                while len(checksum) < 2:
                    checksum += server.recv(2 - len(checksum))
                if int(checksum, 16) != sum(command) % 256:
                    raise AssertionError('Invalid request checksum')
                commands.append(command.decode())
                if stopped.wait(delay):
                    return
                payload = b'78563412'
                packet = b'+$' + payload + b'#' + f'{sum(payload) % 256:02x}'.encode()
                if drip:
                    for byte in packet:
                        if stopped.wait(drip):
                            return
                        server.sendall(bytes([byte]))
                else:
                    server.sendall(packet)
        except OSError:
            if not stopped.is_set():
                errors.append('Unexpected socket failure')
        except BaseException as error:
            errors.append(str(error))

    worker = threading.Thread(target=serve)
    worker.start()
    try:
        yield observer, commands
    finally:
        stopped.set()
        client.close()
        worker.join(2)
        server.close()
        assert not worker.is_alive(), 'Owned RSP fixture did not stop'
        assert not errors, errors


class ObserverDeadlineTests(unittest.TestCase):
    """Keep normal framing, allowed commands and deadline restoration intact."""
    def test_normal_register_read(self):
        """Leave existing transport behavior unchanged outside diagnostic mode."""
        with peer() as (observer, commands):
            self.assertEqual(observer.register(32), 0x12345678)
            self.assertEqual(commands, ['p20'])
            self.assertEqual(observer.socket.gettimeout(), 1.5)

    def test_success_restores_timeout(self):
        """Restore the caller's configured timeout after a successful diagnostic."""
        with peer() as (observer, _):
            with observer.time_limit(.5):
                self.assertEqual(observer.register(1), 0x12345678)
            self.assertIsNone(observer._deadline)
            self.assertEqual(observer.socket.gettimeout(), 1.5)

    def test_slow_partial_reply_has_total_deadline(self):
        """Continuously arriving bytes cannot prolong one diagnostic indefinitely."""
        with peer(drip=.03) as (observer, commands):
            started = time.monotonic()
            with self.assertRaises(TimeoutError), observer.time_limit(.12):
                observer.register(32)
            self.assertLess(time.monotonic() - started, .8)
            self.assertEqual(commands, ['p20'])
            self.assertEqual(observer.socket.gettimeout(), 1.5)

    def test_multiple_requests_share_one_deadline(self):
        """Do not give each register read a fresh diagnostic budget."""
        with peer(delay=.09) as (observer, commands):
            started = time.monotonic()
            with self.assertRaises(TimeoutError), observer.time_limit(.22):
                observer.register(1)
                observer.register(2)
                observer.register(32)
            self.assertGreaterEqual(len(commands), 2)
            self.assertLess(time.monotonic() - started, .8)

    def test_nested_context_cannot_extend_outer_deadline(self):
        """A longer inner capture must still obey the original limit."""
        with peer(delay=.3) as (observer, _):
            started = time.monotonic()
            with self.assertRaises(TimeoutError), observer.time_limit(.06):
                with observer.time_limit(2):
                    observer.register(32)
            self.assertLess(time.monotonic() - started, .6)
            self.assertEqual(observer.socket.gettimeout(), 1.5)

    def test_invalid_budgets_never_send(self):
        """Reject unbounded, nonnumeric, boolean and nonfinite durations."""
        with peer() as (observer, commands):
            for value in (None, True, 0, -1, 31, float('nan'), float('inf')):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    with observer.time_limit(value):
                        observer.register(32)
            self.assertEqual(commands, [])

    def test_diagnostic_still_rejects_state_writes(self):
        """A deadline does not widen the existing read-only RSP command allowlist."""
        with peer() as (observer, commands):
            with observer.time_limit(.5), self.assertRaises(AssertionError):
                observer.request('P20=00000000')
            self.assertEqual(commands, [])

    def test_exception_restores_timeout(self):
        """A failed capture must not leave a tiny timeout in the owner."""
        with peer() as (observer, _):
            with self.assertRaises(ValueError):
                with observer.time_limit(.1):
                    raise ValueError('capture failure')
            self.assertIsNone(observer._deadline)
            self.assertEqual(observer.socket.gettimeout(), 1.5)

    def test_expiry_before_send_does_not_corrupt_stream(self):
        """An expired new request sends nothing and preserves subsequent framing."""
        with peer() as (observer, commands):
            with self.assertRaises(TimeoutError), observer.time_limit(.01):
                time.sleep(.03)
                observer.register(32)
            self.assertEqual(commands, [])
            self.assertEqual(observer.register(32), 0x12345678)

    def test_shorter_existing_timeout_is_preserved(self):
        """A diagnostic budget cannot lengthen the caller's per-socket timeout."""
        with peer(delay=.2, timeout=.03) as (observer, _):
            started = time.monotonic()
            with self.assertRaises(TimeoutError), observer.time_limit(1):
                observer.register(32)
            self.assertLess(time.monotonic() - started, .15)
            self.assertEqual(observer.socket.gettimeout(), .03)


if __name__ == '__main__':
    unittest.main()
