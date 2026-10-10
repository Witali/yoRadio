"""Reject unlabelled lab trust, partial TLS evidence and unexpected retries."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure,sha
from aac_growth import transport_config,check_tls_delivery

CONFIG='\n'.join(('CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y',
    'CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL=y',
    'CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN=16384'))


class TransportTests(unittest.TestCase):
    def test_http_and_complete_explicit_lab_trust(self):
        self.assertEqual(transport_config('',{},None,None,None),'http')
        ca=Mock(read_bytes=Mock(return_value=b'test-ca'))
        file=Mock(is_file=Mock(return_value=True))
        manifest=dict(laboratory_only=True,extra_trust_ca_sha256=sha(b'test-ca'))
        self.assertEqual(transport_config(CONFIG,manifest,ca,file,file),'https')
        for key in manifest:
            with self.assertRaises(Failure):transport_config(CONFIG,dict(manifest,**{key:None}),ca,file,file)
        for line in CONFIG.splitlines():
            with self.assertRaises(Failure):transport_config(CONFIG.replace(line,''),manifest,ca,file,file)
        for params in ((ca,None,None),(None,file,file),(ca,file,None)):
            with self.assertRaises(Failure):transport_config(CONFIG,manifest,*params)
        with self.assertRaises(Failure):
            transport_config(CONFIG,manifest,ca,file,Mock(is_file=Mock(return_value=False)))

    def test_full_encrypted_delivery_not_just_successful_connection(self):
        specs={'a':dict(data=b'0123'),'b':dict(data=b'56789')}
        events=[dict(fixture=n,complete=True,tls_version='TLSv1.2',tls_cipher='cipher',sent=len(s['data']))
                for n,s in specs.items()]
        self.assertEqual(check_tls_delivery(events,specs),dict(transfers=2))
        for change in ({'complete':False},{'tls_version':None},{'tls_cipher':None},
                       {'sent':3},{'fixture':'unknown'}):
            with self.assertRaises(Failure):check_tls_delivery([dict(events[0],**change),events[1]],specs)
        for bad in (events[:1],events+events[:1],[events[0],events[0]]):
            with self.assertRaises(Failure):check_tls_delivery(bad,specs)


if __name__=='__main__':unittest.main()
