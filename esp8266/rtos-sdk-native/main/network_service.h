#pragma once

#include <stdbool.h>

#include "esp_err.h"

esp_err_t network_service_start(void);
void network_service_poll(void);
bool network_service_connected(void);
esp_err_t network_service_set_streaming(bool active);
