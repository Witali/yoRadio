"""Explicit CYD same-image OTA acceptance; imports perform no I/O.

Only /update writes an application. Negative-only acceptance never qualifies a
successful update. Settings/Wi-Fi/playlist snapshots stay in memory. No serial,
generic reboot, settings edits, restoration uploads or deployment fallback exist.
Run with python -m tools.cyd_tests.ota; actual board execution requires an
explicit suite, selected app/backend and fresh output report.
"""
import argparse
from dataclasses import dataclass
import http.client
import json
import os
from pathlib import Path
import re
import struct
import sys
import tempfile
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
if not __package__:
    sys.path.insert(0, str(ROOT))

from tools.cyd_tests.common import CydBoard, Failure, digest, load_artifact, require
from tools.esp32c3_tests.common import exception_details, matches
from tools.esp32c3_tests.ota import BOUNDARY, multipart, snapshot, verify_snapshot

# Pinned ESP-IDF6.0.2 public components/esp_system/include/esp_system.h:
# enum starts UNKNOWN=0, POWERON=1, EXT=2, SW=3 (esp_restart), PANIC=4.
# CYD web_ota.c commits web_reboot.c's esp_restart; no other reset qualifies.
ESP_RST_SW = 3
POLL = .25
OBSERVATION_SECONDS = 2
TRANSPORT_ERRORS = (OSError, TimeoutError, http.client.HTTPException)


@dataclass(frozen=True)
class UploadResult:
    status: object
    body: bytes
    sent_bytes: int


@dataclass(frozen=True)
class Negative:
    name: str
    body: bytes
    expected: object
    declared: object = None
    interrupt: object = None
    send_limit: object = None


def negative_cases(image, max_body_size):
    require(type(max_body_size) is int and 0 < max_body_size < 0xffffffff,
            'Invalid live OTA body limit')
    chip = bytearray(image)
    struct.pack_into('<H', chip, 12, 5)  # ESP32-C3, deliberately different from CYD chip0.
    project = bytearray(image)
    project[80:112] = b'wrong_project'.ljust(32, b'\0')
    corrupt = bytearray(image)
    corrupt[len(corrupt)//2] ^= 1
    truncated = image[:-min(1024, max(1, len(image)//4))]
    return [Negative('wrong-chip', multipart(chip), 400, send_limit=2048),
            Negative('wrong-project', multipart(project), 400, send_limit=2048),
            Negative('corrupt-image', multipart(corrupt), 400),
            Negative('truncated-image', multipart(truncated), 400),
            Negative('extra-byte', multipart(image + b'\0'), 400),
            Negative('missing-boundary', multipart(image, closed=False), 400),
            Negative('spiffs-target', multipart(image, target='spiffs'), 400, send_limit=2048),
            # native_ota_http.c rejects Content-Length before body admission.
            Negative('oversized-request', multipart(image)[:2048], 413, declared=max_body_size+1),
            Negative('disconnect', multipart(image), None, interrupt='disconnect'),
            # NATIVE_OTA_IDLE_US=10000000; a silent sender reaches HTTP408.
            Negative('stall', multipart(image), 408, interrupt='stall')]


def upload(origin, body, *, declared=None, interrupt=None, send_limit=None,
           clock=time, connection_factory=None):
    """A single fixed-route raw request, with fake HTTP/clock seams for tests.

    Abort cases send only a strict prefix. A missing abort response is not an
    HTTP success; the caller must separately prove bounded stable live identity.
    No redirects, retry, reconnect or alternative deployment path is used.
    """
    url = urlsplit(origin)
    require(url.scheme in ('http', 'https') and url.hostname and not url.username and
            not url.password and not url.query and not url.fragment and url.path in ('', '/'),
            'Expected a plain OTA board origin')
    require(type(body) is bytes and body and interrupt in (None, 'disconnect', 'stall'),
            'Invalid explicit OTA upload input')
    require(declared is None or type(declared) is int and declared > 0, 'Invalid declared OTA length')
    require(send_limit is None or type(send_limit) is int and send_limit > 0, 'Invalid OTA prefix limit')
    if connection_factory is None:
        cls = http.client.HTTPSConnection if url.scheme == 'https' else http.client.HTTPConnection
        connection = cls(url.hostname, url.port, timeout=30)
    else:
        connection = connection_factory(url.scheme, url.hostname, url.port, timeout=30)
    sent = 0
    try:
        connection.putrequest('POST', '/update')
        connection.putheader('Content-Type', 'multipart/form-data; boundary=' + BOUNDARY)
        connection.putheader('Content-Length', str(len(body) if declared is None else declared))
        connection.putheader('Connection', 'close')
        connection.endheaders()
        if interrupt:
            prefix = body[:min(8192, max(1, len(body)//2))]
            connection.send(prefix)
            sent = len(prefix)
            if interrupt == 'disconnect':
                return UploadResult(None, b'', sent)
            clock.sleep(13)
        else:
            payload = body if send_limit is None else body[:send_limit]
            for start in range(0, len(payload), 4096):
                part = payload[start:start+4096]
                connection.send(part)
                sent += len(part)
        try:
            response = connection.getresponse()
            response_body = response.read(1025)
        except TRANSPORT_ERRORS:
            if interrupt == 'stall':
                return UploadResult(None, b'', sent)
            raise
        require(type(response.status) is int and len(response_body) <= 1024,
                'Invalid or oversized OTA response')
        return UploadResult(response.status, response_body, sent)
    finally:
        connection.close()


def boot_identity(board):
    value = board.json('/api/native/health')
    require(type(value) is dict and type(value.get('schema')) is int and value['schema'] == 1 and
            type(value.get('boot_id')) is str and re.fullmatch('[0-9a-f]{16}', value['boot_id']) and
            type(value.get('uptime_ms')) is int and 0 <= value['uptime_ms'] < 1 << 64 and
            type(value.get('reset_reason')) is int and 0 <= value['reset_reason'] <= 15 and
            type(value.get('cores')) is int and value['cores'] == 2,
            'Missing or invalid CYD boot identity')
    return {key: value[key] for key in ('boot_id', 'uptime_ms', 'reset_reason')}


class OtaReport:
    """Persist partial action/cleanup state without response bodies or locations."""
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('x', encoding='utf-8'):
            pass
        self.data = dict(schema=1, result='RUNNING', cases=[], cleanup=None,
                         successful_update_qualified=False, finished_stopped=False,
                         scope='Selected HTTP OTA gates only; no physical/serial/acoustic qualification')
        self.data['controller_sha256'] = {
            name: digest((ROOT/name).read_bytes()) for name in (
                'tools/cyd_tests/ota.py', 'tools/cyd_tests/common.py',
                'tools/esp32c3_tests/ota.py', 'tools/esp32c3_tests/common.py',
                'tools/export_cyd_production.py')}
        self.save()

    def save(self):
        # Atomic publication preserves the preceding valid partial report.
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent,
                                         prefix=self.path.name+'.', suffix='.pending', delete=False) as output:
            json.dump(self.data, output, indent=2)
            output.write('\n')
            temporary = output.name
        os.replace(temporary, self.path)

    def step(self, name, action, clock):
        row = dict(name=name, result='RUNNING', started=clock.perf_counter())
        self.data['cases'].append(row)
        self.save()
        try:
            result = action()
            row.update(result='PASS', evidence=result)
            return result
        except BaseException as error:
            row.update(result='FAIL', interrupted=not isinstance(error, Exception), exception_chain=exception_details(error))
            raise
        finally:
            row['ended'] = clock.perf_counter()
            self.save()

    def observed(self, kind, **technical):
        # Call sites pass fixed fields only; never raw responses/settings/URLs.
        self.data['cases'][-1].setdefault('observations', []).append(dict(kind=kind, **technical))
        self.save()


def playback_spec(value, url):
    """Exact controlled PCM fixture metadata; URL/settings never enter reports."""
    require(type(value) is dict and set(value) == {'codec', 'profile', 'rate', 'channels', 'bits'},
            'Expected exact controlled playback format metadata')
    codec = value['codec']
    require(codec in ('aac', 'mp3', 'flac') and
            value['profile'] in {'aac': ('AAC-LC', 'HE-AAC', 'HE-AACv2'),
                                'mp3': ('mp3',), 'flac': ('flac',)}[codec] and
            type(value['rate']) is int and 8000 <= value['rate'] <= 192000 and
            type(value['channels']) is int and value['channels'] in (1, 2) and
            type(value['bits']) is int and value['bits'] in (16, 24, 32),
            'Invalid controlled playback format')
    parsed = urlsplit(url)
    require(parsed.scheme in ('http', 'https') and parsed.hostname and
            not parsed.username and not parsed.password and not parsed.fragment,
            'Expected a controlled HTTP playback URL')
    return dict(value, url=url, label={'aac': 'AAC PCM', 'mp3': 'MP3', 'flac': 'FLAC'}[codec])


class Acceptance:
    def __init__(self, board, report, *, same_image_ota=False, playback=None, uploader=None, clock=None):
        self.board, self.report = board, report
        self.clock, self.uploader = clock if clock is not None else time, uploader if uploader is not None else upload
        self.same_image_ota, self.playback = same_image_ota, playback
        self.authorized = False
        self.info = self.boot = self.before = None

    def frame(self):
        first = boot_identity(self.board)
        info = self.board.check_identity()
        state = self.board.status()
        last = boot_identity(self.board)
        return first, info, state, last

    def observe(self, info, boot, *, updating=False, timeout=45):
        deadline, stable_since, count = self.clock.perf_counter()+timeout, None, 0
        previous = boot
        new_boots, stopped_new_boot = set(), False
        while self.clock.perf_counter() < deadline:
            try:
                first, actual, state, last = self.frame()
            except TRANSPORT_ERRORS as error:
                self.report.observed('transport-gap', exception_chain=exception_details(error))
                stable_since, count = None, 0
                self.clock.sleep(POLL)
                continue
            self.report.observed('live-frame', first_boot=first, last_boot=last,
                                 partition=actual['partition'], live_elf_sha256=actual['app_elf_sha256'],
                                 audio=state['audio'], connecting=state['connecting'], network=state['network'])
            require(self.clock.perf_counter() < deadline, 'CYD observation returned after its deadline')
            require(first['boot_id'] != last['boot_id'] or first['reset_reason'] == last['reset_reason'],
                    'Reset reason changed within one CYD boot')
            if updating:
                for row in (first, last):
                    if row['boot_id'] != boot['boot_id']:
                        new_boots.add(row['boot_id'])
                        require(row['reset_reason'] == ESP_RST_SW, 'OTA restarted with an unexpected reset reason')
                require(len(new_boots) <= 1, 'Multiple or unexpected CYD reboots during OTA')
                if first['boot_id'] != last['boot_id']:
                    stable_since, count = None, 0
                    self.clock.sleep(POLL)
                    continue
                if last['boot_id'] == boot['boot_id']:
                    require(last['reset_reason'] == boot['reset_reason'], 'Reset reason changed without a new boot')
                    require(actual['partition'] != info['partition'], 'OTA partition changed without a reboot')
                    require(last['uptime_ms'] >= previous['uptime_ms'], 'CYD uptime decreased without a new boot')
                    previous = last
                    self.clock.sleep(POLL)
                    continue
            else:
                require(first['boot_id'] == last['boot_id'] == boot['boot_id'], 'Unexpected CYD reboot')
                require(last['reset_reason'] == boot['reset_reason'], 'Reset reason changed without a new boot')
            require(last['uptime_ms'] >= first['uptime_ms'] and
                    (last['boot_id'] != previous['boot_id'] or last['uptime_ms'] >= previous['uptime_ms']),
                    'CYD uptime decreased')
            require(actual['partition'] == info['partition'], 'Unexpected live OTA slot')
            if updating and not stopped_new_boot:
                # The preserved smartstart setting may start saved playback.
                # Stop only after verifying the expected new software boot/slot.
                self.board.stop()
                stopped_new_boot = True
                stable_since, count = None, 0
                self.clock.sleep(POLL)
                continue
            require(state['audio'] is False and state['connecting'] is False,
                    'CYD must remain stopped during OTA verification')
            require(state['network'] == 'client', 'CYD Wi-Fi client did not reconnect')
            previous = last
            if stable_since is None: stable_since = self.clock.perf_counter()
            count += 1
            if count >= 3 and self.clock.perf_counter()-stable_since >= OBSERVATION_SECONDS:
                return actual, last
            self.clock.sleep(POLL)
        raise Failure('Bounded stable CYD image/boot/slot observations were not obtained')

    def prepare(self):
        require(type(self.same_image_ota) is bool, 'Successful OTA selection must be an explicit boolean')
        require(self.playback is None or self.same_image_ota, 'Playback OTA needs explicit same-image authorization')
        if self.playback is not None:
            fields = {'codec', 'profile', 'rate', 'channels', 'bits'}
            require(type(self.playback) is dict and set(self.playback) == fields | {'url', 'label'},
                    'Expected a validated controlled playback fixture')
            require(self.playback == playback_spec({k: self.playback[k] for k in fields}, self.playback['url']),
                    'Controlled playback fixture format differs from its validated profile')
        self.info = self.board.authorize()
        self.authorized = True
        self.boot = boot_identity(self.board)
        self.board.status()
        self.image = self.board.artifact.app.read_bytes()
        require(digest(self.image) == self.board.artifact.hashes[self.board.artifact.app],
                'Selected application bytes changed after identity validation')
        require(len(self.image) <= self.info['max_size'] and
                len(multipart(self.image)) <= self.info['max_body_size'], 'Selected image exceeds live OTA capacity')
        self.board.stop()
        self.info, self.boot = self.observe(self.info, self.boot)
        self.before = snapshot(self.board)
        return dict(artifact=dict(self.board.artifact.evidence), initial_partition=self.info['partition'],
                    initial_boot=self.boot, stopped=True, boot_identity_observed=True)

    def send(self, body, **kwargs):
        active = self.board.check_identity()
        boot = boot_identity(self.board)
        require(active == self.info and boot['boot_id'] == self.boot['boot_id'] and
                boot['reset_reason'] == self.boot['reset_reason'] and
                boot['uptime_ms'] >= self.boot['uptime_ms'], 'CYD changed before an authorized OTA write')
        # Subsequent observations must not roll back below this newest verified
        # sample, even when they remain above the previous stable-window sample.
        self.boot = boot
        self.report.observed('before-upload', partition=active['partition'], boot=boot,
                             live_elf_sha256=active['app_elf_sha256'])
        result = self.uploader(self.board.origin, body, clock=self.clock, **kwargs)
        require(isinstance(result, UploadResult) and type(result.sent_bytes) is int and
                0 < result.sent_bytes <= len(body) and type(result.body) is bytes and
                (result.status is None or type(result.status) is int), 'Invalid upload transport result')
        self.report.observed('upload-result', http=result.status, response_observed=result.status is not None,
                             sent_bytes=result.sent_bytes, planned_body_bytes=len(body))
        return result

    def reject(self, case):
        result = self.send(case.body, declared=case.declared, interrupt=case.interrupt, send_limit=case.send_limit)
        if case.interrupt:
            require(result.sent_bytes < len(case.body), 'Abort sent a complete OTA body')
            require(result.status is None or case.interrupt == 'stall' and result.status == 408,
                    'Unexpected abort HTTP response')
        else:
            require(result.status == case.expected, 'Unexpected negative OTA HTTP status')
        self.info, self.boot = self.observe(self.info, self.boot, timeout=20)
        preserved = verify_snapshot(self.board, self.before)
        return dict(http=result.status, response_observed=result.status is not None,
                    intentional_abort=case.interrupt is not None, active_image_unchanged=True,
                    slot_unchanged=True, partition=self.info['partition'], boot_unchanged=True, boot=self.boot, **preserved)

    def wait_playback(self):
        spec, count, deadline = self.playback, 0, self.clock.perf_counter()+12
        while self.clock.perf_counter() < deadline:
            state = self.board.status()
            require(self.clock.perf_counter() < deadline, 'Playback observation returned after its deadline')
            correct = matches(state, spec) and state['codec'] == spec['codec'].upper()
            count = count+1 if correct else 0
            if count >= 3: return
            self.clock.sleep(.3)
        raise Failure('Controlled full PCM fixture format was not stable before OTA')

    def accept(self):
        require(self.same_image_ota, 'Successful OTA was not explicitly selected')
        if self.playback:
            self.board.play(self.playback['url'], self.playback['codec'])
            self.wait_playback()
        old_partition = self.info['partition']
        target = dict(self.info, partition='app1' if old_partition == 'app0' else 'app0')
        result = self.send(multipart(self.image))
        require(result.status == 200 and result.body == b'OK' and result.sent_bytes == len(multipart(self.image)),
                'Successful OTA did not confirm complete HTTP200 OK')
        self.info, self.boot = self.observe(target, self.boot, updating=True)
        preserved = verify_snapshot(self.board, self.before)
        self.report.data['successful_update_qualified'] = True
        return dict(http=200, live_elf_verified=True, slot_switched=True, software_boot_verified=True,
                    before_partition=old_partition, partition=self.info['partition'], boot=self.boot,
                    live_elf_sha256=self.info['app_elf_sha256'],
                    controlled_playback_before=self.playback is not None, **preserved)

    def cleanup(self):
        require(self.authorized, 'No board write was authorized')
        self.board.stop()
        self.info, self.boot = self.observe(self.info, self.boot, timeout=20)
        if self.before is not None: verify_snapshot(self.board, self.before)
        return dict(stopped=True, expected_boot_preserved=True, snapshot_preserved=self.before is not None)

    def run(self):
        failed = False
        self.report.data['selected'] = dict(negative=True, same_image_ota=self.same_image_ota is True,
                                            controlled_playback=self.playback is not None)
        self.report.save()
        try:
            self.report.step('preflight-and-stop', self.prepare, self.clock)
            for case in negative_cases(self.image, self.info['max_body_size']):
                self.report.step('negative:'+case.name, lambda c=case: self.reject(c), self.clock)
            if self.same_image_ota:
                self.report.step('same-image-ota', self.accept, self.clock)
        except BaseException as error:
            failed = True
            self.report.data['failure'] = exception_details(error)
            self.report.data.update(result='FAIL', interrupted=not isinstance(error, Exception),
                                    successful_update_qualified=False)
            # Publish the primary failure and preceding HTTP/boot observations
            # before any cleanup request, including an interrupted cleanup.
            self.report.save()
        finally:
            if self.authorized:
                try:
                    result = self.report.step('cleanup-stop', self.cleanup, self.clock)
                    self.report.data.update(cleanup=dict(result='PASS', evidence=result), finished_stopped=True)
                except BaseException as error:
                    failed = True
                    self.report.data['cleanup'] = dict(result='FAIL', interrupted=not isinstance(error, Exception),
                                                       exception_chain=exception_details(error))
                    self.report.data.update(result='FAIL', successful_update_qualified=False)
                    self.report.data['interrupted'] = self.report.data.get('interrupted', False) or not isinstance(error, Exception)
                    self.report.save()
            else:
                self.report.data['cleanup'] = dict(result='NOT_AUTHORIZED', writes=0)
            self.report.data['result'] = 'FAIL' if failed else 'PASS'
            if failed: self.report.data['successful_update_qualified'] = False
            self.report.save()
        return 1 if failed else 0


def run_acceptance(board, output, **kwargs):
    return Acceptance(board, OtaReport(output), **kwargs).run()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--backend', choices=('pdm', 'continuous', 'legacy'), required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--negative-only', action='store_true')
    group.add_argument('--same-image-ota', action='store_true')
    parser.add_argument('--play-url')
    parser.add_argument('--play-format', type=Path, help='Controlled codec/profile/rate/channels/bits JSON')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    report = OtaReport(args.output)
    try:
        require(bool(args.play_url) == bool(args.play_format), 'Playback URL and exact format must be selected together')
        playback = playback_spec(json.loads(args.play_format.read_bytes()), args.play_url) if args.play_format else None
        artifact = load_artifact(args.firmware, args.backend)
        board = CydBoard(args.board, artifact)
    except BaseException as error:
        report.data.update(result='FAIL', interrupted=not isinstance(error, Exception), failure=exception_details(error),
                           cleanup=dict(result='NOT_AUTHORIZED', writes=0))
        report.save()
        return 1
    return Acceptance(board, report, same_image_ota=args.same_image_ota, playback=playback).run()


if __name__ == '__main__':
    sys.exit(main())
