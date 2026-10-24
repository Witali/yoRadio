/* CYD radio-owned full-record TLS RX reserve for the guarded SDK profile.
 * Keep disabled until physical CYD resource and playback qualification. */
#include "native_tls_rx_reserve.h"

#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_crt_bundle.h"
#include "esp_idf_version.h"
#include "mbedtls/platform.h"
#include "mbedtls/platform_util.h"
#include "ssl_misc.h"
#include "tf_psa_crypto_common.h"

#if !CONFIG_YORADIO_TLS_STATIC_RX_RESERVE || !CONFIG_IDF_TARGET_ESP32 || \
    !CONFIG_ESP_TLS_USING_MBEDTLS || !CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC || \
    !CONFIG_MBEDTLS_CERTIFICATE_BUNDLE || CONFIG_MBEDTLS_CUSTOM_MEM_ALLOC || \
    CONFIG_MBEDTLS_DYNAMIC_BUFFER || CONFIG_MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH || \
    CONFIG_MBEDTLS_SSL_PROTO_GMTSSL1_1 || CONFIG_MBEDTLS_SSL_CONTEXT_SERIALIZATION || \
    defined(MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH)
#error "CYD RX reserve requires the audited classic ESP32 static/internal profile"
#endif
#if ESP_IDF_VERSION != ESP_IDF_VERSION_VAL(6, 0, 2)
#error "CYD RX reserve requires the audited ESP-IDF6.0.2 declaration/layout profile"
#endif

_Static_assert(MBEDTLS_SSL_IN_CONTENT_LEN == 16384,
               "CYD reservation retains the full input record content capacity");
_Static_assert(MBEDTLS_SSL_IN_BUFFER_LEN >= MBEDTLS_SSL_IN_CONTENT_LEN,
               "The complete SDK RX buffer expression must include its overhead");

/* Exact pinned SDK formula. No donor dynamic-adapter header or numerical size.
 * The slot is permanently withheld from general heap even during plain HTTP.
 * It is not a claim of peak/free heap improvement. */
static _Alignas(max_align_t) unsigned char s_rx[MBEDTLS_SSL_IN_BUFFER_LEN];
/* Soft eligibility limit only. A full registry never evicts a live identity
 * and never changes certificate attach/setup results: that config uses heap. */
enum { RX_CONFIGURATION_CAPACITY = 8 };
static uintptr_t s_radio_configurations[RX_CONFIGURATION_CAPACITY];
static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;
typedef enum { RX_FREE, RX_LOANED, RX_RETURNING } rx_state_t;
static rx_state_t s_state;

/* Configuration lifetime hooks never inspect the object or application data.
 * SAFE accepts the task/ISR contexts of the original pure initializer. The
 * bounded critical section does no allocation, erase or external callback. */
void yoradio_tls_static_rx_forget_configuration(const mbedtls_ssl_config *configuration) {
    if (!configuration) return;
    const uintptr_t identity = (uintptr_t)configuration;
    portENTER_CRITICAL_SAFE(&s_lock);
    for (unsigned index = 0; index < RX_CONFIGURATION_CAPACITY; ++index) {
        if (s_radio_configurations[index] == identity)
            s_radio_configurations[index] = 0;
    }
    portEXIT_CRITICAL_SAFE(&s_lock);
    /* Deliberately independent of s_state. ESP-TLS config_free precedes
     * ssl_free: a live RX loan must remain owned until its exact release. */
}

static void register_configuration(const mbedtls_ssl_config *configuration) {
    const uintptr_t identity = (uintptr_t)configuration;
    unsigned empty = RX_CONFIGURATION_CAPACITY;
    portENTER_CRITICAL_SAFE(&s_lock);
    for (unsigned index = 0; index < RX_CONFIGURATION_CAPACITY; ++index) {
        if (s_radio_configurations[index] == identity) {
            portEXIT_CRITICAL_SAFE(&s_lock);
            return;
        }
        if (!s_radio_configurations[index] && empty == RX_CONFIGURATION_CAPACITY)
            empty = index;
    }
    if (empty != RX_CONFIGURATION_CAPACITY)
        s_radio_configurations[empty] = identity;
    portEXIT_CRITICAL_SAFE(&s_lock);
}

esp_err_t native_tls_rx_reserve_crt_bundle_attach(void *configuration) {
    /* The original callback runs first, outside our lock. Neither kind of
     * application userdata is read or changed, including explicit radio users. */
    esp_err_t result = esp_crt_bundle_attach(configuration);
    if (configuration) {
        if (result == ESP_OK)
            register_configuration(configuration);
        else
            yoradio_tls_static_rx_forget_configuration(configuration);
    }
    return result;
}

void *yoradio_tls_static_rx_calloc(const mbedtls_ssl_config *configuration,
                                 size_t count, size_t bytes) {
    bool claimed = false;
    if (configuration && !xPortInIsrContext() && count == 1 && bytes == sizeof(s_rx)) {
        const uintptr_t identity = (uintptr_t)configuration;
        portENTER_CRITICAL(&s_lock);
        for (unsigned index = 0; index < RX_CONFIGURATION_CAPACITY; ++index) {
            if (s_radio_configurations[index] == identity && s_state == RX_FREE) {
                s_state = RX_LOANED;
                claimed = true;
                break;
            }
        }
        portEXIT_CRITICAL(&s_lock);
    }
    if (!claimed) {
        /* Follow the actual configured dispatcher. When input reclaim is on,
         * its unchanged wrapper still calls the SDK allocator first and then
         * uses its immutable retry budget. No premature pool-floor policy. */
        return mbedtls_calloc(count, bytes);
    }
    /* Do not zero or allocate under an SMP critical section. The state excludes
     * every other loan until zeroing is complete and the pointer is published. */
    memset(s_rx, 0, sizeof(s_rx));
    return s_rx;
}

static bool release_reserved(void *pointer) {
    if (pointer != s_rx) return false;
    /* Both audited SDK release sites run in task context. Ordinary client
     * same-context concurrent use/task deletion remains unsupported. */
    assert(!xPortInIsrContext());
    portENTER_CRITICAL(&s_lock);
    assert(s_state == RX_LOANED);
    s_state = RX_RETURNING;
    portEXIT_CRITICAL(&s_lock);
    /* Erase full capacity before reuse, including setup-failure cleanup, which
     * the ordinary SDK otherwise frees without an explicit zeroize here. */
    mbedtls_platform_zeroize(s_rx, sizeof(s_rx));
    portENTER_CRITICAL(&s_lock);
    assert(s_state == RX_RETURNING);
    s_state = RX_FREE;
    portEXIT_CRITICAL(&s_lock);
    return true;
}

void yoradio_tls_static_rx_free(void *pointer) {
    if (!release_reserved(pointer)) mbedtls_free(pointer);
}

void yoradio_tls_static_rx_zeroize_free(void *pointer, size_t bytes) {
    if (!release_reserved(pointer)) mbedtls_zeroize_and_free(pointer, bytes);
}
