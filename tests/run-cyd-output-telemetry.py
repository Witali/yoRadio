"""Run complete production CYD output backends plus real metrics under ASan/UBSan.

SDK/driver/clock/critical-section seams replace hardware. No PCM/DMA timing,
physical IRQ behavior or target memory placement qualification is claimed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('idf/esp32-cyd2usb-native/main')
TEST = Path('tests/native/cyd_output_telemetry')


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command):
    completed = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return completed.returncode, completed.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out != ROOT and ROOT not in out.parents or ROOT / '.build' in out.parents, 'Use a fresh .build output'
    out.mkdir(parents=True, exist_ok=False)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    inputs = [Path(__file__).resolve().relative_to(ROOT),
              *[MAIN / name for name in ('native_audio_output.c', 'native_audio_output.h',
                                        'native_output_metrics.c', 'native_output_metrics.h', 'board_config.h')],
              *[TEST / name for name in ('test.c', 'platform.h', 'README.md')]]
    frozen = out / 'sources'
    report = dict(passed=False, scope=__doc__, source_sha256={}, cases={}, negative_controls={},
                  physical_hardware=False, target_irq_or_dma=False)
    for relative in inputs:
        copy = frozen / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes((ROOT / relative).read_bytes())
        report['source_sha256'][relative.as_posix()] = sha(copy)
    stubs = out / 'stubs'
    for name in ('esp_err.h', 'esp_attr.h', 'esp_timer.h', 'sdkconfig.h', 'esp_check.h', 'esp_log.h',
                 'native_audio_settings.h', 'native_audio_normalizer.h', 'idf6_i2s_compat.h',
                 'driver/gpio.h', 'driver/i2s_pdm.h', 'driver/dac_continuous.h',
                 'freertos/FreeRTOS.h', 'freertos/task.h'):
        path = stubs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('#pragma once\n#include "platform.h"\n')
    production = frozen / MAIN / 'native_audio_output.c'
    metrics = frozen / MAIN / 'native_output_metrics.c'
    source = production.read_text()

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    status, log = execute(['gcc', '--version'])
    (out / 'compiler.log').write_bytes(log)
    save()
    assert status == 0, log

    def build(directory, unit, backend, diagnostic):
        directory.mkdir(parents=True, exist_ok=True)
        binary = directory / 'test'
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-pthread',
                   '-Wno-unused-function', '-Wno-unused-variable',
                   '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-fsanitize=address,undefined',
                   '-DCONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_' + backend + '=1',
                   *(['-DCONFIG_YORADIO_NATIVE_DIAGNOSTICS=1'] if diagnostic else []),
                   '-I' + host(stubs), '-I' + host(frozen / TEST), '-I' + host(frozen / MAIN),
                   host(unit), host(metrics), host(frozen / TEST / 'test.c'), '-o', host(binary)]
        (directory / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
        code, output = execute(command)
        (directory / 'build.log').write_bytes(output)
        save()
        assert code == 0, output.decode(errors='replace')
        return binary

    def run(binary, case):
        return execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                        'UBSAN_OPTIONS=halt_on_error=1', host(binary), case])

    for backend in ('PDM', 'DAC', 'LEGACY_DAC'):
        for variant, diagnostic in [('quiet', False), ('diagnostic', True)]:
            name = backend.lower() + '/' + variant
            directory = out / name
            binary = build(directory, production, backend, diagnostic)
            cases = ['writes', 'full-tail-idle', 'paused']
            if backend == 'PDM':
                cases += ['registration-failure', 'callback-concurrent']
            for case in cases:
                code, output = run(binary, case)
                (directory / (case + '.log')).write_bytes(output)
                report['cases'][name + '/' + case] = dict(passed=code == 0, status=code,
                                                          output=output.decode(errors='replace'))
                save()
                assert code == 0 and output == ('PASS:' + case + '\n').encode(), (name, case, code, output)
            print('PASS:' + name + ':' + str(len(cases)) + ' cases', flush=True)

    pdm_end = 'native_output_metrics_end_write(bytes, written, result, started);'
    dac_end = 'native_output_metrics_end_write(bytes, *written, result, started);'
    legacy_end = 'native_output_metrics_end_write(frames * sizeof(uint32_t), written, result, started);'
    registration = '''result = i2s_channel_register_event_callback(s_pdm, &callbacks, NULL);
    if (result != ESP_OK) {
        pdm_release(false);
        return result;
    }
    native_output_metrics_observe_queue();'''
    controls = [
        ('pdm-missing-write-hook', pdm_end, '(void)started;', 'PDM', 'writes', 'prime_writes_accounted'),
        ('dac-missing-write-hook', dac_end, '(void)started;', 'DAC', 'writes', 'prime_writes_accounted'),
        ('legacy-missing-write-hook', legacy_end, '(void)started;', 'LEGACY_DAC', 'writes', 'prime_writes_accounted'),
        ('legacy-wrong-request-units', legacy_end,
         'native_output_metrics_end_write(frames, written, result, started);', 'LEGACY_DAC', 'writes', 'prime_writes_accounted'),
        ('pdm-ignored-registration-failure', registration,
         registration.replace('if (result != ESP_OK)', 'if (false)'), 'PDM', 'registration-failure', 'pdm_preload_after_registration'),
        ('pdm-failed-registration-observed', registration,
         'native_output_metrics_observe_queue();\n    ' + registration.replace('    native_output_metrics_observe_queue();', ''),
         'PDM', 'registration-failure', 'failed_registration_unavailable'),
        ('pdm-missing-isr-hook', '    native_output_metrics_queue_drop();', '    /* missing callback hook */',
         'PDM', 'callback-concurrent', 'registered_isr_hook_count'),
        ('dac-missing-idle-hook', '    dac_write_block(s_dac_data, 256, &written, 100);',
         '    dac_continuous_write(s_dac, s_dac_data, 256, &written, 100);', 'DAC', 'full-tail-idle', 'dac_idle_telemetry'),
    ]
    for name, old, new, backend, case, marker in controls:
        assert source.count(old) == 1, (name, source.count(old))
        directory = out / 'mutants' / name
        directory.mkdir(parents=True)
        unit = directory / 'native_audio_output.c'
        unit.write_text(source.replace(old, new, 1))
        binary = build(directory, unit, backend, True)
        code, output = run(binary, case)
        (directory / 'test.log').write_bytes(output)
        assert code == 80 and output.startswith(('SEMANTIC_FAILURE:' + marker + ':').encode()), (name, code, output)
        assert b'AddressSanitizer' not in output and b'runtime error:' not in output
        report['negative_controls'][name] = dict(detected=True, status=code, marker=marker,
                                                case=case, generated_sha256=sha(unit))
        save()
        print('DETECTED:' + name, flush=True)
    report['live_inputs_match_snapshot'] = {name: sha(ROOT / name) == expected
                                           for name, expected in report['source_sha256'].items()}
    assert all(report['live_inputs_match_snapshot'].values())
    report.update(passed=True,
                  complete_output_tu_matches_frozen_bytes=sha(production) == sha(ROOT / MAIN / 'native_audio_output.c'),
                  complete_metrics_tu_matches_frozen_bytes=sha(metrics) == sha(ROOT / MAIN / 'native_output_metrics.c'),
                  generated_stubs_sha256={p.relative_to(stubs).as_posix(): sha(p) for p in stubs.rglob('*') if p.is_file()})
    save()


if __name__ == '__main__':
    main()
