"""Public-metadata preservation tools must never download credential material."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from common import Blocked, Failure
from ota import keep_wifi_profiles, snapshot, verify_snapshot, wifi_metadata
from audit_stream_probe import check_preservation


class BoardFixture:
    def __init__(self):
        self.paths = []
        self.updates = []
        self.metadata = {'revision': '0123456789abcdef-0000000000000001', 'profiles': [
            {'id': 'r1', 'ssid': ' duplicate ', 'ssid_utf8': True},
            {'id': 'r2', 'ssid': 'legacy\ufffd', 'ssid_utf8': False}]}
        self.network = 'client'
        self.unsupported = False

    def json(self, path, data=None, timeout=5, *, headers=None):
        self.paths.append(path)
        if path != '/api/native/wifi':
            raise AssertionError('Unexpected metadata route')
        if self.unsupported:
            raise HTTPError('http://synthetic/api/native/wifi', 404, 'unsupported', None, None)
        if data is not None:
            assert headers == {'Content-Type': 'application/json'}
            self.updates.append(json.loads(data))
            return {'saved': True, 'rebooting': True}
        return copy.deepcopy(self.metadata)

    def request(self, path, **kwargs):
        self.paths.append(path)
        if path != '/data/playlist.csv':
            raise AssertionError('Attempt to read a private file')
        return b'synthetic-public-playlist'

    def settings(self):
        return {'getsystem': {'abuff': 1}, 'gettimezone': {'tzh': 1}}

    def status(self):
        return {'network': self.network}


class PublicWiFiToolTest(unittest.TestCase):
    def test_snapshots_ignore_boot_epoch_and_only_claim_public_evidence(self):
        board = BoardFixture()
        before = snapshot(board)
        board.metadata['revision'] = 'fedcba9876543210-0000000000000012'
        result = verify_snapshot(board, before)
        self.assertEqual(result, {'wifi_metadata_unchanged': True, 'wifi_reconnected': True,
            'wifi_verification': 'public-metadata-and-reconnection',
            'playlist_unchanged': True, 'settings_unchanged': True})
        self.assertNotIn('wifi', before)
        self.assertNotIn('wifi_unchanged', result)
        self.assertEqual(set(board.paths), {'/api/native/wifi', '/data/playlist.csv'})

    def test_keep_update_never_reconstructs_password_or_lossy_ssid(self):
        board = BoardFixture()
        keep_wifi_profiles(board)
        self.assertEqual(board.updates, [{'revision': board.metadata['revision'], 'profiles': [
            {'id': 'r1', 'password_action': 'keep'}, {'id': 'r2', 'password_action': 'keep'}]}])
        self.assertEqual(board.paths, ['/api/native/wifi', '/api/native/wifi'])
        self.assertNotIn('password"', json.dumps(board.updates))
        self.assertNotIn('ssid', json.dumps(board.updates))
        board = BoardFixture(); board.metadata['profiles'] = []
        with self.assertRaises(Blocked):
            keep_wifi_profiles(board)
        self.assertFalse(board.updates)

    def test_changed_metadata_and_failed_reconnection_are_not_preservation(self):
        board = BoardFixture()
        before = snapshot(board)
        board.metadata['profiles'][0]['ssid'] = 'changed'
        with self.assertRaises(Failure):
            verify_snapshot(board, before)
        board.metadata['profiles'][0]['ssid'] = ' duplicate '
        board.network = 'ap'
        with self.assertRaises(Failure):
            verify_snapshot(board, before)

    def test_unsupported_and_secret_bearing_metadata_have_no_csv_fallback(self):
        board = BoardFixture(); board.unsupported = True
        with self.assertRaises(Blocked):
            snapshot(board)
        self.assertEqual(board.paths, ['/api/native/wifi'])
        bad_values = []
        value = BoardFixture().metadata; value['password'] = 'SYNTHETIC_OLD_KEY'; bad_values.append(value)
        value = BoardFixture().metadata; value['profiles'][0]['password'] = 'SYNTHETIC_OLD_KEY'; bad_values.append(value)
        value = BoardFixture().metadata; value['profiles'][1]['id'] = 'r1'; bad_values.append(value)
        value = BoardFixture().metadata; value['revision'] = 'x' * 33; bad_values.append(value)
        value = BoardFixture().metadata; value['profiles'][0]['ssid'] = '\u00e9' * 16; bad_values.append(value)
        for value in bad_values:
            board = BoardFixture(); board.metadata = value
            with self.assertRaises(Failure):
                wifi_metadata(board)
            self.assertEqual(board.paths, ['/api/native/wifi'])

    def test_current_and_historical_report_claims_remain_distinct(self):
        historical = dict(wifi_unchanged=True, playlist_unchanged=True, settings_unchanged=True)
        check_preservation(historical)
        current = dict(wifi_verification='public-metadata-and-reconnection', wifi_metadata_unchanged=True,
                       wifi_reconnected=True, playlist_unchanged=True, settings_unchanged=True)
        check_preservation(current)
        for invalid in [dict(current, wifi_reconnected=False),
                        dict(current, wifi_verification='unknown', **historical)]:
            with self.assertRaises(Failure):
                check_preservation(invalid)

    def test_board_json_preserves_content_type_and_verified_https_origin(self):
        from common import Board
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return b'{"saved":true,"rebooting":true}'
        with patch('common.urlopen', return_value=Response()) as request:
            value = Board('https://synthetic.example').json('/api/native/wifi', b'{}',
                headers={'Content-Type': 'application/json'})
            sent = request.call_args.args[0]
            self.assertEqual(sent.full_url, 'https://synthetic.example/api/native/wifi')
            self.assertEqual(sent.get_header('Content-type'), 'application/json')
            self.assertTrue(value['saved'])
            self.assertNotIn('context', request.call_args.kwargs)  # No unverified SSL override.


if __name__ == '__main__':
    unittest.main()
