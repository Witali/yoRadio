#pragma once
#include "settings.h"
#define FACTORY_SETTINGS_OFFSET 0x3e7000u
#define FACTORY_SETTINGS_BYTES 0x1bcu
/* The raw factory sector is authoritative; NVS remains a compatibility fallback. */
bool factory_settings_decode(const uint8_t raw[FACTORY_SETTINGS_BYTES], tv_settings_t *settings);
void factory_settings_encode(const tv_settings_t *settings, uint8_t raw[FACTORY_SETTINGS_BYTES]);
