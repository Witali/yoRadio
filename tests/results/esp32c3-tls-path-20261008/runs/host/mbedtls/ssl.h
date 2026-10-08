#pragma once
#include <stddef.h>
typedef int mbedtls_ssl_context;
#define MBEDTLS_ERR_SSL_WANT_READ (-0x6900)
#define MBEDTLS_ERR_SSL_WANT_WRITE (-0x6880)
#define MBEDTLS_ERR_SSL_TIMEOUT (-0x6800)
#define MBEDTLS_ERR_SSL_CONN_EOF (-0x7280)
int mbedtls_ssl_read(mbedtls_ssl_context *, unsigned char *, size_t);
int yoradio_mbedtls_ssl_read(mbedtls_ssl_context *, unsigned char *, size_t);
