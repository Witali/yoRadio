#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"
#include "native_state.h"
#include "native_wifi_store.h"
#include "network_runtime.h"

esp_err_t network_service_start(native_state_t *state);
esp_err_t network_service_retry_client(void);
esp_err_t network_service_snapshot(network_snapshot_t *out, uint32_t timeout_ms);

// Initialize once during sequential startup, before exposing save APIs to tasks.
esp_err_t network_service_storage_init(void);
// Non-secret metadata and revision-checked edits share the credential owner.
// Successful edits affect the next boot; the active station stays unchanged.
native_wifi_result_t network_service_wifi_metadata(native_wifi_metadata_t *out);
native_wifi_result_t network_service_wifi_edit(const native_wifi_edit_t *edit);

// Validate the entire bounded TSV file. Saving affects the next boot only;
// the running station configuration is retained until an explicit restart.
esp_err_t network_service_validate_credentials_file(const uint8_t *data,
                                                    size_t size);
esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size);
esp_err_t network_service_save_credentials(const char *ssid,
                                           const char *password);

