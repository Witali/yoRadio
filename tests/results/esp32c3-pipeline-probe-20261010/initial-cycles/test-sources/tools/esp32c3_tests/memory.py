"""Survey full-radio RAM at boot, AAC open, playback and stop; no settings writes."""
import argparse
import json
from pathlib import Path
import time

from common import Board, Report, check_playback, fixtures, require
from ota import snapshot, verify_snapshot
from run import Capture, Suite
from audio_test_server.server import Server


def wait_ready(board, identity):
    time.sleep(3)
    deadline = time.perf_counter() + 40
    while time.perf_counter() < deadline:
        try:
            require(board.info()['app_elf_sha256'] == identity,
                    'Unexpected application after reboot')
            return
        except (OSError, TimeoutError):
            time.sleep(1)
    raise AssertionError('Board did not return after reboot')


def set_audio_buffer(board, blocks):
    with board.websocket() as ws:
        ws.send('abuff=' + str(blocks))
        ws.send('getsystem')
        deadline = time.perf_counter() + 5
        while time.perf_counter() < deadline:
            value = json.loads(ws.recv(timeout=5))
            if 'abuff' in value:
                require(value['abuff'] == blocks, 'Audio buffer setting was not applied')
                return
    raise AssertionError('No audio buffer setting acknowledgement')


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
    parser.add_argument('--minimal', action='store_true',
                        help='Require production RAM logs, without CPU/stack instrumentation')
    parser.add_argument('--audio-buffer-blocks', type=int, choices=range(5, 15),
                        help='Temporarily select 5..14 blocks; restore and verify settings at exit')
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
    before = snapshot(board)
    original_blocks = before['settings']['getsystem']['abuff']
    args.output.mkdir(parents=True, exist_ok=True)
    report = Report(args.output/'report.json', info)
    report.data['fixture_hashes'] = {name: specs[name]['sha256'] for name in names}
    report.data['survey'] = dict(minimal=args.minimal,
        original_audio_buffer_blocks=original_blocks,
        audio_buffer_blocks=args.audio_buffer_blocks or original_blocks)
    report.save()  # Keep the non-private buffer value for recovery if interrupted.
    capture = Capture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:{args.port}', specs, capture, args.output)
    try:
        board.stop()
        if args.audio_buffer_blocks is not None:
            set_audio_buffer(board, args.audio_buffer_blocks)
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
            markers = ('Memory after first decoded frame:',) if args.minimal else (
                'PERF RAM: stage=app-start', 'PERF STACK:',
                'PERF RAM: stage=aac-after-first-process')
            for marker in markers:
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
            if args.audio_buffer_blocks is not None:
                set_audio_buffer(board, original_blocks)
            board.reboot()
            wait_ready(board, info['app_elf_sha256'])
            return dict(rebooted=True, **verify_snapshot(board, before))
        report.case('restore-board', restore)
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
