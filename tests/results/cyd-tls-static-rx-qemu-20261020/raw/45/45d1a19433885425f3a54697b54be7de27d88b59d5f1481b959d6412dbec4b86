#pragma once

#include "sdkconfig.h"
#include "esp_crt_bundle.h"

#if CONFIG_YORADIO_TLS_STATIC_RX_RESERVE
#include <stddef.h>
#include "mbedtls/ssl.h"

/* Radio configuration callback only. Calls the original certificate-bundle
 * attach first; preserves failures and all application userdata without inspecting it.
 * Actual SDK static RX ownership sites use the following paired entries. */
esp_err_t native_tls_rx_reserve_crt_bundle_attach(void *configuration);
void *yoradio_tls_static_rx_calloc(const mbedtls_ssl_config *configuration,
                                 size_t count, size_t bytes);
void yoradio_tls_static_rx_forget_configuration(const mbedtls_ssl_config *configuration);
void yoradio_tls_static_rx_free(void *pointer);
void yoradio_tls_static_rx_zeroize_free(void *pointer, size_t bytes);
#else
/* Preserve the exact original function pointer when the feature is disabled. */
#define native_tls_rx_reserve_crt_bundle_attach esp_crt_bundle_attach
#endif
