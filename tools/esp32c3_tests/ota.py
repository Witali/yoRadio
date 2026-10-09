"""Repeat OTA acceptance on a board already running the selected application.

Uploads only the app, never NVS/SPIFFS/bootloader. All response bodies containing
settings remain in memory. Negative requests may stop playback; reboot restores
the saved station. Physical power-cut recovery is a separate manual test.
"""
import argparse
import http.client
import json
from pathlib import Path
import socket
import struct
import sys
import time
from urllib.parse import urlsplit

from common import Board, Failure, Report, fixtures, matches, require, sha


BOUNDARY = 'yoradio-c3-acceptance-20260930'


def image_info(data):
    require(len(data) > 288 and data[0] == 0xe9, 'Not an ESP application image')
    require(struct.unpack_from('<H',data,12)[0] == 5, 'Not an ESP32-C3 image')
    require(struct.unpack_from('<I',data,32)[0] == 0xabcd5432, 'Missing app descriptor')
    require(data[80:112].split(b'\0')[0] == b'yoradio_esp32c3_oled_native', 'Wrong application project')
    return dict(app_elf_sha256=data[176:208].hex(), sha256=sha(data), bytes=len(data))


def multipart(image, target='fw', closed=True):
    prefix = (f'--{BOUNDARY}\r\nContent-Disposition: form-data; name="updatetarget"\r\n\r\n{target}'
              f'\r\n--{BOUNDARY}\r\nContent-Disposition: form-data; name="update"; filename="app.bin"'
              '\r\nContent-Type: application/octet-stream\r\n\r\n').encode()
    return prefix + image + (f'\r\n--{BOUNDARY}--\r\n'.encode() if closed else b'')


def negative_cases(image, max_size):
    chip = bytearray(image); struct.pack_into('<H',chip,12,0)
    project = bytearray(image); project[80:112] = b'wrong_project'.ljust(32,b'\0')
    corrupt = bytearray(image); corrupt[len(image)//2] ^= 1
    return {
        'wrong-chip': (multipart(chip), None),
        'wrong-project': (multipart(project), None),
        'corrupt-image': (multipart(corrupt), None),
        'truncated-image': (multipart(image[:-1024]), None),
        'extra-byte': (multipart(image+b'\0'), None),
        'missing-boundary': (multipart(image,closed=False), None),
        'spiffs-target': (multipart(image,target='spiffs'), None),
        'oversized-request': (multipart(image)[:2048],max_size+2049),
    }


def upload(origin, body, declared=None, interrupt=None, pace=0, send_limit=None):
    url = urlsplit(origin)
    cls = http.client.HTTPSConnection if url.scheme == 'https' else http.client.HTTPConnection
    conn = cls(url.hostname, url.port, timeout=30)
    try:
        conn.putrequest('POST','/update')
        conn.putheader('Content-Type','multipart/form-data; boundary='+BOUNDARY)
        conn.putheader('Content-Length',str(len(body) if declared is None else declared))
        conn.putheader('Connection','close')
        conn.endheaders()
        if interrupt:
            conn.send(body[:8192])
            if interrupt == 'disconnect':
                return None, b''
            time.sleep(13)
        else:
            payload = body if send_limit is None else body[:send_limit]
            for pos in range(0,len(payload),4096):
                conn.send(payload[pos:pos+4096])
                if pace:
                    time.sleep(pace)
        response = conn.getresponse()
        return response.status, response.read()
    finally:
        conn.close()


def wait_image(board, digest, partition, timeout=45):
    deadline = time.monotonic()+timeout
    while time.monotonic() < deadline:
        try:
            info = board.info()
            if info['app_elf_sha256'] == digest and info['partition'] == partition:
                board.status()
                return info
        except (OSError,TimeoutError,ValueError,http.client.HTTPException):
            pass
        time.sleep(.5)
    raise Failure('Booted app hash/partition did not match the uploaded image')


def snapshot(board):
    # In-memory only, no raw files or credential hashes in reports.
    return dict(wifi=board.request('/data/wifi.csv',timeout=30),
                playlist=board.request('/data/playlist.csv',timeout=30), settings=board.settings())


def verify_snapshot(board, before):
    after = snapshot(board)
    require(before == after, 'OTA changed Wi-Fi, playlist or exposed settings')
    return dict(wifi_unchanged=True, playlist_unchanged=True, settings_unchanged=True)


def wait_playback(board, spec=None, timeout=12):
    """Require full fixture format before OTA; preserve the generic flag-only CLI."""
    deadline = time.monotonic()+timeout
    consecutive = 0
    while time.monotonic() < deadline:
        state = board.status()
        correct = matches(state, spec) if spec is not None else state.get('audio') is True
        consecutive = consecutive+1 if correct else 0
        if consecutive >= (3 if spec is not None else 1):
            return state
        time.sleep(.3)
    raise Failure('Expected playback format was not stable before OTA')


def timed_action(report, name, action):
    """Persist action boundaries on the serial-capture monotonic clock.

    Names come from fixed test operations. Do not retain callback results or
    exception messages: these can include private response bodies and URLs.
    A returned action is not necessarily a passed acceptance gate.
    """
    report.data['timeline_clock'] = 'time.monotonic seconds'
    rows = report.data.setdefault('timeline', [])
    rows.append(dict(action=name, event='begin', at=time.monotonic()))
    report.save()
    try:
        result = action()
    except BaseException as error:
        rows.append(dict(action=name, event='raised', at=time.monotonic(),
                         exception=type(error).__name__))
        report.save()
        raise
    rows.append(dict(action=name, event='returned', at=time.monotonic()))
    report.save()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--suite', choices=('negative','roundtrip','while-playing','slow'), action='append', required=True)
    parser.add_argument('--play-url', help='Controlled audio URL for --suite while-playing')
    parser.add_argument('--play-fixture', help='Require this built-in fixture rate/channels/profile before OTA')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    play_spec = None
    if args.play_fixture:
        known = fixtures()
        require(args.play_fixture in known and 'rate' in known[args.play_fixture], 'Unknown concrete playback fixture')
        play_spec = known[args.play_fixture]
    board = Board(args.board)
    board.status()
    image = args.firmware.read_bytes()
    expected = image_info(image)
    initial = board.info()
    require(initial['app_elf_sha256'] == expected['app_elf_sha256'],
            'Run this repeatability test on the same firmware already running on the board')
    require(len(image) <= initial['max_size'], 'Image does not fit OTA slot')
    board.stop()
    before = snapshot(board)
    report = Report(args.output, initial)
    report.data['image'] = expected
    if play_spec is not None:
        report.data['play_fixture'] = {k:play_spec[k] for k in
            ('codec','profile','rate','channels','bits','sha256')}

    def reject(name, body, declared=None, interrupt=None):
        active = board.info()
        # These errors are detectable from the first part/header. Let the
        # receiver return its rejection instead of racing a megabyte send
        # against the receiver's bounded drain/close window.
        limit = 2048 if name in ('wrong-chip','wrong-project','spiffs-target') else None
        status, _ = timed_action(report, 'ota:'+name+':upload',
            lambda: upload(args.board,body,declared,interrupt,send_limit=limit))
        if interrupt != 'disconnect':
            require(status == 400, f'Expected HTTP 400, received {status}')
        time.sleep(1 if interrupt != 'disconnect' else 2)
        timed_action(report, 'ota:'+name+':verify-active-image',
            lambda: wait_image(board,active['app_elf_sha256'],active['partition']))
        return dict(http=status, active_image_unchanged=True, **verify_snapshot(board,before))

    def accepted(name, slow=False, playing=False):
        playback = None
        if playing:
            from common import Blocked
            if not args.play_url:
                raise Blocked('Provide --play-url for OTA during active playback')
            timed_action(report, name+':play-request', lambda: board.play(args.play_url))
            playback = timed_action(report, name+':stable-playback',
                lambda: wait_playback(board, play_spec))
        active = board.info()
        target = 'app1' if active['partition'] == 'app0' else 'app0'
        start = time.monotonic()
        status, body = timed_action(report, name+':upload',
            lambda: upload(args.board,multipart(image),pace=.08 if slow else 0))
        require(status == 200 and body == b'OK', 'OTA did not return HTTP 200 OK')
        booted = timed_action(report, name+':verify-boot',
            lambda: wait_image(board,expected['app_elf_sha256'],target))
        return dict(partition=booted['partition'], elapsed_seconds=time.monotonic()-start,
                    hash_verified=True, playback_before=playback, **verify_snapshot(board,before))

    try:
        if 'negative' in args.suite:
            for name, (body, declared) in negative_cases(image,initial['max_size']).items():
                report.case('ota:'+name, lambda n=name,b=body,d=declared: reject(n,b,d))
            for interrupt in ('disconnect','stall'):
                report.case('ota:'+interrupt, lambda i=interrupt: reject(i,multipart(image),interrupt=i))
        if 'roundtrip' in args.suite:
            for i in range(2):
                name = 'ota:roundtrip:'+str(i+1)
                report.case(name, lambda n=name: accepted(n))
        if 'while-playing' in args.suite:
            report.case('ota:while-playing',lambda: accepted('ota:while-playing',playing=True))
        if 'slow' in args.suite:
            report.case('ota:slow',lambda: accepted('ota:slow',slow=True))
    finally:
        def restore():
            partition = board.info()['partition']
            timed_action(report, 'restore-saved-station:reboot-request', board.reboot)
            time.sleep(3)
            timed_action(report, 'restore-saved-station:verify-boot',
                lambda: wait_image(board,expected['app_elf_sha256'],partition))
            return verify_snapshot(board,before)
        report.case('restore-saved-station',restore)
    return report.exit_code()


if __name__ == '__main__':
    sys.exit(main())
