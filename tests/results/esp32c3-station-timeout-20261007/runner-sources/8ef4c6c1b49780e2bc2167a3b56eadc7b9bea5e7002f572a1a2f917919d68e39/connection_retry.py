"""Physical transient-connection recovery, cancellation, EOF and idle-memory checks.

Temporarily changes only the watchdog setting, restores it in finally, and keeps
Wi-Fi/playlist/settings contents in RAM. Uses the shared board-independent server.
"""
import argparse
import json
from pathlib import Path
import time

from common import Board, Report, check_playback, check_recovery_heap, fixtures, require
from diagnostic import DiagnosticCapture
from memory import wait_ready
from ota import image_info, snapshot, verify_snapshot
from public_streams import no_runtime_faults
from run import Suite
from audio_test_server.server import Server


def set_watchdog(board, enabled):
    with board.websocket() as ws:
        ws.send('watchdog='+str(int(enabled)))
        ws.send('getsystem')
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            value = json.loads(ws.recv(timeout=5))
            if 'watchdog' in value:
                require(value['watchdog'] == int(enabled), 'Watchdog setting was not applied')
                return
    raise AssertionError('No watchdog setting acknowledgement')


def main():
    choices = ('recover-lc', 'recover-hev2', 'watchdog-off', 'stop', 'switch', 'disable-pending')
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
    specs = fixtures()
    report = Report(args.output/'report.json', info)
    report.data.update(fixture_hashes={n: specs[n]['sha256'] for n in
        ('lc-48000-stereo', 'hev2-44100-stereo', 'lc-22050-mono')}, server_events={})
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
        name = 'hev2-44100-stereo' if label == 'recover-hev2' else 'lc-48000-stereo'
        server = Server(args.host, 8770, specs, initial_failures=2 if recovery else 100)
        try:
            with server:
                try:
                    suite.start(name, 'recover', 'aac')
                    deadline = time.monotonic()+5
                    while not server.events and time.monotonic() < deadline:
                        time.sleep(.05)
                    require(server.events and server.events[0].get('response_status') == 503,
                            'No controlled initial 503 response')
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
        report.case('runtime', lambda: no_runtime_faults(capture.rows))
        def restore():
            board.stop()
            set_watchdog(board, bool(original_watchdog))
            board.reboot()
            wait_ready(board, info['app_elf_sha256'])
            return verify_snapshot(board, before)
        report.case('restore-board', restore)
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
