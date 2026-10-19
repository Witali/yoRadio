#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"
#include "native_state.h"
#include "native_wifi_store.h"

esp_err_t network_service_start(native_state_t *state);
esp_err_t network_service_prepare_sleep(void);
// Nonblocking generation-qualified audio power intent; Wi-Fi is owner-only.
void network_service_audio_accept(uint32_t generation, bool active);
void network_service_audio_receive(uint32_t generation);
void network_service_audio_finish(uint32_t generation);
esp_err_t network_service_retry_client(void);
// Sequential startup before exposing tasks. Saved changes affect the next boot;
// the active connection/fallback cache remains stable until explicit restart.
esp_err_t network_service_storage_init(void);
native_wifi_result_t network_service_wifi_metadata(native_wifi_metadata_t *out);
native_wifi_result_t network_service_wifi_edit(const native_wifi_edit_t *edit);
esp_err_t network_service_save_credentials(const char *ssid,
                                           const char *password);
esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size);


esp_err_t network_service_validate_credentials_file(const uint8_t *data,
                                                    size_t size);
