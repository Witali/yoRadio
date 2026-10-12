"""Compare bounded WebUI IO on a physical C3; restore app and files in finally.

Private files/settings are held only in RAM, never serialized or hashed in logs.
App-only OTA: no erase, bootloader, NVS or SPIFFS image writes.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
from pathlib import Path
import time
from urllib.parse import urlsplit

from common import Board, Failure, sha, exception_details, fixtures, matches, require
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from production_health import read_health
from audio_test_server.server import Server

BOUNDARY = 'yoradio-web-memory-test'


def form(parts, closed=True):
    result = bytearray()
    for field, name, data in parts:
        result.extend((f'--{BOUNDARY}\r\nContent-Disposition: form-data; '
                       f'name="{field}"; filename="{name}"\r\n\r\n').encode())
        result.extend(data)
        result.extend(b'\r\n')
    if closed:
        result.extend(f'--{BOUNDARY}--\r\n'.encode())
    return bytes(result)


def post(board, path, body, *, declared=None, disconnect=False):
    address = urlsplit(board.origin)
    conn = http.client.HTTPConnection(address.hostname, address.port, timeout=40)
    try:
        conn.putrequest('POST', path)
        conn.putheader('Content-Type', f'multipart/form-data; boundary={BOUNDARY}')
        conn.putheader('Content-Length', str(len(body) if declared is None else declared))
        conn.putheader('Connection', 'close')
        conn.endheaders()
        conn.send(body)
        if disconnect:
            return None
        response = conn.getresponse()
        response.read()  # Never store an error body containing private values.
        return response.status
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--restore', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', type=int, default=8772)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    board = Board(args.board)
    original = board.info()
    original_status = board.status()
    require(not original_status['audio'], 'Stop playback before this focused maintenance test')
    require(original['app_elf_sha256'] == image_info(args.restore.read_bytes())['app_elf_sha256'],
            'Restore image does not match the original app')
    private = snapshot(board)
    assets = {path: board.request(path, timeout=30) for path in
              ('/style.css.gz', '/logo.svg.gz', '/player.html.gz')}
    report = {'controller_sha256':sha(Path(__file__).read_bytes()),'initial': original, 'initial_status': original_status,
              'images': {n:image_info(getattr(args, n).read_bytes()) for n in ('baseline', 'candidate', 'restore')},
              'cases': []}

    def save():
        (args.output/'results.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')

    def install(path, force=False):
        image = path.read_bytes()
        expected = image_info(image)
        active = board.info()
        if not force and active['app_elf_sha256'] == expected['app_elf_sha256']:
            return
        board.stop()
        code, body = upload(board.origin, multipart(image))
        require(code == 200 and body == b'OK', 'OTA failed')
        wait_image(board, expected['app_elf_sha256'],
                   'app1' if active['partition'] == 'app0' else 'app0', timeout=60)
        board.stop()
        time.sleep(2)

    def case(name, action):
        row = {'name': name, 'before': read_health(board)}
        report['cases'].append(row)
        started = time.perf_counter()
        try:
            row['measurement'] = action()
            row['result'] = 'PASS' if row['measurement'].get('accepted', True) else 'FAIL'
        except Exception as error:
            row['result'] = 'FAIL'
            row['errors'] = exception_details(error)
            if isinstance(error, Failure):
                row['check'] = str(error)  # Only our literal assertion descriptions.
            if hasattr(error, 'code') and type(error.code) is int:
                row['http'] = error.code
        row['seconds'] = time.perf_counter() - started
        row['after'] = read_health(board)
        if label == 'candidate':
            row['web_memory'] = board.json('/api/native/web-memory')
        save()
        print(name, row['result'], flush=True)

    def restore_playlist():
        require(post(board, '/upload', form([('plfile','playlist.csv',private['playlist'])])) == 200,
                'Cannot restore original playlist')
        require(board.request('/data/playlist.csv',timeout=30) == private['playlist'],
                'Playlist restoration differs')

    def playlist_trial(size):
        require(len(private['playlist']) < size, 'Original playlist too large for test size')
        payload = private['playlist'] + b'\n' * (size - len(private['playlist']))
        body = form([('plfile','playlist.csv',payload)])
        try:
            code = post(board, '/upload', body)
            equal = board.request('/data/playlist.csv',timeout=30) == payload
            # Record allocation rejection as a measured outcome, not a pass.
            result = {'payload_bytes': size, 'request_bytes': len(body), 'http': code, 'exact': equal, 'accepted': code == 200 and equal}
            return result
        finally:
            restore_playlist()

    def downloads():
        def one(path):
            started = time.perf_counter()
            data = board.request(path,timeout=30)
            require(data == assets[path], 'Concurrent file content differs')
            return {'bytes': len(data), 'seconds': time.perf_counter()-started}
        with ThreadPoolExecutor(max_workers=3) as executor:
            rows = list(executor.map(one, list(assets) * 4))
        return {'requests': rows, 'all_exact': True}

    def rejected(path, body, declared=None, disconnect=False):
        code = post(board,path,body,declared=declared,disconnect=disconnect)
        time.sleep(1)
        require(disconnect or code == 400, 'Malformed upload was not rejected')
        require(board.request('/data/playlist.csv',timeout=30) == private['playlist'],
                'Rejected upload changed the playlist')
        require(all(board.request(path,timeout=30) == data for path,data in assets.items()),
                'Rejected upload changed an asset')
        return {'http': code, 'original_files_unchanged': True}

    def wait_reboot(previous):
        deadline = time.monotonic()+60
        while time.monotonic() < deadline:
            time.sleep(1)
            try:
                if read_health(board)['boot_id'] != previous:
                    board.stop()
                    return
            except Exception:
                pass
        raise AssertionError('Reboot did not complete')

    def wifi_upload():
        previous = read_health(board)['boot_id']
        require(post(board,'/upload',form([('wifile','wifi.csv',private['wifi'])])) == 200,
                'Wi-Fi file upload failed')
        wait_reboot(previous)
        return verify_snapshot(board,private)

    def board_upload():
        parts = [('www',path[1:],data) for path,data in assets.items()]
        parts.append(('data','playlist.csv',private['playlist']))
        require(post(board,'/webboard',form(parts)) == 303, 'Recovery file upload failed')
        require(all(board.request(path,timeout=30) == data for path,data in assets.items()),
                'Recovered asset content differs')
        return verify_snapshot(board,private)

    def ota_roundtrip():
        install(args.candidate, force=True)
        return verify_snapshot(board, private)

    specs = fixtures()
    try:
        for label in ('baseline', 'candidate'):
            install(getattr(args,label))
            report[label+'_idle'] = read_health(board)
            case(label+':parallel-downloads', downloads)
            for size in (max(32768, len(private['playlist'])+4096),65536,96000):
                case(label+':playlist-'+str(size), lambda n=size:playlist_trial(n))
            if label == 'candidate':
                case('candidate:truncated', lambda:rejected('/upload',form([('plfile','playlist.csv',b'partial')],False)))
                case('candidate:disconnect', lambda:rejected('/upload',form([('plfile','playlist.csv',b'partial')],False),declared=50000,disconnect=True))
                case('candidate:oversized', lambda:rejected('/upload',b'',declared=98305))
                case('candidate:duplicate-asset', lambda:rejected('/webboard',form([('www','style.css.gz',b'bad'),('www','style.css.gz',b'bad')])) )
                case('candidate:invalid-wifi-form', lambda:rejected('/',form([('ssid','',b'x'*33),('pass','',b'')])) )
                case('candidate:board-multipart', board_upload)
                case('candidate:wifi-upload-reboot', wifi_upload)
                previous = read_health(board)['boot_id']
                def reboot():
                    board.reboot(); wait_reboot(previous)
                    return verify_snapshot(board,private)
                case('candidate:websocket-reboot', reboot)
                def bad_ota():
                    identity = board.info()
                    data = bytearray(args.candidate.read_bytes()); data[len(data)//2] ^= 1
                    code,_ = upload(board.origin,multipart(data))
                    require(code == 400 and board.info() == identity, 'Corrupt OTA changed active image')
                    return verify_snapshot(board,private)
                case('candidate:corrupt-ota',bad_ota)
                case('candidate:ota-roundtrip',ota_roundtrip)
                report['web_memory'] = board.json('/api/native/web-memory')
            with Server(args.host,args.port,specs,pacing_ratio=1.0) as server:
                for name in ('he-48000-stereo','flac-level8'):
                    if name not in specs:
                        continue
                    def playback(n=name):
                        board.play(f'http://{args.host}:{args.port}/stream/{n}')
                        deadline = time.monotonic()+15
                        while time.monotonic() < deadline:
                            if matches(board.status(),specs[n]): break
                            time.sleep(.5)
                        require(matches(board.status(),specs[n]), 'Fixture did not start')
                        before = read_health(board)
                        results = downloads()
                        time.sleep(5)
                        after = read_health(board)
                        report['cases'][-1]['playback_window'] = {'before':before,'after':after,'status':board.status()}
                        require(matches(board.status(),specs[n]), 'Fixture stopped during downloads')
                        board.stop()
                        for key in ('allocation_failures','task_watchdog_events'):
                            require(after[key] == before[key], 'Runtime fault during downloads')
                        require(after['output'] == before['output'], 'Output counters changed during downloads')
                        return {'before':before,'after':after, **results}
                    case(label+':playback-downloads:'+name,playback)
                    board.stop()
            if label == 'candidate':
                report['web_memory_after_playback'] = board.json('/api/native/web-memory')
            save()
    except Exception as error:
        report['controller_error'] = exception_details(error)
        save()
        raise
    finally:
        # File data is restored before returning to the original firmware.
        board.stop()
        try:
            restore_playlist()
        finally:
            install(args.restore)
        board.stop()
        report['restoration'] = {'image':board.info(), **verify_snapshot(board,private),
                                 'assets_unchanged': all(board.request(path,timeout=30) == data for path,data in assets.items()),
                                 'status':board.status()}
        save()
        print('RESTORED',flush=True)


if __name__ == '__main__':
    main()
