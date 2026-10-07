"""Exercise PCB capacity, reuse, forwarding and concurrent ownership with sanitizers."""
from pathlib import Path
import subprocess
import tempfile
import signal

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='tcp-pool-') as directory:
    tmp = Path(directory)
    (tmp/'lwip').mkdir()
    (tmp/'esp_attr.h').write_text('#define RTC_DATA_ATTR\n')
    (tmp/'esp_log.h').write_text('''#include <stdio.h>
#include <stdarg.h>
static inline void pool_test_log(const char *tag, const char *format, ...)
{(void)tag; va_list ap; va_start(ap, format); vprintf(format, ap); va_end(ap); puts(""); fflush(stdout);}
#define ESP_LOGI pool_test_log
''')
    (tmp/'lwip/memp.h').write_text('''#pragma once
#include <assert.h>
#define MEMP_MEM_MALLOC 1
#define MEMP_OVERFLOW_CHECK 0
#define MEM_ALIGNMENT 4
#define LWIP_ASSERT(message, condition) assert(condition)
typedef enum { MEMP_OTHER, MEMP_TCP_PCB, MEMP_MAX } memp_t;
struct stats_mem {unsigned used, max, err;};
struct memp_desc {struct stats_mem *stats;};
extern const struct memp_desc *const memp_pools[MEMP_MAX];
''')
    (tmp/'lwip/sys.h').write_text('''#include <pthread.h>
extern pthread_mutex_t lock;
#define SYS_ARCH_DECL_PROTECT(level) int level
#define SYS_ARCH_PROTECT(level) do {level = pthread_mutex_lock(&lock); assert(!level);} while(0)
#define SYS_ARCH_UNPROTECT(level) do {(void)level; assert(!pthread_mutex_unlock(&lock));} while(0)
''')
    (tmp/'lwip/tcp.h').write_text('#pragma once\nstruct tcp_pcb {union {unsigned words[42]; unsigned state;};};\n')
    (tmp/'test.c').write_text(r'''
#include <assert.h>
#include <pthread.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lwip/memp.h"
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static struct stats_mem stats;
static const struct memp_desc desc = {&stats};
const struct memp_desc *const memp_pools[MEMP_MAX] = {&desc, &desc};
static unsigned forwarded_alloc, forwarded_free;
void *__real_memp_malloc(memp_t type) {assert(type == MEMP_OTHER); ++forwarded_alloc; return malloc(33);}
void __real_memp_free(memp_t type, void *p) {assert(type == MEMP_OTHER); ++forwarded_free; free(p);}
#include "tcp_pcb_pool.c"
static void *worker(void *arg) {
    unsigned pattern = (unsigned)(uintptr_t)arg;
    for (unsigned n = 0; n < 10000; ++n) {
        struct tcp_pcb *p;
        while (!(p = __wrap_memp_malloc(MEMP_TCP_PCB))) sched_yield();
        for (unsigned i = 0; i < 42; ++i) p->words[i] = pattern;
        if (!(n % 13)) sched_yield();
        for (unsigned i = 0; i < 42; ++i) assert(p->words[i] == pattern);
        __wrap_memp_free(MEMP_TCP_PCB, p);
    }
    return NULL;
}
int main(int argc, char **argv) {
    (void)argv;
    if (argc > 1) {
        void *p = __wrap_memp_malloc(MEMP_TCP_PCB);
        assert(p);
        __wrap_memp_free(MEMP_TCP_PCB, p);
        __wrap_memp_free(MEMP_TCP_PCB, p); // Expected ownership assertion.
        return 99;
    }
    void *ordinary = __wrap_memp_malloc(MEMP_OTHER);
    __wrap_memp_free(MEMP_OTHER, ordinary);
    assert(forwarded_alloc == 1 && forwarded_free == 1);
    void *all[MEMP_NUM_TCP_PCB];
    for (unsigned i = 0; i < MEMP_NUM_TCP_PCB; ++i) {
        all[i] = __wrap_memp_malloc(MEMP_TCP_PCB); assert(all[i]);
        assert((uintptr_t)all[i] % MEM_ALIGNMENT == 0);
        for (unsigned j = 0; j < i; ++j) assert(all[i] != all[j]);
    }
    assert(!__wrap_memp_malloc(MEMP_TCP_PCB)); // Same configured limit, no heap fallback.
#if MEMP_STATS
    assert(stats.used == MEMP_NUM_TCP_PCB && stats.max == MEMP_NUM_TCP_PCB && stats.err == 1);
#endif
    __wrap_memp_free(MEMP_TCP_PCB, all[0]);
    assert(__wrap_memp_malloc(MEMP_TCP_PCB) == all[0]);
    for (unsigned i = 0; i < MEMP_NUM_TCP_PCB; ++i) __wrap_memp_free(MEMP_TCP_PCB, all[i]);
    __wrap_memp_free(MEMP_TCP_PCB, NULL);
    pthread_t threads[4];
    for (unsigned i = 0; i < 4; ++i) assert(!pthread_create(&threads[i], NULL, worker, (void *)(uintptr_t)(i+1)));
    for (unsigned i = 0; i < 4; ++i) assert(!pthread_join(threads[i], NULL));
#if MEMP_STATS
    assert(!stats.used && stats.max == MEMP_NUM_TCP_PCB);
#endif
    assert(forwarded_alloc == 1 && forwarded_free == 1);
    printf("TCP_PCB_POOL_PASS capacity=%u stats=%u reuse, alignment, forwarding and 40000 concurrent lifetimes\n",
           MEMP_NUM_TCP_PCB, MEMP_STATS);
}
''')
    for count in (1, 16, 32):
        for stats in (0, 1):
            for trace in (False, True):
                exe = tmp/f'pool-{count}-{stats}-{trace}'
                options = ['-DCONFIG_YORADIO_TCP_PCB_POOL_DIAGNOSTICS=1'] if trace else []
                subprocess.run(['cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                                '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-pthread',
                                '-DMEMP_NUM_TCP_PCB='+str(count), '-DMEMP_STATS='+str(stats),
                                '-I'+str(tmp), '-I'+str(ROOT/'idf/esp32c3-oled-native/main'),
                                *options, str(tmp/'test.c'), '-o', str(exe)], check=True)
                print('diagnostic_trace=' + str(trace), flush=True)
                subprocess.run([str(exe)], check=True)
                invalid = subprocess.run([str(exe), '--invalid-free'], capture_output=True, text=True)
                assert invalid.returncode == -signal.SIGABRT, invalid.stderr
                if trace:
                    assert invalid.stdout.count('PERF TCP_POOL:') == 3, invalid.stdout
                    assert 'action=invalid-free slot=0 state=0 owned=0' in invalid.stdout
                print('invalid free asserted; bounded history checked' if trace else 'invalid free asserted', flush=True)
