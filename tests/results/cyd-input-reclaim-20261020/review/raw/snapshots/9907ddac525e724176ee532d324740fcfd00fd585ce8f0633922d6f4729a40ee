#include "tls_stream_result.h"

int yoradio_mbedtls_ssl_read(mbedtls_ssl_context *ssl, unsigned char *buffer,
                             size_t length) {
    // Only ESP-TLS's caller is redirected here. Keep the SDK's dynamic-buffer
    // --wrap=mbedtls_ssl_read adapter in the chain when it is enabled.
    return tls_stream_result(mbedtls_ssl_read(ssl, buffer, length), length);
}
