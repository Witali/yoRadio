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



typedef struct adaptive_input adaptive_input_t;
typedef struct {
    size_t packet_capacity;
    unsigned resident, minimum, target, occupied;
    unsigned released;
} adaptive_input_stats_t;

// One producer, one consumer. Each acquired pointer is a lease: reclaim never
// touches WRITING, READY or READING slots. The object lives until task teardown.
adaptive_input_t *adaptive_input_create(size_t budget, size_t minimum_bytes,
                                        size_t packet_capacity);
void adaptive_input_destroy(adaptive_input_t *input); // Quiescent callers only.
BaseType_t adaptive_input_acquire(adaptive_input_t *input, void **packet,
                                  size_t size, TickType_t timeout);
BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet);
void *adaptive_input_receive(adaptive_input_t *input, size_t *size,
                             TickType_t timeout);
bool adaptive_input_return(adaptive_input_t *input, void *packet);
bool adaptive_input_release_one(adaptive_input_t *input);
// Only the producer calls restore, between connections after old TLS closes.
// Does not change queued data or leases and never waits for consumers.
void adaptive_input_restore(adaptive_input_t *input);
adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input);


// One fixed, aligned allocation slot. NULL means use the normal allocator;
// every returned pointer must be released through tls_large_reserve_free.
void *tls_large_reserve_calloc(size_t bytes);
bool tls_large_reserve_free(void *pointer);
void tls_large_reserve_poll(void);


// Bind once before creating the stream/decoder tasks. Queue lifetime is the
// application's lifetime; this callback never deletes or replaces the queue.
void tls_input_reserve_bind(adaptive_input_t *input);
// Producer only, after closing the previous connection. A permanent TLS
// reserve keeps the queue at its floor; otherwise restore its target capacity.
void tls_input_reserve_prepare_connection(void);
void tls_input_reserve_poll(void);
// Capacity fixtures are checked independently against the linked pinned SDK.
#define MBEDTLS_SSL_IN_CONTENT_LEN 16384
#define MBEDTLS_SSL_PAYLOAD_OVERHEAD 320
#define MBEDTLS_SSL_HEADER_LEN 13
#define MBEDTLS_SSL_IN_BUFFER_LEN (MBEDTLS_SSL_IN_CONTENT_LEN + MBEDTLS_SSL_PAYLOAD_OVERHEAD + MBEDTLS_SSL_HEADER_LEN)
#define SSL_BUF_HEAD_OFFSET_SIZE 8
#define MALLOC_CAP_INTERNAL 1U
#define MALLOC_CAP_8BIT 2U
#define ESP_LOGI(...) ((void)0)
static int64_t esp_timer_get_time(void) { return (int64_t)xTaskGetTickCount() * 1000; }
static void mbedtls_platform_zeroize(void *data, size_t bytes) {
    volatile unsigned char *p = data;
    while (bytes--) *p++ = 0;
}
static size_t fake_largest;
static atomic_uint normal_allocations, normal_releases;
static size_t heap_caps_get_largest_free_block(unsigned caps) {
    assert(caps == (MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
    return fake_largest;
}
void *__real_esp_mbedtls_mem_calloc(size_t count, size_t size) {
    if (!count || !size || size > SIZE_MAX / count || count * size > fake_largest) return NULL;
    atomic_fetch_add(&normal_allocations, 1);
    return calloc(count, size);
}
// Keep the SDK allocator boundary out of the caller's inlining analysis.
// ASan and the allocation balance still reject passing static storage here.
__attribute__((noinline)) void __real_esp_mbedtls_mem_free(void *pointer) {
    if (pointer) atomic_fetch_add(&normal_releases, 1);
    free(pointer);
}


// Match the largest standard RX allocation in the pinned dynamic adapter,
// including its post-handshake static-RX conversion. No record-size reduction.
enum {
#ifdef CONFIG_YORADIO_TLS_RX_ONLY_RESERVE
    TLS_RESERVE_MIN_REQUEST = 1,
#else
    TLS_RESERVE_MIN_REQUEST = MBEDTLS_SSL_IN_CONTENT_LEN,
#endif
    TLS_RESERVE_CAPACITY = SSL_BUF_HEAD_OFFSET_SIZE + MBEDTLS_SSL_IN_BUFFER_LEN +
                          MBEDTLS_SSL_HEADER_LEN + MBEDTLS_SSL_PAYLOAD_OVERHEAD,
};
_Static_assert(MBEDTLS_SSL_IN_CONTENT_LEN == 16384,
               "Reserve qualification requires full TLS record capacity");
static _Alignas(max_align_t) unsigned char s_tls_large_storage[TLS_RESERVE_CAPACITY];
static atomic_bool s_busy;
static atomic_size_t s_used;
static atomic_uint s_allocations, s_releases, s_busy_fallbacks, s_oversize;

void *tls_large_reserve_calloc(size_t bytes) {
    if (bytes < TLS_RESERVE_MIN_REQUEST) return NULL;
    if (bytes > TLS_RESERVE_CAPACITY) {
        atomic_fetch_add(&s_oversize, 1);
        return NULL;
    }
    bool available = false;
    if (!atomic_compare_exchange_strong(&s_busy, &available, true)) {
        atomic_fetch_add(&s_busy_fallbacks, 1);
        return NULL;
    }
    // The successful claim excludes every other allocator caller. Publish the
    // pointer only after calloc's zeroing requirement has been satisfied.
    memset(s_tls_large_storage, 0, bytes);
    atomic_store(&s_used, bytes);
    atomic_fetch_add(&s_allocations, 1);
    return s_tls_large_storage;
}

bool tls_large_reserve_free(void *pointer) {
    if (pointer != s_tls_large_storage) return false;
    assert(atomic_load(&s_busy));
    // Erase before making the slot available. Other TLS contexts may acquire
    // it next; normal malloc/free and DMA allocators never receive this pointer.
    mbedtls_platform_zeroize(s_tls_large_storage, atomic_load(&s_used));
    atomic_store(&s_used, 0);
    atomic_fetch_add(&s_releases, 1);
    atomic_store(&s_busy, false);
    return true;
}

void tls_large_reserve_poll(void) {
    // One decoder-task caller; no logging or timer queries in calloc/free.
    enum { LOG_INTERVAL_US = 5000000 };
    static unsigned reported_allocations, reported_releases;
    static int64_t reported_at;
    unsigned allocations = atomic_load(&s_allocations);
    unsigned releases = atomic_load(&s_releases);
    if (allocations == reported_allocations && releases == reported_releases) return;
    int64_t now = esp_timer_get_time();
    if (reported_at && now - reported_at < LOG_INTERVAL_US) return;
    reported_at = now;
    reported_allocations = allocations;
    reported_releases = releases;
    ESP_LOGI("tls_reserve", "TLS_RESERVE capacity=%u minimum=%u allocations=%u "
             "releases=%u busy_fallbacks=%u oversize=%u busy=%u used=%u",
             (unsigned)TLS_RESERVE_CAPACITY, (unsigned)TLS_RESERVE_MIN_REQUEST,
             allocations, releases, atomic_load(&s_busy_fallbacks),
             atomic_load(&s_oversize), (unsigned)atomic_load(&s_busy),
             (unsigned)atomic_load(&s_used));
}


#ifdef CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE
#endif

#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
static _Atomic(adaptive_input_t *) s_input;
static atomic_uint s_reclaimed, s_retries;
static atomic_size_t s_last_request;

void tls_input_reserve_bind(adaptive_input_t *input) {
    atomic_store(&s_input, input);
#ifdef CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE
    tls_input_reserve_prepare_connection();
#endif
}

static bool reclaim_one(adaptive_input_t *input, size_t requested) {
    if (!adaptive_input_release_one(input)) return false;
    atomic_store(&s_last_request, requested);
    atomic_fetch_add(&s_reclaimed, 1);
    return true;
}

void tls_input_reserve_prepare_connection(void) {
    adaptive_input_t *input = atomic_load(&s_input);
#ifdef CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE
    // The static TLS slot consumes RAM even for HTTP and small TLS records.
    // Fund it before input slots fill; later allocation hooks cannot reclaim
    // producer/decoder leases or queued bytes. request=0 denotes this policy,
    // rather than an allocation failure. Never regrow while the reserve exists.
    while (reclaim_one(input, 0)) {}
#else
    adaptive_input_restore(input);
#endif
}
#else
static bool reclaim_one(adaptive_input_t *input, size_t requested) {
    (void)input;
    (void)requested;
    return false;
}
#endif

void *__real_esp_mbedtls_mem_calloc(size_t count, size_t size);

static void *allocate(size_t count, size_t size) {
#if defined(CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE) && !defined(CONFIG_YORADIO_TLS_RX_ONLY_RESERVE)
    void *reserved = tls_large_reserve_calloc(count * size);
    if (reserved) return reserved;
#endif
    return __real_esp_mbedtls_mem_calloc(count, size);
}

void *__wrap_esp_mbedtls_mem_calloc(size_t count, size_t size) {
    // Retain the SDK's overflow/zero semantics; malformed requests must not
    // evict audio storage. No bytes already queued for decoding are discarded.
    if (!count || !size || size > SIZE_MAX / count)
        return __real_esp_mbedtls_mem_calloc(count, size);
    size_t requested = count * size;
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    adaptive_input_t *input = atomic_load(&s_input);
#else
    adaptive_input_t *input = NULL;
#endif
    const unsigned caps = MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT;
    // Prefer reclaiming before the allocator reports failure. Largest-block
    // observation is advisory: another task can allocate before our call.
    while (heap_caps_get_largest_free_block(caps) < requested &&
           reclaim_one(input, requested)) {}
    void *result = allocate(count, size);
    while (!result && reclaim_one(input, requested)) {
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
        atomic_fetch_add(&s_retries, 1);
#endif
        result = allocate(count, size);
    }
    return result;
}

#ifdef CONFIG_YORADIO_TLS_RX_ONLY_RESERVE
void *yoradio_tls_rx_calloc(size_t count, size_t size) {
    if (!count || !size || size > SIZE_MAX / count)
        return __real_esp_mbedtls_mem_calloc(count, size);
    // Only the four audited RX call sites use this entry point. Do not tag
    // allocations by size or temporarily swap a process-wide allocator hook.
    void *reserved = tls_large_reserve_calloc(count * size);
    if (reserved) return reserved;
    return __wrap_esp_mbedtls_mem_calloc(count, size);
}
#endif

void tls_input_reserve_poll(void) {
#ifdef CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE
    tls_large_reserve_poll();
#endif
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    // One decoder-task caller. Keep logging outside allocation/queue locks.
    static unsigned reported;
    unsigned reclaimed = atomic_load(&s_reclaimed);
    if (reclaimed == reported) return;
    reported = reclaimed;
    adaptive_input_stats_t stats = adaptive_input_stats(atomic_load(&s_input));
    ESP_LOGI("tls_input", "TLS_INPUT released=%u retries=%u request=%u "
             "resident=%u minimum=%u target=%u occupied=%u capacity=%u",
             reclaimed, atomic_load(&s_retries),
             (unsigned)atomic_load(&s_last_request), stats.resident,
             stats.minimum, stats.target, stats.occupied,
             (unsigned)(stats.resident * stats.packet_capacity));
#endif
}

#ifdef CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE
void __real_esp_mbedtls_mem_free(void *pointer);
void __wrap_esp_mbedtls_mem_free(void *pointer) {
    if (!tls_large_reserve_free(pointer)) __real_esp_mbedtls_mem_free(pointer);
}
#endif


#ifdef CONFIG_YORADIO_TLS_RX_ONLY_RESERVE
#define test_tls_calloc yoradio_tls_rx_calloc
#else
#define test_tls_calloc __wrap_esp_mbedtls_mem_calloc
#endif

static void assert_zero(void *p, size_t size) {
    for (size_t i = 0; i < size; ++i) assert(((unsigned char *)p)[i] == 0);
}

static void *concurrent_client(void *argument) {
    unsigned char pattern = (unsigned char)(uintptr_t)argument;
    for (unsigned n = 0; n < 2000; ++n) {
        size_t size = 16749;
#ifdef CONFIG_YORADIO_TLS_RX_ONLY_RESERVE
        const size_t rx_sizes[] = {24, 1024, 16749};
        size = rx_sizes[n % 3];
#endif
        unsigned char *p = test_tls_calloc(1, size);
        assert(p && (uintptr_t)p % alignof(max_align_t) == 0);
        assert_zero(p, size);
        memset(p, pattern, size);
        for (unsigned i = 0; i < size; ++i) assert(p[i] == pattern);
        __wrap_esp_mbedtls_mem_free(p);
    }
    return NULL;
}

int main(void) {
    assert(TLS_RESERVE_CAPACITY == 17058);
    assert(!tls_large_reserve_calloc(0));
#ifndef CONFIG_YORADIO_TLS_RX_ONLY_RESERVE
    assert(!tls_large_reserve_calloc(16383));
#endif
    assert(!tls_large_reserve_calloc(TLS_RESERVE_CAPACITY + 1));
    assert(!tls_large_reserve_free(NULL));
    fake_largest = 200000;
    unsigned char *p = test_tls_calloc(1, TLS_RESERVE_CAPACITY);
    assert(p == s_tls_large_storage);
    assert((uintptr_t)p % alignof(max_align_t) == 0);
    assert_zero(p, TLS_RESERVE_CAPACITY);
    memset(p, 0xA5, TLS_RESERVE_CAPACITY);
    // A second context gets ordinary heap, without changing the live slot.
    unsigned char *second = test_tls_calloc(1, 16749);
    assert(second && second != p);
    assert_zero(second, 16749);
    memset(second, 0x37, 16749);
    for (unsigned i = 0; i < TLS_RESERVE_CAPACITY; ++i) assert(p[i] == 0xA5);
    __wrap_esp_mbedtls_mem_free(second);
    __wrap_esp_mbedtls_mem_free(p);
    assert_zero(p, TLS_RESERVE_CAPACITY);
    assert(!atomic_load(&s_busy));
    // Small and oversize allocations retain their normal allocation/free pair.
    p = __wrap_esp_mbedtls_mem_calloc(1, 1000);
    assert(p && p != s_tls_large_storage);
    __wrap_esp_mbedtls_mem_free(p);
    p = test_tls_calloc(1, TLS_RESERVE_CAPACITY + 1);
    assert(p && p != s_tls_large_storage);
    __wrap_esp_mbedtls_mem_free(p);
    assert(!test_tls_calloc(SIZE_MAX, 2));
    assert(!test_tls_calloc(0, 16749));
    __wrap_esp_mbedtls_mem_free(NULL);
#ifdef CONFIG_YORADIO_TLS_RX_ONLY_RESERVE
    // Non-RX allocations cannot occupy the slot, even when equally large.
    p = __wrap_esp_mbedtls_mem_calloc(1, 16749);
    assert(p && p != s_tls_large_storage && !atomic_load(&s_busy));
    __wrap_esp_mbedtls_mem_free(p);
    // Record/cache/growing-record lifetimes reuse one block with zeroed data.
    const size_t sizes[] = {24, 1024, 16749, 24, TLS_RESERVE_CAPACITY, 24};
    for (unsigned i = 0; i < sizeof(sizes) / sizeof(sizes[0]); ++i) {
        p = test_tls_calloc(1, sizes[i]);
        assert(p == s_tls_large_storage);
        assert_zero(p, sizes[i]);
        memset(p, 0x5a, sizes[i]);
        __wrap_esp_mbedtls_mem_free(p);
        assert_zero(p, TLS_RESERVE_CAPACITY);
    }
#endif
    // A completely fragmented normal heap still serves one full TLS request.
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    adaptive_input_t *q = adaptive_input_create(16000, 8000, 2060);
    assert(q);
    tls_input_reserve_bind(q);
    // A permanent reservation is funded before streaming, even if the heap
    // could currently satisfy TLS. Preparing another connection never regrows.
    adaptive_input_stats_t initial = adaptive_input_stats(q);
    assert(initial.resident == 4 && initial.target == 8 && initial.released == 4);
    assert(atomic_load(&s_last_request) == 0);
    void *packets[4];
    for (unsigned i = 0; i < 4; ++i) {
        assert(adaptive_input_acquire(q, &packets[i], 4, 0));
        memcpy(packets[i], &i, 4);
        assert(adaptive_input_commit(q, packets[i]));
    }
    size_t packet_size;
    assert(adaptive_input_receive(q, &packet_size, 0) == packets[0]);
    tls_input_reserve_prepare_connection();
    initial = adaptive_input_stats(q);
    assert(initial.resident == 4 && initial.occupied == 4 && initial.released == 4);
    for (unsigned i = 0; i < 4; ++i) {
        if (i) assert(adaptive_input_receive(q, &packet_size, 0) == packets[i]);
        unsigned actual;
        memcpy(&actual, packets[i], 4);
        assert(packet_size == 4 && actual == i);
        assert(adaptive_input_return(q, packets[i]));
    }
    tls_input_reserve_prepare_connection();
    assert(adaptive_input_stats(q).resident == 4);
#endif
    fake_largest = 0;
    unsigned calls_before = atomic_load(&normal_allocations);
    p = test_tls_calloc(1, 16749);
    assert(p == s_tls_large_storage && atomic_load(&normal_allocations) == calls_before);
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    adaptive_input_stats_t stats = adaptive_input_stats(q);
    assert(stats.released == 4 && stats.resident == 4 && stats.minimum == 4);
#endif
    // If both the reserve and normal heap are exhausted, propagate NULL safely.
    assert(!test_tls_calloc(1, 16749));
    __wrap_esp_mbedtls_mem_free(p);
    p = test_tls_calloc(1, 16749);
    assert(p == s_tls_large_storage);
    __wrap_esp_mbedtls_mem_free(p);
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    tls_input_reserve_bind(NULL);
    adaptive_input_destroy(q);
    assert(!atomic_load(&live_allocations));
#endif
    fake_largest = 200000;
    pthread_t clients[4];
    for (uintptr_t i = 0; i < 4; ++i)
        assert(!pthread_create(&clients[i], NULL, concurrent_client, (void *)(i + 1)));
    for (unsigned i = 0; i < 4; ++i) assert(!pthread_join(clients[i], NULL));
    assert(!atomic_load(&s_busy) && !atomic_load(&s_used));
    assert(atomic_load(&s_allocations) == atomic_load(&s_releases));
    assert(atomic_load(&normal_allocations) == atomic_load(&normal_releases));
    assert(atomic_load(&s_busy_fallbacks) > 0);
    tls_input_reserve_poll();
    puts("PASS TLS large reserve: calloc/free pairing, zeroing, alignment, fallback, exhaustion, 8000 concurrent allocations");
}
