"""Separate initial network-buffer growth from continuing heap loss on a C3.

Keep one HTTP audio connection open across initial and settled load windows,
then compare settled idle heaps. This supplements, never replaces, run.py's
original acceptance result. No settings are written; saved playback is restored.
"""
import argparse
import json
from pathlib import Path
import time

from common import (Board, Report, check_cpu, check_playback, check_recovery_heap,
                    fixtures, require)
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
    parser.add_argument('--fixture-manifest', type=Path, required=True)
    parser.add_argument('--case', required=True)
    parser.add_argument('--initial-seconds', type=int, default=40)
    parser.add_argument('--settled-seconds', type=int, default=80)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.initial_seconds >= 40 and args.settled_seconds >= 60,
            'Use at least 40 seconds initially and 60 seconds to test stabilization')
    specs = fixtures(args.fixture_manifest)
    spec = specs[args.case]
    require(spec['seconds'] >= args.initial_seconds+args.settled_seconds+10,
            'Fixture must cover both uninterrupted observation windows')
    board = Board(args.board)
    identity, before = board.info(), snapshot(board)
    report = Report(args.output/'report.json', identity)
    report.data.update(fixture_hashes={args.case: spec['sha256']}, windows=[])
    capture = Capture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:{args.port}', specs, capture, args.output)
    idle = []

    def checkpoint():
        values = suite.idle_heap()
        idle.append(values)
        return values

    def phase(name, seconds, warmup):
        started = time.monotonic()
        try:
            samples = suite.observe(seconds, name, interval=.1)
            result = check_playback(samples, spec, minimum=int(seconds*.6), warmup=warmup)
            require(max(s['request_ms'] for s in samples) < 2000, 'WebUI response exceeded 2 s')
            result.update(check_cpu(capture.since(started+warmup), start=started+warmup,
                                    end=time.monotonic()))
            result['max_http_ms'] = max(s['request_ms'] for s in samples)
            return result
        finally:
            report.data['windows'].append(dict(name=name, start=started, warmup=warmup,
                                                end=time.monotonic()))

    try:
        report.case('idle-before', checkpoint)
        with Server(args.host, args.port, specs) as server:
            suite.start(args.case, 'file', spec['codec'])
            report.case('initial-load', lambda: phase('initial-load', args.initial_seconds, 10))
            # No stop, reconnect, settings change or reboot between these phases.
            report.case('settled-load', lambda: phase('settled-load', args.settled_seconds, 0))
            board.stop()
            report.data['server_events'] = server.events
        report.case('idle-after', checkpoint)

        def recovery():
            require(len(idle) == 2, 'Missing idle checkpoints')
            check_recovery_heap(idle[0], idle[1])
            return dict(heap_recovered=True)

        report.case('settled-idle-recovery', recovery)
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')

        def restore():
            board.stop()
            board.reboot()
            wait_ready(board, identity['app_elf_sha256'])
            return verify_snapshot(board, before)

        report.case('restore-board', restore)
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
