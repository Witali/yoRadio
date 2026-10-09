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



typedef struct adaptive_input adaptive_input_t;
typedef struct {
    size_t packet_capacity;
    unsigned resident, minimum, target, occupied, limit;
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
// Producer only. Best-effort allocation of one absent slot, up to the current
// limit. Existing leases/queued bytes are untouched; allocation stays unlocked.
bool adaptive_input_restore_one(adaptive_input_t *input);
// Bound resident storage between minimum and configured target. Shrink idle
// slots immediately and leased slots only when the consumer returns them.
// May overlap reclamation/consumer return and a producer allocation in flight.
void adaptive_input_set_limit(adaptive_input_t *input, unsigned slots);
adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input);


// Bind once before creating the stream/decoder tasks. Queue lifetime is the
// application's lifetime; this callback never deletes or replaces the queue.
void tls_input_reserve_bind(adaptive_input_t *input);
// Producer only, after closing the previous connection. A permanent TLS
// reserve starts the queue at its floor; otherwise restore its target capacity.
void tls_input_reserve_prepare_connection(void);
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
// Stream task only. Grow once after the first decoded FLAC frame; shrink
// before disposing the client. Queued/leased blocks retire on consumer return.
void tls_input_reserve_expand_flac(void);
void tls_input_reserve_finish_connection(void);
#endif
void tls_input_reserve_poll(void);

#define calloc checked_calloc
#define malloc checked_malloc
#define free checked_free


enum { INPUT_MAX_SLOTS = 16, NO_SLOT = INPUT_MAX_SLOTS };
typedef enum { ABSENT, ALLOCATING, IDLE, WRITING, READY, READING } slot_state_t;
typedef struct {
    void *data;
    size_t size;
    slot_state_t state;
    unsigned next;
} input_slot_t;

struct adaptive_input {
    portMUX_TYPE lock;
    SemaphoreHandle_t data_ready, space_ready;
    size_t packet_capacity;
    unsigned target, minimum, resident, released, limit;
    unsigned head, tail;
    input_slot_t slots[INPUT_MAX_SLOTS];
};

adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input) {
    adaptive_input_stats_t result = {0};
    if (!input) return result;
    portENTER_CRITICAL(&input->lock);
    result.packet_capacity = input->packet_capacity;
    result.resident = input->resident;
    result.minimum = input->minimum;
    result.target = input->target;
    result.limit = input->limit;
    result.released = input->released;
    for (unsigned i = 0; i < input->target; ++i) {
        slot_state_t state = input->slots[i].state;
        if (state == WRITING || state == READY || state == READING)
            ++result.occupied;
    }
    portEXIT_CRITICAL(&input->lock);
    return result;
}

bool adaptive_input_restore_one(adaptive_input_t *input) {
    if (!input) return false;
    for (unsigned i = 0; i < input->target; ++i) {
        portENTER_CRITICAL(&input->lock);
        bool allocate = input->resident < input->limit &&
                        input->slots[i].state == ABSENT;
        if (allocate) input->slots[i].state = ALLOCATING;
        portEXIT_CRITICAL(&input->lock);
        if (!allocate) continue;
        void *data = malloc(input->packet_capacity);
        portENTER_CRITICAL(&input->lock);
        // The policy can shrink while malloc runs. Never publish a new slot
        // beyond that limit, even if allocation itself succeeded.
        bool publish = data && input->resident < input->limit;
        input->slots[i].data = publish ? data : NULL;
        input->slots[i].state = publish ? IDLE : ABSENT;
        if (publish) ++input->resident;
        portEXIT_CRITICAL(&input->lock);
        if (publish) xSemaphoreGive(input->space_ready);
        else free(data);
        return publish;
    }
    return false;
}

void adaptive_input_restore(adaptive_input_t *input) {
    if (!input) return;
    // Bound work even if TLS keeps reclaiming slots during this refill.
    for (unsigned attempt = 0; attempt < input->target; ++attempt) {
        if (!adaptive_input_restore_one(input)) break;
    }
}

void adaptive_input_set_limit(adaptive_input_t *input, unsigned slots) {
    if (!input) return;
    portENTER_CRITICAL(&input->lock);
    if (slots < input->minimum) slots = input->minimum;
    if (slots > input->target) slots = input->target;
    input->limit = slots;
    portEXIT_CRITICAL(&input->lock);
    for (unsigned i = input->target; i > 0; --i) {
        void *data = NULL;
        portENTER_CRITICAL(&input->lock);
        input_slot_t *slot = &input->slots[i - 1];
        if (input->resident > input->limit && slot->state == IDLE) {
            data = slot->data;
            slot->data = NULL;
            slot->state = ABSENT;
            --input->resident;
            ++input->released;
        }
        portEXIT_CRITICAL(&input->lock);
        free(data);
    }
}

adaptive_input_t *adaptive_input_create(size_t budget, size_t minimum_bytes,
                                        size_t packet_capacity) {
    if (!packet_capacity) return NULL;
    // Round up so the legacy 8000-byte setting still provides at least that
    // much allocated packet storage; never silently lower the configured floor.
    size_t target = budget / packet_capacity + (budget % packet_capacity != 0);
    if (target < 2 || target > INPUT_MAX_SLOTS) return NULL;
    adaptive_input_t *input = calloc(1, sizeof(*input));
    if (!input) return NULL;
    input->lock = (portMUX_TYPE)portMUX_INITIALIZER_UNLOCKED;
    input->packet_capacity = packet_capacity;
    input->target = (unsigned)target;
    input->limit = input->target;
    // Round the minimum up, without overflowing on a malformed size argument.
    size_t minimum = minimum_bytes / packet_capacity +
                     (minimum_bytes % packet_capacity != 0);
    if (minimum < 2) minimum = 2;
    if (minimum > input->target) minimum = input->target;
    input->minimum = (unsigned)minimum;
    input->head = input->tail = NO_SLOT;
    input->data_ready = xSemaphoreCreateBinary();
    input->space_ready = xSemaphoreCreateBinary();
    if (!input->data_ready || !input->space_ready) {
        adaptive_input_destroy(input);
        return NULL;
    }
    adaptive_input_restore(input);
    if (input->resident < input->minimum) {
        adaptive_input_destroy(input);
        return NULL;
    }
    return input;
}

void adaptive_input_destroy(adaptive_input_t *input) {
    if (!input) return;
    for (unsigned i = 0; i < input->target; ++i) free(input->slots[i].data);
    if (input->data_ready) vSemaphoreDelete(input->data_ready);
    if (input->space_ready) vSemaphoreDelete(input->space_ready);
    free(input);
}

static bool wait_event(SemaphoreHandle_t event, TickType_t start,
                        TickType_t timeout) {
    TickType_t elapsed = xTaskGetTickCount() - start;
    if (timeout != portMAX_DELAY && elapsed >= timeout) return false;
    TickType_t remaining = timeout == portMAX_DELAY ? timeout : timeout - elapsed;
    return xSemaphoreTake(event, remaining) == pdTRUE;
}

BaseType_t adaptive_input_acquire(adaptive_input_t *input, void **packet,
                                  size_t size, TickType_t timeout) {
    if (packet) *packet = NULL;
    if (!input || !packet || !size || size > input->packet_capacity) return pdFALSE;
    TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&input->lock);
        for (unsigned i = 0; i < input->target; ++i) {
            input_slot_t *slot = &input->slots[i];
            if (slot->state != IDLE) continue;
            slot->state = WRITING;
            slot->size = size;
            *packet = slot->data;
            portEXIT_CRITICAL(&input->lock);
            return pdTRUE;
        }
        portEXIT_CRITICAL(&input->lock);
    } while (wait_event(input->space_ready, start, timeout));
    return pdFALSE;
}

BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet) {
    if (!input || !packet) return pdFALSE;
    portENTER_CRITICAL(&input->lock);
    for (unsigned i = 0; i < input->target; ++i) {
        input_slot_t *slot = &input->slots[i];
        if (slot->data != packet || slot->state != WRITING) continue;
        slot->state = READY;
        slot->next = NO_SLOT;
        if (input->tail != NO_SLOT) input->slots[input->tail].next = i;
        else input->head = i;
        input->tail = i;
        portEXIT_CRITICAL(&input->lock);
        xSemaphoreGive(input->data_ready);
        return pdTRUE;
    }
    portEXIT_CRITICAL(&input->lock);
    return pdFALSE;
}

void *adaptive_input_receive(adaptive_input_t *input, size_t *size,
                             TickType_t timeout) {
    if (size) *size = 0;
    if (!input || !size) return NULL;
    TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&input->lock);
        if (input->head != NO_SLOT) {
            input_slot_t *slot = &input->slots[input->head];
            input->head = slot->next;
            if (input->head == NO_SLOT) input->tail = NO_SLOT;
            slot->state = READING;
            *size = slot->size;
            void *data = slot->data;
            portEXIT_CRITICAL(&input->lock);
            return data;
        }
        portEXIT_CRITICAL(&input->lock);
    } while (wait_event(input->data_ready, start, timeout));
    return NULL;
}

bool adaptive_input_return(adaptive_input_t *input, void *packet) {
    if (!input || !packet) return false;
    portENTER_CRITICAL(&input->lock);
    for (unsigned i = 0; i < input->target; ++i) {
        input_slot_t *slot = &input->slots[i];
        if (slot->data != packet || slot->state != READING) continue;
        bool release = input->resident > input->limit;
        if (release) {
            slot->data = NULL;
            --input->resident;
            ++input->released;
        }
        slot->state = release ? ABSENT : IDLE;
        slot->size = 0;
        portEXIT_CRITICAL(&input->lock);
        if (release) free(packet);
        xSemaphoreGive(input->space_ready);
        return true;
    }
    portEXIT_CRITICAL(&input->lock);
    return false;
}

bool adaptive_input_release_one(adaptive_input_t *input) {
    if (!input) return false;
    void *data = NULL;
    portENTER_CRITICAL(&input->lock);
    if (input->resident > input->minimum) {
        for (unsigned i = input->target; i > 0; --i) {
            input_slot_t *slot = &input->slots[i - 1];
            if (slot->state != IDLE) continue;
            data = slot->data;
            slot->data = NULL;
            slot->state = ABSENT;
            --input->resident;
            ++input->released;
            break;
        }
    }
    portEXIT_CRITICAL(&input->lock);
    // Never call the heap allocator while holding the queue's spinlock.
    bool released = data != NULL;
    free(data);
    return released;
}

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
    // rather than an allocation failure. Only the explicit post-FLAC policy
    // may later restore slots; the next connection always starts at the floor.
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
    adaptive_input_stats_t stats = adaptive_input_stats(input);
    adaptive_input_set_limit(input, stats.minimum);
#endif
    while (reclaim_one(input, 0)) {}
#else
    adaptive_input_restore(input);
#endif
}
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
enum { FLAC_INPUT_HEAP_HEADROOM = 32 * 1024 };

void tls_input_reserve_expand_flac(void) {
    adaptive_input_t *input = atomic_load(&s_input);
    adaptive_input_stats_t stats = adaptive_input_stats(input);
    if (!input) return;
    adaptive_input_set_limit(input, stats.minimum +
                                    CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS);
    // Single producer; each attempt is bounded. The decoder has already
    // allocated its FLAC frame storage. Another task can still allocate after
    // this snapshot, so the threshold is advisory, never a heap guarantee.
    for (unsigned attempt = 0; attempt < CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS;
         ++attempt) {
        size_t available = heap_caps_get_free_size(MALLOC_CAP_INTERNAL |
                                                    MALLOC_CAP_8BIT);
        if (available < FLAC_INPUT_HEAP_HEADROOM ||
            stats.packet_capacity > available - FLAC_INPUT_HEAP_HEADROOM ||
            !adaptive_input_restore_one(input)) break;
    }
    stats = adaptive_input_stats(input);
    ESP_LOGI("tls_input", "PERF FLAC_INPUT: resident=%u minimum=%u limit=%u "
             "target=%u capacity=%u", stats.resident, stats.minimum, stats.limit,
             stats.target, (unsigned)(stats.resident * stats.packet_capacity));
}

void tls_input_reserve_finish_connection(void) {
    adaptive_input_t *input = atomic_load(&s_input);
    adaptive_input_stats_t stats = adaptive_input_stats(input);
    adaptive_input_set_limit(input, stats.minimum);
}
#endif
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

static void test_retained_baseline(void) {
    // Extra buffers may still carry queued/leased data when a stream closes.
    // Keep the original floor buffers; retire the extras as their leases end.
    for (unsigned pressure = 0; pressure < 2; ++pressure) {
        adaptive_input_t *q = adaptive_input_create(16000, 8000, PACKET_CAPACITY);
        assert(q);
        adaptive_input_set_limit(q, 4);
        void *baseline[4];
        for (unsigned i = 0; i < 4; ++i) baseline[i] = q->slots[i].data;
        adaptive_input_set_limit(q, 8);
        adaptive_input_restore(q);
        void *packets[8];
        for (unsigned i = 0; i < 8; ++i) {
            assert(adaptive_input_acquire(q, &packets[i], 4, 0));
            memcpy(packets[i], &i, 4);
            if (i != 7) assert(adaptive_input_commit(q, packets[i]));
        }
        size_t size;
        for (unsigned i = 0; i < 4; ++i) {
            void *p = adaptive_input_receive(q, &size, 0);
            assert(p == baseline[i] && size == 4);
            assert(adaptive_input_return(q, p));
        }
        void *reading = adaptive_input_receive(q, &size, 0);
        assert(reading == packets[4]);
        if (pressure) {
            // Real allocation pressure may reclaim any idle buffer while
            // preserving the count floor. The resulting holes are valid.
            for (unsigned i = 0; i < 4; ++i) assert(adaptive_input_release_one(q));
            assert(!adaptive_input_release_one(q));
        }
        adaptive_input_set_limit(q, 4);
        assert(adaptive_input_stats(q).resident == (pressure ? 4 : 8));
        for (unsigned i = 0; i < 4; ++i)
            assert(q->slots[i].data == (pressure ? NULL : baseline[i]));
        assert(adaptive_input_commit(q, packets[7]));
        for (unsigned i = 4; i < 8; ++i) {
            void *p = i == 4 ? reading : adaptive_input_receive(q, &size, 0);
            unsigned value;
            memcpy(&value, p, 4);
            assert(value == i && size == 4);
            assert(adaptive_input_return(q, p));
            assert(adaptive_input_stats(q).resident == (pressure ? 4 : 11 - i));
        }
        assert(adaptive_input_stats(q).resident == 4);
        for (unsigned i = 0; i < 4; ++i)
            assert(q->slots[i].data == (pressure ? NULL : baseline[i]));
        cleanup(q);
    }
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
    test_retained_baseline();
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
