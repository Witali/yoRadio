"""Reproduce actual historical audio generation/power races with real owners.

All original sources come from one Git commit and are frozen before composing
the harness. Audio function bodies, actual queue/generation control, native
state, adaptive queue, stream reader and the bool network power function run.
Platform includes and SDK/codec/RTOS boundaries are explicit host seams; there
is no board, SDK driver, real PCM, target ABI, timing or SMP qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'af8700e2e1d09fa3560544658d1f86b7223f26bb'
MAIN = Path('idf/esp32c3-oled-native/main')
SHARED = Path('idf/components/native_stream')
TEST = Path('tests/native/network_power_baseline')


def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=ROOT)


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def function(source, name):
    match = re.search(r'^(?:static[ \t]+)?[A-Za-z_]\w*[ \t*]+' + re.escape(name) + r'\s*\(', source, re.M)
    assert match, name
    position = source.index('{', match.start()) + 1; depth = 1
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


def stripped(source, keep=()):
    return re.sub(r'^#include[^\n]*\n', lambda match: match.group(0)
                  if any('"' + name + '"' in match.group(0) for name in keep) else '', source, flags=re.M)


def execute(command, timeout=60):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return result.returncode, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', '--output', dest='out', type=Path, required=True)
    parser.add_argument('--revision', default=BASELINE)
    args = parser.parse_args(); revision = git('rev-parse', '--verify', args.revision + '^{commit}').decode().strip()
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    report = dict(passed=False, scope=__doc__, historical_revision=revision,
                  evidence_kind='actual_historical_audio_interleaving', source_sha256={},
                  source_origin={}, generated_sha256={}, function_sha256={},
                  negative_controls={}, current_production_tested=False,
                  physical_hardware=False, actual_audio_interleaving=True)
    historical = [*[MAIN / name for name in ['audio_service.c', 'native_state.c',
                   'stream_http_reader.c', 'network_service.c']],
                  SHARED / 'adaptive_input.c', SHARED / 'icy_title.c',
                  Path('tests/native/c3_maintenance_platform.h'), Path('tests/native/c3_maintenance_seams.h'),
                  Path('idf/components/custom_flac/custom_flac_adapter.h'),
                  Path('idf/components/custom_legacy_codecs/custom_legacy_adapter.h')]
    tree = git('ls-tree', '-r', '--name-only', revision, '--', str(MAIN).replace('\\', '/'),
               str(SHARED / 'include').replace('\\', '/')).decode().splitlines()
    historical += [Path(name) for name in tree if name.endswith('.h') and
                   (Path(name).parent == MAIN or str(SHARED / 'include').replace('\\', '/') in name)]
    working = [Path(__file__).resolve().relative_to(ROOT), TEST / 'test.c', TEST / 'README.md']
    for relative in sorted(set(historical + working)):
        key = relative.as_posix()
        data = git('show', revision + ':' + key) if relative in historical else (ROOT / relative).read_bytes()
        destination = out / 'sources' / relative; destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data); report['source_sha256'][key] = hashlib.sha256(data).hexdigest()
        report['source_origin'][key] = 'git:' + revision if relative in historical else 'working_harness_snapshot'
    frozen = out / 'sources'; main_dir = frozen / MAIN; test = frozen / 'tests/native'
    audio = (main_dir / 'audio_service.c').read_text()
    network = (main_dir / 'network_service.c').read_text()
    generated = {
        'audio.inc': stripped(audio, ('stream_encoded_router.h', 'stream_start.h')),
        'state.inc': stripped((main_dir / 'native_state.c').read_text()),
        'reader.inc': stripped((main_dir / 'stream_http_reader.c').read_text()),
        'adaptive.inc': stripped((frozen / SHARED / 'adaptive_input.c').read_text()),
        'network-power.inc': function(network, 'network_service_set_streaming'),
    }
    for name in ['stream_task', 'advance_generation', 'play_locked', 'audio_service_play', 'audio_service_stop']:
        body = function(audio, name)
        assert body in generated['audio.inc'], name
        report['function_sha256']['audio_service.c:' + name] = hashlib.sha256(body.encode()).hexdigest()
    report['function_sha256']['network_service.c:network_service_set_streaming'] = hashlib.sha256(generated['network-power.inc'].encode()).hexdigest()
    seams = (test / 'c3_maintenance_seams.h').read_text()
    transformations = [
        ('static void network_service_set_streaming(bool v) {(void)v;}',
         '/* Actual historical network power function is linked by focused test. */'),
        ('barrier_hit("read");vTaskDelay(1);if(tls_error)',
         'barrier_hit("read");vTaskDelay(1);'
         'if(strstr(c->url,"old.invalid")&&c->reads){atomic_store(&baseline_eof_seen,true);return 0;}'
         'if(strstr(c->url,"new.invalid"))return -ESP_ERR_HTTP_EAGAIN;if(tls_error)'),
        ('static bool esp_http_client_is_complete_data_received(void *c) {(void)c;return false;}',
         'static bool esp_http_client_is_complete_data_received(void *c) {'
         'return strstr(((esp_http_client_handle_t)c)->url,"old.invalid")&&atomic_load(&baseline_eof_seen);}'),
    ]
    for old, new in transformations:
        assert seams.count(old) == 1, old; seams = seams.replace(old, new, 1)
    generated['focused-seams.inc'] = seams
    report['sdk_seam_changes'] = [old for old, _ in transformations]
    report['call_interposition'] = 'Only audio call tokens map to power_call_boundary; exact argument/result forwarded to unchanged actual network function'
    for name, text in generated.items():
        data = text.encode(); (out / name).write_bytes(data)
        report['generated_sha256'][name] = hashlib.sha256(data).hexdigest()
    (out / 'freertos').mkdir()
    for name in ['FreeRTOS.h', 'semphr.h', 'task.h', 'ringbuf.h']:
        (out / 'freertos' / name).write_text('#include "' + host(test / 'c3_maintenance_platform.h') + '"\n')
    for name in ['esp_err.h', 'sdkconfig.h', 'esp_audio_simple_dec.h', 'esp_http_client.h']:
        (out / name).write_text('#pragma once\n')
    command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-Wno-unused-variable', '-Wno-unused-function', '-Wno-unused-parameter',
               '-Wno-error=format-truncation',
               '-pthread', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-fsanitize=address,undefined', '-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1',
               '-DCONFIG_YORADIO_FRAME_ROUTER=1', '-DCONFIG_YORADIO_STREAM_CONFIRM=1',
               '-DCONFIG_YORADIO_INPUT_TAIL_COALESCE=1', '-DCONFIG_YORADIO_SHARED_DECODER_ARENA=1',
               '-DCONFIG_YORADIO_INPUT_MIN_BLOCKS=5', '-DCONFIG_YORADIO_OUTPUT_TASK_FIRST=1',
               '-DCONFIG_YORADIO_STREAM_READ_TIMEOUT_MS=100', '-DCONFIG_YORADIO_STREAM_READ_BYTES=2048',
               '-DCONFIG_YORADIO_INPUT_PREFILL_MS=0', '-DCONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=0',
               '-DCONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS=0', '-DCONFIG_YORADIO_MP3_DECODER_HELIX=1',
               '-DCONFIG_YORADIO_AAC_DECODER_ESPRESSIF=1', '-DCONFIG_YORADIO_FLAC_DECODER_CUSTOM=1',
               '-I' + host(out), '-I' + host(test), '-I' + host(frozen / TEST), '-I' + host(main_dir),
               '-I' + host(frozen / SHARED / 'include'),
               '-I' + host(frozen / 'idf/components/custom_flac'),
               '-I' + host(frozen / 'idf/components/custom_legacy_codecs'),
               host(frozen / TEST / 'test.c'), host(frozen / SHARED / 'icy_title.c'), '-o', host(out / 'baseline')]
    report['command'] = command
    code, log = execute(command); (out / 'build.log').write_bytes(log)
    assert code == 0, log.decode(errors='replace')
    for case, marker in [
        ('sequential', None),
        ('stale-finish-after-play', 'old_stream_finish_cannot_override_new_play'),
        ('late-true-after-stop', 'old_stream_true_cannot_override_accepted_stop'),
    ]:
        code, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=' + ('1' if marker is None else '0') + ':halt_on_error=1',
                             'UBSAN_OPTIONS=halt_on_error=1', host(out / 'baseline'), case], 20)
        (out / (case + '.log')).write_bytes(log)
        assert not any(error in log for error in [b'AddressSanitizer', b'runtime error:', b'LeakSanitizer']), log
        if marker is None:
            assert code == 0 and log == b'PASS:sequential_old_finish_then_new_play\n', (code, log)
            report['positive_control'] = dict(passed=True, status=code)
        else:
            assert code == 42 and ('SAFETY_FAILURE:' + marker + '\n').encode() in log, (case, code, log)
            assert re.search(rb'TRACE:old_guard_generation=1 current_generation=2 driver_mode=[01] power_calls=\d+\n', log), log
            report['negative_controls'][case] = dict(detected=True, status=code,
                expected_marker=marker, output=log.decode().strip())
        print(case + ': ' + ('PASS' if marker is None else 'DETECTED'), flush=True)
    report['passed'] = True
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
