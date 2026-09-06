#pragma once

#include "esp_err.h"
#include "freertos/FreeRTOS.h"

esp_err_t input_service_start(void);
void input_service_poll(void);
TickType_t input_service_wait_ticks(TickType_t maximum_wait);
