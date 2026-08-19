#pragma once

#include "esp_err.h"
#include "native_state.h"

esp_err_t network_service_start(native_state_t *state);
esp_err_t network_service_retry_client(void);
esp_err_t network_service_save_credentials(const char *ssid,
                                           const char *password);

