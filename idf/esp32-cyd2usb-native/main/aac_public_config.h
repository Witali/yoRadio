#pragma once

#include "sdkconfig.h"
#include "esp_aac_dec.h"

/* Public configuration only. No private decoder layout or binary hooks. */
static inline esp_aac_dec_cfg_t native_aac_public_config(void) {
    esp_aac_dec_cfg_t config = ESP_AAC_DEC_CONFIG_DEFAULT();
#ifdef CONFIG_YORADIO_AAC_PLUS
    config.aac_plus_enable = true;
#endif
    return config;
}
