#include <stddef.h>
#include <stdint.h>

#include "sdkconfig.h"
#include "esp_idf_version.h"
#include "esp_private/wifi_os_adapter.h"

/* The private queue ABI and dense IDs are qualified against the pinned C2
 * Wi-Fi library. An SDK/target upgrade must recheck the dispatch table. */
#if !CONFIG_IDF_TARGET_ESP32C2 || ESP_IDF_VERSION_MAJOR != 6 || ESP_IDF_VERSION_MINOR != 1
#error "Requalify the private Wi-Fi timer ABI for this SDK/target"
#endif
_Static_assert(sizeof(void *) == 4, "The qualified Wi-Fi queue ABI is RV32");
_Static_assert(ESP_WIFI_OS_ADAPTER_VERSION == 9, "Requalify the Wi-Fi OS adapter ABI");
_Static_assert(offsetof(wifi_osi_funcs_t, _free) == 176, "Wi-Fi message free adapter moved");

/* This is the adapter pointer used by the vendor dispatcher itself, including
 * an application-supplied adapter selected during Wi-Fi initialization. */
extern wifi_osi_funcs_t *g_osi_funcs_p;

/* GNU ld resolves this reference to the original vendor implementation. */
int32_t __real_pp_timer_do_process(void *message);

int32_t __wrap_pp_timer_do_process(void *message)
{
    /* Validate a queued timer before the vendor's table-index prefetch.
     * FIXED_FACTORY: both factory 0x420acc62 and native 0x420d14c0 read
     * table[id].id before bounds checking. Only IDs 0..13 have callbacks.
     * The dispatcher owns a non-null message and frees it on every path;
     * rejected messages must use that same Wi-Fi adapter exactly once. */
    if (message && ((const uint8_t *)message)[0] >= 14u)
    {
        g_osi_funcs_p->_free(message);
        return 0;
    }

    /* Preserve the vendor's null-message handling and complete valid paths. */
    return __real_pp_timer_do_process(message);
}
