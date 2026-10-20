"""Fault-inject actual CYD startup/codec/queue/reclaim publication with host tasks.

Pthreads execute the production notification gate; the complete reclaim module
and canonical queue execute unchanged. Driver, SDK calloc and RTOS allocation
APIs are seams. This does not qualify target scheduling, TLS library or DMA.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('idf/esp32-cyd2usb-native/main')
SHARED = Path('idf/components/native_stream')


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return result.returncode, result.stdout


def function(source, name):
    # A call inside ESP_RETURN_ON_ERROR(...) is not a function definition.
    match = re.search(r'^(?:static )?[^\n;{}()]*\b' + name + r'\(', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out != ROOT and ROOT not in out.parents or ROOT / '.build' in out.parents
    out.mkdir(parents=True, exist_ok=False)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    sources = [Path(__file__).resolve().relative_to(ROOT),
               Path('tests/native/cyd_startup_test.c'), Path('tests/native/audio_power_seam.h'),
               *[MAIN / name for name in ('audio_service.c', 'audio_service.h', 'native_state.c',
                   'native_state.h', 'native_health.h', 'native_output_metrics.h',
                   'decoder_registration.c', 'decoder_registration.h',
                   'native_input_reclaim.c', 'native_input_reclaim.h', 'CMakeLists.txt',
                   'Kconfig.projbuild', 'compat/input_reclaim/enable.cmake')],
               Path('idf/esp32-cyd2usb-native/CMakeLists.txt'),
               SHARED / 'adaptive_input.c',
               *[path.relative_to(ROOT) for path in sorted((ROOT / SHARED / 'include').glob('*.h'))]]
    frozen = out / 'sources'
    report = dict(passed=False, physical_hardware=False, scope=__doc__, source_sha256={},
                  variants={}, negative_controls={})
    for relative in sources:
        target = frozen / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
        report['source_sha256'][relative.as_posix()] = sha(target)
    stubs = out / 'stubs'
    (stubs / 'freertos').mkdir(parents=True)
    (stubs / 'freertos/FreeRTOS.h').write_text('''#pragma once
#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <pthread.h>
typedef struct test_sem *SemaphoreHandle_t;
typedef struct test_task *TaskHandle_t;
typedef void (*TaskFunction_t)(void *);
typedef int BaseType_t;
typedef unsigned UBaseType_t, TickType_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
#define pdTRUE 1
#define pdFALSE 0
#define pdPASS 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
static inline int xPortInIsrContext(void) { return 0; }
SemaphoreHandle_t xSemaphoreCreateMutex(void);
SemaphoreHandle_t xSemaphoreCreateBinary(void);
int xSemaphoreTake(SemaphoreHandle_t,unsigned);
int xSemaphoreGive(SemaphoreHandle_t);
void vSemaphoreDelete(SemaphoreHandle_t);
TickType_t xTaskGetTickCount(void);
void vTaskDelay(unsigned);
size_t strlcpy(char *,const char *,size_t);
''')
    for name in ('semphr.h', 'task.h'):
        (stubs / 'freertos' / name).write_text('#include "FreeRTOS.h"\n')
    (stubs / 'esp_err.h').write_text('''#pragma once
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_TIMEOUT 0x107
''')
    (stubs / 'esp_audio_dec.h').write_text('''#pragma once
typedef int esp_audio_err_t;
#define ESP_AUDIO_ERR_OK 0
#define ESP_AUDIO_ERR_MEM_LACK (-2)
''')
    (stubs / 'esp_audio_dec_default.h').write_text('''#include "esp_audio_dec.h"
esp_audio_err_t esp_mp3_dec_register(void);
esp_audio_err_t esp_aac_dec_register(void);
esp_audio_err_t esp_flac_dec_register(void);
esp_audio_err_t esp_vorbis_dec_register(void);
esp_audio_err_t esp_opus_dec_register(void);
void esp_audio_dec_unregister_all(void);
''')
    (stubs / 'esp_audio_simple_dec_default.h').write_text('''#include "esp_audio_dec.h"
esp_audio_err_t esp_audio_simple_dec_register_default(void);
void esp_audio_simple_dec_unregister_default(void);
''')
    (stubs / 'sdkconfig.h').write_text('#pragma once\n')
    source = (frozen / MAIN / 'audio_service.c').read_text()
    common = source[source.index('#define STREAM_CHUNK_SIZE'):
                    source.index('static esp_audio_simple_dec_type_t')]
    start = source.index('typedef struct {\n    TaskFunction_t run;')
    common += source[start:source.index('static void gated_pipeline_task(', start)]
    unit = common + '\n'.join(function(source, name) for name in (
        'gated_pipeline_task', 'discard_pipeline_startup', 'audio_service_start',
        'audio_service_play', 'audio_service_stop', 'audio_service_input_health'))

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    code, output = execute(['gcc', '--version'])
    (out / 'compiler.log').write_bytes(output)
    assert code == 0

    def build(directory, generated, flags):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'production.inc').write_text(generated)
        (directory / 'adaptive-production.inc').write_bytes((frozen / SHARED / 'adaptive_input.c').read_bytes())
        binary = directory / 'test'
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-Wno-unused-variable', '-Wno-unused-function', '-Wno-format-truncation',
                   '-pthread', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                   '-fno-pie', '-no-pie', *['-D' + flag + '=1' for flag in flags],
                   '-I' + host(directory), '-I' + host(stubs), '-I' + host(frozen / MAIN),
                   '-I' + host(frozen / SHARED / 'include'), '-I' + host(frozen / 'tests/native'),
                   host(frozen / 'tests/native/cyd_startup_test.c'), host(frozen / MAIN / 'native_state.c'),
                   host(frozen / MAIN / 'decoder_registration.c')]
        if 'CONFIG_YORADIO_TLS_INPUT_RECLAIM' in flags:
            command += [host(frozen / MAIN / 'native_input_reclaim.c'), '-Wl,--wrap=native_input_reclaim_bind']
        command += ['-o', host(binary)]
        (directory / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
        status, log = execute(command)
        (directory / 'build.log').write_bytes(log)
        save()
        assert status == 0, log.decode(errors='replace')
        return binary

    def run(binary):
        return execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                        'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '30', host(binary)])

    codecs = [('vendor', ['CONFIG_YORADIO_MP3_DECODER_ESPRESSIF', 'CONFIG_YORADIO_AAC_DECODER_ESPRESSIF']),
              ('mp3-vendor', ['CONFIG_YORADIO_MP3_DECODER_ESPRESSIF']),
              ('aac-vendor', ['CONFIG_YORADIO_AAC_DECODER_ESPRESSIF']), ('custom', [])]
    variants = [('ring-' + name, flags) for name, flags in codecs]
    variants += [('adaptive-' + name, flags + ['CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER',
                                             'CONFIG_YORADIO_STREAM_CONFIRM']) for name, flags in codecs]
    variants += [('reclaim-' + name, flags + ['CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER',
                     'CONFIG_YORADIO_STREAM_CONFIRM', 'CONFIG_YORADIO_TLS_INPUT_RECLAIM']) for name, flags in codecs]
    for name, flags in variants:
        directory = out / name
        binary = build(directory, unit, flags)
        status, log = run(binary)
        (directory / 'test.log').write_bytes(log)
        report['variants'][name] = dict(passed=status == 0, status=status, output=log.decode(errors='replace'))
        save()
        assert status == 0 and b'PASS CYD startup:' in log, (name, status, log)
        if name.startswith('reclaim-'):
            assert re.search(rb'reclaim_probes=[1-9]\d* original_tls_calls=[1-9]\d* health_callback_calls=[1-9]\d*', log)
        print('PASS:' + name + ':' + log.decode().strip().splitlines()[-1], flush=True)

    binding = '''#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    // All fallible startup work has committed. A rejected optional binding
    // must not roll back READY or destroy a pool published to another task.
    if (!native_input_reclaim_bind(s_encoded))
        ESP_LOGW(TAG, "TLS input reclamation not attached");
#endif
'''
    ready = '    atomic_store(&s_start_state, AUDIO_START_READY);\n'
    notify = '    for (unsigned i = 0; i < 3; ++i) xTaskNotifyGive(tasks[i]);\n'
    assert unit.count(ready + binding + notify) == 1
    controls = [
        ('bind-before-ready', ready + binding + notify, binding + ready + notify, 'bind_after_ready_commit'),
        ('bind-after-notification', ready + binding + notify, ready + notify + binding, 'bind_before_first_notification'),
        ('missing-bind', binding, '', 'bind_before_first_notification'),
        ('collision-rollback', '        ESP_LOGW(TAG, "TLS input reclamation not attached");',
         '        { ESP_LOGW(TAG, "TLS input reclamation not attached"); result=ESP_FAIL; goto failed; }',
         'bind_collision_keeps_success'),
    ]
    flags = variants[-1][1]
    for name, old, new, marker in controls:
        assert unit.count(old) == 1, name
        directory = out / 'mutants' / name
        binary = build(directory, unit.replace(old, new, 1), flags)
        status, log = run(binary)
        (directory / 'test.log').write_bytes(log)
        assert status == 80 and log.startswith(('SEMANTIC_FAILURE:' + marker + ':').encode()), (name, status, log)
        assert b'AddressSanitizer' not in log and b'runtime error:' not in log
        report['negative_controls'][name] = dict(detected=True, status=status, marker=marker,
                                                generated_sha256=sha(directory / 'production.inc'))
        save()
        print('DETECTED:' + name, flush=True)
    report['live_inputs_match_snapshot'] = {name: sha(ROOT / name) == expected
                                           for name, expected in report['source_sha256'].items()}
    assert all(report['live_inputs_match_snapshot'].values())
    report.update(passed=True,
                  whole_reclaim_tu_unchanged=sha(frozen / MAIN / 'native_input_reclaim.c') == sha(ROOT / MAIN / 'native_input_reclaim.c'),
                  whole_adaptive_source_unchanged=sha(frozen / SHARED / 'adaptive_input.c') == sha(ROOT / SHARED / 'adaptive_input.c'),
                  generated_stubs_sha256={p.relative_to(stubs).as_posix(): sha(p) for p in stubs.rglob('*') if p.is_file()},
                  hooks='Linker-wrap spy on actual bind; original SDK TLS calloc is a deterministic failure seam. Whole module/queue use public bind/detach/hook only; no registry writes.',
                  teardown='Ordinary fixture task threads joined, then public detach, then test-only production discard. Current runtime has no successful-pool teardown.',
                  global_health_hook='Existing callback identity/registration count and observed original-calloc failures preserved; actual native_health implementation is qualified separately.')
    save()


if __name__ == '__main__':
    main()
