"""Shared, strict acceptance checks. Never save board credentials or station names."""
import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import statistics
import time
import sys
from urllib.request import Request, urlopen

from tls_error_codes import error_detail

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))


class Failure(AssertionError):
    pass


class Blocked(RuntimeError):
    pass


def exception_details(error):
    """Retain transport type/codes without exception text, URLs or credentials."""
    chain, seen = [], set()
    while isinstance(error, BaseException) and id(error) not in seen and len(chain) < 8:
        seen.add(id(error))
        row = {'type': type(error).__name__}
        for key in ('errno', 'winerror'):
            value = getattr(error, key, None)
            if type(value) is int:
                row[key] = value
        chain.append(row)
        reason = getattr(error, 'reason', None)
        error = reason if isinstance(reason, BaseException) else error.__cause__ or error.__context__
    return chain


def require(condition, message):
    if not condition:
        raise Failure(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


TLS_CERTIFICATE_REJECTED = ('TLS failure: component=esp-x509-crt-bundle '
                            'certificate_verification_failed=true')


def filter_tls_line(line):
    # Never retain arbitrary certificate subjects, URLs or hostnames.
    tls = re.match(r'^(?:\x1b\[[0-9;]*m)?E \(\d+\) '
                   r'(Dynamic Impl|SSL TLS|SSL client|SSL Server|'
                   r'esp-tls-mbedtls|esp-tls|esp-x509-crt-bundle):', line)
    if not tls:
        return None
    body = re.sub(r'\x1b\[[0-9;]*m', '', line[tls.end():]).strip()
    if tls.group(1) == 'esp-x509-crt-bundle' and body == 'Failed to verify certificate':
        return TLS_CERTIFICATE_REJECTED
    size = re.search(r'\balloc\((\d+) bytes\) failed\b', body)
    return ('TLS failure: component=' + tls.group(1) +
            (' allocation_bytes=' + size.group(1) if size else '') +
            error_detail(tls.group(1), body))


def check_certificate_rejection(alerts, rows):
    bundle_rejected = any(r['line'] == TLS_CERTIFICATE_REJECTED for r in rows)
    # The ESP-IDF verification callback can yield BADCERT_OTHER, which the
    # pinned mbedTLS maps to ACCESS_DENIED. That alert alone is not proof.
    require(any('CERTIFICATE' in alert or 'UNKNOWN_CA' in alert or
                alert == 'TLSV1_ALERT_ACCESS_DENIED' and bundle_rejected
                for alert in alerts),
            'No certificate-rejection evidence; connection failure alone is insufficient')
    return bundle_rejected


def fixtures(extra_manifest=None):
    from audio_test_server.fixtures import load_fixtures
    specs = load_fixtures(extra_manifest)
    for spec in specs.values():
        if 'profile' in spec:
            spec['label'] = {'AAC-LC':'AAC PCM', 'HE-AAC':'HE-AAC ', 'HE-AACv2':'HE-AACv2 ',
                             'opus':'OGG', 'vorbis':'OGG'}.get(spec['profile'], spec['codec'].upper())
    return specs

TECHNICAL = ('firmware', 'network', 'audio', 'format', 'sample_rate', 'channels',
             'bits_per_sample', 'pcm_sample_rate', 'pcm_channels',
             'format_is_pcm', 'channels_are_core', 'rssi')


class Board:
    def __init__(self, origin):
        self.origin = origin.rstrip('/')

    def request(self, path, data=None, timeout=5):
        with urlopen(Request(self.origin + path, data=data), timeout=timeout) as r:
            return r.read()

    def json(self, path, data=None, timeout=5):
        return json.loads(self.request(path, data, timeout))

    def status(self):
        value = self.json('/api/native/status')
        require(value.get('firmware') == 'esp32c3-oled-native', 'Wrong board firmware')
        return {key: value[key] for key in TECHNICAL if key in value}

    def info(self):
        return self.json('/api/native/ota')

    def stop(self):
        self.json('/api/native/stop', b'')

    def play(self, url, codec='auto'):
        self.json('/api/native/play?codec=' + codec, url.encode())

    def websocket(self):
        from websockets.sync.client import connect
        return connect(self.origin.replace('http', 'ws', 1) + '/ws',
                       compression=None, open_timeout=5, close_timeout=1,
                       ping_interval=None, proxy=None)

    def settings(self):
        # Values stay in memory for equality checks; callers must not serialize.
        values = {}
        with self.websocket() as ws:
            for command, marker in [('getsystem','abuff'), ('getscreen','scrt'),
                                    ('gettimezone','tzh'), ('getcontrols','vols')]:
                ws.send(command)
                deadline = time.perf_counter() + 5
                while time.perf_counter() < deadline:
                    value = json.loads(ws.recv(timeout=5))
                    if marker in value:
                        value.pop('ipaddr', None)  # DHCP may change after boot.
                        values[command] = value
                        break
                require(command in values, 'Missing settings response: ' + command)
        return values

    def reboot(self):
        with self.websocket() as ws:
            ws.send('reboot')
            deadline = time.perf_counter() + 5
            while time.perf_counter() < deadline:
                if json.loads(ws.recv(timeout=5)).get('rebooting') == 1:
                    return
        raise Failure('No reboot acknowledgement')


def matches(state, spec):
    return (state.get('audio') is True and state.get('pcm_sample_rate') == spec['rate']
            and state.get('pcm_channels') == spec['channels']
            and state.get('bits_per_sample') == spec['bits']
            and state.get('format', '').startswith(spec['label'])
            and ('source_channels' not in spec or state.get('channels') == spec['source_channels'])
            and not state.get('channels_are_core', False))


def check_file_runtime(records):
    """Positive file cases must not hide recorded failures behind valid PCM status."""
    faults = (r'allocation failed|decode (?:error|failed)|TLS failure:|'
              r'assert failed|Guru Meditation|CORRUPT HEAP|PANIC|'
              r'serial capture interrupted|task_wdt: Task watchdog got triggered|'
              r'PERF watchdog: task_timeouts=[1-9][0-9]*\b|'
              r'Runtime watchdog timeout|^(?:ESP-ROM:|rst:|waiting for download)')
    require(not any(re.search(faults, r['line']) for r in records),
            'Runtime failure during file playback')


def check_playback(samples, spec, minimum=5, warmup=2):
    stable = [s for s in samples if s['seconds'] >= warmup and s.get('audio')]
    require(len(stable) >= minimum, 'Insufficient actual playback samples')
    require(all(matches(s, spec) for s in stable), 'Wrong decoded rate/channels/profile')
    # Once playing, failures/false flags in the observation window are not success.
    first = next(s['seconds'] for s in samples if s.get('audio'))
    tail = [s for s in samples if s['seconds'] >= max(first, warmup)]
    require(all(s.get('audio') for s in tail), 'Playback stopped during the stable window')
    return dict(samples=len(stable), rate=spec['rate'], channels=spec['channels'])


def check_transitions(samples, expected, minimum=2):
    """Require each format in order, with consecutive confirmation samples."""
    phase = count = 0
    for state in samples:
        if matches(state, expected[phase]):
            count += 1
            if count >= minimum:
                phase += 1
                count = 0
                if phase == len(expected):
                    return
        else:
            count = 0
    raise Failure(f'Missing full-rate transition {phase + 1}/{len(expected)}')


def check_cpu(records, max_busy=85, min_heap=8192, min_largest=4096, start=None, end=None):
    cpu, decode = [], []
    for row in records:
        line = row['line']
        require(not re.search(r'allocation failed|decode (?:error|failed)|TLS failure:|Fail to|assert failed|Guru Meditation|CORRUPT HEAP|serial capture interrupted', line),
                'Runtime decoder/memory failure')
        if 'PERF CPU:' in line:
            fields = {k: float(v) for k,v in re.findall(r'(busy|idle|heap|largest)=([\d.]+)', line)}
            require(set(fields) == {'busy','idle','heap','largest'}, 'Incomplete CPU/heap evidence')
            require(abs(fields['busy'] + fields['idle'] - 100) < .3, 'Invalid CPU window')
            cpu.append(fields)
        match = re.search(r'PERF (?:AAC|MP3|FLAC|OGG): window (\d+) ms, audio (\d+) ms, decode (\d+) ms', line)
        if match:
            decode.append(tuple(map(int, match.groups())))
    require(len(cpu) >= 3 and len(decode) >= 3, 'Missing CPU/decoder windows; use profiling firmware')
    if start is not None and end is not None:
        for pattern in ('PERF CPU:', r'PERF (?:AAC|MP3|FLAC|OGG):'):
            times = [r['at'] for r in records if re.search(pattern,r['line'])]
            require(all(b-a < 11 for a,b in zip([start]+times,times+[end])),
                    'CPU/decoder evidence has a gap longer than two intervals')
    # None makes CPU informational. Keep the historical default for replaying
    # recorded tests that explicitly used the former headroom criterion.
    if max_busy is not None:
        require(max(r['busy'] for r in cpu) <= max_busy, 'CPU budget exceeded')
    require(min(r['heap'] for r in cpu) >= min_heap, 'Free heap below budget')
    require(min(r['largest'] for r in cpu) >= min_largest, 'Largest heap block below budget')
    ratio = sum(r[1] for r in decode) / sum(r[0] for r in decode)
    require(.9 < ratio < 1.1, 'Decoded audio is not progressing in real time')
    if len(cpu) >= 6:
        for key,tolerance in [('heap',2048),('largest',4096)]:
            require(statistics.median(r[key] for r in cpu[:3]) -
                    statistics.median(r[key] for r in cpu[-3:]) <= tolerance,
                    'Progressive '+key+' loss during continuous playback')
    return dict(mean_busy=statistics.mean(r['busy'] for r in cpu),
                peak_busy=max(r['busy'] for r in cpu), minimum_heap=min(r['heap'] for r in cpu),
                minimum_largest=min(r['largest'] for r in cpu), audio_wall_ratio=ratio)


def check_recovery_heap(baseline, final, free_loss=2048, largest_loss=4096):
    require(len(baseline) >= 2 and len(final) >= 2, 'Missing settled idle heap samples')
    for key, tolerance in [('heap',free_loss), ('largest',largest_loss)]:
        before = statistics.median(r[key] for r in baseline)
        after = statistics.median(r[key] for r in final)
        require(before - after <= tolerance, f'Persistent {key} loss: {before - after} bytes')
    require(max(r['tasks'] for r in final) <= max(r['tasks'] for r in baseline), 'Task leak')


class Report:
    def __init__(self, path, info):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = dict(board=info, cases=[], note='PASS covers recorded checks only; no acoustic/IRQ inference')
        self.data['cpu_budget_percent'] = None
        self.data['created_utc'] = datetime.now(timezone.utc).isoformat()
        self.data['host_clock'] = dict(api='time.perf_counter',
                                      **vars(time.get_clock_info('perf_counter')))
        self.data['test_sources_sha256'] = {
            str(p.relative_to(ROOT)).replace('\\','/'): sha(p.read_bytes())
            for directory in ('esp32c3_tests','audio_test_server')
            for p in sorted((ROOT/'tools'/directory).glob('*.py'))}

    def case(self, name, action):
        started = time.perf_counter()
        record = dict(name=name, result='FAIL')
        try:
            record['evidence'] = action()
            record['result'] = 'PASS'
        except Blocked as error:
            record.update(result='BLOCKED', reason=str(error))
        except Exception as error:
            record['exception_chain'] = exception_details(error)
            # URL errors can include private URLs; only our controlled assertion
            # text is retained. Technical samples are saved separately by runner.
            record['reason'] = str(error) if isinstance(error, Failure) else type(error).__name__
        record['seconds'] = round(time.perf_counter() - started, 3)
        self.data['cases'].append(record)
        self.save()
        print(name + ': ' + record['result'] + (' - ' + record['reason'] if 'reason' in record else ''), flush=True)

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2) + '\n', encoding='utf-8')

    def exit_code(self):
        return 0 if self.data['cases'] and all(r['result'] == 'PASS' for r in self.data['cases']) else 1
