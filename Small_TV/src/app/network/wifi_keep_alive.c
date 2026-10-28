#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "sdkconfig.h"
#include "esp_idf_version.h"
#include "esp_private/wifi_os_adapter.h"

/* These private offsets belong to the fully qualified C2 SDK PM object.
 * The post-link guard checks actual symbol sizes, callers and adapter targets. */
#if !CONFIG_IDF_TARGET_ESP32C2 || ESP_IDF_VERSION_MAJOR != 6 || ESP_IDF_VERSION_MINOR != 1
#error "Requalify the private Wi-Fi keep-alive ABI for this SDK/target"
#endif
_Static_assert(sizeof(void *) == 4, "The qualified Wi-Fi timer ABI is RV32");
_Static_assert(ESP_WIFI_OS_ADAPTER_VERSION == 9, "Requalify the Wi-Fi OS adapter ABI");
_Static_assert(offsetof(wifi_osi_funcs_t, _timer_arm) == 224, "Wi-Fi millisecond arm adapter moved");
_Static_assert(offsetof(wifi_osi_funcs_t, _timer_disarm) == 228, "Wi-Fi disarm adapter moved");
_Static_assert(offsetof(wifi_osi_funcs_t, _timer_arm_us) == 240, "Wi-Fi microsecond arm adapter moved");

extern unsigned char g_pm[584];
extern unsigned char g_pm_cfg[76];
extern wifi_osi_funcs_t *g_osi_funcs_p;

void small_tv_wifi_enable_keep_alive_timer(void)
{
    /* Rearm the existing SDK keep-alive timer without narrowing a BSS interval.
     * FIXED_FACTORY: the factory's encoded period can wrap to zero; the newer
     * SDK instead multiplies the complete period in 32-bit microseconds. Its
     * first overflowing negotiated period, 4197, becomes 760704 us. Retain the
     * full 16-bit interval and use the SDK's 64-bit-converting ms backend only
     * when the original microsecond API cannot represent the timeout. */
    uint32_t delay_us = 0;
    uint32_t delay_ms = 0;
    bool milliseconds = false;

    if (g_pm_cfg[52])
    {
        uint16_t period;
        uint32_t adjustment;
        /* memcpy avoids type-punning the vendor's private object declaration. */
        memcpy(&period, g_pm_cfg + 72, sizeof(period));
        memcpy(&adjustment, g_pm_cfg + 56, sizeof(adjustment));
        uint64_t nominal_us = (uint64_t)period * 1024000u;
        if (nominal_us >= adjustment && nominal_us - adjustment > UINT32_MAX)
        {
            /* BSS units are exact milliseconds. This is ceil(timeout_us/1000)
             * without a 64-bit divide. The real setter uses 500000 or 2000000
             * us adjustments, so legitimate negotiated timeouts are exact. */
            delay_ms = (uint32_t)period * 1024u - adjustment / 1000u;
            milliseconds = true;
        }
        else
        {
            /* Preserve representable timeouts and the vendor's 32-bit
             * subtraction for adjustment inputs outside the negotiated range. */
            delay_us = (uint32_t)(nominal_us - adjustment);
        }
    }
    else
    {
        memcpy(&delay_us, g_pm_cfg + 28, sizeof(delay_us));
        if (!delay_us)
            return;
    }

    /* Snapshot configuration before disarm, as the original body does.
     * Reload the selected OS adapter after the callback; do not retain a stale
     * adapter if a platform implementation changes it while disarming. */
    void *timer = g_pm + 492;
    g_osi_funcs_p->_timer_disarm(timer);
    if (milliseconds)
        g_osi_funcs_p->_timer_arm(timer, delay_ms, false);
    else
        g_osi_funcs_p->_timer_arm_us(timer, delay_us, false);
}
