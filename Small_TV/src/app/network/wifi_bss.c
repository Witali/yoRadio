#include <stdint.h>
#include <string.h>

#include "sdkconfig.h"
#include "esp_idf_version.h"

#if !CONFIG_IDF_TARGET_ESP32C2 || ESP_IDF_VERSION_MAJOR != 6 || ESP_IDF_VERSION_MINOR != 1
#error "Requalify the private Wi-Fi BSS ABI for this SDK/target"
#endif
_Static_assert(sizeof(void *) == 4, "The qualified Wi-Fi peer ABI is RV32");

/* Private vendor logging ABI, checked against the original setter object. */
extern void wifi_log(uint32_t type, uint32_t module, uint32_t level,
                     const char *format, ...);

void small_tv_wifi_set_bss_max_idle_period(void *peer, const uint8_t *ie)
{
    /* Retain the previous period when the optional IE is absent or too short.
     * FIXED_FACTORY: factory 0x4206d90e and the pinned SDK setter read three
     * payload bytes without checking the IE length. Both association ingress
     * paths validate the containing extent, but allow lengths 0, 1 and 2.
     * The post-link gate binds those callers and this private peer layout. */
    if (!ie || ie[1] < 3)
        return;

    uint16_t period = (uint16_t)ie[2] | (uint16_t)((uint16_t)ie[3] << 8);
    uint8_t protected_keep_alive = ie[4] & 1u;
    memcpy((uint8_t *)peer + 818, &period, sizeof(period));
    ((uint8_t *)peer)[820] = protected_keep_alive;
    wifi_log(1, 1, 3, "BSS max idle period:%d(1000TU), protected keep alive:%s",
             (int)period, protected_keep_alive ? "TRUE" : "FALSE");
}
