"""Exercise actual SMP fault snapshots, two-core CPU sampling and bounded health JSON."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32-cyd2usb-native/main'
OUT=ROOT/'.build/cyd-health'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    OUT=parser.parse_args().output.resolve()
    OUT.mkdir(parents=True,exist_ok=False);(OUT/'freertos').mkdir()
    sources=[Path(__file__),ROOT/'tests/native/cyd_health_test.c',
        *[MAIN/name for name in ('native_health.c','native_health.h','native_health_json.c','native_output_metrics.h')],
        ROOT/'idf/components/native_stream/include/json_buffer.h',ROOT/'tools/codec_benchmark/run_output_dma_host.py']
    hashes={}
    for path in sources:
        relative=path.relative_to(ROOT)
        target=OUT/'sources'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(path.read_bytes())
        hashes[relative.as_posix()]=hashlib.sha256(target.read_bytes()).hexdigest()
    frozen=OUT/'sources'
    frozen_main=frozen/MAIN.relative_to(ROOT)
    stubs={
        'sdkconfig.h':'''#pragma once
#ifdef TEST_DIAGNOSTIC
#define CONFIG_YORADIO_NATIVE_DIAGNOSTICS 1
#define CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS 1
#define CONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER 1
#endif
''',
        'esp_attr.h':'#define IRAM_ATTR\n#define DRAM_ATTR\n',
        'esp_err.h':'#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_FAIL (-1)\n',
        'esp_timer.h':'#pragma once\n#include <stdint.h>\nint64_t esp_timer_get_time(void);\n',
        'esp_ipc.h':'''#pragma once
#include <stdint.h>
#include "esp_err.h"
esp_err_t esp_ipc_call_blocking(uint32_t,void (*)(void *),void *);
''',
        'esp_heap_caps.h':'''#pragma once
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
typedef void (*esp_alloc_failed_hook_t)(size_t,uint32_t,const char *);
esp_err_t heap_caps_register_failed_alloc_callback(esp_alloc_failed_hook_t);
''',
        'freertos/FreeRTOS.h':'''#pragma once
#include <assert.h>
#include <stdint.h>
#include <pthread.h>
typedef pthread_mutex_t portMUX_TYPE;
typedef int BaseType_t;
typedef unsigned UBaseType_t,TickType_t;
#ifdef TEST_COUNTER64
typedef uint64_t configRUN_TIME_COUNTER_TYPE;
#else
typedef uint32_t configRUN_TIME_COUNTER_TYPE;
#endif
#define configNUMBER_OF_CORES 2
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
#define portENTER_CRITICAL_ISR(p) portENTER_CRITICAL(p)
#define portEXIT_CRITICAL_ISR(p) portEXIT_CRITICAL(p)
#define pdPASS 1
#define pdMS_TO_TICKS(x) (x)
BaseType_t xPortGetCoreID(void);
''',
        'freertos/task.h':'''#pragma once
#include "FreeRTOS.h"
typedef void *TaskHandle_t;
typedef struct { TaskHandle_t xHandle;const char *pcTaskName;UBaseType_t xTaskNumber;
    configRUN_TIME_COUNTER_TYPE ulRunTimeCounter;uint32_t usStackHighWaterMark; } TaskStatus_t;
UBaseType_t uxTaskGetSystemState(TaskStatus_t *,UBaseType_t,configRUN_TIME_COUNTER_TYPE *);
TaskHandle_t xTaskGetIdleTaskHandleForCore(BaseType_t);
BaseType_t xTaskCreatePinnedToCore(void (*)(void *),const char *,unsigned,void *,unsigned,TaskHandle_t *,BaseType_t);
void vTaskDelay(TickType_t);
''',
    }
    for name,body in stubs.items():(OUT/name).write_text(body)
    variants={}
    for name,flags in (('quiet',[]),('diagnostic32',['-DTEST_DIAGNOSTIC=1']),
                       ('diagnostic64',['-DTEST_DIAGNOSTIC=1','-DTEST_COUNTER64=1'])):
        binary=OUT/name
        try:
            build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
                '-Wno-unused-function','-Wno-unused-variable','-pthread',*flags,
                '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                '-I'+host(OUT),'-I'+host(frozen_main),'-I'+host(frozen/'idf/components/native_stream/include'),
                host(frozen/'tests/native/cyd_health_test.c'),host(frozen_main/'native_health_json.c'),
                '-o',host(binary)])
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                'UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary)])
        except subprocess.CalledProcessError as error:
            print(error.output.decode(errors='replace'),file=sys.stderr);raise
        (OUT/(name+'-build.log')).write_bytes(build);(OUT/(name+'-test.log')).write_bytes(log)
        for line in log.decode().splitlines():
            if line.startswith('HEALTH_MAX='):
                row=json.loads(line.split('=',1)[1])
                assert row['boot_id']=='f'*16 and row['uptime_ms']==2**64-1
                assert row['allocation_failures']==2**32-1 and row['decoder_failure']['result']==-(2**31)
                assert row['cpu']['overall_percent']==100.0 and row['cpu']['core_percent']==[100.0,100.0]
                assert row['cpu']['tasks']['decode']['percent_of_one_core']==100.0
                driver=row['output_driver']
                for field in ('requested_bytes','written_bytes','write_us','max_write_us'):
                    assert driver[field]==2**64-1
                for field in ('writes','errors','timeouts','short_writes','timing_samples',
                              'invalid_time_samples','completion_queue_drops'):
                    assert driver[field]==2**32-1
                assert driver['saturated'] is True and driver['timing_enabled'] is True
            elif line.startswith('HEALTH_MAX_BYTES='):
                assert int(line.split('=',1)[1])<2304
        assert all(marker in log.decode().splitlines() for marker in
                   ('HEALTH_UNAVAILABLE_OK','HEALTH_NO_TIMING_SAMPLES_OK','HEALTH_MEASURED_ZERO_OK'))
        variants[name]=log.decode();print(name+': '+log.decode(),end='')
    matches={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected for name,expected in hashes.items()}
    assert all(matches.values()),matches
    (OUT/'report.json').write_text(json.dumps(dict(passed=True,variants=variants,
        source_sha256=hashes,live_inputs_match_snapshot=matches,physical_hardware=False,
        scope='Actual fault/sampler implementation and complete bounded JSON serializer with real host mutexes, scripted SDK task snapshots and IPC. Driver snapshot values are serializer inputs; no backend, kernel, ISR latency or physical CPU qualification.'),indent=2)+'\n')


if __name__=='__main__':main()
