"""Check synthetic ICY title publication and full-rate AAC on a physical C3."""
import argparse
import json
from pathlib import Path
import time

from common import Board, Report, check_playback, fixtures, require, sha
from diagnostic import DiagnosticCapture
from ota import image_info, snapshot, verify_snapshot
from public_streams import no_runtime_faults
from run import Suite
from audio_test_server.icy import IcyServer, PROGRAMS


def web_snapshot(board):
    with board.websocket() as ws:
        ws.send('getindex')
        deadline = time.perf_counter() + 5
        while time.perf_counter() < deadline:
            message = json.loads(ws.recv(timeout=5))
            values = {p['id']: p['value'] for p in message.get('payload', [])}
            if 'meta' in values:
                return values
    raise AssertionError('No WebUI title snapshot')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--serial-port')
    p.add_argument('--functional-only', action='store_true',
                   help='Check playback/title/restore only; explicitly omit UART fault coverage (quiet firmware)')
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists(), 'Use a new output directory')
    config = args.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config and
            'CONFIG_YORADIO_QEMU=y' not in config, 'Use awake physical firmware')
    require(args.functional_only or args.serial_port and
            'CONFIG_LOG_MAXIMUM_LEVEL=0' not in config and
            'CONFIG_ESP_CONSOLE_NONE=y' not in config,
            'UART fault coverage requires logging firmware and --serial-port; use --functional-only for quiet firmware')
    board = Board(args.board)
    identity = board.info()
    require(identity['app_elf_sha256'] == image_info(args.firmware.read_bytes())['app_elf_sha256'],
            'Wrong installed firmware')
    settings = snapshot(board)
    specs = fixtures()
    spec = specs['hev2-44100-stereo']
    report = Report(args.output/'report.json', identity)
    report.data.update(fixture_sha256=spec['sha256'], firmware_sha256=sha(args.firmware.read_bytes()),
        sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        requested_coverage=['playback', 'webui-title', 'settings-restore'] +
                           ([] if args.functional_only else ['uart-runtime-faults']),
        uart_runtime_coverage='not requested' if args.functional_only else 'required',
        note='Synthetic titles only. Host sanitizer tests exhaustively cover read boundaries; TCP may coalesce writes.')
    capture = DiagnosticCapture(None if args.functional_only else args.serial_port)
    suite = Suite(board, f'http://{args.host}:8770', specs, capture, args.output)

    def run_case(name):
        board.stop()
        time.sleep(.8)
        started = time.perf_counter()
        try:
            board.play(f'http://{args.host}:8770/{name}', 'aac')
            samples = suite.observe(7, 'icy:'+name)
            playback = check_playback(samples, spec)
            values = web_snapshot(board)
            require(values['meta'] == PROGRAMS[name][1], 'WebUI title differs from expected synthetic title')
            require(values.get('playerwrap') == 'playing', 'WebUI no longer reports playback')
            if not args.functional_only:
                no_runtime_faults(capture.since(started))
            return dict(**playback, title_matches=True, title_bytes=len(PROGRAMS[name][1].encode()))
        finally:
            board.stop()

    try:
        with IcyServer(args.host, 8770, spec) as server:
            for name in PROGRAMS:
                report.case('icy:'+name, lambda n=name: run_case(n))
            report.data['server_events'] = server.events
    finally:
        if not args.functional_only:
            report.case('runtime', lambda: no_runtime_faults(capture.rows))
        def restore():
            board.stop()
            require(web_snapshot(board)['meta'] == '', 'Stopped title was not cleared')
            return dict(stopped=True, **verify_snapshot(board, settings))
        report.case('restore', restore)
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
