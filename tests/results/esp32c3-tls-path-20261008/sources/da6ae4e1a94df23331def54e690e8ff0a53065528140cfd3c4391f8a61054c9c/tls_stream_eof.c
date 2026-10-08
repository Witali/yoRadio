#include "mbedtls/ssl.h"
#include <stdbool.h>
#include "tls_path_profile.h"

int yoradio_mbedtls_ssl_read(mbedtls_ssl_context *ssl, unsigned char *buffer,
                             size_t length) {
    // Keep ESP-IDF's existing --wrap=mbedtls_ssl_read dynamic-buffer adapter.
    // Only the ESP-TLS caller is redirected here; this call still traverses
    // the SDK wrapper when dynamic TLS buffers are enabled.
    int64_t start = tls_path_profile_begin();
    int result = mbedtls_ssl_read(ssl, buffer, length);
#ifdef CONFIG_YORADIO_TLS_PATH_PROFILE
    bool retry = result == MBEDTLS_ERR_SSL_WANT_READ ||
                 result == MBEDTLS_ERR_SSL_WANT_WRITE || result == MBEDTLS_ERR_SSL_TIMEOUT;
    tls_path_profile_end(TLS_PATH_TLS_READ, start, length, result > 0 ? (size_t)result : 0,
        result > 0 ? TLS_PATH_OK : result == 0 ? TLS_PATH_ZERO : retry ? TLS_PATH_RETRY : TLS_PATH_ERROR);
#else
    (void)start;
#endif
    // mbedTLS documents zero as transport EOF without close_notify. ESP-TLS
    // otherwise collapses it with PEER_CLOSE_NOTIFY before HTTP sees it.
    // Preserve that distinction: an unframed HTTPS body needs a closure alert
    // to be complete (RFC 9112 section 9.8). Explicit HTTP framing still ends
    // at its boundary without an additional TLS read. Keep zero-length calls
    // unchanged, and pass through data, alerts and retryable/error codes.
    return result == 0 && length != 0 ? MBEDTLS_ERR_SSL_CONN_EOF : result;
}
