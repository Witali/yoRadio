"""CYD OTA controller gates with synthetic images/fake HTTP/upload/clock only.

No board, socket, COM, compiler, SDK process, flash or production build is used.
"""
import copy
import hashlib
import http.client
import importlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import export_cyd_production as production
from tools.cyd_tests import ota
from tools.cyd_tests.common import CydBoard, Failure, OUTPUT_NAMES, load_artifact

SECRET = 'private-WIFI-station-token'


def image_bytes(chip=0, project=production.PROJECT_NAME):
    header = bytearray(24)
    header[0], header[1], header[23] = 0xe9, 1, 1
    struct.pack_into('<H', header, 12, chip)
    payload = bytearray(b'\x55' * 8192)
    payload[:256] = b'\0' * 256
    struct.pack_into('<I', payload, 0, 0xabcd5432)
    payload[16:48] = b'fixture-g123456789'.ljust(32, b'\0')
    payload[48:80] = project.encode().ljust(32, b'\0')
    payload[112:144] = b'v6.0.2'.ljust(32, b'\0')
    payload[144:176] = bytes.fromhex('ab' * 32)
    raw = header + struct.pack('<II', 0x3f400020, len(payload)) + payload
    checksum = 0xef
    for value in payload: checksum ^= value
    position = ((len(raw)+1+15)//16)*16-1
    raw += bytes(position-len(raw)) + bytes([checksum])
    return bytes(raw) + hashlib.sha256(raw).digest()


def artifact(folder, backend='pdm', image=None):
    app = Path(folder) / 'app.bin'
    raw = image if image is not None else image_bytes()
    app.write_bytes(raw)
    config = ('CONFIG_IDF_TARGET="esp32"\n# CONFIG_FREERTOS_UNICORE is not set\n' +
              '\n'.join(('CONFIG_'+key+'=y') if name == backend else
                        ('# CONFIG_'+key+' is not set') for name, key in production.BACKENDS.items()) + '\n').encode()
    app.with_name('sdkconfig').write_bytes(config)
    manifest = dict(build_check='PASS', target='esp32', backend=backend, idf_version='v6.0.2',
                    app_sha256=hashlib.sha256(raw).hexdigest(), sdkconfig_sha256=hashlib.sha256(config).hexdigest(),
                    elf_sha256='ab'*32, app_version='fixture-g123456789', app_bytes=len(raw))
    app.with_name('manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return app


class Clock:
    def __init__(self): self.now = 0
    def perf_counter(self): return self.now
    def sleep(self, seconds): self.now += seconds


class Transport:
    def __init__(self, clock, selected):
        self.clock, self.selected = clock, selected
        self.calls, self.writes = [], []
        self.partition, self.boot_number, self.reset_reason = 'app0', 1, 1
        self.boot_start, self.uptime_bias = 0, 10000
        self.elf, self.output = selected.elf_sha256, OUTPUT_NAMES[selected.backend]
        self.audio, self.connecting = False, False
        self.codec, self.format = 'AAC', 'AAC PCM 44.1 kHz stereo'
        self.rate, self.channels, self.bits = 44100, 2, 16
        self.core = False
        self.playlist = ('1,'+SECRET+',http://secret.invalid/?key='+SECRET+'\n').encode()
        self.wifi = dict(revision='a'*16+'-'+'b'*16, profiles=[dict(id='r1', ssid=SECRET, ssid_utf8=True)])
        self.settings = {'settings': dict(volume=17, balance=0, normalization=True, normgain=0,
                                          normtarget=0, normtime=1),
                         'time': dict(utc_offset_minutes=0, sync_interval_minutes=60, server1=SECRET, server2=''),
                         'network-settings': dict(hostname=SECRET, ap_timeout_minutes=5),
                         'radio': dict(smartstart=True)}
        self.read_hook = None
        self.overrides = {}
        self.fail_stop = False
        self.outages = 0

    def reboot(self, *, switch=False, reason=ota.ESP_RST_SW, auto_play=False):
        if switch: self.partition = 'app1' if self.partition == 'app0' else 'app0'
        self.boot_number += 1
        self.boot_start, self.uptime_bias, self.reset_reason = self.clock.now, 0, reason
        self.audio = auto_play

    def __call__(self, path, data=None, timeout=5, headers=None):
        self.calls.append((path, data))
        if self.read_hook: self.read_hook(path, data)
        if self.outages:
            self.outages -= 1
            raise OSError('private transport '+SECRET)
        if data is not None:
            self.writes.append(path)
            if path == '/api/native/stop':
                if self.fail_stop: raise OSError(SECRET)
                self.audio = self.connecting = False
                return b'{"stopped":true}'
            if path.startswith('/api/native/play?codec='):
                self.audio = True
                return b'{"playing":true}'
            raise AssertionError('Unexpected raw write')
        if path == '/api/native/ota':
            value = dict(app_elf_sha256=self.elf, version=self.selected.evidence['app_version'],
                         partition=self.partition, max_size=16384, max_body_size=20480)
        elif path == '/api/native/capabilities':
            value = dict(schema=1, firmware='esp32-cyd2usb-native', audio_output=self.output)
        elif path == '/api/native/status':
            value = dict(firmware='esp-idf-native', network='client', audio=self.audio,
                         connecting=self.connecting, format_is_pcm=True, channels_are_core=self.core,
                         format=self.format, codec=self.codec, generation=1, bitrate=128,
                         sample_rate_hz=self.rate, pcm_sample_rate_hz=self.rate, channels=self.channels,
                         pcm_channels=self.channels, bits_per_sample=self.bits, title=SECRET, station=SECRET)
        elif path == '/api/native/health':
            value = dict(schema=1, boot_id=f'{self.boot_number:016x}', reset_reason=self.reset_reason,
                         uptime_ms=self.uptime_bias+int((self.clock.now-self.boot_start)*1000), cores=2)
        elif path == '/api/native/wifi': value = self.wifi
        elif path == '/data/playlist.csv': return self.playlist
        elif path.startswith('/api/native/') and path[len('/api/native/'):] in self.settings:
            value = self.settings[path[len('/api/native/'):]]
        else: raise AssertionError('Unexpected raw read')
        if path in self.overrides: value.update(self.overrides[path])
        return json.dumps(value).encode()


class Uploader:
    def __init__(self, transport):
        self.transport, self.calls = transport, []
        self.hook = None
        self.positive_reason = ota.ESP_RST_SW
        self.positive_switch = True
        self.positive_body = b'OK'
        self.auto_play = False

    def __call__(self, origin, body, **kwargs):
        index = len(self.calls)
        self.calls.append(dict(origin=origin, body=body, **kwargs))
        if self.hook:
            result = self.hook(index, body, kwargs)
            if result is not None: return result
        if index < 10:
            statuses = [400]*7 + [413, None, 408]
            sent = min(len(body)//2, 8192) if kwargs.get('interrupt') else min(len(body), kwargs.get('send_limit') or len(body))
            return ota.UploadResult(statuses[index], SECRET.encode(), sent)
        self.transport.reboot(switch=self.positive_switch, reason=self.positive_reason, auto_play=self.auto_play)
        return ota.UploadResult(200, self.positive_body, len(body))


class Response:
    def __init__(self, status=400, body=b'rejected'): self.status, self.body = status, body
    def read(self, limit): return self.body[:limit]


class Connection:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.requests, self.headers = response or Response(), error, [], {}
        self.sent, self.closed, self.response_calls = [], False, 0
    def putrequest(self, method, path): self.requests.append((method, path))
    def putheader(self, key, value): self.headers[key] = value
    def endheaders(self): pass
    def send(self, data): self.sent.append(data)
    def getresponse(self):
        self.response_calls += 1
        if self.error: raise self.error
        return self.response
    def close(self): self.closed = True


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cyd-ota-fake-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.app = artifact(self.folder)
        self.selected = load_artifact(self.app, 'pdm')
        self.clock = Clock()
        self.transport = Transport(self.clock, self.selected)
        self.board = CydBoard('http://board.invalid', self.selected, transport=self.transport)
        self.uploader = Uploader(self.transport)
        self.report = self.folder/'report.json'
        # Any accidental default socket or COM access fails the test immediately.
        self.network = patch('socket.socket', side_effect=AssertionError('Real sockets forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)

    def run_gate(self, **kwargs):
        code = ota.run_acceptance(self.board, self.report, clock=self.clock, uploader=self.uploader, **kwargs)
        return code, json.loads(self.report.read_bytes())

    def assert_private(self, report):
        text = json.dumps(report)
        for forbidden in (SECRET, 'secret.invalid', 'board.invalid', str(self.app), 'playlist.csv', 'server1'):
            self.assertNotIn(forbidden, text)

    def test_negative_only_explicitly_does_not_qualify_a_successful_update(self):
        code, report = self.run_gate()
        self.assertEqual(code, 0)
        self.assertEqual(report['result'], 'PASS')
        self.assertFalse(report['successful_update_qualified'])
        self.assertTrue(report['finished_stopped'])
        self.assertEqual(self.transport.boot_number, 1)
        self.assertEqual(len(self.uploader.calls), 10)
        self.assertEqual([x['evidence']['http'] for x in report['cases'][1:11]], [400]*7+[413, None, 408])
        self.assertEqual(self.transport.writes, ['/api/native/stop', '/api/native/stop'])
        self.assertEqual(report['controller_sha256']['tools/cyd_tests/ota.py'],
                         hashlib.sha256((ROOT/'tools/cyd_tests/ota.py').read_bytes()).hexdigest())
        self.assert_private(report)

    def test_same_image_success_requires_real_slot_switch_known_boot_and_preservation(self):
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual((code, report['result'], report['successful_update_qualified']), (0, 'PASS', True))
        self.assertEqual((self.transport.partition, self.transport.boot_number), ('app1', 2))
        self.assertEqual(len(self.uploader.calls), 11)
        self.assertTrue(all(x['result'] == 'PASS' for x in report['cases']))
        self.assertTrue(report['finished_stopped'])
        self.assert_private(report)

    def test_all_existing_backends_bind_before_negative_uploads(self):
        for backend in ('continuous', 'legacy'):
            with self.subTest(backend=backend):
                folder = self.folder/backend
                folder.mkdir()
                selected = load_artifact(artifact(folder, backend), backend)
                clock = Clock()
                transport = Transport(clock, selected)
                board = CydBoard('http://board.invalid', selected, transport=transport)
                code = ota.run_acceptance(board, folder/'report.json', clock=clock, uploader=Uploader(transport))
                self.assertEqual(code, 0)

    def test_wrong_chip_mutation_is_c3_not_cyd_and_donor_default_is_unchanged(self):
        raw = self.app.read_bytes()
        case = ota.negative_cases(raw, 20480)[0]
        start = case.body.index(b'\xe9')
        self.assertEqual(struct.unpack_from('<H', case.body, start+12)[0], 5)
        donor = importlib.import_module('tools.esp32c3_tests.ota')
        donor_case = donor.negative_cases(image_bytes(chip=5), 20480)['wrong-chip'][0]
        self.assertEqual(struct.unpack_from('<H', donor_case, donor_case.index(b'\xe9')+12)[0], 0)
        self.assertEqual(donor.image_info(image_bytes(chip=5, project='yoradio_esp32c3_oled_native'))['bytes'], len(raw))

    def test_complete_image_checksum_chip_and_project_are_offline_gates(self):
        for name, raw in [('chip', image_bytes(chip=5)), ('project', image_bytes(project='other')),
                          ('truncated', self.app.read_bytes()[:-1]), ('extra', self.app.read_bytes()+b'0')]:
            with self.subTest(name=name), self.assertRaises(Exception):
                folder = self.folder/name
                folder.mkdir()
                load_artifact(artifact(folder, image=raw), 'pdm')
        raw = bytearray(self.app.read_bytes())
        raw[400] ^= 1
        folder = self.folder/'corrupt'
        folder.mkdir()
        with self.assertRaises(Exception): load_artifact(artifact(folder, image=raw), 'pdm')

    def test_no_write_after_local_config_manifest_or_image_identity_drift(self):
        for name in ('sdkconfig', 'manifest.json', 'app.bin'):
            path = self.app.with_name(name)
            original = path.read_bytes()
            path.write_bytes(original+b' ')
            with self.subTest(name=name), self.assertRaises(Failure): self.board.authorize()
            self.assertFalse(self.transport.writes)
            path.write_bytes(original)

    def test_live_elf_backend_or_non_strict_status_failure_cannot_pass(self):
        self.transport.elf = 'cd'*32
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertEqual(report['cleanup']['result'], 'NOT_AUTHORIZED')
        self.assertFalse(self.uploader.calls or self.transport.writes)

    def test_backend_failure_before_writes(self):
        self.transport.output = 'some other output'
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertFalse(self.uploader.calls or self.transport.writes)

    def test_malformed_status_is_not_an_acceptable_stopped_state(self):
        self.transport.overrides['/api/native/status'] = {'audio': 'false'}
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertFalse(self.uploader.calls)
        self.assertFalse(report['successful_update_qualified'])

    def test_malformed_boot_identity_cannot_qualify_negative_or_positive_gates(self):
        self.transport.overrides['/api/native/health'] = {'boot_id': 'unknown'}
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertFalse(self.uploader.calls)
        self.assertFalse(report['successful_update_qualified'])

    def test_changed_local_artifact_after_http_is_not_used_for_later_writes(self):
        def changed(index, body, kwargs):
            if index == 0:
                config = self.app.with_name('sdkconfig')
                config.write_bytes(config.read_bytes()+b'\n')
        self.uploader.hook = changed
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertEqual(len(self.uploader.calls), 1)
        self.assertEqual(self.transport.writes, ['/api/native/stop'])
        self.assertEqual(report['cleanup']['result'], 'FAIL')

    def test_generic_posts_and_reboot_remain_unavailable(self):
        self.board.authorize()
        for path in ('/update', '/api/native/wifi', '/api/native/settings'):
            with self.subTest(path=path), self.assertRaises(Failure): self.board.request(path, b'payload')
        with self.assertRaises(Failure): self.board.reboot()
        self.assertFalse(self.transport.writes)

    def test_negative_same_image_reboot_is_a_failure_not_wait_image_success(self):
        def mutate(index, body, kwargs):
            if index == 0: self.transport.reboot()
        self.uploader.hook = mutate
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertFalse(report['successful_update_qualified'])
        self.assertEqual(len(self.uploader.calls), 1)
        self.assertEqual(report['cleanup']['result'], 'FAIL')
        self.assert_private(report)

    def test_negative_wrong_status_is_not_a_success(self):
        self.uploader.hook = lambda i, body, kwargs: ota.UploadResult(200, b'OK', len(body))
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(report['cleanup']['result'], 'PASS')
        self.assertEqual(len(self.uploader.calls), 1)
        action = next(x for x in report['cases'] if x['name'] == 'negative:wrong-chip')
        self.assertEqual(action['observations'][-1]['http'], 200)
        self.assert_private(report)

    def test_uptime_rollback_with_same_boot_identity_is_a_failure(self):
        def rollback(index, body, kwargs):
            if index == 0: self.transport.uptime_bias -= 5000
        self.uploader.hook = rollback
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(len(self.uploader.calls), 1)
        self.assertFalse(report['successful_update_qualified'])

    def test_rollback_between_old_and_newest_pre_upload_uptime_is_a_failure(self):
        delayed = False
        def snapshot_delay(path, data):
            nonlocal delayed
            if path == '/api/native/radio' and not delayed:
                delayed = True
                self.clock.sleep(2)
        def rollback(index, body, kwargs):
            if index == 0: self.transport.uptime_bias -= 1000
        self.transport.read_hook, self.uploader.hook = snapshot_delay, rollback
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(len(self.uploader.calls), 1)
        initial = report['cases'][0]['evidence']['initial_boot']['uptime_ms']
        action = next(x for x in report['cases'] if x['name'] == 'negative:wrong-chip')
        newest = next(x['boot']['uptime_ms'] for x in action['observations'] if x['kind'] == 'before-upload')
        rolled_back = next(x['first_boot']['uptime_ms'] for x in action['observations'] if x['kind'] == 'live-frame')
        self.assertLess(initial, rolled_back)
        self.assertLess(rolled_back, newest)
        self.assertFalse(report['successful_update_qualified'])

    def test_reset_reason_change_without_new_boot_identity_is_a_failure(self):
        def changed(index, body, kwargs):
            if index == 0: self.transport.reset_reason = 4
        self.uploader.hook = changed
        self.assertEqual(self.run_gate()[0], 1)

    def test_abort_without_response_needs_stable_identity_and_a_strict_prefix(self):
        def invalid(index, body, kwargs):
            if index == 8: return ota.UploadResult(None, b'', len(body))
        self.uploader.hook = invalid
        self.assertEqual(self.run_gate()[0], 1)

    def test_stall_may_close_without_fabricating_an_http_status(self):
        def no_response(index, body, kwargs):
            if index == 9: return ota.UploadResult(None, b'', len(body)//2)
        self.uploader.hook = no_response
        code, report = self.run_gate()
        self.assertEqual(code, 0)
        stall = next(x for x in report['cases'] if x['name'] == 'negative:stall')
        self.assertIsNone(stall['evidence']['http'])
        self.assertFalse(stall['evidence']['response_observed'])

    def test_abort_transport_failure_is_bounded_and_cleanup_failure_retained(self):
        def unavailable(index, body, kwargs):
            if index == 8: self.transport.outages = 10000
        self.uploader.hook = unavailable
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(report['cleanup']['result'], 'FAIL')
        self.assertLess(self.clock.now, 100)

    def test_nonzero_or_unknown_upload_result_cannot_be_success(self):
        self.uploader.hook = lambda *args: 7
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(report['result'], 'FAIL')
        self.assertFalse(report['successful_update_qualified'])

    def test_unexpected_reset_reason_fails_successful_update_gate(self):
        # The pinned public enum is UNKNOWN0/POWERON1/EXT2/SW3/PANIC4;
        # watchdogs/brownout/unknown are never treated as the selected OTA reboot.
        self.assertEqual(ota.ESP_RST_SW, 3)
        self.uploader.positive_reason = 4
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertFalse(report['successful_update_qualified'])

    def test_second_software_reboot_during_selected_update_is_not_hidden(self):
        health_reads = 0
        def restarted(path, data):
            nonlocal health_reads
            if self.transport.boot_number >= 2 and path == '/api/native/health':
                health_reads += 1
                if health_reads == 5: self.transport.reboot()
        self.transport.read_hook = restarted
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertFalse(report['successful_update_qualified'])
        self.assertEqual(self.transport.boot_number, 3)

    def test_ota_boot_transition_between_http_reads_is_retried_consistently(self):
        pending = False
        def upload_hook(index, body, kwargs):
            nonlocal pending
            if index == 10:
                pending = True
                return ota.UploadResult(200, b'OK', len(body))
        def between_reads(path, data):
            nonlocal pending
            if pending and path == '/api/native/ota':
                pending = False
                self.transport.reboot(switch=True)
        self.uploader.hook, self.transport.read_hook = upload_hook, between_reads
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 0)
        self.assertTrue(report['successful_update_qualified'])

    def test_a_late_http_observation_cannot_pass_its_deadline(self):
        def slow(path, data):
            if path == '/api/native/health': self.clock.sleep(25)
        self.transport.read_hook = slow
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertFalse(self.uploader.calls)
        self.assertFalse(report['successful_update_qualified'])

    def test_successful_http_with_no_slot_switch_is_failure(self):
        self.uploader.positive_switch = False
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertFalse(report['successful_update_qualified'])

    def test_successful_http_without_reboot_is_bounded_failure(self):
        self.uploader.hook = lambda index, body, kwargs: ota.UploadResult(200, b'OK', len(body)) if index == 10 else None
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertFalse(report['successful_update_qualified'])
        self.assertLess(self.clock.now, 100)

    def test_wrong_success_body_fails_without_retaining_response(self):
        self.uploader.positive_body = SECRET.encode()
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assert_private(report)

    def test_wifi_playlist_or_settings_drift_fails_and_never_restores_by_upload(self):
        def mutate(index, body, kwargs):
            if index == 0: self.transport.settings['settings']['volume'] += 1
        self.uploader.hook = mutate
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertEqual(len(self.uploader.calls), 1)
        self.assertEqual(report['cleanup']['result'], 'FAIL')
        self.assert_private(report)

    def test_changed_wifi_metadata_is_not_restored_or_logged(self):
        def changed(index, body, kwargs):
            if index == 0: self.transport.wifi['profiles'][0]['ssid'] = 'changed-private-SSID'
        self.uploader.hook = changed
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(len(self.uploader.calls), 1)
        self.assertNotIn('changed-private-SSID', json.dumps(report))
        self.assert_private(report)

    def test_changed_playlist_is_not_restored_or_logged(self):
        def changed(index, body, kwargs):
            if index == 0: self.transport.playlist += b'changed-private-playlist\n'
        self.uploader.hook = changed
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(len(self.uploader.calls), 1)
        self.assertNotIn('changed-private-playlist', json.dumps(report))
        self.assert_private(report)

    def test_failure_and_cleanup_are_both_recorded_without_error_secrets(self):
        def fail(*args):
            self.transport.fail_stop = True
            raise OSError(SECRET)
        self.uploader.hook = fail
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(report['cases'][1]['result'], 'FAIL')
        self.assertEqual(report['cleanup']['result'], 'FAIL')
        self.assert_private(report)

    def test_partial_report_exists_before_upload_and_interrupt_is_nonzero(self):
        def interrupt(*args):
            partial = json.loads(self.report.read_bytes())
            self.assertEqual(partial['cases'][-1]['result'], 'RUNNING')
            raise KeyboardInterrupt(SECRET)
        self.uploader.hook = interrupt
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(report['cleanup']['result'], 'PASS')
        self.assertTrue(report['interrupted'])
        self.assert_private(report)

    def test_primary_upload_interrupt_is_saved_before_cleanup_interrupt(self):
        cleanup_seen = []
        def cleanup_interrupt(path, data):
            partial = json.loads(self.report.read_bytes())
            if partial['cases'][-1]['name'] == 'cleanup-stop':
                cleanup_seen.append(partial)
                self.assertEqual(partial['result'], 'FAIL')
                self.assertEqual(partial['failure'][0]['type'], 'KeyboardInterrupt')
                primary = next(x for x in partial['cases'] if x['name'] == 'negative:wrong-chip')
                self.assertEqual(primary['result'], 'FAIL')
                self.assertEqual(primary['observations'][-1]['kind'], 'before-upload')
                raise KeyboardInterrupt(SECRET)
        def interrupt(*args):
            self.transport.read_hook = cleanup_interrupt
            raise KeyboardInterrupt(SECRET)
        self.uploader.hook = interrupt
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertTrue(cleanup_seen)
        self.assertEqual(report['failure'][0]['type'], 'KeyboardInterrupt')
        self.assertEqual(report['cleanup']['exception_chain'][0]['type'], 'KeyboardInterrupt')
        self.assertEqual(report['cleanup']['result'], 'FAIL')
        self.assertFalse(report['successful_update_qualified'])
        self.assert_private(report)

    def test_cleanup_only_interrupt_cannot_turn_completed_upload_into_pass(self):
        def interrupt_cleanup(path, data):
            partial = json.loads(self.report.read_bytes())
            if partial['cases'][-1]['name'] == 'cleanup-stop': raise KeyboardInterrupt(SECRET)
        self.transport.read_hook = interrupt_cleanup
        code, report = self.run_gate(same_image_ota=True)
        self.assertEqual(code, 1)
        self.assertEqual(report['result'], 'FAIL')
        self.assertEqual(report['cleanup']['result'], 'FAIL')
        self.assertFalse(report['successful_update_qualified'])
        self.assertFalse(report['finished_stopped'])
        self.assertTrue(report['interrupted'])
        self.assert_private(report)

    def test_system_exit_is_nonzero_and_preserves_cleanup(self):
        def stop(*args): raise SystemExit(7)
        self.uploader.hook = stop
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(report['failure'][0]['type'], 'SystemExit')
        self.assertEqual(report['cleanup']['result'], 'PASS')
        self.assertTrue(report['interrupted'])

    def test_clock_interrupt_after_http_preserves_http_and_boot_before_cleanup(self):
        original_sleep = self.clock.sleep
        armed = False
        def interrupt_clock(seconds):
            nonlocal armed
            if armed:
                armed = False
                raise KeyboardInterrupt(SECRET)
            original_sleep(seconds)
        def arm(index, body, kwargs):
            nonlocal armed
            if index == 0: armed = True
        self.clock.sleep, self.uploader.hook = interrupt_clock, arm
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        primary = next(x for x in report['cases'] if x['name'] == 'negative:wrong-chip')
        self.assertTrue(any(x.get('http') == 400 for x in primary['observations']))
        self.assertTrue(any(x['kind'] == 'live-frame' for x in primary['observations']))
        self.assertEqual(report['cleanup']['result'], 'PASS')
        self.assert_private(report)

    def test_even_private_failure_subclass_messages_are_not_retained(self):
        def fail(*args): raise Failure(SECRET)
        self.uploader.hook = fail
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assert_private(report)

    def test_existing_report_is_never_overwritten(self):
        self.report.write_bytes(b'preserved')
        with self.assertRaises(FileExistsError): self.run_gate()
        self.assertEqual(self.report.read_bytes(), b'preserved')
        self.assertFalse(self.transport.writes)

    def test_exact_playback_and_smartstart_finish_stopped(self):
        spec = ota.playback_spec(dict(codec='aac', profile='HE-AACv2', rate=44100, channels=2, bits=16),
                                 'http://fixture.invalid/?secret='+SECRET)
        self.uploader.auto_play = True
        code, report = self.run_gate(same_image_ota=True, playback=spec)
        self.assertEqual(code, 0)
        self.assertTrue(report['successful_update_qualified'] and report['finished_stopped'])
        self.assertFalse(self.transport.audio)
        self.assertEqual(len(self.uploader.calls), 11)
        self.assertIn('/api/native/play?codec=aac', self.transport.writes)
        self.assert_private(report)

    def test_wrong_pcm_fixture_blocks_positive_upload(self):
        self.transport.rate = 22050
        spec = ota.playback_spec(dict(codec='aac', profile='HE-AACv2', rate=44100, channels=2, bits=16),
                                 'http://fixture.invalid/')
        code, report = self.run_gate(same_image_ota=True, playback=spec)
        self.assertEqual(code, 1)
        self.assertEqual(len(self.uploader.calls), 10)
        self.assertEqual(report['cleanup']['result'], 'PASS')

    def test_playback_needs_explicit_same_image_selection(self):
        spec = ota.playback_spec(dict(codec='mp3', profile='mp3', rate=44100, channels=2, bits=16),
                                 'http://fixture.invalid/')
        code, report = self.run_gate(playback=spec)
        self.assertEqual(code, 1)
        self.assertFalse(self.transport.writes or self.uploader.calls)

    def test_truthy_strings_do_not_authorize_a_successful_update_or_enter_reports(self):
        code, report = self.run_gate(same_image_ota=SECRET)
        self.assertEqual(code, 1)
        self.assertFalse(self.transport.writes or self.uploader.calls)
        self.assertFalse(report['successful_update_qualified'])
        self.assert_private(report)

    def test_programmatic_playback_fixture_is_validated_before_any_write(self):
        spec = ota.playback_spec(dict(codec='aac', profile='HE-AACv2', rate=44100, channels=2, bits=16),
                                 'http://fixture.invalid/')
        spec['label'] = SECRET
        code, report = self.run_gate(same_image_ota=True, playback=spec)
        self.assertEqual(code, 1)
        self.assertFalse(self.transport.writes or self.uploader.calls)
        self.assert_private(report)

    def test_raw_http_upload_uses_fixed_path_length_and_closes(self):
        connection = Connection(Response(200, b'OK'))
        calls = []
        def factory(*args, **kwargs): calls.append((args, kwargs)); return connection
        body = ota.multipart(self.app.read_bytes())
        result = ota.upload('https://board.invalid:443', body, connection_factory=factory, clock=self.clock)
        self.assertEqual((result.status, result.body, result.sent_bytes), (200, b'OK', len(body)))
        self.assertEqual(connection.requests, [('POST', '/update')])
        self.assertEqual(connection.headers['Content-Length'], str(len(body)))
        self.assertEqual(b''.join(connection.sent), body)
        self.assertTrue(connection.closed)
        self.assertEqual(calls[0][0], ('https', 'board.invalid', 443))

    def test_raw_disconnect_is_a_prefix_without_response_and_stall_waits_past_idle(self):
        body = ota.multipart(self.app.read_bytes())
        connection = Connection()
        result = ota.upload('http://board.invalid', body, interrupt='disconnect', clock=self.clock,
                            connection_factory=lambda *a, **k: connection)
        self.assertIsNone(result.status)
        self.assertLess(result.sent_bytes, len(body))
        self.assertEqual(connection.response_calls, 0)
        self.assertTrue(connection.closed)
        stalled = Connection(Response(408, b'timeout'))
        result = ota.upload('http://board.invalid', body, interrupt='stall', clock=self.clock,
                            connection_factory=lambda *a, **k: stalled)
        self.assertEqual(result.status, 408)
        self.assertGreater(self.clock.now, 10)
        self.assertTrue(stalled.closed)

    def test_raw_stall_close_is_absence_and_other_transport_errors_propagate(self):
        body = ota.multipart(self.app.read_bytes())
        for interrupt in ('stall', None):
            connection = Connection(error=http.client.RemoteDisconnected(SECRET))
            if interrupt:
                result = ota.upload('http://board.invalid', body, interrupt=interrupt, clock=self.clock,
                                    connection_factory=lambda *a, **k: connection)
                self.assertIsNone(result.status)
            else:
                with self.assertRaises(http.client.RemoteDisconnected):
                    ota.upload('http://board.invalid', body, connection_factory=lambda *a, **k: connection)
            self.assertTrue(connection.closed)

    def test_raw_declared_oversize_and_prefix_are_preserved(self):
        connection = Connection(Response(413, b'too large'))
        result = ota.upload('http://board.invalid', b'x'*4000, declared=9000, send_limit=2048,
                            connection_factory=lambda *a, **k: connection)
        self.assertEqual(connection.headers['Content-Length'], '9000')
        self.assertEqual(result.sent_bytes, 2048)
        self.assertEqual(result.status, 413)

    def test_raw_send_failure_and_oversized_response_close_the_connection(self):
        connection = Connection(Response(200, b'X'*1025))
        with self.assertRaises(Failure):
            ota.upload('http://board.invalid', b'body', connection_factory=lambda *a, **k: connection)
        self.assertTrue(connection.closed)
        broken = Connection()
        broken.send = lambda data: (_ for _ in ()).throw(OSError(SECRET))
        with self.assertRaises(OSError):
            ota.upload('http://board.invalid', b'body', connection_factory=lambda *a, **k: broken)
        self.assertTrue(broken.closed)

    def test_invalid_raw_origin_or_lengths_do_not_open_a_connection(self):
        factory = lambda *a, **k: self.fail('Invalid request must not create a transport')
        for origin, kwargs in [('http://user:password@board.invalid', {}),
                               ('http://board.invalid/update', {}),
                               ('http://board.invalid', {'declared': True}),
                               ('http://board.invalid', {'send_limit': False})]:
            with self.subTest(origin=origin, kwargs=kwargs), self.assertRaises(Failure):
                ota.upload(origin, b'body', connection_factory=factory, **kwargs)

    def test_cli_requires_explicit_suite_and_invalid_artifact_retains_partial_failure(self):
        with self.assertRaises(SystemExit) as raised:
            ota.main(['--board', 'http://board.invalid', '--firmware', str(self.app), '--backend', 'pdm',
                      '--output', str(self.report)])
        self.assertEqual(raised.exception.code, 2)
        self.assertFalse(self.report.exists())
        self.app.write_bytes(b'bad')
        code = ota.main(['--board', 'http://board.invalid', '--firmware', str(self.app), '--backend', 'pdm',
                         '--negative-only', '--output', str(self.report)])
        self.assertEqual(code, 1)
        report = json.loads(self.report.read_bytes())
        self.assertEqual(report['cleanup']['result'], 'NOT_AUTHORIZED')
        self.assert_private(report)

    def test_complete_same_image_cli_runs_entirely_through_fake_seams(self):
        with patch.object(ota, 'CydBoard', return_value=self.board), \
                patch.object(ota, 'upload', self.uploader), patch.object(ota, 'time', self.clock):
            code = ota.main(['--board', 'http://board.invalid', '--firmware', str(self.app), '--backend', 'pdm',
                             '--same-image-ota', '--output', str(self.report)])
        self.assertEqual(code, 0)
        report = json.loads(self.report.read_bytes())
        self.assertTrue(report['successful_update_qualified'])
        self.assertEqual(len(self.uploader.calls), 11)
        self.assert_private(report)


if __name__ == '__main__': unittest.main()
