"""Verify exact bytes/boundaries, catch-up, interruption and real HTTP(S)."""
import argparse
from pathlib import Path
import ssl
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.server import DeliveryPauses, DeliveryStats, Server, pause_argument
from audio_test_server.record_test_ca import generate


class Clock:
    def __init__(self, stop_at=float('inf')):
        self.now, self.stop_at = 100., stop_at
        self.stopped = threading.Event()
    def monotonic(self): return self.now
    def is_set(self): return self.stopped.is_set()
    def set(self): self.stopped.set()
    def wait(self, seconds):
        self.now += seconds
        if self.now >= self.stop_at: self.set()
        return self.is_set()


class PauseTests(unittest.TestCase):
    def test_validation_before_socket_creation(self):
        bad = (None, [(0, 0)], [(0, -1)], [(0, float('nan'))], [(0, float('inf'))],
               [(True, .1)], [(0, True)], [(-1, .1)], [(2**63, .1)], [(1., .1)],
               [(0, .1), (0, .2)], [(2, .1), (1, .1)], [(0, 2.1)], [(1,)],
               [(i, .1) for i in range(65)])
        for schedule in bad:
            with self.subTest(schedule=schedule), self.assertRaises(ValueError):
                Server('127.0.0.1', 0, {}, delivery_pauses=schedule)
        for size in (0, 1023, 1048577, True, 4096.):
            with self.subTest(size=size), self.assertRaises(ValueError):
                Server('127.0.0.1', 0, {}, send_buffer_bytes=size)
        self.assertEqual(pause_argument('1001:0.05'), (1001, .05))
        for arg in ('x:1', '1:nan', '-1:.1', '1:0', '1:2:3'):
            with self.subTest(arg=arg), self.assertRaises(argparse.ArgumentTypeError):
                pause_argument(arg)

    def fetch_fake(self, schedule, *, unpaced=False, segments=False, stream=False):
        data = bytes(range(256))*16
        spec = dict(data=data, seconds=4., codec='aac', mime='audio/aac')
        if segments:
            spec['segments'] = [dict(data=data[:1500], seconds=1.), dict(data=data[1500:], seconds=3.)]
        clock = Clock(stop_at=108. if stream else float('inf'))
        finished = threading.Event()
        original = DeliveryStats.finish
        writes = []
        original_write = DeliveryStats.write
        def finish(stats, ended):
            original(stats, ended); finished.set()
        def write(stats, size, *args):
            writes.append(size); return original_write(stats, size, *args)
        with patch('audio_test_server.server.time', SimpleNamespace(monotonic=clock.monotonic)), \
             patch('audio_test_server.server.perf_counter', clock.monotonic), \
             patch.object(DeliveryStats, 'finish', finish), patch.object(DeliveryStats, 'write', write):
            with Server('127.0.0.1', 0, {'sample':spec}, delivery_pauses=schedule,
                        unpaced_files=unpaced, pacing_ratio=1., delivery_stats=True) as server:
                server.closed = clock
                route = 'stream' if stream else 'file'
                with urlopen(f'http://127.0.0.1:{server.http.server_port}/{route}/sample', timeout=3) as response:
                    received = response.read()
                self.assertTrue(finished.wait(2))
            event = server.events[0]
        cumulative, total = {0}, 0
        for size in writes:
            total += size; cumulative.add(total)
        for row in event.get('pauses', []):
            self.assertIn(row['after_bytes'], cumulative)
            self.assertTrue(row['completed'])
            self.assertAlmostEqual(row['elapsed_seconds'], row['requested_seconds'])
        self.assertEqual(received, (data*3)[:len(received)])
        self.assertEqual(event['sent'], len(received))
        self.assertEqual(sum(w['bytes'] for w in event['delivery']['windows']), len(received))
        return event, clock.now-100

    def test_exact_unaligned_boundaries_and_pacing_catches_up(self):
        schedule = [(0,.2), (1024,.1), (1501,.3), (2200,.2)]
        for segments in (False, True):
            with self.subTest(segments=segments):
                event, elapsed = self.fetch_fake(schedule, segments=segments)
                self.assertEqual([r['after_bytes'] for r in event['pauses']], [n for n,_ in schedule])
                self.assertAlmostEqual(elapsed, 4.)
                self.assertTrue(event['complete'])

    def test_unpaced_resume_and_future_pause_is_not_fabricated(self):
        event, elapsed = self.fetch_fake([(7,.1), (3079,.2), (4096,.5)], unpaced=True)
        self.assertAlmostEqual(elapsed, .3)
        self.assertEqual(len(event['pause_schedule']), 3)
        self.assertEqual([r['after_bytes'] for r in event['pauses']], [7,3079])

    def test_repeated_stream_uses_cumulative_byte_positions(self):
        event, elapsed = self.fetch_fake([(4099,.15), (7000,.1)], stream=True)
        self.assertEqual([r['after_bytes'] for r in event['pauses']], [4099,7000])
        self.assertEqual(event['sent'], 8192)
        self.assertAlmostEqual(elapsed, 8.)

    def test_stop_interrupts_pause_without_waiting_full_duration(self):
        closed = threading.Event(); event = {}
        pauses = DeliveryPauses(((0,2.),), closed, event)
        timer = threading.Timer(.04, closed.set); timer.start()
        started = time.perf_counter()
        try: self.assertEqual(pauses.next_size(0,1024), 0)
        finally: timer.join()
        self.assertLess(time.perf_counter()-started, .5)
        self.assertFalse(event['pauses'][0]['completed'])
        with self.assertRaises(ValueError):
            DeliveryPauses(((5,.1),), threading.Event(), {}).next_size(6,100)

    def test_real_http_https_exact_body_and_socket_buffer(self):
        data = bytes(range(256))*24
        specs = {'sample':dict(data=data,seconds=.1,codec='flac',mime='audio/flac')}
        with tempfile.TemporaryDirectory(prefix='yoradio-pauses-') as temp:
            keys = generate('127.0.0.1', Path(temp)/'keys')
            for secure in (False, True):
                with self.subTest(secure=secure):
                    cert, key = (keys['cert'], keys['key']) if secure else (None, None)
                    with Server('127.0.0.1', 0, specs, cert, key, unpaced_files=True,
                                delivery_pauses=[(1025,.05),(3073,.05)], send_buffer_bytes=4096) as server:
                        context = ssl.create_default_context(cafile=str(keys['ca'])) if secure else None
                        scheme = 'https' if secure else 'http'
                        with urlopen(f'{scheme}://127.0.0.1:{server.http.server_port}/file/sample', context=context, timeout=3) as response:
                            self.assertEqual(response.read(), data)
                        event = server.events[0]
                        self.assertEqual(event['sent'], len(data))
                        self.assertEqual(event['send_buffer_requested'], 4096)
                        self.assertGreater(event['send_buffer_actual'], 0)
                        self.assertEqual([r['after_bytes'] for r in event['pauses']], [1025,3073])
                        self.assertTrue(all(r['completed'] and r['elapsed_seconds'] >= .045 for r in event['pauses']))


if __name__ == '__main__': unittest.main()
