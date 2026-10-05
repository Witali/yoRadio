"""Check heap after natural EOF without masking retained state with Stop."""
import argparse
import json
from pathlib import Path

from common import Board, Report, check_playback, check_recovery_heap, fixtures, require
from memory import wait_ready
from ota import snapshot, verify_snapshot
from run import Capture, Suite
from audio_test_server.server import Server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', type=int, default=8770)
    parser.add_argument('--serial-port', required=True)
    parser.add_argument('--case', action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    specs = fixtures()
    require(all(n in specs and specs[n]['seconds'] >= 7 for n in args.case), 'Unknown/short fixture')
    board = Board(args.board)
    identity, settings = board.info(), snapshot(board)
    report = Report(args.output/'report.json', identity)
    report.data['fixture_hashes'] = {n: specs[n]['sha256'] for n in args.case}
    capture = Capture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:{args.port}', specs, capture, args.output)
    try:
        with Server(args.host, args.port, specs) as server:
            for name in args.case:
                for hint in ('auto', specs[name]['codec']):
                    checkpoints = {}
                    prefix = name+':'+hint+':'

                    def checkpoint(label, stop):
                        values = suite.idle_heap(stop=stop)
                        checkpoints[label] = values
                        if not stop:
                            require(all(not s['audio'] and s['format'] == 'stream ended'
                                        for s in suite.observations[-1]['samples']),
                                    'EOF state did not remain stopped')
                        return dict(samples=values, explicit_stop=stop)

                    report.case(prefix+'idle-before', lambda: checkpoint('before', True))

                    def play():
                        suite.start(name, 'file', hint)
                        rows = suite.observe(max(7, specs[name]['seconds']-3), prefix+'playing')
                        result = check_playback(rows, specs[name])
                        tail = suite.observe(8, prefix+'eof')
                        require(all(not s['audio'] and s['format'] == 'stream ended'
                                    for s in tail[-3:]), 'Natural EOF was not observed')
                        return result

                    report.case(prefix+'play-to-eof', play)
                    report.case(prefix+'idle-without-stop', lambda: checkpoint('eof', False))

                    def recovery(label):
                        require('before' in checkpoints and label in checkpoints, 'Missing heap checkpoint')
                        check_recovery_heap(checkpoints['before'], checkpoints[label])
                        return dict(heap_recovered=True)

                    report.case(prefix+'eof-recovery', lambda: recovery('eof'))
                    report.case(prefix+'idle-after-stop', lambda: checkpoint('stop', True))
                    report.case(prefix+'stop-recovery', lambda: recovery('stop'))
            report.data['server_events'] = server.events
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')

        def restore():
            board.stop()
            board.reboot()
            wait_ready(board, identity['app_elf_sha256'])
            return verify_snapshot(board, settings)

        report.case('restore-board', restore)
    return report.exit_code()


if __name__ == '__main__': raise SystemExit(main())
