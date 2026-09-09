#pragma once

#include <stdint.h>

#include "esp_err.h"
#include "volume_scale.h"

esp_err_t radio_control_init(void);
esp_err_t radio_control_play(uint16_t station);
esp_err_t radio_control_stop(void);
esp_err_t radio_control_toggle(void);
esp_err_t radio_control_next(void);
esp_err_t radio_control_previous(void);
/* User-facing percent, inclusive 0..100; deltas are percentage points. */
uint8_t radio_control_volume(void);
esp_err_t radio_control_set_volume(int percent);
esp_err_t radio_control_adjust_volume(int delta);
void radio_control_flush_pending(void);
void radio_control_settings_changed(void);
