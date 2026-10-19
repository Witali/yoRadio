"""Qualify the complete CYD desired network settings source on the host.

The unchanged production C and header are frozen before compilation. pthread
mutexes model FreeRTOS writer admission and the snapshot critical section;
admission failure is injected rather than claimed to reproduce RTOS timing.
The NVS seam models staged writes, commit, read/open errors and durable reload.
It does not qualify target ABI, flash power-loss recovery, NVS internals or RF.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CASES = ["defaults", "validation", "roundtrip", "invalid-record", "read-errors",
         "wrong-type", "save-errors", "mutex-oom", "revision-limit",
         "concurrent-init", "concurrent-save", "candidate-owned"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return result.returncode, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    main_dir = Path('idf/esp32-cyd2usb-native/main')
    fixture = Path('tests/native/cyd_network_settings')
    paths = [Path(__file__).resolve().relative_to(ROOT), main_dir / 'network_settings.c',
             main_dir / 'network_settings.h', fixture / 'platform.h', fixture / 'test.c']
    report = {'passed': False, 'scope': __doc__, 'physical_hardware': False,
              'sanitizers': ['ASan', 'UBSan'], 'source_sha256': {}, 'generated_sha256': {},
              'cases': {}, 'negative_controls': {},
              'validation_contract': 'One ASCII DHCP hostname label, 1-23 bytes, alnum/internal hyphen; AP 0-30 minutes.',
              'donor_difference': 'C3 permits empty/dots/underscores/non-ASCII; this new CYD setting deliberately requires one ASCII label.'}
    frozen = out / 'sources'
    for relative in paths:
        data = (ROOT / relative).read_bytes()
        target = frozen / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        report['source_sha256'][relative.as_posix()] = digest(data)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    generated = {}
    for name in ['esp_err.h', 'nvs.h', 'freertos/FreeRTOS.h', 'freertos/semphr.h']:
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('#pragma once\n#include "platform.h"\n', encoding='utf-8')
        generated[name] = digest(target.read_bytes())
    report['generated_sha256'] = generated
    source_bytes = (frozen / main_dir / 'network_settings.c').read_bytes()
    source = source_bytes.decode('utf-8').replace('\r\n', '\n')
    under_test = out / 'network-settings-under-test.c'
    command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-pthread', '-I' + host(out), '-I' + host(frozen / main_dir),
               '-I' + host(frozen / fixture), host(frozen / fixture / 'test.c'),
               '-o', host(out / 'settings')]
    report['command'] = command
    compiler_status, compiler_version = execute(['gcc', '--version'])
    assert compiler_status == 0, compiler_version
    (out / 'compiler.log').write_bytes(compiler_version)
    report['compiler'] = compiler_version.decode(errors='replace').splitlines()[0]

    def build(name, contents):
        data = contents if isinstance(contents, bytes) else contents.encode('utf-8')
        under_test.write_bytes(data)
        (out / (name + '-source.c')).write_bytes(data)
        status, log = execute(command)
        (out / (name + '-build.log')).write_bytes(log)
        assert status == 0, log.decode(errors='replace')

    def run(name, case, marker=None):
        status, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                               'UBSAN_OPTIONS=halt_on_error=1', host(out / 'settings'), case])
        (out / (name + '.log')).write_bytes(log)
        assert b'AddressSanitizer' not in log and b'runtime error:' not in log, log
        if marker is None:
            assert status == 0 and ('PASS ' + case).encode() in log, (name, status, log)
            report['cases'][case] = {'passed': True, 'exit_status': status}
        else:
            assert status == 80 and ('SEMANTIC_FAILURE:' + marker + ':').encode() in log, (name, status, log)
            report['negative_controls'][name] = {'detected': True, 'case': case,
                                                'exit_status': status, 'expected_marker': marker}

    try:
        build('positive', source_bytes)
        report['compiled_production_matches_frozen_bytes'] = under_test.read_bytes() == source_bytes
        assert report['compiled_production_matches_frozen_bytes']
        for case in CASES:
            run(case, case)
            print('PASS', case, flush=True)
        mutations = [
            ('publish-failed-commit', '    nvs_close(handle);\n    if (result == ESP_OK) {',
             '    nvs_close(handle);\n    if (true) {', 'save-errors', 'failed_commit_never_publishes'),
            ('publish-before-commit', '    if (result == ESP_OK) result = nvs_commit(handle);',
             '    if (result == ESP_OK) {\n        portENTER_CRITICAL(&s_snapshot_lock);\n'
             '        s_settings = candidate; s_revision = revision + 1U;\n'
             '        portEXIT_CRITICAL(&s_snapshot_lock);\n        result = nvs_commit(handle);\n    }',
             'concurrent-save', 'commit_must_precede_publication'),
            ('ignore-canonical-tail', '    if (memcmp(record, canonical, NETWORK_RECORD_SIZE)) return false;',
             '    (void)canonical;', 'invalid-record', 'invalid_record_rejected_without_publication'),
            ('drop-revision-increment', '        s_revision = revision + 1U;',
             '        s_revision = revision;', 'roundtrip', 'successful_save_advances_revision'),
            ('drop-writer-admission', '    return xSemaphoreTake(lock, pdMS_TO_TICKS(SETTINGS_WAIT_MS)) == pdTRUE\n               ? lock : NULL;',
             '    (void)xSemaphoreTake; return lock;', 'defaults', 'writer_admission_required'),
            ('accept-dotted-hostname', "(value >= '0' && value <= '9') || value == '-'",
             "(value >= '0' && value <= '9') || value == '-' || value == '.'",
             'validation', 'invalid_hostname_rejected'),
            ('accept-timeout-31', 'settings->ap_timeout_minutes > NETWORK_SETTINGS_AP_TIMEOUT_MAX_MINUTES',
             'settings->ap_timeout_minutes > (NETWORK_SETTINGS_AP_TIMEOUT_MAX_MINUTES + 1U)',
             'validation', 'bounded_ap_timeout'),
        ]
        for name, old, replacement, case, marker in mutations:
            assert source.count(old) == 1, name
            build(name, source.replace(old, replacement, 1))
            run(name, case, marker)
            print('PASS semantic control', name, flush=True)
        report['sources_unchanged_after'] = {
            relative.as_posix(): digest((ROOT / relative).read_bytes()) == report['source_sha256'][relative.as_posix()]
            for relative in paths}
        assert all(report['sources_unchanged_after'].values()), 'Inputs changed during qualification'
        report['passed'] = True
    finally:
        under_test.write_bytes(source_bytes)
        report['generated_sha256']['network-settings-under-test.c'] = digest(under_test.read_bytes())
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS', len(CASES), 'cases and', len(report['negative_controls']), 'exact semantic controls', flush=True)


if __name__ == '__main__':
    main()
