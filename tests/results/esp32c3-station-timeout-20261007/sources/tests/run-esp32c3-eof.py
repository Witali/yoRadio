"""Run the production EOF queue/state operations with deterministic scheduling."""
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32c3-oled-native/main'


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
        'return_decoded_packet', 'finish_pcm_stream'))
    # Include the actual producer termination and output marker branch, so a
    # regression that moves completion back to the network task is exercised.
    first = source.index('        uint8_t end_reason = stream_stalled')
    last = source.index('\n    }\n}', first)
    generated += '''
static void finish_network(uint32_t generation, bool stream_read_failed) {
    struct { uint32_t generation; } command = {generation};
    bool stream_stalled = false;
    bool stream_unavailable = false;
    native_codec_t codec = NATIVE_CODEC_AAC;
    void *client = NULL;
''' + source[first:last] + '\n}\n'
    first = source.index('        if (packet->end_of_stream) {', source.index('static void output_task('))
    last = source.index('        if (packet->sample_rate', first)
    generated += '''
static void finish_output(pcm_packet_t *packet) {
    do {
''' + source[first:last] + '\n    } while (false);\n}\n'
    (tmp/'production.inc').write_text(generated)
    executable = tmp/'eof'
    subprocess.run([os.environ.get('CC','cc'), '-std=c11', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-I'+str(tmp), '-I'+str(MAIN),
                    str(ROOT/'tests/native/esp32c3_eof_test.c'),
                    str(MAIN/'native_state.c'), '-o', str(executable)], check=True)
    subprocess.run([str(executable)], check=True)
