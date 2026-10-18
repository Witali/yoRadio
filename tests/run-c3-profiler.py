"""Exercise the actual C3 diagnostic sampler across task deletion/reuse."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
OUT=ROOT/'.build/c3-profiler'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'freertos').mkdir(exist_ok=True)
    stubs={
        'sdkconfig.h':'#pragma once\n#define CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS 1\n',
        'esp_err.h':'#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_ERR_NO_MEM 0x101\n#define ESP_ERROR_CHECK(x) assert((x)==ESP_OK)\n',
        'esp_attr.h':'#define IRAM_ATTR\n#define DRAM_ATTR\n',
        'esp_timer.h':'#pragma once\n#include <stdint.h>\nint64_t esp_timer_get_time(void);\n',
        'esp_heap_caps.h':'''#pragma once
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
#define MALLOC_CAP_8BIT 4
typedef struct {size_t total_free_bytes,largest_free_block,total_allocated_bytes,allocated_blocks;} multi_heap_info_t;
void heap_caps_get_info(multi_heap_info_t *,uint32_t);
size_t heap_caps_get_free_size(uint32_t);
size_t heap_caps_get_largest_free_block(uint32_t);
esp_err_t heap_caps_register_failed_alloc_callback(void (*)(size_t,uint32_t,const char *));
''',
        'esp_log.h':'''#pragma once
void test_log(const char *,...);
#define ESP_LOGI(tag,...) test_log(__VA_ARGS__)
#define ESP_LOGW(tag,...) test_log(__VA_ARGS__)
#define ESP_LOGE(tag,...) test_log(__VA_ARGS__)
''',
        'freertos/FreeRTOS.h':'''#pragma once
#include <assert.h>
#include <stdint.h>
typedef unsigned UBaseType_t,TickType_t;
typedef int BaseType_t;
typedef void *TaskHandle_t;
#ifdef TEST_COUNTER64
typedef uint64_t configRUN_TIME_COUNTER_TYPE;
#else
typedef uint32_t configRUN_TIME_COUNTER_TYPE;
#endif
#define configNUMBER_OF_CORES 1
#define configMAX_TASK_NAME_LEN 16
#define portSET_INTERRUPT_MASK_FROM_ISR() 0
#define portCLEAR_INTERRUPT_MASK_FROM_ISR(x) ((void)(x))
#define pdPASS 1
#define pdMS_TO_TICKS(x) (x)
''',
        'freertos/task.h':'''#pragma once
#include "FreeRTOS.h"
typedef struct {TaskHandle_t xHandle;const char *pcTaskName;UBaseType_t xTaskNumber;
 configRUN_TIME_COUNTER_TYPE ulRunTimeCounter;uint32_t usStackHighWaterMark;} TaskStatus_t;
UBaseType_t uxTaskGetSystemState(TaskStatus_t *,UBaseType_t,configRUN_TIME_COUNTER_TYPE *);
void vTaskSuspendAll(void);
BaseType_t xTaskResumeAll(void);
BaseType_t xTaskCreate(void (*)(void *),const char *,unsigned,void *,unsigned,TaskHandle_t *);
void vTaskDelay(TickType_t);
''',
    }
    for name,body in stubs.items(): (OUT/name).write_text(body)
    variants={}
    try:
        for name,flags in [('counter32',[]),('counter64',['-DTEST_COUNTER64=1'])]:
            binary=OUT/name
            build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
                '-Wno-unused-function','-Wno-unused-variable',*flags,
                '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                '-I'+host(OUT),'-I'+host(MAIN),host(ROOT/'tests/native/c3_profiler_test.c'),
                '-o',host(binary)])
            (OUT/(name+'-build.log')).write_bytes(build)
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                'UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary)])
            (OUT/(name+'-test.log')).write_bytes(log)
            variants[name]=log.decode(); print(name+': '+log.decode(),end='')
    except subprocess.CalledProcessError as error:
        (OUT/'failure.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'),file=sys.stderr); raise
    sources=[Path(__file__),ROOT/'tests/native/c3_profiler_test.c',MAIN/'cpu_profiler.c',MAIN/'cpu_profiler.h']
    (OUT/'report.json').write_text(json.dumps(dict(passed=True,variants=variants,
        scope='Actual C3 sampler with scheduler/deletion and logging seams; no kernel timing or physical qualification.',
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')


if __name__=='__main__': main()
