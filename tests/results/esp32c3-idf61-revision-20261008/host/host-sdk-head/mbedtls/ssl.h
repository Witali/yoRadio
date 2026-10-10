#pragma once
#include <stddef.h>
#include "esp_tls_errors.h"
typedef int mbedtls_ssl_context;
int mbedtls_ssl_read(mbedtls_ssl_context *, unsigned char *, size_t);
int yoradio_mbedtls_ssl_read(mbedtls_ssl_context *, unsigned char *, size_t);
