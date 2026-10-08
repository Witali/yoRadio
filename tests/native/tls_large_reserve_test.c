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
/* PRODUCTION_POOL */
/* PRODUCTION_WRAPPER */

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
