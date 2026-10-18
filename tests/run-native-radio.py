"""Execute the shared radio controller with each target's actual state code."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.build/native-radio'
STORAGE=ROOT/'idf/components/native_storage'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'freertos').mkdir(exist_ok=True)
    stubs={
        'sdkconfig.h':'#pragma once\n',
        'esp_err.h':'''#pragma once
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NOT_FOUND (-2)
#define ESP_ERR_INVALID_SIZE (-3)
#define ESP_ERR_INVALID_ARG (-4)
#define ESP_ERR_NO_MEM (-5)
#define ESP_ERR_INVALID_STATE (-6)
#define ESP_ERR_TIMEOUT (-7)
#define ESP_ERR_NVS_NOT_FOUND (-8)
const char *esp_err_to_name(esp_err_t);
''',
        'esp_log.h':'#define ESP_LOGI(...) ((void)0)\n#define ESP_LOGW(...) ((void)0)\n',
        'esp_timer.h':'#pragma once\n#include <stdint.h>\nint64_t esp_timer_get_time(void);\n',
        'esp_check.h':'''#pragma once
#define ESP_RETURN_ON_FALSE(condition,error,...) do {if (!(condition)) return (error);} while (0)
#define ESP_RETURN_ON_ERROR(expression,...) do {int error=(expression);if (error) return error;} while (0)
''',
        'freertos/FreeRTOS.h':'''#pragma once
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <pthread.h>
typedef pthread_mutex_t *SemaphoreHandle_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
SemaphoreHandle_t xSemaphoreCreateMutex(void);
int xSemaphoreTake(SemaphoreHandle_t,unsigned);
void xSemaphoreGive(SemaphoreHandle_t);
size_t strlcpy(char *,const char *,size_t);
''',
        'freertos/semphr.h':'#include "FreeRTOS.h"\n',
        'nvs.h':'''#pragma once
#include <stdint.h>
#include "esp_err.h"
typedef int nvs_handle_t;
#define NVS_READONLY 0
#define NVS_READWRITE 1
esp_err_t nvs_open(const char *,int,nvs_handle_t *);
void nvs_close(nvs_handle_t);
esp_err_t nvs_get_u16(nvs_handle_t,const char *,uint16_t *);
esp_err_t nvs_get_u8(nvs_handle_t,const char *,uint8_t *);
esp_err_t nvs_set_u16(nvs_handle_t,const char *,uint16_t);
esp_err_t nvs_set_u8(nvs_handle_t,const char *,uint8_t);
esp_err_t nvs_commit(nvs_handle_t);
''',
    }
    for name,body in stubs.items(): (OUT/name).write_text(body)
    reports={};sources=[Path(__file__),ROOT/'tests/native/native_radio_test.c',STORAGE/'file_transaction.c',
        *STORAGE.glob('include/*.h')]
    for target,directory in [('c3','esp32c3-oled-native'),('cyd','esp32-cyd2usb-native')]:
        main=ROOT/'idf'/directory/'main';binary=OUT/target
        (OUT/'radio-under-test.inc').write_text('#include "'+host(main/'radio_control.c')+'"\n')
        try:
            build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
                '-Wno-unused-variable','-Wno-format-truncation','-pthread',
                *(['-DTEST_CYD=1'] if target=='cyd' else []),
                '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                '-I'+host(OUT),'-I'+host(main),'-I'+host(STORAGE),'-I'+host(STORAGE/'include'),
                host(ROOT/'tests/native/native_radio_test.c'),host(main/'native_state.c'),'-o',host(binary)])
            (OUT/(target+'-build.log')).write_bytes(build)
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                'UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary)])
            (OUT/(target+'-test.log')).write_bytes(log)
        except subprocess.CalledProcessError as error:
            (OUT/'failure.log').write_bytes(error.output)
            print(error.output.decode(errors='replace'),file=sys.stderr);raise
        sources += [main/name for name in ('radio_control.c','radio_control.h','radio_control_platform.h',
                                           'native_state.c','native_state.h')]
        reports[target]=log.decode();print(target+': '+log.decode(),end='')
    (OUT/'report.json').write_text(json.dumps(dict(passed=True,targets=reports,
        scope='Actual shared controller, actual per-target state, real host mutexes/stdio; audio/NVS/timer API seams, no board timing qualification.',
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')


if __name__=='__main__':main()
