"""Install the audited listening app and retain all private snapshots in memory.

Successful installation leaves the fractional clock image playing for the user.
No bootloader, partition table, filesystem or NVS image is uploaded.
"""
import json
from pathlib import Path
import sys
import time

REPO = Path.cwd()
EVIDENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'tools/esp32c3_tests'))
from common import Board, require, exception_details
from ota import snapshot, verify_snapshot, image_info, upload, multipart, wait_image


def main():
    target_path = REPO / 'firmware/development/esp32c3-idf61-listen-48k/app.bin'
    old_path = REPO / 'firmware/development/esp32c3-idf-6.1-r9a97-production-qio80/app.bin'
    image = target_path.read_bytes()
    expected, rollback = image_info(image), image_info(old_path.read_bytes())
    audit = json.loads((EVIDENCE / 'build-audit.json').read_text())
    require(audit['result'] == 'PASS' and audit['image'] == expected, 'Build audit mismatch')
    report_path = EVIDENCE / 'deployment.json'
    require(not report_path.exists(), 'Preserve the original deployment result')
    board = Board('http://192.168.100.4')
    active, initial = board.info(), board.status()
    require(active['app_elf_sha256'] == rollback['app_elf_sha256'], 'Unexpected initial application')
    require(len(image) <= active['max_size'], 'Image exceeds OTA partition')
    before = snapshot(board)
    target_partition = 'app1' if active['partition'] == 'app0' else 'app0'
    result = dict(result='RUNNING', initial_identity=active, initial_status=initial,
                  candidate=expected, app_only=True, private_snapshots_saved=False)
    report_path.write_text(json.dumps(result, indent=2) + '\n')
    try:
        print('Uploading listening app through WebUI OTA', flush=True)
        board.stop()
        started = time.perf_counter()
        code, body = upload(board.origin, multipart(image))
        require(code == 200 and body == b'OK', 'OTA did not return HTTP 200 OK')
        identity = wait_image(board, expected['app_elf_sha256'], target_partition, timeout=60)
        result.update(identity=identity, ota_http=code,
                      ota_seconds=time.perf_counter() - started,
                      persistence=verify_snapshot(board, before))
        states = []
        for _ in range(3):
            time.sleep(5)
            states.append(board.status())
        result['states'] = states
        require(all(s.get('audio') for s in states), 'Radio did not resume after OTA')
        require(board.info() == identity, 'Application identity changed during observation')
        result.update(result='PASS', installed_for_listening=True, analog_listening='pending')
        print('Installed identity, settings and three playing observations verified', flush=True)
    except Exception as error:
        result.update(result='FAIL', exception_chain=exception_details(error))
        raise
    finally:
        report_path.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
