"""Physical HTTP completion checks over real TLS; explicit negative fixtures."""
import argparse
import copy
import json
from pathlib import Path
import re
import time

from common import Board, Report, fixtures, matches, require, sha
from diagnostic import DiagnosticCapture
from ota import image_info, snapshot, verify_snapshot
from run import Suite
from audio_test_server.tls_framing import FramingServer, MODES


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--serial-port', required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--ca', type=Path, required=True)
    p.add_argument('--cert', type=Path, required=True)
    p.add_argument('--key', type=Path, required=True)
    p.add_argument('--case', default='hev2-44100-stereo')
    p.add_argument('--mode', action='append', choices=MODES)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists(), 'Preserve existing evidence')
    manifest = json.loads(args.firmware.with_name('manifest.json').read_text())
    cfg = args.firmware.with_name('sdkconfig').read_text()
    require(manifest.get('laboratory_only') is True and
            manifest.get('extra_trust_ca_sha256') == sha(args.ca.read_bytes()),
            'Use a labelled lab image trusting exactly this extra CA')
    require('CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y' in cfg and
            'CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL=y' in cfg and
            'CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN=16384' in cfg,
            'Keep full TLS capacity and normal public certificate roots')
    require(all(k+'=y' not in cfg for k in ('CONFIG_YORADIO_QEMU',
            'CONFIG_YORADIO_DEEP_SLEEP_CLOCK', 'CONFIG_ESP_CONSOLE_NONE')),
            'Use awake physical profiling firmware')
    board = Board(args.board)
    identity = board.info()
    require(identity['app_elf_sha256'] == image_info(args.firmware.read_bytes())['app_elf_sha256'],
            'Wrong installed image')
    before = snapshot(board)
    specs = fixtures()
    require(args.case in specs, 'Unknown fixture')
    report = Report(args.output/'report.json', identity)
    report.data.update(firmware_sha256=sha(args.firmware.read_bytes()),
        sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        leaf_certificate_sha256=sha(args.cert.read_bytes()),
        fixture_sha256=specs[args.case]['sha256'], test_ca_sha256=sha(args.ca.read_bytes()),
        scope='Real TLS/HTTP framing, full-format observation and terminal state; not an acoustic or PCM identity test')
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, 'https://'+args.host+':8773', specs, capture, args.output, cpu_budget=None)

    def check(mode, server):
        board.stop()
        time.sleep(.8)
        event_count = len(server.events)
        started = time.monotonic()
        expected = 'stream read failed' if mode in ('length-short','chunked-short','close-raw') else 'stream ended'
        try:
            board.play(f'https://{args.host}:8773/{mode}/{args.case}', specs[args.case]['codec'])
            samples = suite.observe(specs[args.case]['seconds']+7, 'framing:'+mode, interval=.15)
            # Freeze before any assertion or Stop can alter connection evidence.
            events = copy.deepcopy(server.events[event_count:])
            report.data.setdefault('observations', {})[mode] = events
            complete = [s for s in samples if matches(s, specs[args.case])]
            require(len(complete) >= 3, 'No sustained full-format PCM observation')
            first = complete[0]['seconds']
            require(all(matches(s,specs[args.case]) for s in samples if s['seconds'] >= first and s.get('audio')),
                    'Format changed before completion')
            require(all(not s.get('audio') and s.get('format') == expected for s in samples[-3:]),
                    'Wrong terminal state: expected '+expected)
            rows = capture.since(started)
            require(not any(re.search(r'allocation failed|decode (?:error|failed)|PANIC|assert failed|CORRUPT HEAP|serial capture interrupted|watchdog',r['line']) for r in rows),
                    'Runtime decoder/memory/serial failure')
            require(len(events) == 1 and events[0].get('complete') is True and 'error' not in events[0],
                    'Server did not send the complete intended fixture once')
            require(events[0]['dropped_records'] == events[0]['dropped_writes'] == 0,
                    'Truncated TLS evidence')
            return dict(expected_terminal=expected, observed_terminal=samples[-1]['format'],
                        full_format_samples=len(complete), first_full_pcm_seconds=first)
        finally:
            board.stop()

    try:
        with FramingServer(args.host, 8773, {args.case:specs[args.case]}, args.cert, args.key) as server:
            for mode in args.mode or MODES:
                report.case('framing:'+mode, lambda m=mode: check(m,server))
            report.data['server_events'] = server.events
    finally:
        board.stop()
        report.case('settings-preserved', lambda: verify_snapshot(board,before))
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
