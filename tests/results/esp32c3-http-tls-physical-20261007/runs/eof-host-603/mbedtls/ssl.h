#pragma once
#include <stddef.h>
#include "esp_tls_errors.h"
typedef int mbedtls_ssl_context;
int __wrap_mbedtls_ssl_read(mbedtls_ssl_context *, unsigned char *, size_t);
