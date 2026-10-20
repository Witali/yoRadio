/* Canonical-source reserve-off controls. No reserve module/header/RX wrappers. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include "sdkconfig.h"
#include "esp_crt_bundle.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "mbedtls/platform.h"
#include "mbedtls/ssl.h"
#include "ssl_misc.h"
#if CONFIG_YORADIO_TLS_INPUT_RECLAIM
#include "native_input_reclaim.h"
#endif

_Static_assert(MBEDTLS_SSL_IN_CONTENT_LEN == 16384,
               "Disabled controls retain the full RX content capacity");
_Static_assert(MBEDTLS_SSL_IN_BUFFER_LEN >= MBEDTLS_SSL_IN_CONTENT_LEN,
               "Disabled controls retain complete SDK RX storage");

static void require(bool condition, const char *name) {
    if (condition) return;
    printf("TLS_RX_TARGET_FAILURE %s\nTLS_RX_TARGET_CONTROLLED_STOP\n", name);
    fflush(stdout);
    esp_restart();
    for (;;) vTaskDelay(portMAX_DELAY);
}
void app_main(void) {
    puts("TLS_RX_DISABLED_ENTRY ordinary_sdk=1");
    mbedtls_ssl_config configurations[2];
    for (unsigned index = 0; index < 2; ++index) {
        mbedtls_ssl_config_init(&configurations[index]);
        require(mbedtls_ssl_config_defaults(&configurations[index], MBEDTLS_SSL_IS_CLIENT,
            MBEDTLS_SSL_TRANSPORT_STREAM, MBEDTLS_SSL_PRESET_DEFAULT) == 0, "disabled_configuration_defaults");
        /* Direct original callback. No labelled config marker or reserve API. */
        require(esp_crt_bundle_attach(&configurations[index]) == ESP_OK, "disabled_original_bundle_attach");
        require(mbedtls_ssl_conf_get_user_data_p(&configurations[index]) == NULL,
            "disabled_original_userdata_untouched");
    }
#if CONFIG_YORADIO_TLS_INPUT_RECLAIM
    adaptive_input_t *input = adaptive_input_create(8U * 256U, 4U * 256U, 256U);
    require(input && native_input_reclaim_bind(input), "disabled_control_reclaim_bind");
#endif
    size_t minimum_rx_allocation = SIZE_MAX;
    int pre_handshake_payload = -1;
    for (unsigned cycle = 0; cycle < 16; ++cycle) {
        mbedtls_ssl_context contexts[2];
        for (unsigned index = 0; index < 2; ++index) {
            mbedtls_ssl_init(&contexts[index]);
            require(mbedtls_ssl_setup(&contexts[index], &configurations[index]) == 0, "disabled_original_sdk_setup");
            /* This public getter includes the pre-handshake MFL limit. In the
             * pinned SDK, MFL_NONE maps to min(RX, TX), not allocated RX bytes.
             * Check the actual heap block independently without RX wrappers. */
#if defined(MBEDTLS_SSL_MAX_FRAGMENT_LENGTH)
            const int expected_payload = MBEDTLS_TLS_EXT_ADV_CONTENT_LEN;
#else
            const int expected_payload = MBEDTLS_SSL_IN_CONTENT_LEN;
#endif
            pre_handshake_payload = mbedtls_ssl_get_max_in_record_payload(&contexts[index]);
            require(pre_handshake_payload == expected_payload,
                "disabled_pre_handshake_payload_limit");
            void *rx = contexts[index].MBEDTLS_PRIVATE(in_buf);
            require(rx != NULL, "disabled_original_rx_buffer");
            size_t allocated = heap_caps_get_allocated_size(rx);
            require(allocated >= MBEDTLS_SSL_IN_BUFFER_LEN,
                "disabled_original_full_record_storage");
            if (allocated < minimum_rx_allocation) minimum_rx_allocation = allocated;
            require(mbedtls_ssl_session_reset(&contexts[index]) == 0, "disabled_original_session_reset");
        }
        for (unsigned index = 0; index < 2; ++index) {
            mbedtls_ssl_free(&contexts[index]);
            mbedtls_ssl_free(&contexts[index]);
        }
    }
    printf("TLS_RX_DISABLED_CAPACITY content=%u storage=%zu allocated_min=%zu "
           "pre_handshake_payload=%d setups=32\n",
           (unsigned)MBEDTLS_SSL_IN_CONTENT_LEN, (size_t)MBEDTLS_SSL_IN_BUFFER_LEN,
           minimum_rx_allocation, pre_handshake_payload);
    void *ordinary = mbedtls_calloc(1, MBEDTLS_SSL_IN_BUFFER_LEN);
    require(ordinary != NULL, "disabled_ordinary_public_calloc");
    mbedtls_free(ordinary);
#if CONFIG_YORADIO_TLS_INPUT_RECLAIM
    adaptive_input_stats_t stats = adaptive_input_stats(input);
    require(stats.minimum == 4 && stats.target == 8 && stats.released == 0,
        "disabled_control_no_unnecessary_reclaim");
    require(native_input_reclaim_detach(input) == NATIVE_INPUT_RECLAIM_DETACHED,
        "disabled_control_reclaim_detach");
    adaptive_input_destroy(input);
#endif
    for (unsigned index = 0; index < 2; ++index) mbedtls_ssl_config_free(&configurations[index]);
    require(heap_caps_check_integrity_all(true), "disabled_control_heap_integrity");
#if CONFIG_YORADIO_TLS_INPUT_RECLAIM
    const unsigned reclaim = 1;
#else
    const unsigned reclaim = 0;
#endif
    printf("TLS_RX_DISABLED_COMPLETE reserve=0 reclaim=%u cycles=16 ordinary_sdk=1\n", reclaim);
    fflush(stdout);
    esp_restart();
}
