"""Offline CYD controller qualification: synthetic images and injected HTTP only."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.cyd_tests.common import (CydBoard, Failure, OUTPUT_NAMES, digest, load_artifact,
                                    status_fields, cyd_fixtures)
from tools.cyd_tests.health import HealthBoard, check_health, playback_window, validate_health
from tools.cyd_tests.run import acceptance, CydSuite, delivery_evidence, main
from tools import export_cyd_production as production
from tools.audio_test_server.fixtures import SEQUENCES


def image(*, chip=0, project=production.PROJECT_NAME, version='controller-test', elf='ab'*32, sdk='v6.0.2'):
    header = bytearray(24)
    header[:2] = bytes([0xe9, 1]);header[23] = 1
    struct.pack_into('<H', header, 12, chip)
    payload = bytearray(512)
    struct.pack_into('<I', payload, 0, 0xabcd5432)
    for offset, text in ((16, version), (48, project), (112, sdk)):
        payload[offset:offset+len(text)] = text.encode()
    payload[144:176] = bytes.fromhex(elf)
    raw = header + struct.pack('<II', 0x3f400020, len(payload)) + payload
    checksum = 0xef
    for value in payload:checksum ^= value
    raw.extend(bytes((-(len(raw)+1)) % 16));raw.append(checksum)
    return bytes(raw) + hashlib.sha256(raw).digest()


def artifact_files(folder, backend='pdm', *, diagnostics=False, raw=None):
    folder.mkdir(parents=True, exist_ok=True)
    raw = image() if raw is None else raw
    app = folder/'app.bin';app.write_bytes(raw)
    config = 'CONFIG_IDF_TARGET="esp32"\n# CONFIG_FREERTOS_UNICORE is not set\n'
    for name, key in production.BACKENDS.items():
        config += f'CONFIG_{key}=y\n' if name == backend else f'# CONFIG_{key} is not set\n'
    if diagnostics:config += 'CONFIG_YORADIO_NATIVE_DIAGNOSTICS=y\n'
    (folder/'sdkconfig').write_bytes(config.encode())
    manifest = dict(build_check='PASS', target='esp32', backend=backend, idf_version='v6.0.2',
                    app_sha256=digest(raw), sdkconfig_sha256=digest(config.encode()), elf_sha256='ab'*32,
                    app_version='controller-test', app_bytes=len(raw))
    (folder/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return app


def specs():
    result = {}
    names = {n for values in SEQUENCES.values() for n in values}
    for index, name in enumerate(sorted(names | {'sample'})):
        codec = 'mp3' if name.startswith('mp3') else 'aac'
        rate = 22050 if '22050' in name else 44100 if '44100' in name else 48000
        result[name] = dict(codec=codec, label='MP3' if codec == 'mp3' else 'AAC PCM', rate=rate,
                            channels=1 if 'mono' in name else 2, bits=16, seconds=11,
                            sha256=digest(b'synthetic'), data=b'synthetic', mime='audio/aac')
    for name, sequence in SEQUENCES.items():
        result[name] = dict(codec='auto', seconds=len(sequence)*3, sequence=sequence,
                            sha256=digest(b'synthetic sequence'), data=b'synthetic sequence', mime=None)
    for codec in ('vorbis','opus'):
        payload = ('standalone synthetic '+codec+' container').encode()
        result['vendor-'+codec] = dict(codec=codec,label='OGG',rate=48000,channels=2,bits=16,
                                      seconds=11,sha256=digest(payload),data=payload,mime='audio/ogg')
    return result


def raw_health(*, backend='pdm', uptime=100000, writes=10, diagnostics=False, active=True):
    row = dict(schema=1, boot_id='0123456789abcdef', uptime_ms=uptime, reset_reason=1,
               heap=80000, largest=40000, minimum_heap=79000, tasks=9, allocation_failures=0, cores=2,
               memory=dict(internal_free=80000, internal_largest=40000, dma_free=70000, dma_largest=30000),
               last_allocation_failure=dict(size=0, caps=0),
               decoder_failure=dict(sequence=0, generation=0, codec=0, stage=0, result=0, completion=0,
                                    input_bytes=0, allocation_sequence=0),
               stream_failure=dict(sequence=0, generation=0, completion=0, result=0),
               output=dict(failures=0, write_errors=0, configure_errors=0, flush_errors=0, generation=0, stage=0, result=0),
               output_driver=dict(writes=writes, requested_bytes=writes*64, written_bytes=writes*64,
                                  errors=0, timeouts=0, short_writes=0, saturated=False,
                                  completion_queue_drops=0 if backend == 'pdm' and active else None,
                                  timing_enabled=diagnostics, timing_samples=writes if diagnostics else 0, invalid_time_samples=0,
                                  write_us=writes*10 if diagnostics else None, max_write_us=10 if diagnostics else None),
               input=dict(available=True, leased=True, resident=8, minimum=4, target=8, limit=8,
                          ready=1, reading=1, writing=0, released=0, ready_payload_bytes=32, reading_payload_bytes=32))
    row['cpu'] = dict(enabled=diagnostics, available=diagnostics, sample_uptime_ms=uptime if diagnostics else 0,
                      snapshot_failures=0, overall_percent=30.0 if diagnostics else None,
                      core_percent=[20.0, 40.0] if diagnostics else [None, None],
                      tasks={role: dict(percent_of_one_core=10.0 if diagnostics else None,
                                        stack_free_min=2048 if diagnostics else None)
                             for role in ('stream', 'decode', 'output', 'http')})
    return row


class Clock:
    def __init__(self):self.now = 100.0
    def perf_counter(self):return self.now
    def sleep(self, seconds):self.now += seconds


class Transport:
    def __init__(self, artifact, clock, fixtures):
        self.artifact, self.clock, self.specs = artifact, clock, fixtures
        self.calls, self.posts = [], []
        self.name = self.mode = None
        self.started = 0;self.generation = 1;self.writes = 0
        self.elf = artifact.elf_sha256;self.backend_name = OUTPUT_NAMES[artifact.backend]
        self.initial_active = False;self.fail_status = False;self.fail_stop = False
        self.health_update = None;self.ever_played = False
        self.servers = {}
        self.interrupt_after_playing_status = None
        self.interrupt_error = KeyboardInterrupt()
        self.playing_status_reads = 0
        self.interrupt_sent = False
        self.interrupt_durable_before_diagnostic = False
        self.interrupt_cleanup = False
        self.output = None
        self.fixture_closed_while_playing = []

    def state(self):
        active = self.initial_active or self.name is not None and (self.mode == 'stream' or
                     self.clock.now-self.started < self.specs[self.name]['seconds'])
        spec = self.specs[self.name] if self.name else self.specs['sample']
        if active and 'sequence' in spec:
            sequence = spec['sequence'];index = min(len(sequence)-1, int((self.clock.now-self.started)//3))
            spec = self.specs[sequence[index]]
        return dict(firmware='esp-idf-native', network='client', audio=active, connecting=False,
                    format=spec['label']+' test' if active else 'stream ended' if self.name else 'stopped',
                    codec=('OGG' if spec['codec'] in ('ogg','opus','vorbis') else spec['codec'].upper()) if active else '',
                    generation=self.generation, bitrate=128,
                    sample_rate_hz=spec['rate'] if active else 0, pcm_sample_rate_hz=spec['rate'] if active else 0,
                    channels=spec['channels'] if active else 0, pcm_channels=spec['channels'] if active else 0,
                    bits_per_sample=spec['bits'] if active else 0, format_is_pcm=True, channels_are_core=False,
                    station='PRIVATE STATION', password='PRIVATE KEY')

    def __call__(self, path, data=None, timeout=5, headers=None):
        self.calls.append(path)
        if data is not None:
            self.posts.append(path)
            if path == '/api/native/stop':
                if self.interrupt_cleanup and self.output and (self.output/'report.json').is_file():
                    saved = json.loads((self.output/'report.json').read_text())
                    if saved['cases'] and saved['cases'][-1]['name'] == 'cleanup-stop':
                        self.interrupt_cleanup = False
                        raise KeyboardInterrupt()
                if self.fail_stop:raise OSError('PRIVATE CLEANUP ERROR')
                self.name = self.mode = None
            else:
                parsed = urlsplit(data.decode());self.mode, self.name = parsed.path.strip('/').split('/')
                self.started = self.clock.now;self.ever_played = True
                server = self.servers.get(parsed.port or (443 if parsed.scheme == 'https' else 80))
                if server is not None:
                    event = dict(mode=self.mode,fixture=self.name,sent=len(self.specs[self.name]['data']),
                                 complete=True,pacing_ratio=1.0)
                    if parsed.scheme == 'https':event.update(tls_version='TLSv1.2',tls_cipher='TEST-SYNTHETIC-CIPHER')
                    server.events.append(event)
            self.generation += 1
            return b'{}'
        if path == '/api/native/ota':
            result = dict(version='controller-test', partition='app0', max_size=1700000,
                          max_body_size=1702048, app_elf_sha256=self.elf)
        elif path == '/api/native/capabilities':
            result = dict(schema=1, firmware='esp32-cyd2usb-native', audio_output=self.backend_name)
        elif path == '/api/native/status':
            if self.interrupt_sent and self.output:
                saved = json.loads((self.output/'report.json').read_text())
                self.interrupt_durable_before_diagnostic = ('controller_error' in saved and
                    any(r.get('interrupted') and r['result']=='FAIL' for r in saved['cases']) and not saved['passed'])
            if self.ever_played:
                self.playing_status_reads += 1
                if self.playing_status_reads == self.interrupt_after_playing_status:
                    self.interrupt_sent = True
                    raise self.interrupt_error
            if self.fail_status and self.ever_played:raise OSError('PRIVATE URL AND KEY')
            result = self.state()
        elif path == '/api/native/health':
            self.writes += 2 if self.state()['audio'] else 1
            result = raw_health(backend=self.artifact.backend, uptime=int(self.clock.now*1000), writes=self.writes,
                                diagnostics=self.artifact.diagnostics, active=self.ever_played)
            if self.health_update and self.ever_played:self.health_update(result)
        elif path == '/api/native/settings':
            result = dict(volume=100, balance=0, normalization=True, normgain=1, normtarget=-2, normtime=1000)
        elif path == '/api/native/time':
            result = dict(utc_offset_minutes=60, sync_interval_minutes=60, server1='private.local', server2='')
        elif path == '/api/native/network-settings':result = dict(hostname='private-radio', ap_timeout_minutes=0)
        elif path == '/api/native/radio':result = dict(smartstart=True, station='PRIVATE STATION')
        else:raise AssertionError('Unexpected fake request: '+path)
        return json.dumps(result).encode()


class Server:
    def __init__(self, *args, **kwargs):self.events = []
    def __enter__(self):return self
    def __exit__(self, *args):return False


class Offline(unittest.TestCase):
    def setUp(self):
        temporary_root = ROOT/'.build/cyd-controller-test-temp'
        temporary_root.mkdir(parents=True, exist_ok=True)
        self.assertTrue(temporary_root.resolve().is_relative_to((ROOT/'.build').resolve()))
        self.temp = tempfile.TemporaryDirectory(dir=temporary_root)
        self.assertTrue(Path(self.temp.name).resolve().is_relative_to(temporary_root.resolve()))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # These tests fail immediately if any real socket/serial path is reached.
        self.addCleanup(patch.stopall)
        patch('socket.socket', side_effect=AssertionError('No sockets in offline tests')).start()
        patch('socket.create_connection', side_effect=AssertionError('No connections in offline tests')).start()

    def board(self, backend='pdm', diagnostics=False):
        app = artifact_files(self.root/backend, backend, diagnostics=diagnostics)
        artifact = load_artifact(app, backend);clock = Clock();transport = Transport(artifact, clock, specs())
        board = HealthBoard('http://unused.invalid', artifact, transport=transport)
        return app, artifact, clock, transport, board

    def test_three_saved_backends_and_live_identity_before_every_post(self):
        for backend in OUTPUT_NAMES:
            _, artifact, _, transport, board = self.board(backend)
            with self.assertRaises(Failure):board.stop()
            self.assertEqual(transport.posts, [])
            board.authorize();board.play('http://fixture.invalid/file/sample', 'aac');board.stop()
            self.assertEqual(transport.posts, ['/api/native/play?codec=aac', '/api/native/stop'])
            for index, path in enumerate(transport.calls):
                if path in transport.posts:self.assertEqual(transport.calls[index-2:index], ['/api/native/ota', '/api/native/capabilities'])
            transport.elf = 'cd'*32
            with self.assertRaises(Failure):board.stop()
            self.assertEqual(len(transport.posts), 2)
            self.assertEqual(artifact.backend, backend)

    def test_image_chip_project_sdk_segments_checksums_and_manifest_rejections(self):
        broken = [('chip', image(chip=5)), ('project', image(project='wrong')),
                  ('sdk', image(sdk='v6.0.20')), ('truncated', image()[:-1]), ('trailer', image()+b'x')]
        raw = bytearray(image());raw[40] ^= 1;broken.append(('checksum', bytes(raw)))
        raw = bytearray(image());raw[-1] ^= 1;broken.append(('sha', bytes(raw)))
        raw = bytearray(image());raw[1] = 0;broken.append(('segments', bytes(raw)))
        for name, raw in broken:
            with self.subTest(name=name):
                app = artifact_files(self.root/name, raw=raw)
                with self.assertRaises((Failure, production.ValidationError)):load_artifact(app, 'pdm')
        app = artifact_files(self.root/'manifest')
        path = app.with_name('manifest.json');original = json.loads(path.read_text())
        for key, value in (('backend','legacy'), ('target','esp32c3'), ('app_sha256','0'*64),
                           ('sdkconfig_sha256','0'*64), ('elf_sha256','0'*64), ('app_bytes',True),
                           ('app_version','wrong'), ('build_check','FAIL')):
            path.write_text(json.dumps(dict(original, **{key:value})))
            with self.subTest(key=key), self.assertRaises(Failure):load_artifact(app, 'pdm')

    def test_config_conflict_and_artifact_drift_reject_writes(self):
        app, artifact, _, transport, board = self.board()
        board.authorize();app.with_name('sdkconfig').write_bytes(b'changed')
        with self.assertRaises(Failure):board.stop()
        self.assertFalse(transport.posts)
        app = artifact_files(self.root/'conflict')
        config = app.with_name('sdkconfig');config.write_text(config.read_text().replace(
            '# CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC is not set', 'CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC=y'))
        manifest = app.with_name('manifest.json');data = json.loads(manifest.read_text())
        data['sdkconfig_sha256'] = digest(config.read_bytes());manifest.write_text(json.dumps(data))
        with self.assertRaises(Failure):load_artifact(app, 'pdm')

    def test_status_normalization_privacy_and_strict_types(self):
        _, _, _, transport, _ = self.board();raw = transport.state();row = status_fields(raw)
        self.assertNotIn('station', row);self.assertNotIn('password', row)
        self.assertIn('pcm_sample_rate', row);self.assertNotIn('pcm_sample_rate_hz', row)
        for key, value in (('firmware','esp32c3-oled-native'), ('audio',1), ('sample_rate_hz',True),
                           ('channels',-1), ('format',None)):
            with self.subTest(key=key), self.assertRaises(Failure):status_fields(dict(raw, **{key:value}))

    def test_actual_rest_settings_no_display_reboot_or_arbitrary_writes(self):
        _, _, _, transport, board = self.board();board.authorize()
        value = board.settings();self.assertEqual(set(value), {'settings','time','network-settings','radio'})
        self.assertFalse(transport.posts)
        with self.assertRaises(Failure):board.reboot()
        for path in ('/update','/api/native/wifi','/api/native/settings'):
            with self.assertRaises(Failure):board.request(path, b'x')
        self.assertFalse(transport.posts)

    def test_saved_manifest_backend_is_not_guessed_from_generic_status(self):
        _, _, _, transport, board = self.board()
        transport.backend_name = OUTPUT_NAMES['continuous']
        self.assertEqual(board.status()['firmware'], 'esp-idf-native')
        with self.assertRaises(Failure):board.authorize()
        with self.assertRaises(Failure):board.stop()
        self.assertFalse(transport.posts)

    def test_all_native_health_groups_and_unavailable_quiet_measurements(self):
        for backend in OUTPUT_NAMES:
            row = validate_health(raw_health(backend=backend), backend)
            self.assertEqual(row['cpu']['core_percent'], [None,None])
            self.assertNotIn('task_watchdog_events', row)
            self.assertFalse(check_health([row])['watchdog_counter_available'])
            if backend != 'pdm':self.assertIsNone(row['output_driver']['completion_queue_drops'])
        for mutator in (lambda r:r.pop('stream_failure'), lambda r:r.update(cores=1),
                        lambda r:r.update(allocation_failures=True),
                        lambda r:r['output_driver'].update(short_writes=-1),
                        lambda r:r['memory'].update(dma_largest=90000)):
            row = raw_health();mutator(row)
            with self.assertRaises(Failure):validate_health(row, 'pdm')

    def test_cpu_freshness_denominator_and_missing_diagnostic_tasks(self):
        row = raw_health(diagnostics=True);parsed = validate_health(row,'pdm')
        self.assertTrue(check_health([parsed],require_cpu=True)['cpu_observed'])
        for mutate in (lambda r:r['cpu'].update(sample_uptime_ms=1),
                       lambda r:r['cpu'].update(core_percent=[20]),
                       lambda r:r['cpu'].update(overall_percent=60),
                       lambda r:r['cpu'].update(available=False),
                       lambda r:r['cpu']['tasks']['stream'].update(percent_of_one_core=True)):
            changed = copy.deepcopy(row);mutate(changed)
            with self.assertRaises(Failure):validate_health(changed,'pdm')
        parsed['cpu']['tasks']['output']['stack_free_min'] = None
        with self.assertRaises(Failure):check_health([parsed],require_cpu=True)

    def window(self, backend='pdm'):
        states = [dict(seconds=i,audio=True,pcm_sample_rate=48000,pcm_channels=2) for i in range(8)]
        rows = [validate_health(raw_health(backend=backend,uptime=100000+i*1000,writes=10+i),backend) for i in range(8)]
        return states, rows

    def test_output_progress_nullable_dac_and_pdm_registration(self):
        for backend in OUTPUT_NAMES:
            states, rows = self.window(backend)
            result = playback_window(states, rows)
            self.assertGreater(result['driver_delta']['written_bytes'],0)
            self.assertEqual(result['queue_observation_available'], backend == 'pdm')
        states, rows = self.window();rows[-1]['output_driver']['completion_queue_drops'] = None
        with self.assertRaises(Failure):playback_window(states, rows)
        states, rows = self.window('continuous');raw = raw_health(backend='continuous')
        raw['output_driver']['completion_queue_drops'] = 0
        with self.assertRaises(Failure):validate_health(raw,'continuous')

    def test_counter_saturation_decrease_errors_no_progress_pairing_and_faults(self):
        changes = [lambda rows:rows[-1]['output_driver'].update(saturated=True),
                   lambda rows:rows[-1]['output_driver'].update(writes=0),
                   lambda rows:rows[-1]['output_driver'].update(errors=1),
                   lambda rows:rows[-1]['output_driver'].update(short_writes=1),
                   lambda rows:rows[-1]['output_driver'].update(completion_queue_drops=1),
                   lambda rows:rows[-1].update(boot_id='fedcba9876543210'),
                   lambda rows:rows[-1].update(uptime_ms=1),
                   lambda rows:rows[-1].update(allocation_failures=1),
                   lambda rows:rows[-1]['stream_failure'].update(sequence=1),
                   lambda rows:rows[-1]['decoder_failure'].update(sequence=1),
                   lambda rows:rows[-1]['output'].update(flush_errors=1)]
        for mutate in changes:
            states, rows = self.window();mutate(rows)
            with self.subTest(mutate=mutate), self.assertRaises(Failure):playback_window(states, rows)
        states, rows = self.window()
        for row in rows:row['output_driver'] = copy.deepcopy(rows[0]['output_driver'])
        with self.assertRaises(Failure):playback_window(states, rows)
        states, rows = self.window()
        with self.assertRaises(Failure):playback_window(states, rows[:-1])
        states[4]['audio'] = False
        with self.assertRaises(Failure):playback_window(states, rows)

    def run_controller(self, suites=('http',), *, backend='pdm', configure=None, diagnostics=False, cases=None):
        app, artifact, clock, transport, _ = self.board(backend,diagnostics)
        if configure:configure(transport)
        out = self.root/('result-'+backend+'-'+str(len(list(self.root.glob('result-*')))))
        transport.output = out
        args = SimpleNamespace(output=out,backend=backend,suite=list(suites),firmware=app,require_cpu=diagnostics,
                               fixture_manifest=None,case=cases or ['sample'],board='http://unused.invalid',host='fixture.invalid',
                               port=8770,https_origin=None,tls_cert=None,tls_key=None,tls_port=8771,
                               cycles=3,load_seconds=40,soak_seconds=60)
        if 'https' in suites:
            args.https_origin='https://fixture.invalid:8771'
            args.tls_cert=self.root/'public-cert.pem';args.tls_cert.write_text('synthetic public cert')
            args.tls_key=self.root/'private-key.pem';args.tls_key.write_text('PRIVATE KEY')
        class Board(HealthBoard):
            def websocket(self):
                class WS:
                    def __enter__(own):return own
                    def __exit__(own,*_):return False
                    def send(own,command):
                        require_command=command=='getindex'
                        if not require_command:raise AssertionError('Unexpected WS command')
                    def recv(own,timeout=5):
                        return json.dumps(dict(payload=[dict(id='fmt',value=transport.state()['format']),
                                                       dict(id='playerwrap',value='playing')]))
                return WS()
        factory = lambda origin, selected:Board(origin,selected,transport=transport)
        def server_factory(*args,**kwargs):
            class ObservedServer(Server):
                def __exit__(own,*_):
                    transport.fixture_closed_while_playing.append(transport.state()['audio'])
                    return False
            server=ObservedServer();transport.servers[args[1]]=server;return server
        code = acceptance(args,board_factory=factory,server_factory=server_factory,fixture_loader=lambda _:specs(),clock=clock)
        return code,json.loads((out/'report.json').read_text()),out,transport,args

    def test_whole_controller_three_profiles_http_eof_stop_switch_and_settings(self):
        for backend in OUTPUT_NAMES:
            code, report, out, transport, _ = self.run_controller(('http','eof','stop','switch'),backend=backend)
            self.assertEqual(code,0,report)
            self.assertTrue(report['passed']);self.assertFalse(transport.state()['audio'])
            text=(out/'report.json').read_text()+(out/'status.json').read_text()+(out/'health.json').read_text()
            self.assertNotIn('PRIVATE',text);self.assertNotIn('private.local',text)
            self.assertFalse(report['deployment']);self.assertFalse(report['reboot'])

    def test_whole_controller_transitions_load_soak_and_diagnostic_cpu(self):
        code, report, _, _, _ = self.run_controller(('transitions','load','soak'),diagnostics=True)
        self.assertEqual(code,0,report)
        self.assertTrue(any(row['name']=='transition:mp3-he-mp3' for row in report['cases']))

    def test_healthy_sustained_and_websocket_stop_before_fixture_teardown(self):
        for selected in (('load',),('websocket',)):
            code,report,_,transport,_=self.run_controller(selected)
            self.assertEqual(code,0,report)
            self.assertTrue(transport.fixture_closed_while_playing)
            self.assertFalse(any(transport.fixture_closed_while_playing))

    def test_https_and_implemented_websocket_use_only_controlled_transports(self):
        code,report,out,transport,_=self.run_controller(('https','websocket'))
        self.assertEqual(code,0,report)
        row=next(r for r in report['cases'] if r['name']=='https:sample:auto')
        self.assertEqual(row['evidence']['delivery']['tls_version'],'TLSv1.2')
        self.assertEqual(len(report['tls_events']),2)
        self.assertNotIn('PRIVATE KEY',(out/'report.json').read_text())

    def test_controlled_delivery_rejects_incomplete_wrong_or_missing_tls_evidence(self):
        spec=specs()['sample'];valid=dict(mode='file',fixture='sample',complete=True,sent=len(spec['data']),
                                         pacing_ratio=1.0,tls_version='TLSv1.2',tls_cipher='TEST')
        for field,value in (('complete',False),('sent',1),('fixture','wrong'),('pacing_ratio',1.02),
                            ('tls_version',None),('tls_cipher',None)):
            with self.subTest(field=field),self.assertRaises(Failure):
                delivery_evidence([dict(valid,**{field:value})],'sample',spec,tls=True)
        with self.assertRaises(Failure):delivery_evidence([],'sample',spec)

    def test_live_identity_or_initial_active_refuses_all_mutations(self):
        for change in (lambda t:setattr(t,'elf','0'*64),lambda t:setattr(t,'initial_active',True)):
            code, report, _, transport, _ = self.run_controller(configure=change)
            self.assertEqual(code,1);self.assertFalse(transport.posts)
            self.assertIn('controller_error',report)

    def test_partial_transport_error_precedes_cleanup_and_preserves_original(self):
        def configure(t):t.fail_status=True;t.fail_stop=False
        code, report, out, transport, _ = self.run_controller(configure=configure)
        self.assertEqual(code,1)
        self.assertEqual(report['cases'][0]['exception_chain'][0]['type'],'OSError')
        self.assertIn('http:sample:auto',report['failure_snapshots'])
        self.assertTrue((out/'status.json').exists());self.assertTrue((out/'health.json').exists())
        self.assertNotIn('PRIVATE',(out/'report.json').read_text())
        self.assertIn('/api/native/stop',transport.posts)

    def test_output_fault_and_cleanup_failure_remain_separate_failed_rows(self):
        def configure(t):
            def fault(row):
                row['output']['write_errors']=1;t.fail_stop=True
            t.health_update=fault
        code, report, _, _, _ = self.run_controller(configure=configure)
        self.assertEqual(code,1)
        failures={r['name']:r for r in report['cases'] if r['result']=='FAIL'}
        self.assertIn('http:sample:auto',failures);self.assertIn('cleanup-stop',failures)
        self.assertIn('allocation/stream/decoder/output failure',failures['http:sample:auto']['reason'])
        self.assertEqual(failures['cleanup-stop']['exception_chain'][0]['type'],'OSError')

    def test_fresh_output_rejection_has_no_transport_or_overwrite(self):
        _, _, out, transport, args = self.run_controller()
        before=(out/'report.json').read_bytes();transport.calls.clear()
        with self.assertRaises(Failure):acceptance(args,board_factory=lambda *_:self.fail('No factory call'))
        self.assertEqual((out/'report.json').read_bytes(),before);self.assertFalse(transport.calls)

    def test_keyboard_interrupt_mid_positive_and_load_are_durable_before_cleanup(self):
        for suites in (('http',),('load',)):
            code,report,out,transport,_=self.run_controller(suites,configure=lambda t:setattr(t,'interrupt_after_playing_status',4))
            self.assertEqual(code,130)
            self.assertFalse(report['passed']);self.assertEqual(report['controller_error']['type'],'KeyboardInterrupt')
            self.assertTrue(transport.interrupt_durable_before_diagnostic)
            failed=next(r for r in report['cases'] if r.get('interrupted'))
            self.assertEqual(failed['result'],'FAIL')
            self.assertGreater(len(json.loads((out/'status.json').read_text())[-2]['samples']),0)
            self.assertTrue(any(r['name']=='cleanup-stop' for r in report['cases']))

    def test_primary_interrupt_and_cleanup_interrupt_remain_separate(self):
        def configure(t):t.interrupt_after_playing_status=4;t.interrupt_cleanup=True
        code,report,_,_,_=self.run_controller(configure=configure)
        self.assertEqual(code,130);self.assertFalse(report['passed'])
        self.assertEqual(report['controller_error']['location'],'http:sample:auto')
        interrupted=[r for r in report['cases'] if r.get('interrupted')]
        self.assertEqual([r['name'] for r in interrupted],['http:sample:auto','cleanup-stop'])
        self.assertTrue(all(r['result']=='FAIL' for r in interrupted))

    def test_cleanup_only_interrupt_and_systemexit_zero_never_pass(self):
        code,report,_,_,_=self.run_controller(configure=lambda t:setattr(t,'interrupt_cleanup',True))
        self.assertEqual(code,130);self.assertFalse(report['passed'])
        self.assertEqual(report['cases'][-1]['name'],'cleanup-stop');self.assertTrue(report['cases'][-1]['interrupted'])
        def configure(t):t.interrupt_after_playing_status=4;t.interrupt_error=SystemExit(0)
        code,report,_,_,_=self.run_controller(configure=configure)
        self.assertEqual(code,1);self.assertFalse(report['passed'])
        self.assertEqual(report['controller_error']['type'],'SystemExit')

    def test_actual_cli_parser_and_process_exit_are_nonzero_on_fake_interrupt(self):
        folder=self.root/'interrupt-cli'
        process=subprocess.run([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),
                                '--interrupt-cli-fixture',str(folder)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
        self.assertEqual(process.returncode,130,process.stdout.decode())
        report=json.loads((folder/'result/report.json').read_text())
        self.assertFalse(report['passed']);self.assertEqual(report['controller_error']['type'],'KeyboardInterrupt')
        print('OFFLINE_INTERRUPT_CLI terminal_exit=130 passed=false',flush=True)

    def test_common_fixtures_preserve_encoded_bytes_and_cyd_pcm_contract(self):
        values=cyd_fixtures()
        for spec in values.values():
            self.assertEqual(digest(spec['data']),spec['sha256'])
            if spec['codec']=='aac':self.assertEqual(spec['label'],'AAC PCM')

    def test_vendor_ogg_finite_and_eof_auto_explicit_matrix_on_three_backends(self):
        for backend in OUTPUT_NAMES:
            code,report,_,transport,_=self.run_controller(('http','eof'),backend=backend,
                                                         cases=['vendor-vorbis','vendor-opus'])
            self.assertEqual(code,0,report)
            measured=[r for r in report['cases'] if r['name'].startswith(('http:','eof:'))]
            self.assertEqual(len(measured),8)
            self.assertEqual({r['name'] for r in measured},
                {f'{suite}:vendor-{codec}:{hint}' for suite in ('http','eof') for codec in ('vorbis','opus')
                 for hint in ('auto',codec)})
            self.assertTrue(all(r['result']=='PASS' and r['evidence']['eof']['explicit_stop'] is False for r in measured))
            hints=[parse_qs(urlsplit(path).query)['codec'][0] for path in transport.posts if '/play?' in path]
            self.assertEqual(hints.count('auto'),4);self.assertEqual(hints.count('vorbis'),2);self.assertEqual(hints.count('opus'),2)

    def test_default_matrix_contains_shared_vendor_ogg_and_status_schema_accepts_ogg(self):
        actual=cyd_fixtures()
        self.assertTrue(any(s['codec']=='vorbis' and s['label']=='OGG' for s in actual.values()))
        self.assertTrue(any(s['codec']=='opus' and s['label']=='OGG' for s in actual.values()))
        _,_,_,transport,board=self.board();board.authorize()
        for hint in ('ogg','opus','vorbis'):
            board.play('http://fixture.invalid:8770/file/vendor-opus',hint)
            value=board.status();self.assertEqual(value['codec'],'OGG');self.assertTrue(value['format'].startswith('OGG'))

    def test_short_finite_ogg_soak_rejects_without_repeating_raw_container(self):
        code,report,_,transport,_=self.run_controller(('soak',),cases=['vendor-opus'])
        self.assertEqual(code,1)
        failure=next(r for r in report['cases'] if r['name']=='soak:vendor-opus')
        self.assertIn('outlast',failure['reason'])
        self.assertFalse(any('/play?' in path for path in transport.posts))

    def test_long_finite_ogg_soak_keeps_file_route_and_original_container(self):
        app,artifact,clock,transport,board=self.board();board.authorize()
        fixtures=specs();fixtures['vendor-opus']['seconds']=70;transport.specs=fixtures
        suite=CydSuite(board,'http://fixture.invalid:8770',fixtures,self.root/'long-ogg',clock=clock)
        result=suite.sustained(60,'vendor-opus')
        self.assertGreater(result['output']['driver_delta']['written_bytes'],0)
        self.assertEqual(transport.mode,'file');self.assertEqual(fixtures['vendor-opus']['data'],b'standalone synthetic opus container')


def interrupt_cli_fixture(folder):
    folder=Path(folder);app=artifact_files(folder/'image');artifact=load_artifact(app,'pdm')
    clock=Clock();transport=Transport(artifact,clock,specs());transport.interrupt_after_playing_status=4
    transport.output=folder/'result'
    def server_factory(*args,**kwargs):
        server=Server();transport.servers[args[1]]=server;return server
    with patch('socket.socket',side_effect=AssertionError('No socket in CLI fixture')):
        return main(['--board','http://unused.invalid','--host','fixture.invalid','--backend','pdm',
                     '--firmware',str(app),'--suite','http','--case','sample','--output',str(transport.output)],
                    board_factory=lambda origin,selected:HealthBoard(origin,selected,transport=transport),
                    server_factory=server_factory,fixture_loader=lambda _:specs(),clock=clock)


if __name__ == '__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--interrupt-cli-fixture':
        raise SystemExit(interrupt_cli_fixture(sys.argv[2]))
    unittest.main(verbosity=2)
