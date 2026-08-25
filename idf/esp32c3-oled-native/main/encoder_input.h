#pragma once

#include <stdint.h>

#include "esp_err.h"

typedef esp_err_t (*encoder_rotate_callback_t)(int32_t delta, void *context);
typedef esp_err_t (*encoder_click_callback_t)(void *context);

typedef struct {
    encoder_rotate_callback_t rotate;
    encoder_click_callback_t click;
    void *context;
} encoder_input_callbacks_t;

esp_err_t encoder_input_start(const encoder_input_callbacks_t *callbacks);
