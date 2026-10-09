"""Exact EOF gates apply equally to HTTP and HTTPS, without hiding timeouts."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
import run
from common import Failure


PLAYING=dict(audio=True,pcm_sample_rate=48000,pcm_channels=2,format='HE-AAC 48 kHz stereo')
STOPPED=dict(audio=False,pcm_sample_rate=0,pcm_channels=0,format='stream ended')


class WebSocket:
    def __init__(self, *, playing=False):self.playing=playing
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def send(self,message):assert message=='getindex'
    def recv(self,timeout):
        return json.dumps(dict(payload=[dict(id='fmt',value='stream ended'),
            dict(id='playerwrap',value='playing' if self.playing else 'stopped')]))


class EofTests(unittest.TestCase):
    def setUp(self):
        # observe() is stubbed below, so no evidence files are written.
        self.folder=Path(__file__).resolve().parent
        self.board=Mock()
        self.board.websocket.side_effect=lambda:WebSocket()
        self.suite=run.Suite(self.board,'http://fixture.test:8770',
            {'he':dict(seconds=12)},Mock(),self.folder)
        self.suite.observe=Mock(side_effect=[[PLAYING],[PLAYING,STOPPED,STOPPED]])

    def invoke(self,origin=None):
        with patch.object(run.time,'sleep'):
            return self.suite.eof('he','aac',origin)

    def test_default_http_and_https_origin_preserve_eof_checks(self):
        for origin,expected in ((None,'http://fixture.test:8770/file/he'),
                                ('https://fixture.test:8771','https://fixture.test:8771/file/he')):
            with self.subTest(origin=origin):
                self.suite.observe.side_effect=[[PLAYING],[PLAYING,STOPPED,STOPPED]]
                result=self.invoke(origin)
                self.board.play.assert_called_with(expected,'aac')
                self.assertEqual(result['terminal_samples'],2)
                self.assertTrue(result['websocket_stopped'])

    def test_interrupted_observation_is_not_retried_or_accepted(self):
        error=URLError(TimeoutError())
        self.suite.observe.side_effect=[[PLAYING],error]
        with self.assertRaises(URLError) as raised:self.invoke('https://fixture.test:8771')
        self.assertIs(raised.exception,error)
        self.assertEqual(self.suite.observe.call_count,2)
        self.board.websocket.assert_not_called()
        self.assertEqual(self.board.stop.call_count,2)

    def test_stale_pcm_after_stop_fails(self):
        self.suite.observe.side_effect=[[PLAYING],[STOPPED,dict(STOPPED,pcm_sample_rate=48000)]]
        with self.assertRaises(Failure):self.invoke('https://fixture.test:8771')

    def test_late_playing_state_fails(self):
        self.suite.observe.side_effect=[[PLAYING],[STOPPED,PLAYING]]
        with self.assertRaises(Failure):self.invoke('https://fixture.test:8771')

    def test_single_stopped_sample_is_insufficient(self):
        self.suite.observe.side_effect=[[PLAYING],[PLAYING,STOPPED]]
        with self.assertRaises(Failure):self.invoke()

    def test_missing_decoded_playback_fails(self):
        self.suite.observe.side_effect=[[dict(PLAYING,pcm_sample_rate=0)]]
        with self.assertRaises(Failure):self.invoke()

    def test_websocket_still_playing_fails(self):
        self.board.websocket.side_effect=lambda:WebSocket(playing=True)
        with self.assertRaises(Failure):self.invoke('https://fixture.test:8771')

    def test_https_cli_rejects_missing_or_http_origin_before_board_access(self):
        for extra in ([],['--https-origin','http://fixture.test']):
            args=['run.py','--board','http://board.test','--host','127.0.0.1',
                '--suite','eof','--eof-protocol','https','--output',str(self.folder),*extra]
            with self.subTest(extra=extra),patch.object(sys,'argv',args),patch.object(run,'Board') as board:
                with self.assertRaises(Failure):run.main()
                board.assert_not_called()


if __name__=='__main__':unittest.main()
