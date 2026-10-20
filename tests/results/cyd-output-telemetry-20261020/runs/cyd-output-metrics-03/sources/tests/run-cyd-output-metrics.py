"""Qualify the complete CYD output counter service with SDK/ISR clock seams.

Both quiet and diagnostic units execute with pthread critical sections and
ASan/UBSan. This is not backend integration, target IRQ/IRAM or DMA evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('idf/esp32-cyd2usb-native/main')
TEST = Path('tests/native/cyd_output_metrics')
CASES = ['initial', 'writes', 'clocks', 'queue', 'bytes-limit', 'time-limit', 'concurrent']


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
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__).resolve().relative_to(ROOT),
             *[TEST / name for name in ('platform.h', 'test.c', 'README.md')],
             *[MAIN / name for name in ('native_output_metrics.c', 'native_output_metrics.h')]]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(passed=False, scope=__doc__, source_sha256={}, cases={}, negative_controls={},
                  physical_hardware=False, target_irq_or_dma=False)
    for relative in files:
        target = out / 'sources' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
        report['source_sha256'][relative.as_posix()] = sha(target)
    frozen = out / 'sources'
    stubs = out / 'stubs'
    (stubs / 'freertos').mkdir(parents=True)
    for name in ('esp_err.h', 'esp_attr.h', 'esp_timer.h', 'sdkconfig.h', 'freertos/FreeRTOS.h'):
        (stubs / name).write_text('#pragma once\n#include "platform.h"\n')
    code, log = execute(['gcc', '--version'])
    (out / 'compiler.log').write_bytes(log)
    assert code == 0, log
    production = frozen / MAIN / 'native_output_metrics.c'
    body = production.read_text()

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    def build(directory, unit, diagnostic):
        directory.mkdir(parents=True, exist_ok=True)
        binary = directory / 'test'
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-pthread',
                   '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-fsanitize=address,undefined',
                   *(['-DCONFIG_YORADIO_NATIVE_DIAGNOSTICS=1'] if diagnostic else []),
                   '-I' + host(stubs), '-I' + host(frozen / TEST), '-I' + host(frozen / MAIN),
                   host(unit), host(frozen / TEST / 'test.c'), '-o', host(binary)]
        (directory / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
        status, output = execute(command)
        (directory / 'build.log').write_bytes(output)
        save()
        assert status == 0, output.decode(errors='replace')
        return binary

    def run(binary, case, leaks=True):
        return execute(['env', 'ASAN_OPTIONS=detect_leaks=' + ('1' if leaks else '0') + ':halt_on_error=1',
                        'UBSAN_OPTIONS=halt_on_error=1', host(binary), case])

    seed = 'static DRAM_ATTR native_output_metrics_t s_output_metrics;'
    seeded = ('static DRAM_ATTR native_output_metrics_t s_output_metrics = {'
              '.writes=UINT32_MAX,.errors=UINT32_MAX,.timeouts=UINT32_MAX,'
              '.short_writes=UINT32_MAX,.timing_samples=UINT32_MAX,'
              '.invalid_time_samples=UINT32_MAX,.completion_queue_drops=UINT32_MAX};')
    assert body.count(seed) == 1
    for variant, diagnostic in [('quiet', False), ('diagnostic', True)]:
        directory = out / variant
        binary = build(directory, production, diagnostic)
        for case in CASES:
            status, output = run(binary, case)
            (directory / (case + '.log')).write_bytes(output)
            report['cases'][variant + '/' + case] = dict(passed=status == 0, status=status,
                                                        output=output.decode(errors='replace'))
            save()
            assert status == 0 and output == ('PASS:' + case + '\n').encode(), (variant, case, status, output)
        boundary = directory / 'count-boundary'
        boundary.mkdir()
        unit = boundary / 'native_output_metrics.c'
        unit.write_text(body.replace(seed, seeded, 1))
        binary = build(boundary, unit, diagnostic)
        status, output = run(binary, 'count-limit')
        (boundary / 'test.log').write_bytes(output)
        assert status == 0 and output == b'PASS:count-limit\n', (variant, status, output)
        report['cases'][variant + '/count-limit'] = dict(passed=True, status=0,
            explicit_static_initial_counter_seed=True, source_sha256=sha(unit))
        save()
        print('PASS:' + variant + ':8 cases', flush=True)
    controls = [
        ('ignore-short-error', 'if (result != ESP_OK || written != requested)', 'if (result != ESP_OK)',
         False, 'writes', 'error_and_incomplete_classification'),
        ('accept-negative-start', 'started_us >= 0 && ended_us >= started_us', 'ended_us >= started_us',
         True, 'clocks', 'invalid_time_is_not_unsigned_elapsed'),
        ('lose-isr-counter', 'increment(&s_output_metrics.completion_queue_drops);',
         '(void)s_output_metrics.completion_queue_drops;', False, 'queue', 'actual_isr_calls_increment_queue_drops'),
        ('wrap-byte-totals', 'if (delta > UINT64_MAX - value)', 'if (false)',
         False, 'bytes-limit', 'byte_totals_saturate'),
        ('quiet-clock-read', '#else\n    return 0;\n#endif', '#else\n    return esp_timer_get_time();\n#endif',
         False, 'writes', 'quiet_has_no_clock_reads'),
        ('wrap-valid-timing-counter', 'increment(&s_output_metrics.timing_samples);',
         '++s_output_metrics.timing_samples;', True, 'count-limit', 'timing_event_counts_saturate'),
        ('wrap-invalid-timing-counter', 'else increment(&s_output_metrics.invalid_time_samples);',
         'else ++s_output_metrics.invalid_time_samples;', True, 'count-limit', 'timing_event_counts_saturate'),
    ]
    for name, old, new, diagnostic, case, marker in controls:
        assert body.count(old) == 1, (name, body.count(old))
        directory = out / 'mutants' / name
        directory.mkdir(parents=True)
        unit = directory / 'native_output_metrics.c'
        mutated = body.replace(old, new, 1)
        if case == 'count-limit':
            mutated = mutated.replace(seed, seeded, 1)
        unit.write_text(mutated)
        binary = build(directory, unit, diagnostic)
        status, output = run(binary, case, False)
        (directory / 'test.log').write_bytes(output)
        assert status == 80 and output.startswith(('SEMANTIC_FAILURE:' + marker + ':').encode()), (name, status, output)
        assert b'AddressSanitizer' not in output and b'runtime error:' not in output
        report['negative_controls'][name] = dict(detected=True, status=status, marker=marker,
                                                case=case, generated_sha256=sha(unit),
                                                explicit_static_initial_counter_seed=case == 'count-limit')
        save()
        print('DETECTED:' + name, flush=True)
    report['live_inputs_match_snapshot'] = {name: sha(ROOT / name) == expected
                                           for name, expected in report['source_sha256'].items()}
    assert all(report['live_inputs_match_snapshot'].values())
    report.update(passed=True, complete_normal_tu_matches_frozen_bytes=sha(production) == sha(ROOT / MAIN / 'native_output_metrics.c'),
                  static_boundary_seed=seeded,
                  generated_stubs_sha256={p.relative_to(stubs).as_posix(): sha(p) for p in stubs.rglob('*') if p.is_file()})
    save()


if __name__ == '__main__':
    main()
