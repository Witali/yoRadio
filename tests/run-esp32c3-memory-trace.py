"""Execute the real bounded codec allocation tracer with host platform stubs."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32c3-oled-native/main'
with tempfile.TemporaryDirectory(prefix='c3-memory-trace-') as folder:
    tmp = Path(folder)
    (tmp/'freertos').mkdir()
    (tmp/'sdkconfig.h').write_text('#define CONFIG_YORADIO_CODEC_MEMORY_TRACE 1\n')
    (tmp/'esp_log.h').write_text('#include <stdio.h>\n#define ESP_LOGI(tag, fmt, ...) printf(fmt "\\n", __VA_ARGS__)\n')
    (tmp/'freertos/FreeRTOS.h').write_text('''typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define taskENTER_CRITICAL(p) ((void)(p))
#define taskEXIT_CRITICAL(p) ((void)(p))
''')
    (tmp/'freertos/task.h').write_text('')
    (tmp/'test.c').write_text('''
#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
static bool fail_realloc;
static void *test_realloc(void *p, size_t size) {
    if (fail_realloc && size) return NULL;
    return realloc(p, size);
}
#define realloc test_realloc
#include "codec_memory_trace.c"
#undef realloc
int main(void) {
    unsigned char *p = media_lib_module_calloc("aac", 4, 8);
    assert(p && live == 32 && peak == 32);
    for (unsigned i=0; i<32; ++i) assert(p[i] == 0);
    memset(p, 0x5a, 32);
    fail_realloc = true;
    assert(!media_lib_module_realloc("aac", p, 128));
    assert(live == 32 && peak == 32);
    for (unsigned i=0; i<32; ++i) assert(p[i] == 0x5a);
    fail_realloc = false;
    p = media_lib_module_realloc("aac", p, 64);
    assert(p && live == 64 && peak == 64);
    for (unsigned i=0; i<32; ++i) assert(p[i] == 0x5a);
    assert(!media_lib_module_calloc("aac", SIZE_MAX, 2));
    void *q = media_lib_module_malloc("ps", 256);
    assert(q && live == 320 && peak == 320);
    media_lib_free(p); media_lib_free(q); media_lib_free(NULL);
    assert(live == 0 && lost == 0);
    codec_memory_trace_dump("closed");
    assert(count == 0);
    for (unsigned i=0; i<200; ++i) {
        p = media_lib_module_malloc("aac", 32);
        media_lib_free(p);
    }
    assert(live == 0 && lost > 0 && count == TRACE_EVENTS);
    puts("PASS: live/peak accounting, zeroing, realloc failure, cleanup and bounded overflow");
}
''')
    binary = tmp/'trace-test'
    subprocess.run([os.environ.get('CC','cc'),'-std=c11','-O2','-Wall','-Wextra','-Werror',
                    '-I'+str(tmp),'-I'+str(MAIN),str(tmp/'test.c'),'-o',str(binary)],check=True)
    output = subprocess.run([str(binary)],check=True,capture_output=True,text=True).stdout
    print(output, end='')
    sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
    from allocations import analyze
    report = analyze(output)
    assert report['peak_bytes'] == 320 and report['final_live_bytes'] == 0
    for broken in (output.replace('lost=0','lost=1'),
                   '\n'.join(line for line in output.splitlines() if 'op=+ id=1 ' not in line)):
        try:
            analyze(broken)
        except ValueError:
            pass
        else:
            raise AssertionError('Incomplete trace was accepted')
    print('PASS: trace analyzer rejects overflow and missing lifetime events')
