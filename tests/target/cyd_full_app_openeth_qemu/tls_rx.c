#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "mbedtls/ssl.h"

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
    return buffer;
}

void __wrap_yoradio_tls_static_rx_free(void *buffer) {
    bool reserved = is_reserved(buffer);
    __real_yoradio_tls_static_rx_free(buffer);
    if (reserved) puts("CYD_OPENETH_TLS_RX return");
}

void __wrap_yoradio_tls_static_rx_zeroize_free(void *buffer, size_t bytes) {
    bool reserved = is_reserved(buffer);
    __real_yoradio_tls_static_rx_zeroize_free(buffer, bytes);
    if (reserved) puts("CYD_OPENETH_TLS_RX return");
}
