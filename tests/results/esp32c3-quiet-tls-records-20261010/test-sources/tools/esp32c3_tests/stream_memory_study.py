"""Continuous AAC memory investigation with explicitly incomplete checkpoints.

Uses the existing /stream pacing, playback/CPU/heap gates and passive filtered
UART capture. No Stop, reconnect or reset occurs inside the load window.
"""
import argparse
import json
from pathlib import Path
import time

from common import Board, Report, check_recovery_heap, fixtures, require, sha
from diagnostic import DiagnosticCapture
from memory import wait_ready
from ota import image_info, snapshot, verify_snapshot
from public_streams import no_runtime_faults
from run import Suite
from audio_test_server.server import Server


def save_json(path, value):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    temporary.replace(path)


class Checkpoint:
    def __init__(self, output, capture, seconds=30, clock=time.perf_counter):
        self.output, self.capture, self.seconds, self.clock = output, capture, seconds, clock
        self.next = 0

    def __call__(self, completed, current):
        now = self.clock()
        if now < self.next:
            return
        self.next = now+self.seconds
        partial = dict(current, in_progress=True, observed_until=now)
        save_json(self.output/'status.json', completed+[partial])
        save_json(self.output/'performance.json', list(self.capture.rows))
        save_json(self.output/'checkpoint.json', dict(complete=False, at=now,
                  case=current['case'], elapsed_seconds=now-current['started_at'],
                  samples=len(current['samples'])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--serial-port', required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--case', default='hev2-44100-stereo')
    parser.add_argument('--seconds', type=int, default=600,
                        help='Continuous playback duration in seconds (default: %(default)s)')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.seconds >= 60, 'Use at least sixty seconds')
    require(not args.output.exists(), 'Use a new result directory')
    config = args.firmware.with_name('sdkconfig').read_text()
    require(all(k+'=y' not in config for k in ('CONFIG_YORADIO_QEMU',
        'CONFIG_YORADIO_DEEP_SLEEP_CLOCK')), 'Use awake physical firmware')
    specs = fixtures(None)
    require(args.case in specs and specs[args.case]['codec'] == 'aac',
            'This continuous stream investigation requires an AAC fixture')
    board = Board(args.board)
    identity = board.info()
    require(identity['app_elf_sha256'] == image_info(args.firmware.read_bytes())['app_elf_sha256'],
            'Wrong installed image')
    settings = snapshot(board)
    report = Report(args.output/'report.json', identity)
    report.data.update(firmware_sha256=sha(args.firmware.read_bytes()),
        sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        fixture_hashes={args.case: specs[args.case]['sha256']}, load_seconds=args.seconds,
        rx_diagnostics='CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=y' in config,
        cpu_budget_percent=None,
        server_options=dict(unpaced_files=False, delivery_stats=True),
        note='Diagnostic timing is not production CPU/IRQ qualification. Original failed gates retained.')
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:8770', specs, capture, args.output,
                  checkpoint=Checkpoint(args.output, capture), cpu_budget=None)
    idle = {}

    def settle(name):
        samples = suite.idle_heap()
        idle[name] = samples
        return dict(samples=samples)

    try:
        with Server(args.host, 8770, specs, delivery_stats=True) as server:
            report.case('idle-before', lambda: settle('before'))
            report.case('cpu-under-http-load:'+args.case,
                        lambda: suite.sustained(args.seconds, args.case, cpu=True, load=True))
            report.case('idle-after', lambda: settle('after'))
            def recovery():
                require(set(idle) == {'before', 'after'}, 'Missing settled idle checkpoint')
                check_recovery_heap(idle['before'], idle['after'])
                return dict(heap_recovered=True)
            report.case('stop-recovery', recovery)
            report.data['server_events'] = server.events
    finally:
        capture.close()
        save_json(args.output/'performance.json', capture.rows)
        report.case('runtime', lambda: no_runtime_faults(capture.rows))
        def restore():
            board.stop()
            board.reboot()
            wait_ready(board, identity['app_elf_sha256'])
            return dict(rebooted=True, **verify_snapshot(board, settings))
        report.case('restore-board', restore)
        report.save()
        expected = ['idle-before', 'cpu-under-http-load:'+args.case, 'idle-after',
                    'stop-recovery', 'runtime', 'restore-board']
        complete = [case['name'] for case in report.data['cases']] == expected
        # An interrupted load can run cleanup successfully without completing
        # its acceptance check. Do not turn that into a completed/PASS study.
        save_json(args.output/'checkpoint.json', dict(finished=True, complete=complete,
                  all_cases_pass=complete and report.exit_code() == 0, at=time.perf_counter()))
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
