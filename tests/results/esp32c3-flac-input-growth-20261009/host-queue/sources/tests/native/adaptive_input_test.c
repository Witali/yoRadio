#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdalign.h>
#include <stddef.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef int BaseType_t;
typedef uint32_t TickType_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(pthread_mutex_lock(p) == 0)
#define portEXIT_CRITICAL(p) assert(pthread_mutex_unlock(p) == 0)
#define pdTRUE 1
#define pdFALSE 0
#define portMAX_DELAY UINT32_MAX
typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t condition;
    bool signalled;
} *SemaphoreHandle_t;
static atomic_int fail_after = -1;
static atomic_uint live_allocations, slot_frees;
static void (*after_allocation)(void);
typedef union { max_align_t alignment; size_t size; } allocation_header_t;
static void *checked_calloc(size_t count, size_t size) {
    if (size && count > SIZE_MAX / size) return NULL;
    int remaining = atomic_load(&fail_after);
    if (remaining == 0) return NULL;
    if (remaining > 0) atomic_fetch_sub(&fail_after, 1);
    size_t bytes = count * size;
    if (bytes > SIZE_MAX - sizeof(allocation_header_t)) return NULL;
    allocation_header_t *header = calloc(1, sizeof(*header) + bytes);
    if (!header) return NULL;
    header->size = bytes;
    atomic_fetch_add(&live_allocations, 1);
    if (after_allocation) {
        void (*hook)(void) = after_allocation;
        after_allocation = NULL;
        hook();
    }
    return header + 1;
}
static void *checked_malloc(size_t bytes) { return checked_calloc(1, bytes); }
static void checked_free(void *pointer) {
    if (!pointer) return;
    allocation_header_t *header = (allocation_header_t *)pointer - 1;
    if (header->size == 2060) atomic_fetch_add(&slot_frees, 1);
    atomic_fetch_sub(&live_allocations, 1);
    free(header);
}
static SemaphoreHandle_t xSemaphoreCreateBinary(void) {
    SemaphoreHandle_t s = checked_calloc(1, sizeof(*s));
    if (!s) return NULL;
    assert(!pthread_mutex_init(&s->mutex, NULL));
    assert(!pthread_cond_init(&s->condition, NULL));
    return s;
}
static void vSemaphoreDelete(SemaphoreHandle_t s) {
    assert(!pthread_cond_destroy(&s->condition));
    assert(!pthread_mutex_destroy(&s->mutex));
    checked_free(s);
}
static BaseType_t xSemaphoreGive(SemaphoreHandle_t s) {
    assert(!pthread_mutex_lock(&s->mutex));
    s->signalled = true;
    assert(!pthread_cond_signal(&s->condition));
    assert(!pthread_mutex_unlock(&s->mutex));
    return pdTRUE;
}
static BaseType_t xSemaphoreTake(SemaphoreHandle_t s, TickType_t timeout) {
    struct timespec until;
    assert(!clock_gettime(CLOCK_REALTIME, &until));
    until.tv_sec += timeout / 1000;
    until.tv_nsec += (timeout % 1000) * 1000000L;
    if (until.tv_nsec >= 1000000000L) { ++until.tv_sec; until.tv_nsec -= 1000000000L; }
    assert(!pthread_mutex_lock(&s->mutex));
    int error = 0;
    while (!s->signalled && !error) {
        error = timeout == portMAX_DELAY ? pthread_cond_wait(&s->condition, &s->mutex)
            : pthread_cond_timedwait(&s->condition, &s->mutex, &until);
    }
    assert(!error || error == ETIMEDOUT);
    bool ready = s->signalled;
    s->signalled = false;
    assert(!pthread_mutex_unlock(&s->mutex));
    return ready ? pdTRUE : pdFALSE;
}
static uint32_t tick_offset;
static TickType_t xTaskGetTickCount(void) {
    struct timespec now;
    assert(!clock_gettime(CLOCK_MONOTONIC, &now));
    return (TickType_t)((uint64_t)now.tv_sec * 1000 + now.tv_nsec / 1000000) + tick_offset;
}

/* PRODUCTION_HEADER */
#define calloc checked_calloc
#define malloc checked_malloc
#define free checked_free
/* PRODUCTION_QUEUE */
#undef calloc
#undef malloc
#undef free

#define MALLOC_CAP_INTERNAL 1U
#define MALLOC_CAP_8BIT 2U
#define ESP_LOGI(...) ((void)0)
static size_t fake_largest;
static unsigned freed_before, allocator_calls;
static bool coalesce, lose_first_allocation;
static size_t heap_caps_get_largest_free_block(unsigned caps) {
    assert(caps == (MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
    return fake_largest + (coalesce ? (atomic_load(&slot_frees) - freed_before) * 2060U : 0U);
}
void *__real_esp_mbedtls_mem_calloc(size_t count, size_t size) {
    ++allocator_calls;
    if (!count || !size || size > SIZE_MAX / count) return NULL;
    if (lose_first_allocation) { lose_first_allocation = false; return NULL; }
    if (count * size > heap_caps_get_largest_free_block(3)) return NULL;
    return calloc(count, size);
}
/* PRODUCTION_TLS */

enum { PACKET_CAPACITY = 2060, STRESS_PACKETS = 30000 };
static adaptive_input_t *queue;
static atomic_bool done;
static void *producer(void *unused) {
    (void)unused;
    for (uint32_t n = 0; n < STRESS_PACKETS; ++n) {
        size_t size = 4 + n % (PACKET_CAPACITY - 3);
        void *p;
        assert(adaptive_input_acquire(queue, &p, size, 5000));
        memcpy(p, &n, sizeof(n));
        memset((uint8_t *)p + 4, (uint8_t)n, size - 4);
        assert(adaptive_input_commit(queue, p));
        if (n % 97 == 0) {
            adaptive_input_set_limit(queue, (n / 97) % 2 ? 4 : 8);
            adaptive_input_restore(queue);
        }
    }
    return NULL;
}
static void *consumer(void *unused) {
    (void)unused;
    for (uint32_t n = 0; n < STRESS_PACKETS; ++n) {
        size_t size;
        void *p = adaptive_input_receive(queue, &size, 5000);
        assert(p && size == 4 + n % (PACKET_CAPACITY - 3));
        uint32_t actual;
        memcpy(&actual, p, sizeof(actual));
        assert(actual == n);
        for (size_t i = 4; i < size; ++i) assert(((uint8_t *)p)[i] == (uint8_t)n);
        assert(adaptive_input_return(queue, p));
    }
    atomic_store(&done, true);
    return NULL;
}
static void *reclaimer(void *unused) {
    (void)unused;
    do {
        adaptive_input_release_one(queue);
        adaptive_input_stats_t s = adaptive_input_stats(queue);
        assert(s.resident >= s.minimum && s.occupied <= s.resident);
        struct timespec delay = {0, 100000};
        nanosleep(&delay, NULL);
    } while (!atomic_load(&done));
    return NULL;
}
static void cleanup(adaptive_input_t *q) {
    tls_input_reserve_bind(NULL);
    adaptive_input_destroy(q);
    assert(atomic_load(&live_allocations) == 0);
}
static void pressure_setup(adaptive_input_t *q, size_t largest, bool merging) {
    tls_input_reserve_bind(q);
    fake_largest = largest;
    freed_before = atomic_load(&slot_frees);
    allocator_calls = 0;
    coalesce = merging;
}

static void shrink_during_allocation(void) {
    adaptive_input_set_limit(queue, 4);
}

static void test_deferred_limit(void) {
    adaptive_input_t *q = adaptive_input_create(16000, 8000, PACKET_CAPACITY);
    assert(q);
    void *packets[6];
    for (unsigned i = 0; i < 6; ++i) {
        assert(adaptive_input_acquire(q, &packets[i], 4, 0));
        memcpy(packets[i], &i, 4);
        if (i != 5) assert(adaptive_input_commit(q, packets[i]));
    }
    size_t size;
    assert(adaptive_input_receive(q, &size, 0) == packets[0]);
    // One READING, four READY, one WRITING: shrink only the two idle slots.
    adaptive_input_set_limit(q, 0);
    adaptive_input_stats_t s = adaptive_input_stats(q);
    assert(s.limit == 4 && s.resident == 6 && s.occupied == 6);
    assert(!adaptive_input_restore_one(q));
    assert(adaptive_input_commit(q, packets[5]));
    for (unsigned i = 0; i < 6; ++i) {
        void *p = i ? adaptive_input_receive(q, &size, 0) : packets[0];
        unsigned value;
        memcpy(&value, p, 4);
        assert(value == i && size == 4);
        assert(adaptive_input_return(q, p));
        assert(adaptive_input_stats(q).resident == (i == 0 ? 5 : 4));
    }
    adaptive_input_restore(q);
    assert(adaptive_input_stats(q).resident == 4);
    adaptive_input_set_limit(q, UINT32_MAX);
    assert(adaptive_input_stats(q).limit == 8);
    atomic_store(&fail_after, 0);
    assert(!adaptive_input_restore_one(q));
    atomic_store(&fail_after, -1);
    assert(adaptive_input_restore_one(q) && adaptive_input_stats(q).resident == 5);
    adaptive_input_restore(q);
    assert(adaptive_input_stats(q).resident == 8);
    cleanup(q);

    // A successful malloc is discarded if a concurrent policy shrinks first.
    queue = adaptive_input_create(16000, 8000, PACKET_CAPACITY);
    adaptive_input_set_limit(queue, 4);
    adaptive_input_set_limit(queue, 8);
    unsigned allocations = atomic_load(&live_allocations);
    after_allocation = shrink_during_allocation;
    assert(!adaptive_input_restore_one(queue));
    assert(adaptive_input_stats(queue).resident == 4);
    assert(atomic_load(&live_allocations) == allocations);
    cleanup(queue);
    queue = NULL;
    adaptive_input_set_limit(NULL, 2);
    assert(!adaptive_input_restore_one(NULL));
}

int main(void) {
    test_deferred_limit();
    assert(!adaptive_input_create(1000, 0, PACKET_CAPACITY));
    assert(!adaptive_input_create(SIZE_MAX, 0, PACKET_CAPACITY));
    assert(!adaptive_input_create(16000, 8000, 0));
    // Allocation failure at every constructor stage: no leaks, usable floor.
    for (int step = 0; step < 12; ++step) {
        atomic_store(&fail_after, step);
        adaptive_input_t *q = adaptive_input_create(16000, 8000, PACKET_CAPACITY);
        if (q) assert(adaptive_input_stats(q).resident >= 4);
        cleanup(q);
    }
    atomic_store(&fail_after, -1);
    adaptive_input_t *q = adaptive_input_create(16000, 8000, PACKET_CAPACITY);
    assert(q);
    adaptive_input_stats_t stats = adaptive_input_stats(q);
    assert(stats.resident == 8 && stats.minimum == 4);
    void *writing, *ready;
    assert(adaptive_input_acquire(q, &writing, 16, 0));
    assert(adaptive_input_acquire(q, &ready, 12, 0));
    memset(writing, 0x51, 16);
    memset(ready, 0x27, 12);
    assert(!adaptive_input_return(q, writing));
    assert(adaptive_input_commit(q, ready));
    assert(!adaptive_input_commit(q, ready));
    size_t size;
    void *reading = adaptive_input_receive(q, &size, 0);
    assert(reading == ready && size == 12);
    for (unsigned i = 0; i < 4; ++i) assert(adaptive_input_release_one(q));
    assert(!adaptive_input_release_one(q));
    for (unsigned i = 0; i < 12; ++i) assert(((uint8_t *)reading)[i] == 0x27);
    assert(adaptive_input_return(q, reading));
    assert(!adaptive_input_return(q, reading));
    assert(adaptive_input_commit(q, writing));
    reading = adaptive_input_receive(q, &size, 0);
    assert(reading == writing && size == 16);
    for (unsigned i = 0; i < 16; ++i) assert(((uint8_t *)reading)[i] == 0x51);
    assert(adaptive_input_return(q, reading));
    // A stale semaphore token must not extend the original timeout; tick wrap.
    tick_offset = UINT32_MAX - xTaskGetTickCount() - 4;
    TickType_t start = xTaskGetTickCount();
    assert(!adaptive_input_receive(q, &size, 20));
    assert((TickType_t)(xTaskGetTickCount() - start) >= 20);
    tick_offset = 0;
    atomic_store(&fail_after, 0);
    adaptive_input_restore(q);
    assert(adaptive_input_stats(q).resident == 4);
    atomic_store(&fail_after, -1);
    adaptive_input_restore(q);
    assert(adaptive_input_stats(q).resident == 8);
    cleanup(q);
    // Fixed floor can be capped by a smaller user target, never under 2 slots.
    q = adaptive_input_create(8000, SIZE_MAX, PACKET_CAPACITY);
    assert(adaptive_input_stats(q).minimum == 4 && !adaptive_input_release_one(q));
    cleanup(q);

    // All queued slots are protected, even when TLS needs memory immediately.
    q = adaptive_input_create(16000, 8000, PACKET_CAPACITY);
    for (unsigned i = 0; i < 8; ++i) {
        void *p;
        assert(adaptive_input_acquire(q, &p, 4, 0));
        memcpy(p, &i, 4);
        assert(adaptive_input_commit(q, p));
    }
    pressure_setup(q, 15360, true);
    assert(!__wrap_esp_mbedtls_mem_calloc(1, 16749));
    assert(adaptive_input_stats(q).resident == 8 && allocator_calls == 1);
    for (unsigned i = 0; i < 8; ++i) {
        unsigned n;
        void *p = adaptive_input_receive(q, &size, 0);
        assert(p && size == 4);
        memcpy(&n, p, 4);
        assert(n == i && adaptive_input_return(q, p));
    }
    // Coalescing free space can satisfy TLS; success data retains calloc zeros.
    pressure_setup(q, 15360, true);
    void *tls = __wrap_esp_mbedtls_mem_calloc(1, 16749);
    assert(tls && allocator_calls == 1 && adaptive_input_stats(q).resident == 7);
    for (unsigned i = 0; i < 16749; ++i) assert(((uint8_t *)tls)[i] == 0);
    free(tls);
    // Raced allocation failure retries only after reclaiming another idle slot.
    pressure_setup(q, 20000, true);
    lose_first_allocation = true;
    tls = __wrap_esp_mbedtls_mem_calloc(1, 16749);
    assert(tls && allocator_calls == 2 && adaptive_input_stats(q).resident == 6);
    free(tls);
    // Scattered frees cannot make a contiguous allocation: stop at the floor.
    pressure_setup(q, 15360, false);
    assert(!__wrap_esp_mbedtls_mem_calloc(1, 16749));
    assert(adaptive_input_stats(q).resident == 4 && allocator_calls == 1);
    tls_input_reserve_prepare_connection();
    assert(adaptive_input_stats(q).resident == 8);
    pressure_setup(q, 0, true);
    assert(!__wrap_esp_mbedtls_mem_calloc(SIZE_MAX, 2));
    assert(!__wrap_esp_mbedtls_mem_calloc(0, 16749));
    assert(adaptive_input_stats(q).resident == 8);
    cleanup(q);
    pressure_setup(NULL, 20000, true);
    tls = __wrap_esp_mbedtls_mem_calloc(1, 16749);
    assert(tls); free(tls);

    queue = adaptive_input_create(16000, 8000, PACKET_CAPACITY);
    pthread_t threads[3];
    assert(!pthread_create(&threads[0], NULL, producer, NULL));
    assert(!pthread_create(&threads[1], NULL, consumer, NULL));
    assert(!pthread_create(&threads[2], NULL, reclaimer, NULL));
    for (unsigned i = 0; i < 3; ++i) assert(!pthread_join(threads[i], NULL));
    assert(adaptive_input_stats(queue).occupied == 0);
    cleanup(queue);
    puts("PASS adaptive input: ownership, FIFO, deferred limit, allocation race/faults, TLS pressure, tick wrap, 30000 concurrent packets");
}
