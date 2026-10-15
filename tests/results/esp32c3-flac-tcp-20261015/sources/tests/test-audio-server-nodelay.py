"""Check actual socket options and exact HTTP(S) bytes with both Nagle policies."""
from pathlib import Path
import ssl
import sys
import tempfile
import time
import unittest
from urllib.request import urlopen

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.server import Server
from audio_test_server.record_test_ca import generate


class NodelayTests(unittest.TestCase):
    def test_invalid_policy_rejected(self):
        for value in (0,1,'true',[],{},.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Server('127.0.0.1',0,{},tcp_nodelay=value)

    def test_http_https_payload_pauses_and_observed_policy(self):
        data=bytes(range(256))*24
        specs={'sample':dict(data=data,seconds=.04,codec='flac',mime='audio/flac')}
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'keys';generate('127.0.0.1',folder)
            context=ssl.create_default_context(cafile=str(folder/'ca.pem'))
            for tls in (False,True):
                for policy in (None,False,True):
                    with self.subTest(tls=tls,policy=policy):
                        options=dict(cert=str(folder/'server.pem'),key=str(folder/'server.key')) if tls else {}
                        with Server('127.0.0.1',0,specs,unpaced_files=True,delivery_stats=True,
                                    tcp_nodelay=policy,send_buffer_bytes=4096,
                                    delivery_pauses=[(1501,.01)],**options) as server:
                            url=f'{"https" if tls else "http"}://127.0.0.1:{server.http.server_port}/file/sample'
                            with urlopen(url,context=context if tls else None,timeout=5) as response:
                                self.assertEqual(response.read(),data)
                            deadline=time.perf_counter()+2
                            while time.perf_counter()<deadline and not server.events[0]['delivery']['finished']:
                                time.sleep(.005)
                            event=server.events[0]
                        self.assertTrue(event['complete'])
                        self.assertTrue(event['delivery']['finished'])
                        self.assertEqual(event['tcp_nodelay_requested'],policy)
                        self.assertIs(type(event['tcp_nodelay_actual']),bool)
                        if policy is not None:self.assertEqual(event['tcp_nodelay_actual'],policy)
                        self.assertEqual(event['sent'],len(data))
                        self.assertEqual(sum(w['bytes'] for w in event['delivery']['windows']),len(data))
                        self.assertEqual(event['pauses'][0]['after_bytes'],1501)
                        self.assertTrue(event['pauses'][0]['completed'])


if __name__=='__main__':unittest.main()
