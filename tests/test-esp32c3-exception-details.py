"""Transport failures keep useful OS codes while excluding private text."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import exception_details
from run import Suite


class ExceptionDetailsTests(unittest.TestCase):
    def test_urlerror_retains_nested_os_code_only(self):
        error = URLError(ConnectionRefusedError(10061, 'private URL and password'))
        self.assertEqual(exception_details(error), [
            {'type': 'URLError'}, {'type': 'ConnectionRefusedError', 'errno': 10061}])

    def test_text_reason_is_not_saved(self):
        self.assertEqual(exception_details(URLError('private hostname')), [{'type': 'URLError'}])

    def test_cycle_is_bounded(self):
        a, b = RuntimeError('a'), TimeoutError('b')
        a.__cause__, b.__context__ = b, a
        self.assertEqual(exception_details(a), [{'type': 'RuntimeError'}, {'type': 'TimeoutError'}])

    def test_codes_must_be_integers(self):
        error = OSError('private')
        error.errno, error.winerror = 'private', 10060
        self.assertEqual(exception_details(error), [{'type': 'OSError', 'winerror': 10060}])

    def test_observation_retains_failure_and_reraises(self):
        class Board:
            def status(self):
                raise URLError(TimeoutError(10060, 'secret'))
        with tempfile.TemporaryDirectory() as directory:
            suite = Suite(Board(), '', {}, None, directory)
            with self.assertRaises(URLError): suite.observe(1, 'case')
            saved = json.loads((Path(directory)/'status.json').read_text())
            self.assertEqual(saved[0]['samples'], [])
            self.assertEqual(saved[0]['interrupted'], 'URLError')
            self.assertEqual(saved[0]['exception_chain'][-1]['errno'], 10060)
            self.assertNotIn('secret', json.dumps(saved))


if __name__ == '__main__': unittest.main()
