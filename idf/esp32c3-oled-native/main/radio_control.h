#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"
#include "native_state.h"

esp_err_t radio_control_init(native_state_t *state);
esp_err_t radio_control_play(uint16_t item);
esp_err_t radio_control_toggle(void);
esp_err_t radio_control_next(void);
esp_err_t radio_control_previous(void);
uint16_t radio_control_current_item(void);
void radio_control_current_name(char *name, size_t name_size);
