"""OTA action timing must preserve failures without logging response secrets."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
import ota


class Report:
    def __init__(self):
        self.data = {}
        self.saved = []

    def save(self):
        self.saved.append(copy.deepcopy(self.data))


class Tests(unittest.TestCase):
    def test_boundaries_saved_before_and_after_action_without_return_data(self):
        report = Report()
        response = (200, b'private-response')
        calls = []
        def operation():
            self.assertEqual(len(report.saved), 1)
            self.assertEqual(report.saved[0]['timeline'][0]['event'], 'begin')
            calls.append(True)
            return response
        with patch.object(ota.time, 'monotonic', side_effect=[1.5, 3.0]):
            self.assertIs(ota.timed_action(report, 'ota:while-playing:upload', operation), response)
        self.assertEqual(calls, [True])
        self.assertEqual([r['at'] for r in report.data['timeline']], [1.5, 3.0])
        self.assertEqual([r['event'] for r in report.data['timeline']], ['begin', 'returned'])
        self.assertEqual(len(report.saved), 2)
        self.assertNotIn('private-response', str(report.saved))

    def test_transport_exception_is_preserved_without_retry_or_message(self):
        report = Report()
        error = OSError('private-url-and-credentials')
        calls = []
        def fail():
            calls.append(True)
            raise error
        with self.assertRaises(OSError) as raised:
            ota.timed_action(report, 'restore-saved-station:reboot-request', fail)
        self.assertIs(raised.exception, error)
        self.assertEqual(calls, [True])
        self.assertEqual(report.saved[-1]['timeline'][-1]['exception'], 'OSError')
        self.assertEqual(report.saved[-1]['timeline'][-1]['event'], 'raised')
        self.assertNotIn('private-url', str(report.saved))

    def test_interruption_is_not_recorded_as_success(self):
        report = Report()
        def interrupt():
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            ota.timed_action(report, 'ota:slow:upload', interrupt)
        self.assertEqual(report.saved[-1]['timeline'][-1]['event'], 'raised')

    def test_http_rejection_is_returned_not_marked_as_pass(self):
        report = Report()
        self.assertEqual(ota.timed_action(report, 'ota:wrong-chip:upload',
                                        lambda: (400, b'error')), (400, b'error'))
        self.assertNotIn('PASS', str(report.saved))


if __name__ == '__main__':
    unittest.main()
