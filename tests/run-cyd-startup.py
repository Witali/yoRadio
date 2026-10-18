"""Fault-inject actual CYD startup, codec registry and adaptive queue with host tasks.

Real pthreads execute the production notification gate. Driver and RTOS
allocation APIs are seams; this does not qualify ESP32 scheduling or DMA.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32-cyd2usb-native/main'
SHARED = ROOT / 'idf/components/native_stream'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'freertos').mkdir(exist_ok=True)
    (out / 'freertos/FreeRTOS.h').write_text('''#pragma once
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
        (out / 'freertos' / name).write_text('#include "FreeRTOS.h"\n')
    (out / 'esp_err.h').write_text('''#pragma once
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
''')
    (out / 'esp_audio_dec.h').write_text('''#pragma once
typedef int esp_audio_err_t;
#define ESP_AUDIO_ERR_OK 0
#define ESP_AUDIO_ERR_MEM_LACK (-2)
''')
    (out / 'esp_audio_dec_default.h').write_text('''#include "esp_audio_dec.h"
esp_audio_err_t esp_mp3_dec_register(void);
esp_audio_err_t esp_aac_dec_register(void);
esp_audio_err_t esp_flac_dec_register(void);
esp_audio_err_t esp_vorbis_dec_register(void);
esp_audio_err_t esp_opus_dec_register(void);
void esp_audio_dec_unregister_all(void);
''')
    (out / 'esp_audio_simple_dec_default.h').write_text('''#include "esp_audio_dec.h"
esp_audio_err_t esp_audio_simple_dec_register_default(void);
void esp_audio_simple_dec_unregister_default(void);
''')
    (out / 'sdkconfig.h').write_text('')
    spec = importlib.util.spec_from_file_location('cyd_helpers', ROOT / 'tests/run-cyd-lifecycle.py')
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    source = (MAIN / 'audio_service.c').read_text()
    unit = source[source.index('#define STREAM_CHUNK_SIZE'):
                  source.index('static esp_audio_simple_dec_type_t')]
    start = source.index('typedef struct {\n    TaskFunction_t run;')
    unit += source[start:source.index('static void gated_pipeline_task(', start)]
    unit += '\n'.join(helpers.function(source, name) for name in (
        'gated_pipeline_task', 'discard_pipeline_startup', 'audio_service_start',
        'audio_service_play', 'audio_service_stop', 'audio_service_input_health'))
    (out / 'production.inc').write_text(unit)
    (out / 'adaptive-production.inc').write_bytes((SHARED / 'adaptive_input.c').read_bytes())
    results = {}
    variants = (
        ('ring-vendor', ['CONFIG_YORADIO_MP3_DECODER_ESPRESSIF', 'CONFIG_YORADIO_AAC_DECODER_ESPRESSIF']),
        ('ring-mp3-vendor', ['CONFIG_YORADIO_MP3_DECODER_ESPRESSIF']),
        ('ring-aac-vendor', ['CONFIG_YORADIO_AAC_DECODER_ESPRESSIF']),
        ('ring-custom', []),
    )
    variants += tuple(('adaptive-' + name[5:], flags + [
        'CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER', 'CONFIG_YORADIO_STREAM_CONFIRM'])
        for name, flags in variants)
    try:
        for name, flags in variants:
            binary = out / name
            build = run(['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                '-Wno-unused-variable', '-Wno-unused-function', '-Wno-format-truncation',
                '-pthread', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                '-fno-pie', '-no-pie', *['-D' + flag + '=1' for flag in flags],
                '-I' + host(out), '-I' + host(MAIN), '-I' + host(SHARED / 'include'),
                host(ROOT / 'tests/native/cyd_startup_test.c'), host(MAIN / 'native_state.c'),
                host(MAIN / 'decoder_registration.c'), '-o', host(binary)])
            (out / (name + '-build.log')).write_bytes(build)
            log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                       'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '30', host(binary)])
            (out / (name + '-test.log')).write_bytes(log)
            results[name] = log.decode().strip()
            print(name + ': ' + log.decode().strip())
    except subprocess.CalledProcessError as error:
        (out / 'failure.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    sources = [Path(__file__), ROOT / 'tests/native/cyd_startup_test.c',
        ROOT / 'tests/run-cyd-lifecycle.py',
        *[MAIN / name for name in ('audio_service.c', 'audio_service.h', 'native_state.c',
          'native_state.h', 'native_health.h', 'decoder_registration.c', 'decoder_registration.h')],
        SHARED / 'adaptive_input.c', SHARED / 'include/adaptive_input.h']
    sources += [SHARED / 'include/stream_probe.h', SHARED / 'include/stream_bitrate.h']
    for path in sources:
        dest = out / 'sources' / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
    (out / 'report.json').write_text(json.dumps(dict(passed=True, physical_hardware=False,
        scope='Actual startup/control/readiness/cleanup, codec registration and adaptive queue, including all nested adaptive allocations; pthread notification gate and concurrent/reentrant callers. Driver/RTOS APIs are deterministic host seams; no DMA/target scheduler evidence.',
        variants=results, source_sha256={p.relative_to(ROOT).as_posix():
            hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}), indent=2) + '\n')


if __name__ == '__main__':
    main()
