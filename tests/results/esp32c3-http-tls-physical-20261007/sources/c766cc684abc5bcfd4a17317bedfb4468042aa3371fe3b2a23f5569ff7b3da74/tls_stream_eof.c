#include "mbedtls/ssl.h"

int __real_mbedtls_ssl_read(mbedtls_ssl_context *ssl, unsigned char *buffer,
                            size_t length);

int __wrap_mbedtls_ssl_read(mbedtls_ssl_context *ssl, unsigned char *buffer,
                            size_t length) {
    int result = __real_mbedtls_ssl_read(ssl, buffer, length);
    // mbedTLS documents zero as transport EOF without close_notify. ESP-TLS
    // otherwise collapses it with PEER_CLOSE_NOTIFY before HTTP sees it.
    // Preserve that distinction: an unframed HTTPS body needs a closure alert
    // to be complete (RFC 9112 section 9.8). Explicit HTTP framing still ends
    // at its boundary without an additional TLS read. Keep zero-length calls
    // unchanged, and pass through data, alerts and retryable/error codes.
    return result == 0 && length != 0 ? MBEDTLS_ERR_SSL_CONN_EOF : result;
}
