#include "tls_input_reserve.h"

#include <stdint.h>
#include <stdatomic.h>
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE
#include "tls_large_reserve.h"
#endif

#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
static _Atomic(adaptive_input_t *) s_input;
static atomic_uint s_reclaimed, s_retries;
static atomic_size_t s_last_request;
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
adaptive_input_stats_t tls_input_reserve_input_stats(void) {
    return adaptive_input_stats(atomic_load(&s_input));
}
#endif

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
    // rather than an allocation failure. Only explicit post-decoder policies
    // may later restore slots; the next connection always starts at the floor.
#ifdef YORADIO_INPUT_EXPANSION_ENABLED
    adaptive_input_stats_t stats = adaptive_input_stats(input);
    adaptive_input_set_limit(input, stats.minimum);
    // The limit retires busy extras when their leases end. Preserve the
    // original floor buffers here; allocation-pressure reclaim stays enabled
    // in the TLS allocator if memory is actually needed before then.
#else
    while (reclaim_one(input, 0)) {}
#endif
#else
    adaptive_input_restore(input);
#endif
}
#ifdef YORADIO_INPUT_EXPANSION_ENABLED
enum { INPUT_EXPANSION_HEAP_HEADROOM = 32 * 1024 };

static void expand_input(unsigned extra_slots, const char *codec) {
    (void)codec; // Logging may be compiled out in production and host tests.
    adaptive_input_t *input = atomic_load(&s_input);
    adaptive_input_stats_t stats = adaptive_input_stats(input);
    if (!input) return;
    adaptive_input_set_limit(input, stats.minimum + extra_slots);
    // Single producer; each attempt is bounded. The decoder has already
    // allocated its working storage. Another task can still allocate after
    // this snapshot, so the threshold is advisory, never a heap guarantee.
    for (unsigned attempt = 0; attempt < extra_slots;
         ++attempt) {
        size_t available = heap_caps_get_free_size(MALLOC_CAP_INTERNAL |
                                                    MALLOC_CAP_8BIT);
        if (available < INPUT_EXPANSION_HEAP_HEADROOM ||
            stats.packet_capacity > available - INPUT_EXPANSION_HEAP_HEADROOM ||
            !adaptive_input_restore_one(input)) break;
    }
    stats = adaptive_input_stats(input);
    ESP_LOGI("tls_input", "PERF %s_INPUT: resident=%u minimum=%u limit=%u "
             "target=%u capacity=%u", codec, stats.resident, stats.minimum, stats.limit,
             stats.target, (unsigned)(stats.resident * stats.packet_capacity));
}
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
void tls_input_reserve_expand_flac(void) {
    expand_input(CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS, "FLAC");
}
#endif
#if CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS > 0
void tls_input_reserve_expand_aac(void) {
    expand_input(CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS, "AAC");
}
#endif

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
