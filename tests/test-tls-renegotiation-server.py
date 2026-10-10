"""Real certificate-verified TLS 1.2 renegotiation and exact audio continuity."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import ssl
import sys
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.record_test_ca import generate
from audio_test_server.tls_renegotiation import RenegotiationServer,backend_versions


class RenegotiationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='yoradio-renegotiation-')
        cls.keys=generate('127.0.0.1',Path(cls.tmp.name)/'certs')
        cls.data=bytes(range(256))*64
        cls.spec=dict(codec='aac',data=cls.data,seconds=.2,sha256=hashlib.sha256(cls.data).hexdigest())
        print(json.dumps(backend_versions()),flush=True)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def transfer(self,*,refuse=False):
        with RenegotiationServer('127.0.0.1',0,dict(fixture=self.spec),self.keys['cert'],self.keys['key'],
                                 seconds=1.5,grow_seconds=0,renegotiate_seconds=.35,pacing_ratio=1.0) as server:
            ctx=ssl.create_default_context(cafile=str(self.keys['ca']))
            if refuse:ctx.options|=ssl.OP_NO_RENEGOTIATION
            received=bytearray()
            with socket.create_connection(server.server.server_address,timeout=5) as plain:
                with ctx.wrap_socket(plain,server_hostname='127.0.0.1',suppress_ragged_eofs=False) as secure:
                    secure.sendall(b'GET /small/fixture HTTP/1.1\r\nHost: localhost\r\n\r\n')
                    try:
                        while chunk:=secure.recv(32768):received.extend(chunk)
                    except ssl.SSLError:
                        if not refuse:raise
            limit=time.perf_counter()+2
            while 'ended_at' not in server.events[0] and time.perf_counter()<limit:time.sleep(.005)
            event=copy.deepcopy(server.events[0])
        return bytes(received),event

    def test_completed_full_handshake_and_exact_audio(self):
        received,event=self.transfer()
        print(json.dumps({k:event[k] for k in ('handshake_callbacks','renegotiation_requests','renegotiation_completions')}) ,flush=True)
        header,audio=received.split(b'\r\n\r\n',1)
        self.assertIn(b'200 OK',header)
        self.assertEqual(audio,(self.data*(len(audio)//len(self.data)+1))[:len(audio)])
        self.assertTrue(event['complete'])
        self.assertNotIn('error',event)
        completed=[h for h in event['handshake_callbacks'] if not h['pending']]
        self.assertEqual([h['renegotiations'] for h in completed],[0,1])
        self.assertTrue(any(h['pending'] for h in event['handshake_callbacks']))
        self.assertEqual(len(event['renegotiation_requests']),1)
        self.assertEqual(len(event['renegotiation_completions']),1)
        self.assertEqual(event['renegotiation_completions'][0]['after'],1)
        self.assertFalse(event['renegotiation_completions'][0]['pending'])
        done=event['renegotiation_completions'][0]['at']
        self.assertTrue(any(w['phase']=='body-small' and w['at']>done for w in event['writes']))
        self.assertEqual(event['audio_bytes'],len(audio))
        self.assertFalse(event['session_cache_enabled'])
        self.assertFalse(event['session_tickets_enabled'])
        self.assertEqual(event['version'],'TLSv1.2')
        self.assertTrue(any(r['type']==21 for r in event['records'] if r['phase']=='close'))

    def test_refusal_cannot_count_as_completion(self):
        _,event=self.transfer(refuse=True)
        self.assertFalse(event['complete'])
        self.assertIn('error',event)
        self.assertEqual(len(event['renegotiation_requests']),1)
        self.assertEqual(len([h for h in event['handshake_callbacks'] if not h['pending']]),1)
        self.assertEqual(event['renegotiation_completions'],[])


if __name__=='__main__':unittest.main()
