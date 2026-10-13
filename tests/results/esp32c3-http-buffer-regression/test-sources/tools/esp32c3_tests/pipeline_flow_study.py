"""Profile selected existing files and deliberately starve one as a control.

Installs nothing. Uses the existing load gates; an expected diagnostic failure
remains FAIL. Settings/credentials are never written to result files.
"""
import argparse
import json
from pathlib import Path

from common import Board, Report, fixtures, require, sha
from diagnostic import DiagnosticCapture
from ota import image_info
from public_streams import no_runtime_faults
from run import Suite
from audio_test_server.server import Server
from pipeline_flow import summarize


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--serial-port', required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--case', action='append', required=True)
    p.add_argument('--seconds', type=int, default=60)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists(), 'Use a fresh result directory')
    config = args.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_YORADIO_PIPELINE_PROFILE=y' in config, 'Profile is disabled')
    require('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config and
            'CONFIG_YORADIO_QEMU=y' not in config, 'Use an awake physical image')
    require(args.seconds >= 40, 'At least 40 seconds per load case')
    board = Board(args.board)
    initial = board.info()
    require(initial['app_elf_sha256'] == image_info(args.firmware.read_bytes())['app_elf_sha256'],
            'Wrong installed image')
    specs = fixtures(args.fixtures)
    require(all(n in specs for n in args.case), 'Unknown fixture')
    report = Report(args.output/'report.json', initial)
    report.data.update(firmware_sha256=sha(args.firmware.read_bytes()),
        sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        fixture_hashes={n: specs[n]['sha256'] for n in args.case},
        load_seconds=args.seconds, warmup_seconds=10,
        server_options=dict(unpaced_files=True, delivery_stats=True),
        control='First case served through /jitter, paced at 1.02x with 35 ms added per 8192 bytes')
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:8770', specs, capture, args.output)

    def save():
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')

    try:
        with Server(args.host, 8770, specs, unpaced_files=True, delivery_stats=True) as server:
            for name in args.case:
                report.case('load:'+name, lambda n=name: suite.sustained(args.seconds, n, cpu=True, load=True))
                save()
            name = args.case[0]
            def jitter():
                suite.start(name, 'jitter', specs[name]['codec'])
                try:
                    samples = suite.observe(40, 'input-jitter:'+name, interval=.1)
                    require(any(s['audio'] for s in samples), 'No playback in starvation control')
                    save()
                    case = summarize(args.output)['cases'][-1]
                    flow = case['flow_decoder']
                    require(flow.get('input', {}).get('count', 0) > 0 and
                            flow.get('input', {}).get('us', 0) > 0,
                            'Input-starvation control was not observed')
                    return dict(input_empty_observed=True)
                finally:
                    board.stop()
            report.case('control:input-jitter', jitter)
            report.data['server_events'] = server.events
    finally:
        def restore():
            board.stop()
            require(board.info()['app_elf_sha256'] == initial['app_elf_sha256'], 'Image changed')
            return dict(left_stopped=True)
        report.case('restore-board', restore)
        capture.close()
        save()
        report.case('runtime', lambda: no_runtime_faults(capture.rows))
        report.save()
        if (args.output/'status.json').exists():
            (args.output/'summary.json').write_text(json.dumps(summarize(args.output), indent=2)+'\n')
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
