#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "mbedtls/ssl.h"

#ifdef CYD_OPENETH_TLS_OVERLAP_PROBE
#include <inttypes.h>
#include <stdatomic.h>
#include "esp_timer.h"
#include "esp_tls.h"
static atomic_uint s_heap_rx;

unsigned cyd_openeth_heap_rx_owners(void) {
    return atomic_load(&s_heap_rx);
}

static void heap_rx_returned(bool borrowed) {
    if (!borrowed) return;
    atomic_fetch_sub(&s_heap_rx, 1);
    puts("CYD_OPENETH_TLS_HEAP_RX return");
}

esp_err_t __real_esp_tls_server_session_init(esp_tls_cfg_server_t *, int, esp_tls_t *);
esp_err_t __wrap_esp_tls_server_session_init(esp_tls_cfg_server_t *config, int socket, esp_tls_t *tls) {
    int64_t start = esp_timer_get_time();
    esp_err_t result = __real_esp_tls_server_session_init(config, socket, tls);
    printf("CYD_OPENETH_HTTPS init=%d elapsed_us=%" PRId64 "\n",
           (int)result, esp_timer_get_time() - start);
    return result;
}

int __real_esp_tls_server_session_continue_async(esp_tls_t *);
int __wrap_esp_tls_server_session_continue_async(esp_tls_t *tls) {
    int64_t start = esp_timer_get_time();
    int result = __real_esp_tls_server_session_continue_async(tls);
    printf("CYD_OPENETH_HTTPS step=%d elapsed_us=%" PRId64 "\n",
           result, esp_timer_get_time() - start);
    return result;
}
#endif

extern const char _bss_start[], _bss_end[];

void *__real_yoradio_tls_static_rx_calloc(const mbedtls_ssl_config *, size_t, size_t);
void __real_yoradio_tls_static_rx_free(void *);
void __real_yoradio_tls_static_rx_zeroize_free(void *, size_t);

static bool is_reserved(const void *buffer) {
    // The reserve is in application BSS. Heap fallback comes from outside it.
    uintptr_t address = (uintptr_t)buffer;
    return address >= (uintptr_t)_bss_start && address < (uintptr_t)_bss_end;
}

void *__wrap_yoradio_tls_static_rx_calloc(const mbedtls_ssl_config *config,
                                       size_t count, size_t bytes) {
    void *buffer = __real_yoradio_tls_static_rx_calloc(config, count, bytes);
    if (is_reserved(buffer)) puts("CYD_OPENETH_TLS_RX loan");
#ifdef CYD_OPENETH_TLS_OVERLAP_PROBE
    else if (buffer) {
        atomic_fetch_add(&s_heap_rx, 1);
        puts("CYD_OPENETH_TLS_HEAP_RX loan");
    }
#endif
    return buffer;
}

void __wrap_yoradio_tls_static_rx_free(void *buffer) {
    bool reserved = is_reserved(buffer);
#ifdef CYD_OPENETH_TLS_OVERLAP_PROBE
    bool borrowed = buffer && !reserved;
#endif
    __real_yoradio_tls_static_rx_free(buffer);
    if (reserved) puts("CYD_OPENETH_TLS_RX return");
#ifdef CYD_OPENETH_TLS_OVERLAP_PROBE
    heap_rx_returned(borrowed);
#endif
}

void __wrap_yoradio_tls_static_rx_zeroize_free(void *buffer, size_t bytes) {
    bool reserved = is_reserved(buffer);
#ifdef CYD_OPENETH_TLS_OVERLAP_PROBE
    bool borrowed = buffer && !reserved;
#endif
    __real_yoradio_tls_static_rx_zeroize_free(buffer, bytes);
    if (reserved) puts("CYD_OPENETH_TLS_RX return");
#ifdef CYD_OPENETH_TLS_OVERLAP_PROBE
    heap_rx_returned(borrowed);
#endif
}
