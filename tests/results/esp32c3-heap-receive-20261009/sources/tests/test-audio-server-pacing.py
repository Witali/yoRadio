"""Exercise actual HTTP routes with deterministic delivery time and exact bytes."""
from pathlib import Path
import sys
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audio_test_server.server import Server, DeliveryStats


class Clock:
    def __init__(self, stop_at=float('inf')):
        self.now = 100.
        self.stop_at = stop_at
        self.stopped = threading.Event()

    def monotonic(self):
        return self.now

    def wait(self, seconds):
        self.now += seconds
        if self.now >= self.stop_at:
            self.set()
        return self.is_set()

    def is_set(self):
        return self.stopped.is_set()

    def set(self):
        self.stopped.set()


class PacingTests(unittest.TestCase):
    def fetch(self, mode='file', ratio=None, unpaced=False, segments=False):
        # Two segments have different encoded rates, exposing an implementation
        # that accidentally uses the aggregate duration for every segment.
        data = bytes(range(256)) * 12
        spec = dict(data=data, seconds=3., codec='aac', mime='audio/aac')
        if segments:
            spec['segments'] = [dict(data=data[:1024], seconds=2.),
                                dict(data=data[1024:], seconds=1.)]
        kwargs = {} if ratio is None else dict(pacing_ratio=ratio)
        clock = Clock(stop_at=106. if mode == 'stream' else float('inf'))
        completed = threading.Event()
        original_finish = DeliveryStats.finish

        def finish(stats, ended):
            original_finish(stats, ended)
            completed.set()

        # Patch only this module's clock; the HTTP server/client keep real time.
        with patch('audio_test_server.server.time', SimpleNamespace(monotonic=clock.monotonic)), \
             patch.object(DeliveryStats, 'finish', finish):
            with Server('127.0.0.1', 0, {'sample': spec}, unpaced_files=unpaced,
                        delivery_stats=True, **kwargs) as server:
                server.closed = clock
                with urlopen(f'http://127.0.0.1:{server.http.server_port}/{mode}/sample', timeout=5) as response:
                    received = response.read()
                # Content-Length lets read() return before the final pacing
                # wait; observe handler completion before stopping the server.
                self.assertTrue(completed.wait(2), 'Handler did not finish')
            event = server.events[0]
        self.assertEqual(sum(w['bytes'] for w in event['delivery']['windows']), len(received))
        return received, event, clock.now - 100, data

    def test_default_preserved_and_both_rate_directions(self):
        for ratio in (None, .5, 1., 2.):
            with self.subTest(ratio=ratio):
                received, event, elapsed, data = self.fetch(ratio=ratio)
                effective = 1.02 if ratio is None else ratio
                self.assertEqual(received, data)
                self.assertEqual(event['pacing_ratio'], effective)
                self.assertAlmostEqual(elapsed, 3 / effective)

    def test_each_transition_segment_uses_its_own_duration(self):
        received, event, elapsed, data = self.fetch(ratio=2., segments=True)
        self.assertEqual(received, data)
        self.assertAlmostEqual(elapsed, 1.5)

    def test_unpaced_file_ignores_rate_but_live_stream_stays_paced(self):
        received, event, elapsed, data = self.fetch(ratio=.5, unpaced=True)
        self.assertEqual(received, data)
        self.assertIsNone(event['pacing_ratio'])
        self.assertEqual(elapsed, 0)
        received, event, elapsed, data = self.fetch('stream', ratio=1., unpaced=True)
        self.assertEqual(received, data * 2)
        self.assertEqual(event['pacing_ratio'], 1.)
        self.assertEqual(elapsed, 6.)

    def test_invalid_ratios_rejected_before_listening(self):
        for ratio in (0, -1, float('nan'), float('inf'), -float('inf'), True, '1'):
            with self.subTest(ratio=ratio), self.assertRaises(ValueError):
                Server('127.0.0.1', 0, {}, pacing_ratio=ratio)


if __name__ == '__main__':
    unittest.main()
