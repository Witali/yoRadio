"""Install a different C3 app through OTA while a controlled AAC stream plays.

Both firmware files must have their exact sdkconfig beside them. Only the app
is written. Settings, Wi-Fi and playlist contents stay in RAM for comparison.
"""
import argparse
import json
from pathlib import Path
import time

from common import Board, Report, check_playback, fixtures, require
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from run import Capture, Suite
from audio_test_server.server import Server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', type=int, default=8770)
    parser.add_argument('--current-firmware', type=Path, required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--serial-port')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for path in (args.current_firmware, args.firmware):
        config = path.with_name('sdkconfig').read_text()
        require('CONFIG_YORADIO_QEMU=y' not in config, 'Never install a QEMU test image')
        require('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config, 'Use awake qualification images')
    board = Board(args.board)
    initial = board.info()
    current = image_info(args.current_firmware.read_bytes())
    target_bytes = args.firmware.read_bytes()
    target = image_info(target_bytes)
    require(initial['app_elf_sha256'] == current['app_elf_sha256'], 'Wrong initial image')
    require(target['app_elf_sha256'] != current['app_elf_sha256'], 'Use ota.py for same-image tests')
    require(len(target_bytes) <= initial['max_size'], 'Image exceeds OTA slot')
    before = snapshot(board)
    report = Report(args.output/'report.json', initial)
    report.data.update(current_image=current, target_image=target)
    specs = fixtures()
    name = 'lc-48000-stereo'
    report.data['fixture_hashes'] = {name: specs[name]['sha256']}
    capture = Capture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:{args.port}', specs, capture, args.output)

    def transition():
        suite.start(name, 'stream', 'aac')
        playback = check_playback(suite.observe(7, 'before-ota'), specs[name])
        slot = 'app0' if initial['partition'] == 'app1' else 'app1'
        started = time.monotonic()
        # Deliberately do not stop first: the firmware must quiesce playback.
        status, body = upload(board.origin, multipart(target_bytes))
        require(status == 200 and body == b'OK', 'OTA did not return HTTP 200 OK')
        after = wait_image(board, target['app_elf_sha256'], slot)
        return dict(playing_before_upload=playback, after=after,
                    elapsed_seconds=time.monotonic()-started,
                    **verify_snapshot(board, before))

    try:
        with Server(args.host, args.port, specs):
            report.case('ota:transition-while-playing', transition)
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
