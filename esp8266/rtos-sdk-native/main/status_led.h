#pragma once

#include "esp_err.h"
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"

esp_err_t status_led_init(void);
void status_led_poll(void);
TickType_t status_led_wait_ticks(TickType_t maximum);
/* Read-only post-gain PCM tap; no allocation or retained PCM pointer. */
/* One cheap flag check per PCM block; scanning is requested only at 10/20 Hz. */
extern volatile bool status_led_capture_requested;
void status_led_capture_pcm(const int16_t *samples, size_t count, uint8_t channels);
void status_led_clear(void);
