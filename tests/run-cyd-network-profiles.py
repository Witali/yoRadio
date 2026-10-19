"""Qualify the actual CYD boot profile loader and existing file recovery.

The unchanged complete loader, physical-row helper, volatile erase, existing
web_upload_open_file/backup_name bodies and file_transaction.c run with mapped
real stdio, cookie read/close errors and RTOS lock seams. No Wi-Fi hardware,
SPIFFS power-loss durability, scheduling or full network runtime is qualified.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return result.returncode, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    main_dir = ROOT / 'idf/esp32-cyd2usb-native/main'
    storage = ROOT / 'idf/components/native_storage'
    wifi = ROOT / 'idf/components/native_wifi_store'
    test = ROOT / 'tests/native/cyd_network_profiles_test.c'
    helper = ROOT / 'tests/run-web-warning-regressions.py'
    files = [Path(__file__).resolve(), test, helper, main_dir / 'network_profiles.c',
             main_dir / 'network_profiles.h', main_dir / 'web_upload.c',
             main_dir / 'web_upload.h', storage / 'file_transaction.c',
             storage / 'include/file_transaction.h', storage / 'include/credential_line.h',
             wifi / 'native_wifi_store.c', wifi / 'include/native_wifi_store.h',
             ROOT / 'tools/codec_benchmark/run_output_dma_host.py']
    report = {'passed': False, 'scope': __doc__, 'physical_hardware': False,
              'sanitizers': ['ASan', 'UBSan'], 'source_sha256': {},
              'negative_controls': {}}
    frozen = out / 'sources'
    for path in files:
        data = path.read_bytes()
        relative = path.relative_to(ROOT)
        snapshot = frozen / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(data)
        report['source_sha256'][relative.as_posix()] = hashlib.sha256(data).hexdigest()
    sys.path.insert(0, str(frozen / 'tools/codec_benchmark'))
    spec = importlib.util.spec_from_file_location('frozen_helpers', frozen / helper.relative_to(ROOT))
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    web = (frozen / main_dir.relative_to(ROOT) / 'web_upload.c').read_text()
    (out / 'storage-production.inc').write_text(''.join(helpers.function(web, name)
        for name in ['backup_name', 'web_upload_open_file']))
    loader = (frozen / main_dir.relative_to(ROOT) / 'network_profiles.c').read_text()
    (out / 'esp_err.h').write_text('''#pragma once
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_NOT_FOUND 0x105
''')
    (out / 'esp_http_server.h').write_text('''#pragma once
#include "esp_err.h"
typedef struct httpd_req httpd_req_t;
''')
    command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-I' + host(out), '-I' + host(frozen / main_dir.relative_to(ROOT)),
               '-I' + host(frozen / storage.relative_to(ROOT)),
               '-I' + host(frozen / storage.relative_to(ROOT) / 'include'),
               '-I' + host(frozen / wifi.relative_to(ROOT)),
               '-I' + host(frozen / wifi.relative_to(ROOT) / 'include'),
               host(frozen / test.relative_to(ROOT)), '-o', host(out / 'profiles')]

    def run_case(name, source, expected_marker=None):
        (out / 'network_profiles-production.c').write_text(source)
        (out / (name + '-source.c')).write_text(source)
        status, log = execute(command)
        (out / (name + '-build.log')).write_bytes(log)
        assert status == 0, log.decode(errors='replace')
        fs = out / ('fs-' + name)
        fs.mkdir()
        status, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                               'UBSAN_OPTIONS=halt_on_error=1', host(out / 'profiles'), host(fs)])
        (out / (name + '.log')).write_bytes(log)
        assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log, log
        if expected_marker is None:
            assert status == 0, log.decode(errors='replace')
            report['positive'] = log.decode().strip()
            print(log.decode(), end='')
        else:
            assert status == 80 and ('SEMANTIC_FAILURE:' + expected_marker + ':').encode() in log, (name, status, log)
            report['negative_controls'][name] = {'detected': True,
                'expected_marker': expected_marker, 'exit_status': status}

    run_case('positive', loader)
    mutations = [
        ('old-first-row-only', '            ++staged.count;',
         '            ++staged.count; break;', 'complete_profile_count'),
        ('partial-publish-on-failure', '    if (result == ESP_OK) *out = staged;',
         '    *out = staged;', 'failed_io_never_publishes_partial'),
        ('ignore-full-file-read-error', '    result = ferror(file) ? ESP_FAIL : ESP_OK;',
         '    result = ESP_OK;', 'expected_error_contract'),
        ('ignore-close-error', '    if (fclose(file) != 0) result = ESP_FAIL;',
         '    (void)fclose(file);', 'expected_error_contract'),
        ('skip-temporary-table-wipe', '    native_wifi_erase(&staged, sizeof(staged));',
         '    /* Deliberate omitted erase. */', 'all_secret_workspaces_wiped'),
        ('skip-line-wipe', '    native_wifi_erase(line, sizeof(line));',
         '    /* Deliberate omitted erase. */', 'all_secret_workspaces_wiped'),
        ('stop-after-fifth-profile', '            ++staged.count;',
         '            ++staged.count; if (staged.count == NETWORK_PROFILES_MAX) break;',
         'whole_file_read_after_five'),
    ]
    for name, old, new, marker in mutations:
        assert loader.count(old) == 1, name
        run_case(name, loader.replace(old, new, 1), marker)
    (out / 'network_profiles-production.c').write_text(loader)
    report['command'] = command
    report['passed'] = True
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS', len(mutations), 'exact semantic negative controls')


if __name__ == '__main__':
    main()
