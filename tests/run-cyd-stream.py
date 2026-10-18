"""Exercise actual CYD stream task/HTTP helpers/status with deterministic I/O."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32-cyd2usb-native/main'
SHARED=ROOT/'idf/components/native_stream'
OUT=ROOT/'.build/cyd-stream'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
sys.path.insert(0,str(ROOT/'tests'))
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('cyd_lifecycle_runner',ROOT/'tests/run-cyd-lifecycle.py')
helpers=module_from_spec(spec);spec.loader.exec_module(helpers)


def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'freertos').mkdir(exist_ok=True)
    (OUT/'freertos/FreeRTOS.h').write_text('''#pragma once
#include <stddef.h>
#include <stdint.h>
typedef void *SemaphoreHandle_t;
typedef int BaseType_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
static inline void *xSemaphoreCreateMutex(void) { return (void *)1; }
static inline int xSemaphoreTake(void *p, unsigned t) { (void)t; return !!p; }
static inline void xSemaphoreGive(void *p) { (void)p; }
size_t strlcpy(char *, const char *, size_t);
''')
    (OUT/'freertos/semphr.h').write_text('#include "FreeRTOS.h"\n')
    (OUT/'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n')
    source=(MAIN/'audio_service.c').read_text()
    unit=source[source.index('#define STREAM_CHUNK_SIZE'):source.index('static esp_audio_simple_dec_type_t')]
    for name in ('codec_name','state_set_audio','stream_header_event','open_stream',
                 'read_stream','send_encoded','stream_transport_reset',
                 'stream_initial_pending','stream_confirmation_expired',
                 'send_stream_audio','finish_stream_audio','stream_audio',
                 'stream_title','stream_task'):
        unit+=helpers.function(source,name)
    unit+=helpers.function((MAIN/'web_service.c').read_text(),'status_handler')
    unit+=helpers.function(source,'audio_service_input_health')
    unit+=helpers.function((MAIN/'web_service.c').read_text(),'health_handler')
    unit+=helpers.function((MAIN/'web_service.c').read_text(),'parse_station_number')
    unit+=helpers.function((MAIN/'web_service.c').read_text(),'radio_handler')
    unit+=helpers.function((MAIN/'web_service.c').read_text(),'stop_handler')
    (OUT/'production.inc').write_text(unit)
    binary=OUT/'test'
    try:
        build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
            '-Wno-unused-variable','-Wno-unused-function','-fsanitize=address,undefined',
            '-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+host(OUT),
            '-I'+host(MAIN),'-I'+host(SHARED/'include'),
            host(ROOT/'tests/native/cyd_stream_test.c'),host(MAIN/'native_state.c'),
            host(MAIN/'native_health_json.c'),host(SHARED/'icy_title.c'),'-o',host(binary)])
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    except subprocess.CalledProcessError as error:
        print(error.output.decode(errors='replace'),file=sys.stderr);raise
    rows={}
    for line in log.decode().splitlines():
        if line.startswith(('STATUS=','MAX_STATUS=','UTF8_STATUS=','HEALTH=','RADIO=')):
            key,value=line.split('=',1);rows[key]=json.loads(value)
    row=rows['STATUS']
    assert row['station']=='station " \\' and row['format']=='format\nline'
    assert row['title']=='title " \\ Привет 🌍\n' and row['audio'] is True
    assert row['volume']==123 and row['balance']==-4 and row['arduino'] is False
    maximum=rows['MAX_STATUS']
    assert maximum['station']=='\1'*95 and maximum['title']=='\1'*191 and maximum['format']=='\1'*47
    assert rows['UTF8_STATUS']['title']=='а'*95+'\ufffd'
    health=rows['HEALTH']
    assert health['boot_id']=='0123456789abcdef' and health['uptime_ms']==12345
    assert (health['heap'],health['largest'],health['minimum_heap'],health['tasks'],health['cores'])==(10000,9000,8000,7,2)
    assert health['memory']==dict(internal_free=8000,internal_largest=7000,dma_free=4000,dma_largest=3000)
    assert health['allocation_failures']==3 and health['decoder_failure']['sequence']==2
    assert health['cpu']['overall_percent'] is None and health['cpu']['tasks']['decode']['stack_free_min'] is None
    assert not health['input']['available'] and not health['input']['leased']
    radio=rows['RADIO']
    assert radio['current']==65535 and radio['count']==65535 and radio['smartstart'] is True
    assert radio['station']=='\1'*143 and radio['connecting'] is True and radio['playing'] is False
    (OUT/'build.log').write_bytes(build);(OUT/'test.log').write_bytes(log)
    sources=[Path(__file__),ROOT/'tests/native/cyd_stream_test.c',ROOT/'tests/run-cyd-lifecycle.py',
        *[MAIN/name for name in ('audio_service.c','web_service.c','native_state.c','native_state.h','native_health.h','native_health_json.c')],
        SHARED/'icy_title.c',*[SHARED/'include'/name for name in
        ('audio_completion.h','icy_title.h','stream_body.h','stream_probe.h','stream_tags.h','json_buffer.h')]]
    sources += [MAIN/'radio_control.h',ROOT/'idf/components/native_storage/include/radio_control.h']
    (OUT/'report.json').write_text(json.dumps(dict(passed=True,physical_hardware=False,
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
    print('\n'.join(line for line in log.decode().splitlines() if line.startswith('PASS')))


if __name__=='__main__':main()
