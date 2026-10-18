"""Exercise actual C3 Play/Stop/Resume ordering with deterministic preemption."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
OUT=ROOT/'.build/c3-command-concurrency'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'freertos').mkdir(exist_ok=True)
    (OUT/'freertos/FreeRTOS.h').write_text('''#pragma once
#include <stddef.h>
#include <stdint.h>
#include <pthread.h>
#include <assert.h>
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
SemaphoreHandle_t xSemaphoreCreateMutex(void);
int xSemaphoreTake(SemaphoreHandle_t,unsigned);
void xSemaphoreGive(SemaphoreHandle_t);
size_t strlcpy(char *,const char *,size_t);
''')
    (OUT/'freertos/semphr.h').write_text('#include "FreeRTOS.h"\n')
    (OUT/'esp_err.h').write_text('''#pragma once
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_INVALID_ARG (-2)
#define ESP_ERR_INVALID_STATE (-3)
''')
    spec=importlib.util.spec_from_file_location('cyd_helpers',ROOT/'tests/run-cyd-lifecycle.py')
    helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
    audio=MAIN/'audio_service.c';source=audio.read_text()
    start=source.index('typedef struct {\n    uint32_t generation;\n    native_codec_t requested_codec;')
    end=source.index('} play_command_t;',start)+len('} play_command_t;')
    generated=source[start:end]+'\n'
    names=['advance_generation','state_set_audio']
    if 'static esp_err_t play_locked(' in source:names.append('play_locked')
    names+=['audio_service_play','audio_service_resume','audio_service_stop']
    generated+='\n'.join(helpers.function(source,name) for name in names)
    (OUT/'production.inc').write_text(generated)
    binary=OUT/'test'
    sources=[ROOT/'tests/native/c3_command_concurrency_test.c',MAIN/'native_state.c']
    build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
        '-Wno-format-truncation','-Wno-unused-variable','-pthread',
        '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
        '-I'+host(OUT),'-I'+host(MAIN),*map(host,sources),'-o',host(binary)])
    (OUT/'build.log').write_bytes(build)
    try:
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1','timeout','20',host(binary)])
        passed=True
    except subprocess.CalledProcessError as error:
        log=error.output;passed=False
    (OUT/'test.log').write_bytes(log)
    sources += [Path(__file__),audio,MAIN/'native_state.h',MAIN/'audio_service.h']
    (OUT/'report.json').write_text(json.dumps(dict(passed=passed,physical_hardware=False,
        scope='Actual command/state functions, deterministic preemption before state lock, real host mutexes and queue API seam; no RTOS/board timing qualification.',
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
    print(log.decode(errors='replace'),end='')
    raise SystemExit(0 if passed else 1)


if __name__=='__main__':main()
