#pragma once

#include <stddef.h>
#include "mbedtls/ssl.h"

// Preserve transport EOF without close_notify before ESP-TLS folds both into
// zero. An unframed HTTPS body requires a closure alert to be complete. Framed
// HTTP bodies finish at their boundary without needing an extra TLS read.
static inline int tls_stream_result(int result, size_t length) {
    return result == 0 && length != 0 ? MBEDTLS_ERR_SSL_CONN_EOF : result;
}
