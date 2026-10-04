"""Physical C3 acceptance suite. See docs/ESP32C3_TESTING.md before running."""
import argparse
import json
from pathlib import Path
import re
import statistics
import sys
import threading
import time

from common import (Blocked, Board, Failure, Report, check_cpu, check_playback,
                    check_recovery_heap, check_transitions, fixtures, require,
                    filter_tls_line, check_certificate_rejection, exception_details)
from audio_test_server.server import Server
from audio_test_server.fixtures import SEQUENCES


class Capture:
    def __init__(self, port):
        self.rows = []
        self.closed = threading.Event()
        self.port = None
        if port:
            import serial
            self.port = serial.Serial(port=None, baudrate=115200, timeout=.2)
            self.port.dtr = self.port.rts = False
            self.port.port = port
            self.port.open()
            self.thread = threading.Thread(target=self.read, daemon=True)
            self.thread.start()

    def read(self):
        while not self.closed.is_set():
            try:
                line = self.port.readline().decode('utf-8', errors='replace').strip()
            except OSError:
                self.rows.append(dict(at=time.monotonic(), line='serial capture interrupted'))
                return
            tls = filter_tls_line(line)
            if tls:
                self.rows.append(dict(at=time.monotonic(), line=tls))
            elif re.search(r'PERF |Memory .*: free=|decode (?:error|failed)|allocation failed|assert failed|Guru Meditation|CORRUPT HEAP', line):
                self.rows.append(dict(at=time.monotonic(), line=line))

    def since(self, at):
        return [r for r in self.rows if r['at'] >= at]

    def close(self):
        self.closed.set()
        if self.port:
            self.thread.join(timeout=2)
            self.port.close()


class Suite:
    def __init__(self, board, origin, specs, capture, output):
        self.board, self.origin, self.specs = board, origin.rstrip('/'), specs
        self.capture, self.output = capture, Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.observations = []

    def url(self, mode, name, origin=None):
        return (origin or self.origin).rstrip('/') + '/' + mode + '/' + name

    def observe(self, seconds, name, interval=.4):
        start = time.monotonic()
        samples = []
        batch = dict(case=name, started_at=start, samples=samples)
        try:
            while time.monotonic() - start < seconds:
                requested = time.monotonic()
                state = self.board.status()
                row = dict(seconds=time.monotonic() - start, request_ms=(time.monotonic()-requested)*1000, **state)
                samples.append(row)
                time.sleep(interval)
        except Exception as error:
            # Keep partial evidence on transport failures without retaining URLs
            # or exception text that could contain station/credential details.
            batch['interrupted'] = type(error).__name__
            batch['exception_chain'] = exception_details(error)
            batch['elapsed_seconds'] = time.monotonic() - start
            raise
        finally:
            batch['ended_at'] = time.monotonic()
            self.observations.append(batch)
            (self.output / 'status.json').write_text(json.dumps(self.observations, indent=2)+'\n', encoding='utf-8')
        return samples

    def start(self, name, mode='file', hint='auto', origin=None):
        self.board.stop()
        time.sleep(.8)
        self.board.play(self.url(mode, name, origin), hint)

    def file(self, name, hint='auto', origin=None, mode='file'):
        spec = self.specs[name]
        self.start(name, mode, hint, origin)
        try:
            samples = self.observe(max(7, spec['seconds']-3), name)
            evidence = check_playback(samples, spec)
            tail = self.observe(8, name + ':eof')
            require(any(not s['audio'] for s in tail), 'Finite stream never reached EOF')
            # No explicit stop: test that the next playback recovers from EOF.
            return evidence
        finally:
            self.board.stop()

    def transition(self, name, expected):
        self.start(name, hint='aac')
        try:
            samples = self.observe(self.specs[name]['seconds']-1, name)
            check_transitions(samples, [self.specs[n] for n in expected])
            return dict(sequence=expected)
        finally:
            self.board.stop()

    def fault(self, mode):
        name = 'lc-48000-stereo'
        self.start(name, mode, 'aac')
        # A truncated Content-Length body can be classified only after the
        # firmware's 10 s stream watchdog, plus the initial 3 s of valid data.
        samples = self.observe(20 if mode in ('stall','drop') else 7, 'fault:' + mode)
        require(any(not r['audio'] for r in samples[-3:]), 'Fault did not leave playback')
        # A new command must supersede the failed connection and stale callbacks.
        self.start('lc-22050-mono', hint='aac')
        try:
            restored = self.observe(7, 'recovered:' + mode)
            check_playback(restored, self.specs['lc-22050-mono'])
            return dict(recovered=True)
        finally:
            self.board.stop()

    def stop_race(self):
        self.start('lc-48000-stereo', 'stall', 'aac')
        time.sleep(.1)
        self.board.stop()
        self.board.play(self.url('file','lc-22050-mono'), 'aac')
        try:
            samples = self.observe(7, 'stop-play-generation')
            check_playback(samples, self.specs['lc-22050-mono'])
            return dict(stale_generation_rejected=True)
        finally:
            self.board.stop()

    def eof(self, name, hint='auto'):
        """Check terminal status independently of HE-AAC full-rate acceptance."""
        self.start(name, hint=hint)
        try:
            samples = self.observe(max(7, self.specs[name]['seconds']-3), name+':playing')
            require(any(s['audio'] and s.get('pcm_sample_rate') for s in samples),
                    'No decoded playback before EOF')
            tail = self.observe(10, name+':terminal')
            stopped = next((i for i,s in enumerate(tail) if not s['audio']), None)
            require(stopped is not None and len(tail)-stopped >= 2,
                    'No confirmed stopped state after EOF')
            require(all(not s['audio'] and s['format']=='stream ended' and
                        not s['pcm_sample_rate'] and not s['pcm_channels']
                        for s in tail[stopped:]),
                    'EOF state was replaced by stale PCM metadata or a decode error')
            with self.board.websocket() as ws:
                ws.send('getindex')
                deadline = time.monotonic()+5
                while time.monotonic() < deadline:
                    message = json.loads(ws.recv(timeout=5))
                    values = {p['id']:p['value'] for p in message.get('payload',[])}
                    if 'fmt' in values:
                        require(values['fmt']=='stream ended' and
                                values.get('playerwrap')!='playing',
                                'WebSocket did not retain terminal state')
                        break
                else:
                    raise Failure('No WebSocket EOF snapshot')
            return dict(scope='EOF state only; decoded profile acceptance is separate',
                        observed_formats=sorted({s['format'] for s in samples if s['audio']}),
                        terminal_samples=len(tail)-stopped, websocket_stopped=True)
        finally:
            self.board.stop()

    def websocket_format(self):
        self.start('lc-48000-stereo','stream','aac')
        try:
            check_playback(self.observe(7,'ws-warmup'), self.specs['lc-48000-stereo'])
            for reconnect in range(2):
                with self.board.websocket() as ws:
                    ws.send('getindex')
                    deadline = time.monotonic()+5
                    while time.monotonic() < deadline:
                        message = json.loads(ws.recv(timeout=5))
                        values = {p['id']:p['value'] for p in message.get('payload',[])}
                        if 'fmt' in values:
                            require(values['fmt'] == self.board.status()['format'], 'WebSocket has stale stream format')
                            require(values.get('playerwrap') == 'playing', 'WebSocket has stale player state')
                            break
                    else:
                        raise Failure('No WebSocket format snapshot after reconnect')
            return dict(reconnects=2, format_matches_rest=True)
        finally:
            self.board.stop()

    def tls_rejection(self, origin, server):
        if not origin or server is None:
            raise Blocked('Provide untrusted --https-origin and --tls-cert/key to capture handshake rejection')
        first_event = len(server.events)
        started = time.monotonic()
        self.start('lc-48000-stereo',hint='aac',origin=origin)
        samples = self.observe(12,'untrusted-tls')
        require(not any(s['audio'] for s in samples), 'Untrusted TLS connection was accepted')
        errors = [e['reason'] for e in server.events[first_event:] if e['mode']=='tls-handshake-failure']
        bundle_rejected = check_certificate_rejection(errors, self.capture.since(started))
        self.start('lc-48000-stereo',hint='aac')
        try:
            check_playback(self.observe(7,'after-tls-rejection'),self.specs['lc-48000-stereo'])
            return dict(untrusted_rejected=True, http_recovered=True, tls_alerts=errors,
                        certificate_bundle_rejected=bundle_rejected)
        finally:
            self.board.stop()

    def boot_time(self):
        self.board.stop()
        self.board.reboot()
        started = time.monotonic()
        unavailable = False
        deadline = started+45
        while time.monotonic() < deadline:
            try:
                state = self.board.status()
                if unavailable and state.get('network') == 'client':
                    return dict(ready_ms=(time.monotonic()-started)*1000,
                                metric='reboot acknowledgement to HTTP client-mode response')
            except (OSError,ValueError,TimeoutError):
                unavailable = True
            time.sleep(.1)
        raise Failure('Reboot outage and client-mode return were not observed')

    def idle_heap(self):
        if not self.capture.port:
            raise Blocked('Settled heap test requires --serial-port and profiling firmware')
        self.board.stop()
        started = time.monotonic()
        self.observe(12, 'settled-idle')
        result = []
        for row in self.capture.since(started):
            found = re.search(r'PERF CPU:.*heap=(\d+) largest=(\d+) tasks=(\d+)', row['line'])
            if found:
                result.append(dict(zip(('heap','largest','tasks'), map(int,found.groups()))))
        require(len(result) >= 2, 'Profiling firmware did not supply idle heap evidence')
        return result

    def switching(self, names, cycles):
        require(cycles >= 3, 'At least three station cycles are required')
        if not self.capture.port:
            raise Blocked('Station memory test requires --serial-port and profiling firmware')
        failures, checkpoints = [], []
        for cycle in range(cycles):
            for name in names:
                self.start(name)
                try:
                    check_playback(self.observe(7, f'switch:{cycle}:{name}'), self.specs[name])
                except Failure as error:
                    failures.append(dict(cycle=cycle, fixture=name, reason=str(error)))
                finally:
                    self.board.stop()
            checkpoints.append(self.idle_heap())
        (self.output / 'switching.json').write_text(json.dumps(dict(failures=failures, checkpoints=checkpoints), indent=2)+'\n')
        require(not failures, 'One or more station changes failed; see switching.json')
        check_recovery_heap(checkpoints[0], checkpoints[-1])
        return dict(cycles=cycles, station_changes=len(names)*cycles)

    def sustained(self, seconds, name='lc-48000-stereo', cpu=False, load=False):
        if cpu and not self.capture.port:
            raise Blocked('CPU/heap checks require --serial-port and profiling firmware')
        spec = self.specs[name]
        mode = 'stream' if spec['codec'] == 'aac' else 'file'
        if mode == 'file' and spec['seconds'] < seconds+3:
            raise Blocked('Generate a continuous fixture at least 3 s longer than this test')
        self.start(name, mode, spec['codec'])
        started = time.monotonic()
        try:
            samples = self.observe(seconds, ('load:' if load else 'soak:') + name,
                                   interval=.1 if load else 1)
            check_playback(samples, self.specs[name], minimum=max(5, int(seconds*.6)), warmup=5)
            require(max(s['request_ms'] for s in samples) < 2000, 'WebUI response exceeded 2 s')
            evidence = dict(duration=seconds, status_samples=len(samples),
                            max_http_ms=max(s['request_ms'] for s in samples))
            if cpu:
                evidence.update(check_cpu(self.capture.since(started+10),start=started+10,end=time.monotonic()))
            return evidence
        finally:
            self.board.stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True, help='Local IPv4 reachable from board')
    parser.add_argument('--port', type=int, default=8770)
    parser.add_argument('--suite', action='append', choices=('http','https','eof','tls-rejection','transitions','faults','switch','soak','load','websocket','boot-time'), required=True)
    parser.add_argument('--case', action='append', help='Restrict matrix/switch/soak/load fixtures')
    parser.add_argument('--serial-port')
    parser.add_argument('--fixture-manifest', type=Path)
    parser.add_argument('--cycles', type=int, default=3)
    parser.add_argument('--soak-seconds', type=int, default=3600)
    parser.add_argument('--load-seconds', type=int, default=40,
                        help='Duration under frequent WebUI polling; keep the original CPU/heap gates')
    parser.add_argument('--load-idle-recovery', action='store_true',
                        help='Measure settled heap before and after each load case, even when playback fails')
    parser.add_argument('--https-origin', help='Trusted HTTPS origin serving identical /file routes')
    parser.add_argument('--tls-cert', type=Path)
    parser.add_argument('--tls-key', type=Path)
    parser.add_argument('--tls-port', type=int, default=8771)
    parser.add_argument('--sdkconfig', type=Path, help='Exact config of tested image, for A/B provenance')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--leave-stopped', action='store_true', help='Do not reboot to restore saved station')
    args = parser.parse_args()
    require(args.soak_seconds >= 60, 'Soak must last at least 60 seconds; default is one hour')
    require(args.load_seconds >= 40, 'Load must last at least the original 40 seconds')
    specs = fixtures(args.fixture_manifest)
    names = args.case or [n for n in specs if n not in SEQUENCES]
    require(all(n in specs for n in names), 'Unknown fixture name')
    sequences = SEQUENCES
    board = Board(args.board)
    board.status()
    info = board.info()
    args.output.mkdir(parents=True, exist_ok=True)
    report = Report(args.output/'report.json', info)
    report.data['fixture_hashes'] = {n:specs[n]['sha256'] for n in names}
    report.data['requested_suites'] = args.suite
    if 'load' in args.suite:
        report.data['load_options'] = dict(seconds=args.load_seconds,
                                          idle_recovery=args.load_idle_recovery)
    if args.sdkconfig:
        import hashlib
        config = args.sdkconfig.read_text()
        report.data['config'] = dict(sha256=hashlib.sha256(args.sdkconfig.read_bytes()).hexdigest(),
            wifi_iram=bool(re.search(r'^CONFIG_ESP_WIFI_IRAM_OPT=y$',config,re.M)),
            wifi_rx_iram=bool(re.search(r'^CONFIG_ESP_WIFI_RX_IRAM_OPT=y$',config,re.M)))
    capture = Capture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:{args.port}', specs, capture, args.output)
    tls = None
    try:
        with Server(args.host, args.port, specs) as server:
            if args.tls_cert:
                require(args.tls_key and args.https_origin, 'TLS server requires key and HTTPS hostname')
                tls = Server(args.host, args.tls_port, specs, args.tls_cert, args.tls_key).__enter__()
            for protocol in ('http','https'):
                if protocol in args.suite:
                    for name in names:
                        for hint in ('auto',specs[name]['codec']):
                            def play(n=name, h=hint, p=protocol):
                                if p == 'https' and not args.https_origin:
                                    raise Blocked('Provide --https-origin with a certificate trusted by production firmware')
                                return suite.file(n, h, args.https_origin if p == 'https' else None)
                            report.case(f'{protocol}:{name}:{hint}', play)
            if 'transitions' in args.suite:
                for name, sequence in sequences.items():
                    report.case('transition:'+name, lambda n=name,s=sequence: suite.transition(n,s))
                report.case('stop-play-generation', suite.stop_race)
            if 'eof' in args.suite:
                for name in names:
                    for hint in ('auto',specs[name]['codec']):
                        report.case(f'eof:{name}:{hint}',lambda n=name,h=hint: suite.eof(n,h))
            if 'faults' in args.suite:
                for mode in ('drop','stall','error'):
                    report.case('network:'+mode, lambda m=mode: suite.fault(m))
                for mode in ('redirect','jitter'):
                    report.case('network:'+mode, lambda m=mode: suite.file('lc-48000-stereo', 'aac', mode=m))
            if 'switch' in args.suite:
                report.case('switching-and-heap', lambda: suite.switching(names,args.cycles))
            if 'websocket' in args.suite:
                report.case('websocket-format-and-reconnect',suite.websocket_format)
            if 'tls-rejection' in args.suite:
                report.case('untrusted-tls-rejected',lambda: suite.tls_rejection(args.https_origin,tls))
            if 'boot-time' in args.suite:
                for cycle in range(args.cycles):
                    report.case('boot-ready:'+str(cycle+1),suite.boot_time)
            for name in (names if args.case else ['lc-48000-stereo','he-48000-stereo','hev2-44100-stereo']):
                if 'soak' in args.suite:
                    report.case('soak:'+name, lambda n=name: suite.sustained(args.soak_seconds,n,cpu=True))
                if 'load' in args.suite:
                    baseline = []
                    if args.load_idle_recovery:
                        def baseline_heap():
                            baseline.extend(suite.idle_heap())
                            return dict(samples=baseline)
                        report.case('load-idle-baseline:'+name, baseline_heap)
                    report.case('cpu-under-http-load:'+name, lambda n=name: suite.sustained(args.load_seconds,n,cpu=True,load=True))
                    if args.load_idle_recovery:
                        def recovered_heap():
                            final = suite.idle_heap()
                            check_recovery_heap(baseline,final)
                            return dict(samples=final)
                        report.case('load-idle-recovery:'+name, recovered_heap)
            report.data['server_events'] = server.events
            if tls:
                report.data['tls_events'] = tls.events
    finally:
        if tls:
            tls.__exit__()
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n',encoding='utf-8')
        def restore():
            board.stop()
            if not args.leave_stopped:
                board.reboot()
                time.sleep(3)
                deadline = time.monotonic()+40
                while time.monotonic() < deadline:
                    try:
                        require(board.info()['app_elf_sha256'] == info['app_elf_sha256'], 'Unexpected firmware after test')
                        return dict(rebooted=True)
                    except (OSError, TimeoutError):
                        time.sleep(1)
                raise Failure('Board did not return after restoring saved station')
            return dict(left_stopped=True)
        report.case('restore-board', restore)
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    sys.exit(main())
