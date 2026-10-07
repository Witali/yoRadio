"""Matched all-codec load, EOF and switching checks for C3 scheduling.

Requires an awake image with flow profiling disabled. Installs nothing and
retains every original acceptance failure. No settings are saved to disk.
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

SHORT = ['mp3-320', 'lc-48000-stereo', 'he-48000-stereo', 'hev2-44100-stereo',
         'vorbis-q10', 'opus-510', 'flac-level8']
LOAD = ['stress-mp3-48000-2ch-16bit-200s', 'lc-48000-stereo', 'he-48000-stereo',
        'hev2-44100-stereo', 'stress-vorbis-48000-2ch-16bit-200s',
        'stress-opus-48000-2ch-16bit-200s', 'stress-flac-48000-2ch-16bit-120s',
        'radio-groovesalad-lpc32', 'radio-indiepop-lpc32']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--serial-port', required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--seconds', type=int, default=40)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists(), 'Use a new result directory')
    require(args.seconds >= 40, 'Keep at least the original 40-second load window')
    config = args.firmware.with_name('sdkconfig').read_text()
    require(all(setting+'=y' not in config for setting in
        ('CONFIG_YORADIO_PIPELINE_PROFILE', 'CONFIG_YORADIO_QEMU', 'CONFIG_YORADIO_DEEP_SLEEP_CLOCK')),
        'Use awake physical firmware with flow profiling off')
    board = Board(args.board)
    identity = board.info()
    require(identity['app_elf_sha256'] == image_info(args.firmware.read_bytes())['app_elf_sha256'],
            'Wrong installed image')
    settings = snapshot(board)
    specs = fixtures(args.fixtures)
    require(all(n in specs for n in LOAD+SHORT), 'Missing matrix fixture')
    report = Report(args.output/'report.json', identity)
    report.data.update(firmware_sha256=sha(args.firmware.read_bytes()),
        sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        output_priority=8 if 'CONFIG_YORADIO_OUTPUT_TASK_FIRST=y' in config else 6,
        fixture_hashes={n: specs[n]['sha256'] for n in LOAD+SHORT}, load_seconds=args.seconds,
        server_options=dict(unpaced_files=True, delivery_stats=True))
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:8770', specs, capture, args.output)

    def save():
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')

    checkpoints = []
    def settle():
        samples = suite.idle_heap()
        checkpoints.append(samples)
        return dict(samples=samples)

    try:
        with Server(args.host, 8770, specs, unpaced_files=True, delivery_stats=True) as server:
            report.case('idle-baseline', settle)
            for name in LOAD:
                report.case('cpu-under-http-load:'+name,
                    lambda n=name: suite.sustained(args.seconds, n, cpu=True, load=True))
                report.case('idle-after:'+name, settle)
                def recovery():
                    require(len(checkpoints) >= 2, 'Missing settled heap observations')
                    check_recovery_heap(checkpoints[-2], checkpoints[-1])
                    return dict(heap_recovered=True)
                report.case('stop-recovery:'+name, recovery)
                save()
            for name in SHORT:
                report.case('file-eof:'+name, lambda n=name: suite.file(n))
                save()
            report.case('stop-play-generation', suite.stop_race)
            report.case('switching-and-heap', lambda: suite.switching(SHORT, 3))
            report.data['server_events'] = server.events
    finally:
        capture.close()
        save()
        report.case('runtime', lambda: no_runtime_faults(capture.rows))
        def restore():
            board.stop()
            board.reboot()
            wait_ready(board, identity['app_elf_sha256'])
            return dict(rebooted=True, **verify_snapshot(board, settings))
        report.case('restore-board', restore)
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
