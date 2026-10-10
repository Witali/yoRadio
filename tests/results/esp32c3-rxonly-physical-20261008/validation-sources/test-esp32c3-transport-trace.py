"""Tracing must preserve transport behavior and omit all private contents."""
import http.client
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from trace_transport import TransportTrace


class FakeConnection:
    failure = None

    def __init__(self, host, timeout=5):
        self.host, self.timeout = host, timeout
        self.sock = Mock()
        self.sock.getsockname.return_value = ('127.0.0.1', 54321)
        self.connect_calls = 0

    def connect(self):
        self.connect_calls += 1
        if self.failure:
            raise self.failure

    def request(self, *args, **kwargs):
        self.forwarded = args, kwargs
        self.connect()

    def getresponse(self):
        return Mock(read=Mock(return_value=b'private-response'))


class TransportTraceTests(unittest.TestCase):
    def test_request_response_timeout_and_private_contents(self):
        output = io.StringIO()
        with patch.object(http.client, 'HTTPConnection', FakeConnection):
            with TransportTrace('board.test', output) as trace:
                connection = http.client.HTTPConnection('board.test', timeout=3)
                args = ('POST', '/private-path?secret=value')
                kwargs = dict(body=b'private-password', headers={'Authorization': 'private-token'})
                connection.request(*args, **kwargs)
                self.assertEqual(connection.forwarded, (args, kwargs))
                self.assertEqual(connection.getresponse().read(), b'private-response')
                self.assertEqual(connection.timeout, 3)
                self.assertEqual(connection.connect_calls, 1)
                self.assertEqual(trace.connections, 1)
            self.assertIs(http.client.HTTPConnection, FakeConnection)
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r['phase'] for r in rows],
                         ['connect', 'request_including_connect', 'response_headers', 'response_body'])
        self.assertEqual(rows[0]['local_port'], 54321)
        self.assertNotIn('private', output.getvalue())
        self.assertNotIn('secret', output.getvalue())
        self.assertTrue(all(r['result'] == 'PASS' for r in rows))

    def test_failed_connect_preserves_exception_without_retry_or_message(self):
        output = io.StringIO()
        failure = OSError(10048, 'private-server-detail')
        with patch.object(http.client, 'HTTPConnection', FakeConnection), \
             patch.object(FakeConnection, 'failure', failure):
            with self.assertRaises(OSError) as raised:
                with TransportTrace('board.test', output):
                    connection = http.client.HTTPConnection('board.test')
                    connection.request('GET', '/private-path')
            self.assertIs(http.client.HTTPConnection, FakeConnection)
        self.assertIs(raised.exception, failure)
        self.assertEqual(connection.connect_calls, 1)
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r['errno'] == 10048 and r['result'] == 'FAIL' for r in rows))
        self.assertNotIn('private', output.getvalue())

    def test_other_hosts_are_not_recorded(self):
        output = io.StringIO()
        with patch.object(http.client, 'HTTPConnection', FakeConnection):
            with TransportTrace('board.test', output) as trace:
                connection = http.client.HTTPConnection('unrelated.test')
                connection.request('GET', '/private-path')
                self.assertEqual(connection.getresponse().read(), b'private-response')
                self.assertEqual(trace.connections, 0)
        self.assertEqual(output.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
