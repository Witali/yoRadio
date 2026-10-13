import hashlib
from pathlib import Path
import sys
import time
import unittest
from urllib.request import Request,urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.relay import AudioRelay
from audio_test_server.server import Server
from audio_test_server.icy import IcyFramer


class RelayTests(unittest.TestCase):
    def test_invalid_configuration(self):
        for url in ('ftp://localhost/x','http://user:pass@localhost/x','http://localhost/x?a=b'):
            with self.assertRaises(ValueError):AudioRelay('127.0.0.1',0,url)

    def test_bytes_headers_negotiation_and_eof(self):
        audio=bytes(range(256))*29
        specs={'sample':dict(data=audio,codec='mp3',mime='audio/mpeg',seconds=.1)}
        with Server('127.0.0.1',0,specs,unpaced_files=True,icy_interval=1023) as upstream:
            source=f'http://127.0.0.1:{upstream.http.server_port}/file/sample'
            with AudioRelay('127.0.0.1',0,source) as relay:
                for icy in (False,True):
                    request=Request(f'http://127.0.0.1:{relay.http.server_port}/stream',headers={'Icy-MetaData':'1'} if icy else {})
                    with urlopen(request,timeout=5) as response:
                        output=response.read()
                        self.assertEqual(response.headers.get('icy-metaint'),'1023' if icy else None)
                        self.assertIsNone(response.headers.get('Content-Length'))
                    expected=IcyFramer(1023).feed(audio) if icy else audio
                    self.assertEqual(output,expected)
                    deadline=time.perf_counter()+2
                    while not relay.events[-1]['ended'] and time.perf_counter()<deadline:time.sleep(.005)
                    event=relay.events[-1]
                    self.assertEqual(event['termination'],'upstream-eof')
                    self.assertEqual(event['received'],len(expected))
                    self.assertEqual(event['sent'],len(expected))
                    self.assertEqual(event['sent_sha256'],hashlib.sha256(expected).hexdigest())
                    self.assertEqual(event['received_sha256'],event['sent_sha256'])
                    self.assertEqual(sum(w['bytes'] for w in event['delivery']['windows']),len(expected))


if __name__=='__main__':unittest.main()
