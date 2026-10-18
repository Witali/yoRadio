#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"
#include "native_state.h"

esp_err_t network_service_start(native_state_t *state);
esp_err_t network_service_retry_client(void);

// Initialize once during sequential startup, before exposing save APIs to tasks.
esp_err_t network_service_storage_init(void);

// Validate the entire bounded TSV file. Saving affects the next boot only;
// the running station configuration is retained until an explicit restart.
esp_err_t network_service_validate_credentials_file(const uint8_t *data,
                                                    size_t size);
esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size);
esp_err_t network_service_save_credentials(const char *ssid,
                                           const char *password);

