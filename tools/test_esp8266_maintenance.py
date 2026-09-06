"""Opt-in destructive maintenance acceptance on a backed-up native board.

Uploads the same saved Wi-Fi/playlist/assets, and an explicitly supplied native
application to the inactive OTA slot. Never changes the partition table.
No credential bytes or their hashes are printed or included in the report.
"""
import argparse
import hashlib
import http.client
import json
from pathlib import Path
import time

p = argparse.ArgumentParser()
p.add_argument('--host', default='192.168.100.6')
p.add_argument('--firmware', required=True)
p.add_argument('--backup-directory', required=True, help='Private saved SPIFFS tree')
p.add_argument('--report', required=True)
p.add_argument('--ota-rounds', type=int, choices=[0, 1, 2], default=2)
p.add_argument('--confirm-maintenance', action='store_true')
a = p.parse_args()
if not a.confirm_maintenance:
    p.error('Requires explicit --confirm-maintenance and an existing backup')
backup = Path(a.backup_directory)
firmware = Path(a.firmware).read_bytes()
wifi = (backup/'data/wifi.csv').read_bytes()
playlist = (backup/'data/playlist.csv').read_bytes()
asset = (backup/'www/script.js.gz').read_bytes()
report = {'host': a.host, 'app_sha256': hashlib.sha256(firmware).hexdigest(), 'checks': []}

def request_once(method, uri, data=None, headers=None):
    c = http.client.HTTPConnection(a.host, timeout=125 if method == 'POST' else 8)
    try:
        c.request(method, uri, body=data, headers={'Connection': 'close', **(headers or {})})
        r = c.getresponse()
        until = time.monotonic() + (125 if method == 'POST' else 20)
        chunks = []
        while not r.isclosed():
            left = until - time.monotonic()
            if left <= 0:
                raise TimeoutError('complete HTTP response deadline')
            if c.sock:
                c.sock.settimeout(min(left, 8))
            data = r.read1(4096)
            if not data:
                break
            chunks.append(data)
        return r.status, b''.join(chunks)
    finally:
        c.close()

def request(method, uri, data=None, headers=None):
    # Match the UI's bounded retry of idempotent reads. Never retry writes:
    # a lost POST response does not prove the update was rejected.
    for attempt in range(3 if method == 'GET' else 1):
        try:
            return request_once(method, uri, data, headers)
        except (OSError, http.client.HTTPException) as error:
            if method != 'GET' or attempt == 2:
                raise
            report.setdefault('get_retries', []).append({
                'uri': uri, 'attempt': attempt+1, 'error': type(error).__name__})
            print('RETRY GET', uri, type(error).__name__, flush=True)
            time.sleep(1)

def check(name, valid, **detail):
    report['checks'].append({'name': name, 'pass': bool(valid), **detail})
    print(('PASS' if valid else 'FAIL'), name, json.dumps(detail), flush=True)
    if not valid:
        raise AssertionError(name)

def status():
    code, body = request('GET', '/api/native/status')
    if code != 200:
        raise RuntimeError('status HTTP '+str(code))
    return json.loads(body)

def ready(expected=None):
    end = time.monotonic()+110
    while time.monotonic() < end:
        try:
            s = status()
            if s['network'] == 1 and (expected is None or s['app_address'] == expected):
                return s
        except (OSError, ValueError, http.client.HTTPException):
            pass
        time.sleep(1)
    raise RuntimeError('board did not return with expected OTA address')

def multipart(uri, fields):
    boundary = 'YoRadioMaintenance20260905'
    pieces = []
    for name, filename, data in fields:
        header = '--'+boundary+'\r\nContent-Disposition: form-data; name="'+name+'"'
        if filename:
            header += '; filename="'+filename+'"'
        pieces += [(header+'\r\n\r\n').encode(), data, b'\r\n']
    pieces += [('--'+boundary+'--\r\n').encode()]
    return request('POST', uri, b''.join(pieces),
                   {'Content-Type': 'multipart/form-data; boundary='+boundary})

try:
    initial = ready()
    check('initial OTA slot', initial['app_address'] in (0x10000, 0x110000),
          address=initial['app_address'], free_heap=initial['free_heap'])
    code, saved_wifi = request('GET', '/data/wifi.csv')
    check('Wi-Fi matches private backup', code == 200 and saved_wifi == wifi)
    code, original_list = request('GET', '/data/playlist.csv')
    check('read supported playlist', code == 200 and len(original_list)>0, bytes=len(original_list))
    for cycle in range(a.ota_rounds):
        before = ready()
        target = 0x110000 if before['app_address'] == 0x10000 else 0x10000
        # "firmware" is accepted by the first migration build; "fw" is the
        # original shared HTML form and is tested after that first update.
        kind = b'firmware' if cycle == 0 else b'fw'
        print('RUN OTA', hex(before['app_address']), '->', hex(target), flush=True)
        start = time.monotonic()
        code, body = multipart('/update', [('updatetarget', None, kind),
                                         ('update', 'app.bin', firmware)])
        check('OTA accepted '+str(cycle+1), code == 200 and body == b'OK',
              http=code, seconds=round(time.monotonic()-start, 3))
        time.sleep(3)
        current = ready(target)
        check('booted OTA slot '+str(cycle+1), current['app_address'] == target,
              address=current['app_address'], free_heap=current['free_heap'])
        code, content = request('GET', '/data/wifi.csv')
        check('Wi-Fi preserved after OTA '+str(cycle+1), code == 200 and content == wifi)
        code, content = request('GET', '/data/playlist.csv')
        check('playlist preserved after OTA '+str(cycle+1), code == 200 and content == original_list)
    before = status()['app_address']
    code, _ = multipart('/update', [('updatetarget', None, b'fw'),
                                    ('update', 'bad.bin', b'not an ESP image')])
    check('invalid OTA rejected', code == 400)
    check('invalid OTA leaves boot slot', status()['app_address'] == before)
    code, _ = multipart('/upload', [('plfile', 'playlist.csv', playlist)])
    check('identical playlist upload', code == 200)
    code, content = request('GET', '/data/playlist.csv')
    check('playlist readback', code == 200 and content == original_list)
    code, _ = multipart('/webboard', [('www', 'script.js.gz', asset)])
    check('WebUI asset upload', code == 303)
    code, content = request('GET', '/script.js')
    check('WebUI asset readback', code == 200 and content == asset)
    code, _ = multipart('/upload', [('wifile', 'wifi.csv', wifi)])
    check('Wi-Fi upload', code == 200)
    time.sleep(3)
    ready(before)
    code, content = request('GET', '/data/wifi.csv')
    check('Wi-Fi upload reboot and readback', code == 200 and content == wifi)
    check('embedded emergency page route', request('GET', '/emergency')[0] == 200)
except Exception as error:
    report['fatal'] = type(error).__name__+': '+str(error)
    raise
finally:
    Path(a.report).write_text(json.dumps(report, indent=2), encoding='utf-8')
