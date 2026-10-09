"""Actual TLS/HTTP roundtrip; assert encrypted record lengths and exact audio."""
import hashlib
import copy
from pathlib import Path
import socket
import ssl
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.record_test_ca import generate
from audio_test_server.tls_records import RecordServer
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from tls_records import capture_record_observation, record_evidence


class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='yoradio-record-test-')
        cls.keys = generate('127.0.0.1', Path(cls.temporary.name)/'keys')
        cls.data = bytes(range(256)) * 64
        cls.specs = {'fixture':dict(codec='aac', data=cls.data, seconds=.2,
                                  sha256=hashlib.sha256(cls.data).hexdigest())}

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_verified_tls_records_and_audio(self):
        for mode in ('small', 'large', 'grow', 'alternate'):
            with self.subTest(mode=mode), RecordServer('127.0.0.1', 0, self.specs,
                    self.keys['cert'], self.keys['key'], seconds=.8, grow_seconds=.2) as server:
                context = ssl.create_default_context(cafile=str(self.keys['ca']))
                port = server.server.server_address[1]
                with socket.create_connection(('127.0.0.1', port), timeout=5) as plain:
                    with context.wrap_socket(plain, server_hostname='127.0.0.1',
                                             suppress_ragged_eofs=False) as secure:
                        secure.sendall(f'GET /{mode}/fixture HTTP/1.1\r\nHost: localhost\r\n\r\n'.encode())
                        wire = bytearray()
                        while chunk := secure.recv(32768):
                            wire.extend(chunk)
                header, audio = bytes(wire).split(b'\r\n\r\n', 1)
                self.assertIn(b'200 OK', header)
                self.assertEqual(audio, (self.data * (len(audio)//len(self.data)+1))[:len(audio)])
                event = server.events[0]
                self.assertEqual(event['pacing_ratio'], 1.02)
                self.assertTrue(event['complete'])
                self.assertEqual(event['audio_bytes'], len(audio))
                self.assertEqual(event['dropped_records'], 0)
                self.assertEqual(event['dropped_writes'], 0)
                self.assertTrue(any(r['phase'] == 'close' and r['type'] == 21
                                    for r in event['records']))
                self.assertEqual(event['version'], 'TLSv1.2')
                self.assertEqual(event['cipher'], 'ECDHE-RSA-AES128-GCM-SHA256')
                body = [r for r in event['records'] if r['phase'].startswith('body-')]
                expected = {1048} if mode == 'small' else {16408} if mode == 'large' else {1048,16408}
                self.assertEqual({r['wire_payload_bytes'] for r in body}, expected)
                self.assertTrue(all(r['type'] == 23 for r in body))
                writes = [w for w in event['writes'] if w['phase'].startswith('body-')]
                self.assertEqual([w['plaintext_bytes']+24 for w in writes], [r['wire_payload_bytes'] for r in body])
                self.assertEqual(set(record_evidence([event], mode)['record_counts']), expected)
                with self.assertRaises(AssertionError):
                    record_evidence([event, event], mode)
                with self.assertRaises(AssertionError):
                    record_evidence([{'error':'SSLError'}, event], mode)
                broken = copy.deepcopy(event)
                next(r for r in broken['records'] if r['phase'].startswith('body-'))['wire_payload_bytes'] += 1
                with self.assertRaises(AssertionError):
                    record_evidence([broken], mode)
                broken = copy.deepcopy(event)
                broken['dropped_records'] = 1
                with self.assertRaises(AssertionError):
                    record_evidence([broken], mode)

    def test_normal_trust_rejects_ephemeral_ca(self):
        with RecordServer('127.0.0.1', 0, self.specs, self.keys['cert'], self.keys['key'], seconds=1, grow_seconds=0) as server:
            context = ssl.create_default_context()
            with socket.create_connection(('127.0.0.1', server.server.server_address[1]), timeout=5) as plain:
                with self.assertRaises(ssl.SSLCertVerificationError):
                    context.wrap_socket(plain, server_hostname='127.0.0.1')

    def test_explicit_pacing_controls_real_tls_delivery(self):
        duration = .8
        for ratio in (.5, 1.0, 2.0):
            with self.subTest(ratio=ratio), RecordServer('127.0.0.1', 0, self.specs,
                    self.keys['cert'], self.keys['key'], seconds=duration,
                    grow_seconds=0, pacing_ratio=ratio) as server:
                context = ssl.create_default_context(cafile=str(self.keys['ca']))
                with socket.create_connection(server.server.server_address, timeout=5) as plain:
                    with context.wrap_socket(plain, server_hostname='127.0.0.1',
                                             suppress_ragged_eofs=False) as secure:
                        secure.sendall(b'GET /small/fixture HTTP/1.1\r\nHost: localhost\r\n\r\n')
                        received = bytearray()
                        while chunk := secure.recv(32768):
                            received.extend(chunk)
                _, audio = bytes(received).split(b'\r\n\r\n', 1)
                event = server.events[0]
                deadline = time.perf_counter()+1
                while 'ended_at' not in event and time.perf_counter() < deadline:
                    time.sleep(.005)
                self.assertTrue(event['complete'])
                self.assertEqual(event['pacing_ratio'], ratio)
                bps = len(self.data) / self.specs['fixture']['seconds'] * ratio
                self.assertEqual(event['target_audio_bytes_per_second'], bps)
                self.assertEqual(audio, (self.data * (len(audio)//len(self.data)+1))[:len(audio)])
                # Check delivered bytes over wall time, with scheduling slack
                # and at most one record sent ahead of its pacing deadline.
                elapsed = event['ended_at'] - event['started_at']
                self.assertAlmostEqual(len(audio)/bps, elapsed, delta=.15)
                self.assertGreaterEqual(len(audio), (duration-.15)*bps)
                self.assertLessEqual(len(audio), (duration+.15)*bps+1024)
                self.assertEqual(set(record_evidence([event], 'small')['record_counts']), {1048})

    def test_invalid_pacing_rejected_before_listening(self):
        for ratio in (0, -1, float('nan'), float('inf'), -float('inf'), True, '1.0'):
            with self.subTest(ratio=ratio), self.assertRaises(ValueError):
                RecordServer('127.0.0.1', 0, self.specs, self.keys['cert'], self.keys['key'],
                             seconds=1, grow_seconds=0, pacing_ratio=ratio)

    def test_gate_snapshot_survives_later_server_writes(self):
        with RecordServer('127.0.0.1', 0, self.specs, self.keys['cert'], self.keys['key'], seconds=3, grow_seconds=0) as server:
            context = ssl.create_default_context(cafile=str(self.keys['ca']))
            with socket.create_connection(('127.0.0.1', server.server.server_address[1]), timeout=5) as plain:
                with context.wrap_socket(plain, server_hostname='127.0.0.1') as secure:
                    secure.sendall(b'GET /small/fixture HTTP/1.1\r\nHost: localhost\r\n\r\n')
                    deadline = time.perf_counter()+2
                    while True:
                        self.assertTrue(secure.recv(4096))
                        snapshot = capture_record_observation(server.events)
                        try:
                            evidence = record_evidence(snapshot['events'], 'small')
                            break
                        except AssertionError:
                            self.assertLess(time.perf_counter(), deadline)
                    count = len(snapshot['events'][0]['records'])
                    while len(server.events[0]['records']) <= count:
                        self.assertTrue(secure.recv(4096))
                        self.assertLess(time.perf_counter(), deadline)
            self.assertGreater(len(server.events[0]['records']), count)
            self.assertEqual(len(snapshot['events'][0]['records']), count)
            self.assertEqual(record_evidence(snapshot['events'], 'small'), evidence)

    def test_key_generation_never_overwrites(self):
        before = self.keys['key'].read_bytes()
        with self.assertRaises(FileExistsError):
            generate('127.0.0.1', self.keys['key'].parent)
        self.assertEqual(self.keys['key'].read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
