"""Exercise the acceptance oracles, generic server, and real production wrapper."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import ssl
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
import common
import ota
import compare_latency
import run as acceptance_run
from audio_test_server.server import Server


def state(rate=48000, channels=2, label='AAC PCM 48 kHz stereo', seconds=3):
    return dict(audio=True,pcm_sample_rate=rate,pcm_channels=channels,
                bits_per_sample=16,format=label,seconds=seconds)


class AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = common.fixtures()

    def test_matrix_has_all_firmware_codec_families_and_aac_profiles(self):
        self.assertEqual({s['codec'] for s in self.specs.values()}, {'aac','mp3','flac','vorbis','opus'})
        self.assertEqual({s.get('profile') for s in self.specs.values() if s['codec']=='aac' and 'profile' in s},
                         {'AAC-LC','HE-AAC','HE-AACv2'})
        self.assertEqual(len(self.specs),13)

    def test_core_fallback_and_stale_playback_never_pass(self):
        for spec, samples in [
            (self.specs['he-48000-stereo'],[state(rate=24000)]*8),
            (self.specs['hev2-44100-stereo'],[state(rate=22050,channels=1)]*8),
            (self.specs['lc-48000-stereo'],[state()]*5+[dict(state(),audio=False)]),
            (self.specs['lc-48000-stereo'],[]),
        ]:
            with self.subTest(spec=spec.get('profile')), self.assertRaises(common.Failure):
                common.check_playback(samples,spec)

    def test_valid_mono_and_stereo(self):
        common.check_playback([state()]*6,self.specs['lc-48000-stereo'])
        common.check_playback([state(22050,1,'AAC PCM 22.05 kHz mono')]*6,self.specs['lc-22050-mono'])

    def test_observations_survive_transport_failure_without_exception_details(self):
        board = Mock()
        board.status.side_effect = [{k:v for k,v in state().items() if k != 'seconds'},
                                    TimeoutError('private stream details')]
        with tempfile.TemporaryDirectory() as tmp, patch.object(acceptance_run.time, 'sleep'):
            suite = acceptance_run.Suite(board, 'http://localhost', {}, None, tmp)
            with self.assertRaises(TimeoutError):
                suite.observe(60, 'interrupted-test')
            raw = (Path(tmp)/'status.json').read_text()
            rows = json.loads(raw)
            self.assertEqual(len(rows[0]['samples']), 1)
            self.assertEqual(rows[0]['interrupted'], 'TimeoutError')
            self.assertGreaterEqual(rows[0]['elapsed_seconds'], 0)
            self.assertGreaterEqual(rows[0]['ended_at'], rows[0]['started_at'])
            self.assertGreaterEqual(rows[0]['ended_at'] - rows[0]['started_at'],
                                    rows[0]['samples'][0]['seconds'])
            self.assertNotIn('private stream details', raw)

    def test_long_load_checks_recovery_even_after_playback_failure(self):
        for remaining, recovered in ((16000,True),(8000,False)):
            board = Mock()
            board.info.return_value = {'app_elf_sha256':'test-image'}
            capture = Mock(rows=[])
            suite = Mock()
            suite.sustained.side_effect = common.Failure('injected playback failure')
            suite.idle_heap.side_effect = [[dict(heap=16000,largest=8192,tasks=17)]*2,
                                          [dict(heap=remaining,largest=8192,tasks=17)]*2]
            server = MagicMock()
            server.__enter__.return_value.events = []
            with tempfile.TemporaryDirectory() as tmp, self.subTest(recovered=recovered), \
                 patch.object(acceptance_run,'Board',return_value=board), \
                 patch.object(acceptance_run,'Capture',return_value=capture), \
                 patch.object(acceptance_run,'Suite',return_value=suite), \
                 patch.object(acceptance_run,'Server',return_value=server) as make_server, \
                 patch.object(sys,'argv',['run.py','--board','http://localhost','--host','localhost',
                     '--suite','load','--case','lc-48000-stereo','--serial-port','TEST',
                     '--load-seconds','180','--load-idle-recovery','--unpaced-files','--leave-stopped','--output',tmp]):
                self.assertEqual(acceptance_run.main(),1)
                suite.sustained.assert_called_once_with(180,'lc-48000-stereo',cpu=True,load=True)
                self.assertEqual(suite.idle_heap.call_count,2)
                report = json.loads((Path(tmp)/'report.json').read_text())
                self.assertEqual(report['load_options'],{'seconds':180,'idle_recovery':True})
                self.assertEqual(report['server_options'],{'unpaced_files':True})
                self.assertTrue(make_server.call_args.kwargs['unpaced_files'])
                self.assertEqual([r['result'] for r in report['cases']],
                                 ['PASS','FAIL','PASS' if recovered else 'FAIL','PASS'])

    def test_eof_acceptance_rejects_resurrection_and_decode_error(self):
        terminal = dict(state(), audio=False, pcm_sample_rate=0, pcm_channels=0,
                        format='stream ended')
        message = json.dumps(dict(payload=[dict(id='fmt',value='stream ended'),
                                            dict(id='playerwrap',value='stopped')]))
        for tail, passed in [([terminal]*3,True),
                             ([terminal,state(),terminal],False),
                             ([dict(terminal,format='decode failed')]*3,False),
                             ([terminal],False)]:
            with tempfile.TemporaryDirectory() as tmp, self.subTest(tail=tail):
                board = Mock()
                socket = Mock()
                socket.recv.return_value = message
                from contextlib import nullcontext
                board.websocket.return_value = nullcontext(socket)
                suite = acceptance_run.Suite(board,'http://localhost',self.specs,None,tmp)
                suite.start = Mock()
                suite.observe = Mock(side_effect=[[state()]*6, tail])
                if passed:
                    self.assertTrue(suite.eof('he-48000-stereo')['websocket_stopped'])
                else:
                    with self.assertRaises(common.Failure):
                        suite.eof('he-48000-stereo')
                board.stop.assert_called_once()

    def test_transition_order_and_implicit_sbr_regression(self):
        expected = [self.specs['lc-22050-mono'],self.specs['hev2-44100-stereo'],self.specs['lc-48000-stereo']]
        mono = state(22050,1,'AAC PCM 22.05 kHz mono')
        he = state(44100,2,'HE-AACv2 44.1 kHz stereo')
        common.check_transitions([mono]*3+[he]*3+[state()]*3,expected)
        for samples in ([mono]*6+[state()]*3,[he]*3+[mono]*3+[state()]*3):
            with self.assertRaises(common.Failure):
                common.check_transitions(samples,expected)

    def test_cpu_checks_require_progress_and_reject_memory_failures(self):
        rows = [dict(line='PERF CPU: busy=35.0% idle=65.0% heap=22000 largest=10000'),
                dict(line='PERF AAC: window 5000 ms, audio 5000 ms, decode 900 ms')]*3
        common.check_cpu(rows)
        for change in ('heap=22000|heap=1000', 'largest=10000|largest=500',
                       'busy=35.0% idle=65.0%|busy=96.0% idle=4.0%', 'audio 5000|audio 100'):
            before,after = change.split('|')
            with self.subTest(change=change), self.assertRaises(common.Failure):
                common.check_cpu([dict(line=r['line'].replace(before,after)) for r in rows])
        with self.assertRaises(common.Failure):
            common.check_cpu(rows+[dict(line='PERF allocation failed: requested=55128')])
        with self.assertRaises(common.Failure):
            common.check_cpu([])
        timed=[dict(row,at=5*(i//2+1)) for i,row in enumerate(rows)]
        common.check_cpu(timed,start=0,end=20)
        with self.assertRaisesRegex(common.Failure,'gap'):
            common.check_cpu(timed,start=0,end=40)

    def test_heap_recovery_rejects_leak_and_missing_evidence(self):
        initial = [dict(heap=50000,largest=20000,tasks=12)]*2
        common.check_recovery_heap(initial,initial)
        for final in ([],[dict(heap=40000,largest=20000,tasks=12)]*2,
                      [dict(heap=50000,largest=10000,tasks=12)]*2,
                      [dict(heap=50000,largest=20000,tasks=13)]*2):
            with self.assertRaises(common.Failure):
                common.check_recovery_heap(initial,final)

    def test_access_denied_needs_independent_certificate_rejection_evidence(self):
        alert = ['TLSV1_ALERT_ACCESS_DENIED']
        proof = [dict(line=common.TLS_CERTIFICATE_REJECTED)]
        self.assertTrue(common.check_certificate_rejection(alert, proof))
        for alerts, rows in ((alert, []), ([], proof),
                            (alert, [dict(line='TLS failure: component=esp-x509-crt-bundle')]),
                            (['UNEXPECTED_EOF_WHILE_READING'], proof)):
            with self.subTest(alerts=alerts, rows=rows), self.assertRaises(common.Failure):
                common.check_certificate_rejection(alerts, rows)
        for value in ('TLSV1_ALERT_UNKNOWN_CA', 'SSLV3_ALERT_BAD_CERTIFICATE'):
            common.check_certificate_rejection([value], [])

    def test_real_recorded_he_failure_is_rejected(self):
        rows = json.loads((ROOT/'tests/results/esp32c3-radio-hardware-20260930/wifi-flash/radio-status.json').read_text())
        for name in ('he-48000-stereo','hev2-44100-stereo'):
            with self.assertRaises(common.Failure):
                common.check_playback([r for r in rows if r['case']==name],self.specs[name])

    def test_generic_server_bytes_mime_eof_redirect_and_allowlist(self):
        specs = {n:dict(s,seconds=.01) for n,s in self.specs.items() if 'sequence' not in s}
        with Server('127.0.0.1',0,specs) as server:
            base = 'http://127.0.0.1:'+str(server.http.server_port)
            for name,spec in specs.items():
                with urlopen(base+'/file/'+name,timeout=5) as response:
                    self.assertEqual(response.headers['Content-Type'],spec['mime'])
                    self.assertEqual(response.read(),spec['data'])
            with urlopen(base+'/redirect/lc-48000-stereo') as response:
                self.assertEqual(response.read(),specs['lc-48000-stereo']['data'])
            for route in ('/file/../../secret','/file/missing','/error/lc-48000-stereo','/stream/flac-level8'):
                with self.assertRaises(HTTPError):
                    urlopen(base+route).close()
            with urlopen(base+'/manifest.json') as response:
                manifest=json.load(response)
            self.assertNotIn('data',manifest['lc-48000-stereo'])

    def test_unpaced_download_preserves_bytes_and_other_routes_keep_pacing(self):
        # A nominal 60-second file must download immediately on loopback.
        # Fault routes still use the original pacing even with the option set.
        spec = dict(data=b'fixture-data'*512, seconds=60, codec='mp3', mime='audio/mpeg')
        with Server('127.0.0.1',0,{'test':spec},unpaced_files=True) as server:
            base = 'http://127.0.0.1:'+str(server.http.server_port)
            with urlopen(base+'/file/test',timeout=2) as response:
                self.assertEqual(response.read(),spec['data'])
            self.assertIsNone(server.events[0]['pacing_ratio'])
            with urlopen(base+'/stall/test',timeout=2) as response:
                self.assertEqual(response.read(12),b'fixture-data')
            self.assertEqual(server.events[1]['pacing_ratio'],1.02)

    def test_generic_https_requires_certificate_trust(self):
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID
        from datetime import datetime,timedelta,timezone
        import ipaddress
        key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'localhost')])
        now=datetime.now(timezone.utc)
        cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
              .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=1))
              .not_valid_after(now+timedelta(days=1))
              .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]),critical=False)
              .add_extension(x509.BasicConstraints(ca=True,path_length=None),critical=True).sign(key,hashes.SHA256()))
        with tempfile.TemporaryDirectory() as tmp:
            certpath=Path(tmp)/'cert.pem'; keypath=Path(tmp)/'key.pem'
            certpath.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
            keypath.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
            specs={'tone':dict(data=b'abc',seconds=.01,codec='aac',mime='audio/aac')}
            with Server('127.0.0.1',0,specs,certpath,keypath) as server:
                url='https://127.0.0.1:'+str(server.http.server_port)+'/file/tone'
                with self.assertRaises(OSError):
                    urlopen(url,timeout=3).close()
                with urlopen(url,context=ssl.create_default_context(cafile=str(certpath))) as response:
                    self.assertEqual(response.read(),b'abc')
                self.assertTrue(any(e['mode']=='tls-handshake-failure' for e in server.events))

    def test_ota_image_identity_and_negative_payloads(self):
        data=bytearray(4096); data[0]=0xe9
        struct.pack_into('<H',data,12,5); struct.pack_into('<I',data,32,0xabcd5432)
        data[80:112]=b'yoradio_esp32c3_oled_native'.ljust(32,b'\0')
        data[176:208]=b'\x12'*32
        self.assertEqual(ota.image_info(data)['app_elf_sha256'],'12'*32)
        cases=ota.negative_cases(data,8192)
        self.assertEqual(len(cases),8)
        self.assertGreater(cases['oversized-request'][1],8192+2048)
        self.assertNotEqual(cases['corrupt-image'][0],ota.multipart(data))
        self.assertFalse(cases['missing-boundary'][0].endswith(b'--\r\n'))
        data[12]=0
        with self.assertRaises(common.Failure):
            ota.image_info(data)

    def test_blocked_and_failed_cases_make_exit_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=common.Report(Path(tmp)/'report.json',{})
            report.case('ok',lambda: dict(ok=True))
            self.assertEqual(report.exit_code(),0)
            def blocked(): raise common.Blocked('Needs TLS server')
            report.case('https',blocked)
            self.assertEqual(report.exit_code(),1)

    def test_latency_requires_real_samples_and_enforces_both_budgets(self):
        compare_latency.compare([10]*30,[11]*30,1.25,12)
        for before,after,ratio,budget in [([],[],1.25,12),([10]*29,[10]*30,1.25,12),
                ([10]*30,[13]*30,1.25,15),([10]*30,[11]*30,1.25,10),
                ([10]*30,[float('nan')]*30,1.25,15)]:
            with self.assertRaises(common.Failure):
                compare_latency.compare(before,after,ratio,budget)

    def test_generated_manifest_is_verified_and_cannot_escape_its_directory(self):
        from audio_test_server.fixtures import load_fixtures
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            entry=dict(name='extra',file='extra.aac',seconds=10,codec='aac',
                       sha256=common.sha(b'abc'),rate=48000,channels=2,bits=16,profile='AAC-LC')
            (folder/'extra.aac').write_bytes(b'abc')
            manifest=folder/'manifest.json'
            manifest.write_text(json.dumps(dict(fixtures=[entry])))
            self.assertEqual(load_fixtures(manifest)['extra']['data'],b'abc')
            (folder/'extra.aac').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                load_fixtures(manifest)
            entry['file']='../outside.aac'
            manifest.write_text(json.dumps(dict(fixtures=[entry])))
            with self.assertRaisesRegex(ValueError,'escapes'):
                load_fixtures(manifest)


class ProductionConfigTests(unittest.TestCase):
    def test_real_production_wrapper_overrides_reused_wifi_iram_config(self):
        shell=shutil.which('pwsh') or shutil.which('powershell')
        if not shell:
            self.skipTest('Requires PowerShell; run this test on Windows')
        with tempfile.TemporaryDirectory(prefix='c3-production-config-') as tmp:
            folder=Path(tmp)
            shutil.copyfile(ROOT/'idf/esp32c3-oled-native/build-production.ps1',folder/'build-production.ps1')
            (folder/'build.ps1').write_text('''param([switch]$DeepSleepClock,[switch]$Rtc32kCrystal,[string]$BuildDirectory,
                [string]$Sdkconfig,[string[]]$SdkconfigDefaults,[string[]]$IdfArguments,[string]$DependencyRoot,[switch]$Setup)
                $global:LASTEXITCODE=0
                exit 0
            ''')
            for absolute in (False,True):
                for original in ('CONFIG_ESP_WIFI_IRAM_OPT=y\nCONFIG_ESP_WIFI_RX_IRAM_OPT=y\n',
                                 '# CONFIG_ESP_WIFI_IRAM_OPT is not set\r\nCONFIG_ESP_WIFI_RX_IRAM_OPT=y\r\n',''):
                    config=folder/'saved.config'
                    config.write_text('CONFIG_KEEP_ME=123\n'+original,encoding='utf-8')
                    command=[shell,'-NoProfile','-File',str(folder/'build-production.ps1'),
                             '-Sdkconfig',str(config) if absolute else 'saved.config','-NoFirmwareExport']
                    subprocess.run(command,check=True,capture_output=True)
                    data=config.read_text()
                    self.assertIn('CONFIG_KEEP_ME=123',data)
                    for option in ('ESP_WIFI_IRAM_OPT','ESP_WIFI_RX_IRAM_OPT'):
                        self.assertEqual(data.count('# CONFIG_'+option+' is not set'),1)
                        self.assertNotIn('CONFIG_'+option+'=y',data)
                    subprocess.run(command,check=True,capture_output=True)
                    self.assertEqual(data,config.read_text())


if __name__ == '__main__':
    unittest.main()
