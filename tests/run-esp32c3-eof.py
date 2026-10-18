"""Run the production EOF queue/state operations with deterministic scheduling."""
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32c3-oled-native/main'
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host, run


def function(source, name):
    match = re.search(r'^static [^\n]*\b' + name + r'\(', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


with tempfile.TemporaryDirectory(prefix='c3-eof-') as directory:
    tmp = Path(directory)
    (tmp/'freertos').mkdir()
    (tmp/'freertos/FreeRTOS.h').write_text('''#pragma once
#include <stddef.h>
typedef void *SemaphoreHandle_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY 0xffffffffU
static inline void *xSemaphoreCreateMutex(void) { return (void *)1; }
static inline int xSemaphoreTake(void *p, unsigned t) { (void)t; return !!p; }
static inline void xSemaphoreGive(void *p) { (void)p; }
size_t strlcpy(char *, const char *, size_t);
typedef int BaseType_t;
''')
    (tmp/'freertos/semphr.h').write_text('#include "FreeRTOS.h"\n')
    (tmp/'sdkconfig.h').write_text('')
    (tmp/'freertos/ringbuf.h').write_text('#include "FreeRTOS.h"\n')
    source = (MAIN/'audio_service.c').read_text()
    first = source.index('typedef struct {\n    uint32_t generation;\n    native_codec_t codec;')
    last = source.index('typedef struct {\n    uint32_t generation;\n    native_codec_t codec;\n    int64_t', first)
    generated = source[first:last]
    generated += '\n'.join(function(source, name) for name in (
        'state_set_audio', 'send_encoded', 'send_pcm', 'send_pcm_end',
        'return_decoded_packet', 'finish_pcm_stream', 'finish_stream_audio'))
    # Include the actual producer termination and output marker branch, so a
    # regression that moves completion back to the network task is exercised.
    first = source.index('        uint8_t end_reason = stream_unavailable ?',
                         source.index('static void stream_task('))
    last = source.index('\n    }\n}', first)
    generated += '''
static void finish_network(uint32_t generation, bool stream_read_failed) {
    struct { uint32_t generation; } command = {generation};
    bool stream_stalled = false;
    bool stream_unavailable = false;
    bool format_unknown = false;
    bool first_chunk = false;
    native_codec_t codec = NATIVE_CODEC_AAC;
    void *client = NULL;
''' + source[first:last] + '\n}\n'
    first = source.index('        if (packet->end_of_stream) {', source.index('static void output_task('))
    last = source.index('        if (packet->sample_rate', first)
    generated += '''
static void finish_output(pcm_packet_t *packet) {
    do {
''' + source[first:last] + '\n    } while (false);\n}\n'
    start = source.index('#if CONFIG_YORADIO_INPUT_PREFILL_MS > 0',
                         source.index('if (packet->generation != generation || packet->codec != codec)'))
    end = source.index('#endif', start)+len('#endif')
    generated += '''
#define CONFIG_YORADIO_INPUT_PREFILL_MS 1000
static void check_segment_prefill(native_codec_t codec, encoded_packet_t *packet) {
    do {
''' + source[start:end] + '\n    } while (false);\n}\n'
    (tmp/'production.inc').write_text(generated)
    executable = tmp/'eof'
    try:
        compile_log = run([os.environ.get('CC','cc'), '-std=c11', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-fsanitize=address,undefined',
                    '-fno-pie', '-no-pie', '-I'+host(tmp), '-I'+host(MAIN),
                    host(ROOT/'tests/native/esp32c3_eof_test.c'),
                    host(MAIN/'native_state.c'), '-o', host(executable)])
    except subprocess.CalledProcessError as error:
        print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    print(compile_log.decode(), end='')
    print(run([host(executable)]).decode(), end='')
