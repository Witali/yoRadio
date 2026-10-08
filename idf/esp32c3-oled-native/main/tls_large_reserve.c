#include "tls_large_reserve.h"

#include <assert.h>
#include <stdatomic.h>
#include <stdint.h>
#include <string.h>
#include "esp_mbedtls_dynamic_impl.h"
#include "mbedtls/platform_util.h"
#include "esp_timer.h"

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
