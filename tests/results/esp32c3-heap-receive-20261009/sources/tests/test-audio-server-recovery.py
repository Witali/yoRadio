"""Prove the shared recovery fixture counts requests and preserves file bytes."""
import sys
from pathlib import Path
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from audio_test_server.server import Server


class RecoveryServer(unittest.TestCase):
    def test_failures_then_exact_file_per_fixture(self):
        specs = {name: dict(data=bytes(range(256))*3, seconds=.01, codec='flac', mime='audio/flac')
                 for name in ('first', 'second')}
        with Server('127.0.0.1', 0, specs, initial_failures=2, unpaced_files=True) as server:
            origin = 'http://127.0.0.1:'+str(server.http.server_port)
            for name in specs:
                for _ in range(2):
                    with self.assertRaises(HTTPError) as error:
                        urlopen(origin+'/recover/'+name)
                    self.assertEqual(error.exception.code, 503)
                    self.assertEqual(error.exception.read(), b'')
                    error.exception.close()
                for _ in range(2):
                    with urlopen(origin+'/recover/'+name) as response:
                        self.assertEqual(response.read(), specs[name]['data'])
            with urlopen(origin+'/file/first') as response:
                self.assertEqual(response.read(), specs['first']['data'])
        for name in specs:
            rows = [e for e in server.events if e['mode']=='recover' and e['fixture']==name]
            self.assertEqual([e['attempt'] for e in rows], [1,2,3,4])
            self.assertEqual([e['response_status'] for e in rows], [503,503,200,200])
        self.assertEqual(server.events[-1]['mode'], 'file')

    def test_invalid_failure_count(self):
        for value in (-1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Server('127.0.0.1', 0, {}, initial_failures=value)


if __name__ == '__main__':
    unittest.main()
