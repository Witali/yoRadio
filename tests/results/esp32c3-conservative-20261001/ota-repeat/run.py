"""Reproduce same-image OTA gates with filtered serial evidence and a local AAC fixture.

Run from the repository root. Does not write settings or reset serial lines.
The normal OTA runner keeps its private preservation snapshot in RAM only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import fixtures, require
from diagnostic import DiagnosticCapture
from audio_test_server.server import Server
import ota


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--serial-port', required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = args.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_YORADIO_QEMU=y' not in config, 'Do not flash a QEMU image')
    require('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config, 'Use an awake image')
    args.output.mkdir(parents=True, exist_ok=True)
    specs = fixtures()
    metadata = dict(script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    fixture_hashes={'lc-48000-stereo': specs['lc-48000-stereo']['sha256']})
    capture = DiagnosticCapture(args.serial_port)
    try:
        with Server(args.host, 8770, specs) as server:
            sys.argv = ['ota.py', '--board', args.board, '--firmware', str(args.firmware),
                        '--suite', 'negative', '--suite', 'roundtrip',
                        '--suite', 'while-playing', '--suite', 'slow',
                        '--play-url', f'http://{args.host}:8770/stream/lc-48000-stereo',
                        '--output', str(args.output/'report.json')]
            result = ota.main()
            metadata['server_events'] = server.events
            return result
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')
        (args.output/'capture.json').write_text(json.dumps(metadata, indent=2)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
