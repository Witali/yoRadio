"""Physical transient-connection recovery, cancellation, EOF and idle-memory checks.

Temporarily changes watchdog/timeout settings, restores them in finally, and keeps
Wi-Fi/playlist/settings contents in RAM. Uses the shared board-independent server.
"""
import argparse
import json
import re
from pathlib import Path
import time

from common import Board, Report, check_playback, check_recovery_heap, fixtures, require
from diagnostic import DiagnosticCapture
from memory import wait_ready
from ota import image_info, snapshot, verify_snapshot
from public_streams import no_runtime_faults
from run import Suite
from audio_test_server.server import Server


def set_system(board, key, value):
    with board.websocket() as ws:
        ws.send(key+'='+str(value))
        ws.send('getsystem')
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            message = json.loads(ws.recv(timeout=5))
            if key in message:
                require(message[key] == value, 'System setting was not applied')
                return
    raise AssertionError('No system setting acknowledgement')


def set_watchdog(board, enabled):
    set_system(board, 'watchdog', int(enabled))


def check_runtime(rows, planned_reboots):
    allowed = set()
    for interval in planned_reboots:
        require(0 < interval['end']-interval['start'] <= 45, 'Invalid planned reboot interval')
        boot = [(i,r) for i,r in enumerate(rows) if interval['start'] <= r['at'] <= interval['end']
                and re.match(r'^(ESP-ROM:|rst:)', r['line'])]
        require(len(boot) == 2 and boot[0][1]['line'].startswith('ESP-ROM:') and
                re.match(r'^rst:0xc \(RTC_SW_CPU_RST\),boot:0x[0-9a-f]+ \(SPI_FAST_FLASH_BOOT\)$',
                         boot[1][1]['line']), 'Planned software reboot evidence missing or unexpected')
        require(not allowed.intersection(i for i,_ in boot), 'Overlapping reboot intervals')
        allowed.update(i for i,_ in boot)
    # Only the exact requested software-reset banners are excluded. Panic,
    # watchdog, allocation/decoder failures and additional boots still fail.
    no_runtime_faults([r for i,r in enumerate(rows) if i not in allowed])
    return dict(planned_software_reboots=len(planned_reboots))


def main():
    choices = ('recover-lc', 'recover-hev2', 'watchdog-off', 'stop', 'switch', 'disable-pending',
               'timeout-3', 'timeout-10', 'timeout-stall', 'settings-persistence')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--serial-port', required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--case', action='append', choices=choices)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists(), 'Choose a new output directory')
    config = args.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_YORADIO_QEMU=y' not in config and
            'CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config, 'Use awake physical firmware')
    board = Board(args.board)
    info = board.info()
    require(info['app_elf_sha256'] == image_info(args.firmware.read_bytes())['app_elf_sha256'],
            'Wrong installed image')
    before = snapshot(board)
    original_watchdog = before['settings']['getsystem']['watchdog']
    original_timeout = before['settings']['getsystem'].get('stationtimeout')
    specs = fixtures()
    report = Report(args.output/'report.json', info)
    report.data.update(fixture_hashes={n: specs[n]['sha256'] for n in
        ('lc-48000-stereo', 'hev2-44100-stereo', 'lc-22050-mono')}, server_events={}, planned_reboots=[])
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:8770', specs, capture, args.output)
    idle = {}

    def settle(name):
        idle[name] = suite.idle_heap()
        return dict(samples=idle[name])

    def exercise(label):
        recovery = label.startswith('recover-')
        enabled = label != 'watchdog-off'
        board.stop()
        set_watchdog(board, enabled)
        timeout = 3 if label in ('timeout-3', 'timeout-stall') else 10
        if original_timeout is not None:
            set_system(board, 'stationtimeout', timeout)
        name = 'hev2-44100-stereo' if label == 'recover-hev2' else 'lc-48000-stereo'
        server = Server(args.host, 8770, specs, initial_failures=2 if recovery else 100)
        try:
            with server:
                try:
                    if label == 'settings-persistence':
                        require(original_timeout is not None, 'Missing configurable station timeout')
                        set_system(board, 'stationtimeout', 3)
                        reboot_started = time.monotonic()
                        board.reboot()
                        wait_ready(board, info['app_elf_sha256'])
                        report.data['planned_reboots'].append(dict(start=reboot_started, end=time.monotonic()))
                        require(board.settings()['getsystem']['stationtimeout'] == 3,
                                'Station timeout did not persist across reboot')
                        for invalid in ('0', '121', '-1', '3.5', 'abc', '256'):
                            with board.websocket() as ws:
                                ws.send('stationtimeout='+invalid)
                                deadline = time.monotonic()+5
                                rejected = False
                                while time.monotonic() < deadline:
                                    if 'commandError' in json.loads(ws.recv(timeout=5)):
                                        rejected = True
                                        break
                                require(rejected, 'Invalid setting was not rejected')
                            require(board.settings()['getsystem']['stationtimeout'] == 3,
                                    'Invalid value changed station timeout')
                        return dict(reboot_persisted=True, rejected_invalid_values=6)
                    if label == 'timeout-stall':
                        suite.start(name, 'stall', 'aac')
                        samples = suite.observe(13, label)
                        require(any(s['audio'] and s['pcm_sample_rate']==48000 for s in samples),
                                'No playback before the stall')
                        require(all(not s['audio'] and s['format']=='station unavailable'
                                    for s in samples[-5:]), 'Stalled station did not stop as unavailable')
                        return dict(timeout_seconds=timeout, stalled_stream_stopped=True)
                    suite.start(name, 'recover', 'aac')
                    deadline = time.monotonic()+5
                    while not server.events and time.monotonic() < deadline:
                        time.sleep(.05)
                    require(server.events and server.events[0].get('response_status') == 503,
                            'No controlled initial 503 response')
                    if label.startswith('timeout-'):
                        samples = suite.observe(timeout+4, label)
                        ended = next((s for s in samples if s['format']=='station unavailable'), None)
                        require(ended is not None and timeout-.5 <= ended['seconds'] <= timeout+1.5,
                                'Station unavailable status did not follow configured timeout')
                        require(all(not s['audio'] and s['format']=='station unavailable'
                                    for s in samples if s['seconds'] >= ended['seconds']),
                                'Unavailable station restarted without a new command')
                        require(all(e['requested_at']-server.events[0]['requested_at'] < timeout
                                    for e in server.events), 'Request after station deadline')
                        return dict(timeout_seconds=timeout, observed_seconds=ended['seconds'],
                                    attempts=len(server.events), terminal=True)
                    if recovery:
                        samples = suite.observe(10, label+':recover')
                        # The initial 1+2 s backoff is expected. Require full decoded
                        # format and continuous active status after five seconds.
                        playback = check_playback(samples, specs[name], warmup=5)
                        tail = suite.observe(15, label+':eof')
                        require(all(not s['audio'] and s['format']=='stream ended'
                                    for s in tail[-5:]), 'Finite file restarted or failed after EOF')
                        requests = [e for e in server.events if e['mode']=='recover']
                        require([e['response_status'] for e in requests] == [503,503,200],
                                'Unexpected retries or missing successful recovery')
                        gaps = [b['requested_at']-a['requested_at'] for a,b in zip(requests,requests[1:])]
                        require(1 <= gaps[0] <= 3 and 2 <= gaps[1] <= 4,
                                'Retry timing outside expected bounded backoff')
                        return dict(playback=playback, retry_intervals_seconds=gaps, eof_not_restarted=True)
                    if label == 'stop':
                        board.stop()
                    elif label == 'switch':
                        board.play(suite.url('file', 'lc-22050-mono'), 'aac')
                    elif label == 'disable-pending':
                        set_watchdog(board, False)
                    requests_before = sum(e['mode']=='recover' for e in server.events)
                    samples = suite.observe(7, label+':after-action')
                    require(sum(e['mode']=='recover' for e in server.events) == requests_before,
                            'Cancelled/disabled connection retried')
                    if label == 'switch':
                        check_playback(samples, specs['lc-22050-mono'])
                    else:
                        require(all(not s['audio'] for s in samples), 'Cancelled/disabled stream became active')
                    return dict(requests_before=requests_before, cancelled=True,
                                new_station_plays=label=='switch')
                finally:
                    board.stop()
        finally:
            report.data['server_events'][label] = server.events
            report.save()

    try:
        report.case('idle-before', lambda: settle('before'))
        for label in args.case or choices:
            report.case(label, lambda label=label: exercise(label))
        report.case('idle-after', lambda: settle('after'))
        report.case('stop-recovery', lambda: check_recovery_heap(idle['before'], idle['after']))
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')
        report.case('runtime', lambda: check_runtime(capture.rows, report.data['planned_reboots']))
        def restore():
            board.stop()
            set_watchdog(board, bool(original_watchdog))
            if original_timeout is not None:
                set_system(board, 'stationtimeout', original_timeout)
            board.reboot()
            wait_ready(board, info['app_elf_sha256'])
            return verify_snapshot(board, before)
        report.case('restore-board', restore)
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
