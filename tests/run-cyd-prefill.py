"""Sanitize the actual CYD bounded first-input wait with scripted time/queue seams."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.build/cyd-prefill'
MAIN=ROOT/'idf/esp32-cyd2usb-native/main'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'freertos').mkdir(exist_ok=True)
    (OUT/'freertos/FreeRTOS.h').write_text('''#pragma once
#include <stdint.h>
typedef int BaseType_t;
typedef unsigned TickType_t;
''')
    sources=[ROOT/'tests/native/cyd_prefill_test.c',MAIN/'input_prefill.h',
             ROOT/'idf/components/native_stream/include/adaptive_input.h',Path(__file__)]
    binary=OUT/'test'
    try:
        build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(OUT),'-I'+host(MAIN),'-I'+host(ROOT/'idf/components/native_stream/include'),
            host(sources[0]),'-o',host(binary)])
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary)])
    except subprocess.CalledProcessError as error:
        print(error.output.decode(errors='replace'),file=sys.stderr);raise
    (OUT/'build.log').write_bytes(build);(OUT/'test.log').write_bytes(log)
    (OUT/'report.json').write_text(json.dumps(dict(passed=True,
        scope='Actual bounded wait with scripted queue/time/task seams; no RTOS scheduling or physical network timing qualification.',
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
    print(log.decode(),end='')


if __name__=='__main__':main()
