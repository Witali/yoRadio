"""Exercise actual C3 bitrate publication with deterministic preemption and ASan/UBSan.

The optional source-main lets a frozen pre-fix source run the same assertions.
Only timer, RTOS mutex and atomic-operation seams are supplied by the host.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32c3-oled-native/main'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-main', type=Path, default=MAIN)
    parser.add_argument('--cases', nargs='+', default=[
        'old-meter-generation', 'decoder-measured-preemption', 'decoder-rounding',
        'meter-rounding', 'meter-clock-zero', 'decoder-clock-zero',
        'priority-and-generation', 'concurrent-priority'])
    args = parser.parse_args()
    out = args.output.resolve()
    source_main = args.source_main.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'freertos').mkdir(exist_ok=True)
    (out / 'freertos/FreeRTOS.h').write_text('''#pragma once
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
    (out / 'freertos/semphr.h').write_text('#include "FreeRTOS.h"\n')
    spec = importlib.util.spec_from_file_location('cyd_helpers', ROOT / 'tests/run-cyd-lifecycle.py')
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    audio = source_main / 'audio_service.c'
    source = audio.read_text()
    priority = 'native_state_publish_bitrate(' in (source_main / 'native_state.h').read_text()
    generated = '#define BITRATE_UPDATE_INTERVAL_US 1000000LL\n'
    if '#include "stream_bitrate.h"' in source:
        generated += '#include "stream_bitrate.h"\n'
    else:
        end = source.index('} stream_bitrate_meter_t;') + len('} stream_bitrate_meter_t;')
        start = source.rindex('typedef struct {', 0, end)
        generated += '#define STREAM_BITRATE_INTERVAL_US 5000000LL\n' + source[start:end] + '\n'
    start = source.index('static uint32_t s_published_bitrate_bps;')
    end = source.index('// One stream task owns', start)
    generated += source[start:end] + '\n'
    generated += '\n'.join(helpers.function(source, name) for name in (
        'stream_bitrate_add', 'reset_decoder_bitrate_tracking', 'state_set_decoder_bitrate'))
    (out / 'production.inc').write_text(generated)
    binary = out / 'test'
    test = ROOT / 'tests/native/c3_bitrate_test.c'
    include = ROOT / 'idf/components/native_stream/include'
    sources = [test, source_main / 'native_state.c']
    build = run(['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
        '-Wno-format-truncation', '-Wno-unused-function', '-pthread',
        *(['-DC3_HAS_PRIORITY=1'] if priority else []),
        '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
        '-I' + host(out), '-I' + host(source_main), '-I' + host(include),
        *map(host, sources), '-o', host(binary)])
    (out / 'build.log').write_bytes(build)
    results = {}
    logs = []
    for case in args.cases:
        try:
            log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                       'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '20', host(binary), case])
            passed = True
        except subprocess.CalledProcessError as error:
            log = error.output
            passed = False
        (out / (case + '.log')).write_bytes(log)
        logs.append(log)
        results[case] = {'passed': passed}
    (out / 'test.log').write_bytes(b''.join(logs))
    sources += [Path(__file__), audio, source_main / 'native_state.h', include / 'stream_bitrate.h']
    source_sha256 = {}
    for path in sources:
        key = path.relative_to(ROOT).as_posix()
        source_sha256[key] = hashlib.sha256(path.read_bytes()).hexdigest()
        dest = out / 'sources' / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
    report = dict(passed=all(case['passed'] for case in results.values()),
        physical_hardware=False, source_priority_api=priority, cases=results,
        scope='Actual C3 bitrate functions and state; controlled preemption before atomic return or mutex acquisition, real pthread contention, timer seam. No board timing measurement.',
        source_sha256=source_sha256)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
