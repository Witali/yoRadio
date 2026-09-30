"""Survey full-radio RAM at boot, AAC open, playback and stop; no settings writes."""
import argparse
import json
from pathlib import Path
import time

from common import Board, Report, check_playback, fixtures, require
from run import Capture, Suite
from audio_test_server.server import Server


def wait_ready(board, identity):
    time.sleep(3)
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        try:
            require(board.info()['app_elf_sha256'] == identity,
                    'Unexpected application after reboot')
            return
        except (OSError, TimeoutError):
            time.sleep(1)
    raise AssertionError('Board did not return after reboot')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--serial-port', required=True)
    parser.add_argument('--port', type=int, default=8770)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fixture-manifest', type=Path)
    parser.add_argument('--case', action='append')
    parser.add_argument('--seconds', type=int, default=35)
    args = parser.parse_args()
    require(args.seconds >= 35, 'At least 35 seconds covers a stack survey')
    specs = fixtures(args.fixture_manifest)
    names = args.case or ['lc-48000-stereo', 'he-48000-stereo', 'hev2-44100-stereo']
    require(all(name in specs for name in names), 'Unknown fixture')
    for name in names:
        require(specs[name]['codec'] == 'aac' or specs[name]['seconds'] >= args.seconds + 3,
                'Non-AAC fixtures must be longer than the observation window')
    board = Board(args.board)
    info = board.info()
    args.output.mkdir(parents=True, exist_ok=True)
    report = Report(args.output/'report.json', info)
    report.data['fixture_hashes'] = {name: specs[name]['sha256'] for name in names}
    capture = Capture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:{args.port}', specs, capture, args.output)
    try:
        board.stop()
        board.reboot()
        wait_ready(board, info['app_elf_sha256'])
        board.stop()
        time.sleep(12)
        with Server(args.host, args.port, specs) as server:
            for name in names:
                def measure(name=name):
                    spec = specs[name]
                    suite.start(name, 'stream' if spec['codec'] == 'aac' else 'file', spec['codec'])
                    try:
                        return check_playback(suite.observe(args.seconds, name, interval=1), spec)
                    finally:
                        board.stop()
                        time.sleep(12)
                report.case('memory-playback:'+name, measure)
            report.data['server_events'] = server.events
        def evidence():
            lines = [row['line'] for row in capture.rows]
            for marker in ('PERF RAM: stage=app-start', 'PERF STACK:',
                           'PERF RAM: stage=aac-after-first-process'):
                require(any(marker in line for line in lines), 'Missing diagnostic evidence: '+marker)
            require(not any('serial capture interrupted' in line for line in lines),
                    'Serial capture interrupted')
            return dict(records=len(lines))
        report.case('memory-survey-evidence', evidence)
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
        def restore():
            board.stop()
            board.reboot()
            wait_ready(board, info['app_elf_sha256'])
            return dict(rebooted=True)
        report.case('restore-board', restore)
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
