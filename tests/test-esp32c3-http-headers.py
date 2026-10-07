"""Exercise malformed header bytes through a real local socket, without a board."""
import socket
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from http_headers import HEADER_CASES, request_bytes, request_status


class HeaderTransportTests(unittest.TestCase):
    def test_raw_invalid_lengths_reach_peer_without_large_body(self):
        for name, lengths, status in HEADER_CASES:
            with self.subTest(name=name), socket.socket() as server:
                server.bind(('127.0.0.1', 0))
                server.listen(1)
                server.settimeout(5)
                host = '127.0.0.1:' + str(server.getsockname()[1])
                received = []
                expected = request_bytes(host, lengths)
                self.assertLess(len(expected), 256)
                self.assertEqual(expected.split(b'\r\n\r\n', 1)[1], b'x')

                def peer():
                    with server.accept()[0] as connection:
                        connection.settimeout(5)
                        data = b''
                        while len(data) < len(expected):
                            chunk = connection.recv(256)
                            if not chunk:
                                break
                            data += chunk
                        received.append(data)
                        connection.sendall(f'HTTP/1.1 {status} Rejected\r\nContent-Length: 0\r\nConnection: close\r\n\r\n'.encode())

                thread = threading.Thread(target=peer)
                thread.start()
                try:
                    self.assertEqual(request_status('http://' + host, lengths), status)
                finally:
                    thread.join(timeout=6)
                self.assertFalse(thread.is_alive())
                self.assertEqual(received, [expected])
                self.assertEqual(received[0].count(b'Content-Length:'), len(lengths))


if __name__ == '__main__':
    unittest.main()
