"""Qualify actual CYD Wi-Fi persistence with bounded and injected IO failures.

Actual production functions and shared file transactions run over mapped stdio
and pthread mutex seams. No Wi-Fi credentials are printed and no board is used.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32-cyd2usb-native/main'
SHARED = ROOT / 'idf/components/native_storage'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run

spec = importlib.util.spec_from_file_location('web_warning_helpers', ROOT / 'tests/run-web-warning-regressions.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    test = ROOT / 'tests/native/cyd_wifi_storage_test.c'
    files = [Path(__file__), test, ROOT / 'tests/native/cyd_wifi_warning_test.c',
             ROOT / 'tests/run-cyd-wifi-warning.py', ROOT / 'tests/run-web-warning-regressions.py',
             MAIN / 'network_service.c', MAIN / 'network_service.h', MAIN / 'web_upload.c', MAIN / 'web_upload.h',
             SHARED / 'file_transaction.c', SHARED / 'include/file_transaction.h', SHARED / 'include/credential_line.h']
    # Compile the frozen snapshot so another task can edit unrelated web code
    # without changing the identity of the functions or dependencies qualified.
    hashes = {}
    for path in files:
        relative = path.relative_to(ROOT)
        data = path.read_bytes()
        hashes[relative.as_posix()] = hashlib.sha256(data).hexdigest()
        snapshot = out / 'sources' / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(data)
    source_root = out / 'sources'
    network = (source_root / (MAIN / 'network_service.c').relative_to(ROOT)).read_text()
    storage = (source_root / (MAIN / 'web_upload.c').relative_to(ROOT)).read_text()
    network_names = ['network_service_storage_init', 'read_credentials',
                     'network_service_validate_credentials_file',
                     'network_service_save_credentials_file', 'network_service_save_credentials']
    storage_names = ['web_upload_storage_init', 'backup_name', 'web_upload_open_file',
                     'web_upload_publish_file']
    (out / 'cyd-wifi-production.inc').write_text(''.join(helpers.function(network, name) for name in network_names))
    (out / 'cyd-storage-production.inc').write_text('static SemaphoreHandle_t s_storage_lock;\n' +
        ''.join(helpers.function(storage, name) for name in storage_names))
    binary = out / 'cyd-wifi-storage'
    frozen_shared = source_root / SHARED.relative_to(ROOT)
    command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
        '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-pthread',
        '-I' + host(out), '-I' + host(frozen_shared), '-I' + host(frozen_shared / 'include'),
        host(source_root / test.relative_to(ROOT)), '-o', host(binary)]
    try:
        build_log = run(command)
    except subprocess.CalledProcessError as error:
        (out / 'build.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    (out / 'build.log').write_bytes(build_log)
    fs = out / 'fs'
    fs.mkdir()
    try:
        log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS=halt_on_error=1',
                   'timeout', '30', host(binary), host(fs)])
    except subprocess.CalledProcessError as error:
        (out / 'test.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    (out / 'test.log').write_bytes(log)
    print(log.decode(), end='')
    report = {'passed': True, 'sanitizers': ['ASan', 'UBSan'], 'physical_flash_tested': False,
              'fixture_groups': int(re.search(rb': (\d+) fixture groups;', log)[1]),
              'source_sha256': hashes,
              'scope': 'Actual bounded validation, save, first-valid reader and storage/transaction functions; mapped host filesystem with SPIFFS no-overwrite rename rules, explicit stdio/stat/rename/remove/OOM/timeout faults and pthread concurrent saves. No hardware flash durability, network reconnection, or reboot timing claim.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
