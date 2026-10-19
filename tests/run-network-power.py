"""Execute shared power policy and actual C3 permanent task integration.

The complete shared production translation unit runs with a pthread portMUX.
Actual frozen C3 apply/RSSI/intent/sleep bodies run in integration cases. Driver,
RSSI/state and clock/delay boundaries are field-model host seams. No target ABI,
Wi-Fi power savings, hardware timing, real RTOS or SMP-safety claim is made.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = Path('idf/components/native_network_power')
MAIN = Path('idf/esp32c3-oled-native/main')
TEST = Path('tests/native/network_power')
CASES = ['idle-known', 'generation-equality', 'generation-wrap', 'same-generation-retry',
         'failure-budget', 'blocked-success', 'blocked-error', 'stale-error-budget',
         'invalidate-success', 'invalidate-error', 'clock-limit', 'invalid-poll',
         'concurrent', 'c3-periods', 'c3-sleep-error', 'c3-blocked']


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return result.returncode, result.stdout


def function(source, name):
    match = re.search(r'^(?:static[ \t]+)?[A-Za-z_]\w*[ \t*]+' + re.escape(name) + r'\s*\(', source, re.M)
    assert match, name; position = source.index('{', match.start()) + 1; depth = 1
    while depth:
        if source.startswith('//', position): position = source.index('\n', position) + 1
        elif source.startswith('/*', position): position = source.index('*/', position + 2) + 2
        elif source[position] in ('"', "'"):
            quote = source[position]; position += 1
            while source[position] != quote: position += 2 if source[position] == '\\' else 1
            position += 1
        else:
            depth += (source[position] == '{') - (source[position] == '}'); position += 1
    return source[match.start():position] + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', '--output', dest='out', type=Path, required=True)
    parser.add_argument('--case', action='append', choices=CASES)
    parser.add_argument('--skip-mutants', action='store_true')
    args = parser.parse_args(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__).resolve().relative_to(ROOT),
             *[TEST / name for name in ['platform.h', 'test.c', 'README.md']],
             COMPONENT / 'native_network_power.c', COMPONENT / 'include/native_network_power.h',
             MAIN / 'network_service.c', MAIN / 'network_service.h']
    report = dict(passed=False, scope=__doc__, complete_matrix=not args.case,
                  source_sha256={}, cases={}, negative_controls={})
    for relative in files:
        data = (ROOT / relative).read_bytes(); destination = out / 'sources' / relative
        destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(data)
        report['source_sha256'][relative.as_posix()] = hashlib.sha256(data).hexdigest()
    frozen = out / 'sources'; (out / 'freertos').mkdir()
    for relative in ['esp_err.h', 'freertos/FreeRTOS.h']:
        (out / relative).write_text('#pragma once\n#include "platform.h"\n')
    source = (frozen / MAIN / 'network_service.c').read_text()
    names = ['apply_power', 'rssi_task', 'network_service_audio_accept',
             'network_service_audio_receive', 'network_service_audio_finish', 'network_service_prepare_sleep']
    bodies = [function(source, name) for name in names]
    c3 = '\n'.join(bodies).encode(); (out / 'c3-power.inc').write_bytes(c3)
    report['actual_c3_functions'] = {name: hashlib.sha256(body.encode()).hexdigest() for name, body in zip(names, bodies)}
    report['generated_sha256'] = {'c3-power.inc': hashlib.sha256(c3).hexdigest()}

    def save(): (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    def build(binary, unit):
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-pthread',
                   '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-fsanitize=address,undefined',
                   '-I' + host(out), '-I' + host(frozen / TEST), '-I' + host(frozen / COMPONENT / 'include'),
                   host(unit), host(frozen / TEST / 'test.c'), '-o', host(binary)]
        report.setdefault('commands', []).append(command)
        code, log = execute(command); (out / (binary.name + '-build.log')).write_bytes(log)
        if code: save(); raise RuntimeError(log.decode(errors='replace'))

    binary = out / 'power'; production = frozen / COMPONENT / 'native_network_power.c'; build(binary, production)
    for case in args.case or CASES:
        code, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                             'UBSAN_OPTIONS=halt_on_error=1', host(binary), case])
        (out / (case + '.log')).write_bytes(log)
        report['cases'][case] = dict(passed=code == 0, status=code, output=log.decode(errors='replace').strip()); save()
        assert code == 0 and log == ('PASS:' + case + '\n').encode(), (case, code, log)
        print('PASS:' + case, flush=True)
    if not args.skip_mutants:
        text = production.read_text()
        controls = [
            ('stale_generation_updates_intent', 's_power.generation == generation && s_power.desired_active != active',
             '((void)generation, s_power.desired_active != active)', 'generation-equality', 'stale_finish_ignored'),
            ('stale_success_not_recorded', 'if (result == ESP_OK) {',
             'if (result == ESP_OK && s_power.desired_revision == intent.desired_revision) {',
             'blocked-success', 'stale_success_recorded_for_repair'),
            ('stale_error_spends_new_budget', 'if (s_power.desired_revision == intent.desired_revision) {',
             'if (true) {', 'stale-error-budget', 'stale_error_preserves_new_budget'),
            ('invalidated_result_recorded', 'if (driver_revision != s_driver_revision) {',
             'if (false && driver_revision != s_driver_revision) {',
             'invalidate-success', 'invalidated_driver_result_ignored'),
        ]
        for name, old, new, case, marker in controls:
            assert text.count(old) == 1, (name, text.count(old))
            directory = out / 'mutants' / name; directory.mkdir(parents=True)
            unit = directory / 'native_network_power.c'; unit.write_bytes(text.replace(old, new, 1).encode())
            binary = directory / name; build(binary, unit)
            code, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=0:halt_on_error=1',
                                 'UBSAN_OPTIONS=halt_on_error=1', host(binary), case])
            (directory / 'test.log').write_bytes(log)
            assert code == 80 and log.startswith(('SEMANTIC_FAILURE:' + marker + ':').encode()), (name, code, log)
            assert not any(error in log for error in [b'AddressSanitizer', b'runtime error:']), log
            report['negative_controls'][name] = dict(detected=True, status=code, expected_marker=marker,
                case=case, sha256=hashlib.sha256(unit.read_bytes()).hexdigest()); save()
            print('DETECTED:' + name, flush=True)
    report['mutants_enabled'] = not args.skip_mutants; report['passed'] = True; save()


if __name__ == '__main__':
    main()
