"""Run C3 OTA checks and fail on retained panic/capture errors despite HTTP success."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from common import fixtures, require
from diagnostic import DiagnosticCapture
from audio_test_server.server import Server
import ota


FAULT = re.compile(r'assert failed|Guru Meditation|CORRUPT HEAP|PANIC registers:|'
                   r'serial capture interrupted|TCP_POOL:.*\baction=invalid-free')


def serial_health(rows):
    faults = [r for r in rows if FAULT.search(r['line'])]
    return dict(name='ota:serial-health', result='PASS' if rows and not faults else 'FAIL',
                evidence=dict(records=len(rows), faults=faults),
                note='Expected OTA reboot banners are allowed; panic/capture errors are not.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--serial-port', required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--suite', action='append', choices=('negative', 'roundtrip', 'while-playing', 'slow'))
    args = parser.parse_args()
    config = args.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_YORADIO_QEMU=y' not in config, 'Do not flash a QEMU image')
    require('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config, 'Use an awake image')
    args.output.mkdir(parents=True, exist_ok=True)
    specs = fixtures()
    metadata = dict(script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    fixture_hashes={'lc-48000-stereo': specs['lc-48000-stereo']['sha256']})
    capture = DiagnosticCapture(args.serial_port)
    argv = sys.argv
    result = 1
    try:
        with Server(args.host, 8770, specs) as server:
            suites = args.suite or ['negative', 'roundtrip', 'while-playing', 'slow']
            sys.argv = ['ota.py', '--board', args.board, '--firmware', str(args.firmware),
                        '--play-url', f'http://{args.host}:8770/stream/lc-48000-stereo',
                        '--output', str(args.output/'report.json')]
            for suite in suites:
                sys.argv += ['--suite', suite]
            result = ota.main()
            metadata['server_events'] = server.events
    finally:
        sys.argv = argv
        capture.close()
        health = serial_health(capture.rows)
        for name, value in [('performance.json', capture.rows), ('capture.json', metadata),
                            ('serial-health.json', health)]:
            (args.output/name).write_text(json.dumps(value, indent=2)+'\n', newline='\n')
    print(health['name'] + ': ' + health['result'], flush=True)
    return 1 if result or health['result'] != 'PASS' else 0


if __name__ == '__main__':
    raise SystemExit(main())
