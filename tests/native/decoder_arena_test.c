#include "decoder_arena.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
_Thread_local bool test_isr;
void *__real_malloc(size_t n) { return malloc(n); }
void *__real_calloc(size_t n, size_t s) { return calloc(n, s); }
void *__real_realloc(void *p, size_t n) { return realloc(p, n); }
void __real_free(void *p) { free(p); }
size_t __real_heap_caps_get_allocated_size(void *p) { (void)p; return 123; }
void *__wrap_malloc(size_t n);
void *__wrap_calloc(size_t n, size_t s);
void *__wrap_realloc(void *p, size_t n);
void __wrap_free(void *p);
size_t __wrap_heap_caps_get_allocated_size(void *p);

static void verify(const void *p, size_t n, unsigned char v) {
    assert(p && (uintptr_t)p % _Alignof(max_align_t) == 0);
    for (size_t i = 0; i < n; ++i) assert(((const unsigned char *)p)[i] == v);
}
static void *other_task(void *unused) {
    (void)unused;
    void *system = __wrap_malloc(64);
    assert(system && !decoder_arena_owns(system));
    __wrap_free(system);
    assert(!decoder_arena_select(true));
    for (unsigned i = 0; i < 500; ++i) {
        void *p = __wrap_calloc(13, i % 37 + 1);
        assert(decoder_arena_owns(p));
        verify(p, 13 * (i % 37 + 1), 0);
        __wrap_free(p);
    }
    return NULL;
}
int main(void) {
    assert(decoder_arena_init());
    decoder_arena_stats_t empty = decoder_arena_stats();
    assert(empty.live == 0 && empty.blocks == 0 && empty.failures == 0);
    void *system = __wrap_malloc(27);
    assert(system && !decoder_arena_owns(system));
    assert(!decoder_arena_select(true));
    system = __wrap_realloc(system, 61);
    assert(system && !decoder_arena_owns(system));
    __wrap_free(system);
    test_isr = true;
    system = __wrap_malloc(32);
    assert(system && !decoder_arena_owns(system));
    __wrap_free(system);
    test_isr = false;
    assert(__wrap_malloc(0) == NULL);
    assert(__wrap_calloc(SIZE_MAX, 2) == NULL);
    assert(__wrap_malloc(SIZE_MAX) == NULL);
    pthread_t thread;
    assert(!pthread_create(&thread, NULL, other_task, NULL));
    for (unsigned i = 1; i < 600; ++i) {
        size_t n = i % 113 + 1;
        void *p = __wrap_malloc(n);
        void *obstacle = __wrap_malloc(64);
        assert(decoder_arena_owns(p));
        memset(p, 0xa5, n);
        assert(__wrap_heap_caps_get_allocated_size(p) == n);
        void *q = __wrap_realloc(p, 2000 + n);
        verify(q, n, 0xa5);
        memset(q, 0x5a, 2000 + n);
        p = __wrap_realloc(q, n);
        verify(p, n, 0x5a);
        assert(!__wrap_realloc(p, SIZE_MAX));
        verify(p, n, 0x5a);
        assert(decoder_arena_select(false));
        __wrap_free(p); // Ownership wins even outside the decoder task.
        __wrap_free(obstacle);
        assert(!decoder_arena_select(true));
    }
    assert(!pthread_join(thread, NULL));
    void *blocks[256];
    size_t count = 0;
    while (count < 256 && (blocks[count] = __wrap_malloc(1000))) ++count;
    assert(count > 0 && count < 256); // No fallback to the system heap.
    for (size_t i = 0; i < count; i += 2) __wrap_free(blocks[i]);
    for (size_t i = 1; i < count; i += 2) __wrap_free(blocks[i]);
    assert(decoder_arena_init()); // Initialization is idempotent, never resets.
    void *p = __wrap_malloc(60000);
    assert(p && !__wrap_realloc(p, 0));
    decoder_arena_stats_t final = decoder_arena_stats();
    assert(final.live == 0 && final.blocks == 0);
    assert(final.free_bytes == empty.free_bytes && final.largest == empty.largest);
    assert(final.failures == 602);
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
    for (unsigned i = 0; i < ARENA_OPERATIONS; ++i) {
        assert(final.timing[i].calls > 0);
        assert(final.timing[i].max_us == 1); // Synthetic host clock, not latency.
    }
#endif
    printf("PASS: domain isolation, ISR bypass, alignment, realloc, exhaustion, coalescing, concurrent reuse; peak=%zu failures=%u\n", final.peak, final.failures);
}
