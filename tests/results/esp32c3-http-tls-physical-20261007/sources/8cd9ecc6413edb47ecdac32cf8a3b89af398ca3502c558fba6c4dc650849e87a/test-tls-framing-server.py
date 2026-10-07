"""Verify exact HTTP bytes and real TLS closure behavior of all framing fixtures."""
import hashlib
from pathlib import Path
import socket
import ssl
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.record_test_ca import generate
from audio_test_server.tls_framing import FramingServer, MODES


class FramingTests(unittest.TestCase):
    def test_all_modes(self):
        data = bytes(range(256))*17
        spec = dict(data=data, mime='audio/aac', sha256=hashlib.sha256(data).hexdigest())
        with tempfile.TemporaryDirectory(prefix='yoradio-framing-') as folder:
            keys = generate('127.0.0.1', Path(folder)/'keys')
            context = ssl.create_default_context(cafile=str(keys['ca']))
            with FramingServer('127.0.0.1', 0, {'audio':spec}, keys['cert'], keys['key']) as server:
                for mode in MODES:
                    with self.subTest(mode=mode):
                        before = len(server.events)
                        wire = bytearray()
                        abrupt = False
                        with socket.create_connection(('127.0.0.1', server.server.server_address[1]), timeout=5) as plain:
                            with context.wrap_socket(plain, server_hostname='127.0.0.1', suppress_ragged_eofs=False) as secure:
                                secure.sendall(f'GET /{mode}/audio HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n'.encode())
                                try:
                                    while chunk := secure.recv(4096):
                                        wire.extend(chunk)
                                except ssl.SSLEOFError:
                                    abrupt = True
                        self.assertEqual(abrupt, mode.endswith('-raw'))
                        header, body = bytes(wire).split(b'\r\n\r\n', 1)
                        if mode.startswith('chunked-'):
                            self.assertIn(b'Transfer-Encoding: chunked', header)
                            expected = b''.join(f'{len(data[i:i+1024]):x};fixture=1\r\n'.encode()+data[i:i+1024]+b'\r\n'
                                                for i in range(0, len(data), 1024))
                            if mode != 'chunked-short':
                                expected += b'0\r\nX-Fixture: complete\r\n\r\n'
                            self.assertEqual(body, expected)
                        else:
                            self.assertEqual(body, data)
                            if mode.startswith('length-'):
                                declared = len(data)+(mode == 'length-short')
                                self.assertIn(f'Content-Length: {declared}\r\n'.encode(), header+b'\r\n')
                            else:
                                self.assertNotIn(b'Content-Length:', header)
                                self.assertNotIn(b'Transfer-Encoding:', header)
                        deadline = time.monotonic()+2
                        while 'ended_at' not in server.events[before] and time.monotonic()<deadline:
                            time.sleep(.01)
                        self.assertEqual(len(server.events), before+1)
                        event = server.events[before]
                        self.assertTrue(event['complete'])
                        self.assertNotIn('error', event)
                        alerts = [r for r in event['records'] if r['type'] == 21 and r['phase'] == 'close']
                        self.assertEqual(len(alerts), 0 if abrupt else 1)
                        self.assertEqual(event['body_bytes'], len(data))
                        self.assertEqual(event['dropped_records'], 0)


if __name__ == '__main__':
    unittest.main()
