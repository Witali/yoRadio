"""Exercise the production arena adapter with the real ESP-IDF TLSF allocator.

Host pthread locking replaces the C3 critical section; this does not measure
target interrupt latency. All SDK allocator sources are retained for replay.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    files = [ROOT / 'idf/esp32c3-oled-native/main' / name for name in
             ('decoder_arena.c', 'decoder_arena.h')]
    files += [ROOT / 'tests/native/decoder_arena_test.c']
    heap = a.sdk_root / 'components/heap'
    files += [heap / name for name in ('multi_heap.c', 'multi_heap_internal.h',
                                     'multi_heap_config.h', 'multi_heap_platform.h')]
    files += list((heap / 'tlsf').rglob('*.h')) + [heap / 'tlsf/tlsf.c']
    files += [heap / 'include/multi_heap.h']
    hashes = {}
    for source in files:
        data = source.read_bytes()
        (a.output / source.name).write_bytes(data)
        hashes[str(source)] = hashlib.sha256(data).hexdigest()
    (a.output / 'sdkconfig.h').write_text(
        '#define CONFIG_YORADIO_SHARED_DECODER_ARENA 1\n'
        '#define CONFIG_YORADIO_SHARED_DECODER_ARENA_BYTES 98304\n')
    (a.output / 'freertos').mkdir()
    (a.output / 'freertos/FreeRTOS.h').write_text('''#pragma once
#include <pthread.h>
#include <stdbool.h>
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) pthread_mutex_lock(p)
#define portEXIT_CRITICAL(p) pthread_mutex_unlock(p)
extern _Thread_local bool test_isr;
static inline bool xPortInIsrContext(void) { return test_isr; }
''')
    (a.output / 'freertos/task.h').write_text('#pragma once\n')
    (a.output / 'esp_attr.h').write_text('#define IRAM_ATTR\n')
    command = ['gcc', '-std=gnu11', '-O2', '-g', '-Wall', '-Wextra',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
               '-fno-pie', '-no-pie', '-pthread', '-I' + host(a.output)]
    jobs = []
    # Espressif's port uses four-byte headers even on this x86-64 host.
    # Preserve SDK source bytes; suppress alignment instrumentation only for
    # the two SDK objects. The adapter and payload alignment remain checked.
    for name in ('multi_heap', 'tlsf', 'decoder_arena', 'decoder_arena_test'):
        flags = ['-fno-sanitize=alignment'] if name in ('multi_heap', 'tlsf') else []
        jobs.append((name, command + flags + ['-c', host(a.output / (name + '.c')),
                         '-o', host(a.output / (name + '.o'))]))
    jobs.append(('link', command + [host(a.output / (n + '.o')) for n in
        ('decoder_arena', 'decoder_arena_test', 'multi_heap', 'tlsf')] +
        ['-o', host(a.output / 'test')]))
    jobs.append(('run', ['env',
            'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1', host(a.output / 'test')]))
    for name, cmd in jobs:
        try:
            log = run(cmd)
        except subprocess.CalledProcessError as e:
            (a.output / (name + '.log')).write_bytes(e.output)
            print(e.output.decode(errors='replace'))
            raise
        (a.output / (name + '.log')).write_bytes(log)
    (a.output / 'report.json').write_text(json.dumps(
        {'result': 'PASS', 'source_sha256': hashes}, indent=2) + '\n')
    print(log.decode())

if __name__ == '__main__':
    main()
