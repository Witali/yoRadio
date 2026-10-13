#pragma once

#include "sdkconfig.h"
#include "esp_aac_dec.h"

#ifdef CONFIG_YORADIO_AAC_PLUS
#define NATIVE_AAC_PLUS_ENABLED true
#else
#define NATIVE_AAC_PLUS_ENABLED false
#endif

static inline esp_aac_dec_cfg_t native_aac_decoder_config(void) {
    esp_aac_dec_cfg_t config = ESP_AAC_DEC_CONFIG_DEFAULT();
    config.aac_plus_enable = NATIVE_AAC_PLUS_ENABLED;
    return config;
}
