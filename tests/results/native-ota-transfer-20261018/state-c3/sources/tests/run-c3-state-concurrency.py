"""Compile actual C3 title publication/state with real host mutexes and sanitizers."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'.build/c3-state-concurrency')
OUT=parser.parse_args().output
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'freertos').mkdir(exist_ok=True)
    (OUT/'freertos/FreeRTOS.h').write_text('''#pragma once
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
''')
    (OUT/'freertos/semphr.h').write_text('#include "FreeRTOS.h"\n')
    spec=importlib.util.spec_from_file_location('cyd_helpers',ROOT/'tests/run-cyd-lifecycle.py')
    helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
    (OUT/'production.inc').write_text(helpers.function((MAIN/'audio_service.c').read_text(),'publish_icy_title'))
    binary=OUT/'test'
    sources=[ROOT/'tests/native/c3_state_concurrency_test.c',MAIN/'native_state.c']
    try:
        build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
            '-Wno-format-truncation', # Unrelated bounded status formatting intentionally truncates.
            *(['-DC3_HAS_STREAM_TITLE=1'] if 'native_state_set_stream_title(' in (MAIN/'native_state.h').read_text() else []),
            '-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(OUT),'-I'+host(MAIN),*map(host,sources),'-o',host(binary)])
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    except subprocess.CalledProcessError as error:
        (OUT/'failure.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'),file=sys.stderr);raise
    (OUT/'build.log').write_bytes(build);(OUT/'test.log').write_bytes(log)
    sources += [Path(__file__),MAIN/'audio_service.c',MAIN/'native_state.h']
    (OUT/'report.json').write_text(json.dumps(dict(passed=True,physical_hardware=False,
        scope='Actual C3 metadata publication/state with deterministic preemption before its mutex, real pthread contention; no scheduler or board timing qualification.',
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
    print(log.decode(),end='')


if __name__=='__main__':main()
