"""Exercise actual CYD decoder/output tasks, state and PDM tails under sanitizers."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT/'idf/esp32-cyd2usb-native/main'
OUT = ROOT/'.build/cyd-lifecycle'
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host, run


def function(source, name):
    match = re.search(r'^(?:static )?[^\n]*\b' + name + r'\(', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'freertos').mkdir(exist_ok=True)
    (OUT/'freertos/FreeRTOS.h').write_text('''#pragma once
#include <stddef.h>
#include <stdint.h>
#include <assert.h>
#include <pthread.h>
#include <stdlib.h>
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef int BaseType_t;
typedef unsigned TickType_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
static inline SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    SemaphoreHandle_t p=malloc(sizeof(*p)); assert(p);
    assert(!pthread_mutex_init(p,NULL)); return p;
}
static inline int xSemaphoreTake(SemaphoreHandle_t p, unsigned t) {
    (void)t; assert(!pthread_mutex_lock(p)); return 1;
}
static inline void xSemaphoreGive(SemaphoreHandle_t p) { assert(!pthread_mutex_unlock(p)); }
size_t strlcpy(char *, const char *, size_t);
''')
    (OUT/'freertos/semphr.h').write_text('#include "FreeRTOS.h"\n')
    source = (MAIN/'audio_service.c').read_text()
    first = source.index('#define STREAM_CHUNK_SIZE')
    last = source.index('static esp_audio_simple_dec_type_t')
    generated = source[first:last]
    generated += re.search(r'^#define STREAM_INPUT_ACTIVE[^\n]+', source, re.M).group(0)+'\n'
    generated += source[source.index('static uint32_t s_decoder_bitrate_generation'):
                        source.index('static void state_set_decoder_bitrate')]
    for name in ('simple_decoder_type', 'codec_name', 'state_set_decoder_bitrate','publish_stream_info','state_set_audio',
                 'fail_generation', 'send_encoded', 'send_pcm', 'send_pcm_end',
                 'CUSTOM', 'decoder_release', 'decoder_task', 'output_task',
                 'audio_service_play', 'audio_service_stop', 'audio_service_input_health'):
        if name == 'CUSTOM':
            start = source.index('#ifdef YORADIO_CUSTOM_LEGACY_DECODER\ntypedef struct')
            generated += source[start:source.index('static void decoder_release(', start)]
        else:
            if name == 'decoder_task':
                generated += '#if CONFIG_YORADIO_INPUT_PREFILL_MS > 0\n#include "input_prefill.h"\n#endif\n'
            generated += function(source, name)
    (OUT/'production.inc').write_text(generated)
    output = (MAIN/'native_audio_output.c').read_text()
    generated = '\n'.join(function(output, name) for name in (
        'reset_resampler', 'pdm_flush', 'native_audio_output_discard_pcm',
        'native_audio_output_flush_pcm'))
    (OUT/'pdm-tail.inc').write_text(generated)
    results = {}
    try:
        variants = (
            ('espressif', []),
            ('helix', ['-DYORADIO_CUSTOM_LEGACY_DECODER=1',
                       '-DCONFIG_YORADIO_AAC_DECODER_HELIX=1',
                       '-DCONFIG_YORADIO_MP3_DECODER_HELIX=1']),
            ('minimp3', ['-DYORADIO_CUSTOM_LEGACY_DECODER=1',
                         '-DCONFIG_YORADIO_MP3_DECODER_MINIMP3=1',
                         '-DCONFIG_YORADIO_AAC_DECODER_HELIX=1']),
        )
        variants += tuple(('adaptive-'+name,defines+['-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1',
            '-DCONFIG_YORADIO_STREAM_CONFIRM=1','-DCONFIG_YORADIO_INPUT_PREFILL_MS=250']) for name,defines in variants)
        for name, defines in variants:
            binary = OUT/name
            build = run(['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                     '-pthread', *defines,
                     '-Wno-unused-variable', '-Wno-unused-function',
                     '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                     '-fno-pie', '-no-pie', '-I'+host(OUT), '-I'+host(MAIN),
                     '-I'+host(ROOT/'idf/components/native_stream/include'),
                     host(ROOT/'tests/native/cyd_lifecycle_test.c'),
                     host(MAIN/'native_state.c'), '-o', host(binary)])
            log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
            (OUT/(name+'-build.log')).write_bytes(build)
            (OUT/(name+'-test.log')).write_bytes(log)
            results[name] = log.decode()
            print(name+':\n'+log.decode(), end='')
    except subprocess.CalledProcessError as error:
        print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    (OUT/'report.json').write_text(json.dumps({
        'passed': True, 'physical_hardware': False,
        'variants': results, 'compiler': run(['gcc','--version']).decode().splitlines()[0],
        'source_sha256': {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__), ROOT/'tests/native/cyd_lifecycle_test.c',
                      ROOT/'idf/components/native_stream/include/audio_completion.h',
                      ROOT/'idf/components/native_stream/include/adaptive_input.h',
                      MAIN/'input_prefill.h',
                      MAIN/'native_health.h',
                      *[MAIN/name for name in ('audio_service.c','native_state.c','native_state.h',
                                              'native_audio_output.c','native_audio_output.h')]]},
    }, indent=2)+'\n')


if __name__ == '__main__':
    main()
