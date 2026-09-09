#pragma once

#include "esp_err.h"
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"

esp_err_t status_led_init(void);
void status_led_poll(void);
TickType_t status_led_wait_ticks(TickType_t maximum);
/* One flag check per PCM block; the gain loop samples its own output at 10/20 Hz. */
extern volatile bool status_led_capture_requested;
void status_led_publish_peak(uint16_t peak);
void status_led_clear(void);
