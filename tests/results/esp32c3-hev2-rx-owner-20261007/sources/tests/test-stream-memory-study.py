"""Check incomplete capture handling and advisory CPU without hiding faults."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import Failure, check_cpu
from run import Suite
from stream_memory_study import Checkpoint
from summarize_sustained import window


class Clock:
    def __init__(self): self.now = 0
    def monotonic(self): return self.now
    def sleep(self, seconds): self.now += seconds


class MemoryStudy(unittest.TestCase):
    def setUp(self):
        (ROOT/'.build').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='stream-memory-test-', dir=ROOT/'.build')
        self.output = Path(self.temp.name)
        self.assertEqual(self.output.resolve().parent, (ROOT/'.build').resolve())
        self.addCleanup(self.temp.cleanup)

    def test_checkpoint_is_incomplete_throttled_and_does_not_mutate(self):
        clock = Clock()
        capture = SimpleNamespace(rows=[dict(at=0, line='PERF test')])
        checkpoint = Checkpoint(self.output, capture, seconds=30, clock=clock.monotonic)
        batch = dict(case='load:test', started_at=0, samples=[dict(seconds=0)])
        checkpoint([], batch)
        before = (self.output/'status.json').read_bytes()
        self.assertNotIn('in_progress', batch)
        saved = json.loads(before)[0]
        self.assertTrue(saved['in_progress'])
        self.assertNotIn('ended_at', saved)
        self.assertFalse(json.loads((self.output/'checkpoint.json').read_text())['complete'])
        batch['samples'].append(dict(seconds=1))
        clock.now = 1
        checkpoint([], batch)
        self.assertEqual((self.output/'status.json').read_bytes(), before)
        clock.now = 30
        checkpoint([], batch)
        self.assertEqual(len(json.loads((self.output/'status.json').read_text())[0]['samples']), 2)
        self.assertFalse(list(self.output.glob('*.tmp')))

    def test_finished_observation_replaces_partial_checkpoint(self):
        clock = Clock()
        board = SimpleNamespace(status=lambda: dict(audio=True))
        capture = SimpleNamespace(rows=[])
        suite = Suite(board, 'http://unused.invalid', {}, capture, self.output,
                      checkpoint=Checkpoint(self.output, capture, seconds=.3, clock=clock.monotonic))
        with patch('run.time', clock):
            result = suite.observe(1, 'load:test', interval=.4)
        saved = json.loads((self.output/'status.json').read_text())[0]
        self.assertEqual(len(result), 3)
        self.assertIn('ended_at', saved)
        self.assertNotIn('in_progress', saved)
        self.assertEqual(saved['samples'], result)

    def test_advisory_cpu_keeps_memory_and_progress_gates(self):
        rows = []
        for at in (5, 10, 15):
            rows += [dict(at=at, line='PERF CPU: busy=98.0% idle=2.0% heap=22000 largest=10000'),
                     dict(at=at, line='PERF AAC: window 5000 ms, audio 5000 ms, decode 4000 ms')]
        self.assertEqual(check_cpu(rows, max_busy=None)['peak_busy'], 98)
        with self.assertRaisesRegex(Failure, 'CPU budget exceeded'):
            check_cpu(rows)
        self.assertEqual(window(rows, 0, 20)['strict']['result'], 'FAIL')
        self.assertEqual(window(rows, 0, 20, max_busy=None)['strict']['result'], 'PASS')
        for old, new in [('heap=22000', 'heap=1000'), ('audio 5000', 'audio 100'),
                         ('largest=10000', 'largest=1000')]:
            with self.subTest(old=old), self.assertRaises(Failure):
                check_cpu([dict(row, line=row['line'].replace(old, new)) for row in rows], max_busy=None)
        with self.assertRaises(Failure):
            check_cpu([], max_busy=None)


if __name__ == '__main__':
    unittest.main()
