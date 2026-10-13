"""Keep trial boundaries and fault evidence in the DMA diagnosis."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from common import Failure
from decoder_arena_flac_review import review


class Review(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parents[1] / '.build'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch, prefix='arena-review-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'candidate').mkdir()
        batches, health = [], []
        for trial in (1, 2):
            for suffix, counts in (('', (10, 13)), (':eof', (13, 500))):
                batches.append(dict(case=f'flac-level8:trial-{trial}' + suffix,
                    started_at=0, ended_at=10, samples=[dict(seconds=t, rssi=-60) for t in (3, 6)]))
                for count in counts:
                    health.append(dict(boot_id='same', uptime_ms=(len(health)+1)*1000,
                        heap=40000, largest=16000, allocation_failures=3, task_watchdog_events=0,
                        output=dict(available=True, completion_queue_drops=count, write_errors=0)))
        for name, data in (('candidate/status.json', batches), ('candidate-health.json', health),
                           ('candidate-arena.json', [None]*len(health)), ('server.json', [])):
            self.write(name, data)

    def write(self, name, data):
        (self.root / name).write_text(json.dumps(data))

    def test_trials_exclude_eof_and_keep_faults(self):
        data = review(self.root, 'candidate')
        self.assertEqual(len(data['cases']), 2)
        for case in data['cases'].values():
            self.assertEqual(case['output']['completion_queue_drops'], 3)
            self.assertEqual(case['faults']['allocation_failures'], [3, 3])
        self.assertEqual(len(data['input_sha256']), 4)

    def test_missing_pair_fails(self):
        self.write('candidate-arena.json', [None])
        with self.assertRaises(Failure): review(self.root, 'candidate')

    def test_duplicate_trial_fails(self):
        path = self.root / 'candidate/status.json'
        batches = json.loads(path.read_text())
        batches[2]['case'] = batches[0]['case']
        self.write('candidate/status.json', batches)
        with self.assertRaises(Failure): review(self.root, 'candidate')


if __name__ == '__main__': unittest.main()
