#pragma once

#include "esp_err.h"
#include "esp_http_server.h"
#include "native_state.h"
#include <stdint.h>

esp_err_t websocket_service_register(httpd_handle_t server,
                                     native_state_t *state);
void websocket_service_notify_playlist_changed(void);

// Served by the existing status task; readiness must precede OTA activation.
bool websocket_service_reboot_ready(void);
void websocket_service_request_reboot(unsigned delay_ms);
// Zero-initialized owner lease prevents a reboot during OTA. Pending reboots
// reject admission atomically; ordinary requests during OTA are deferred.
typedef struct { uint64_t epoch; } websocket_reboot_lease_t;
esp_err_t websocket_service_reboot_reserve(websocket_reboot_lease_t *lease);
esp_err_t websocket_service_reboot_cancel(websocket_reboot_lease_t *lease);
esp_err_t websocket_service_reboot_commit(websocket_reboot_lease_t *lease,
                                          unsigned delay_ms);
// The exclusive owner may restart immediately after its final eligibility
// check. Do not copy, cancel or commit this lease concurrently. Keep it reserved
// across esp_restart(), outside the portMUX, blocking ordinary pending reboots
// and other owners. A real successful restart never returns. A returning test
// double returns ESP_OK while this same lease remains reserved and owned.
esp_err_t websocket_service_reboot_restart_reserved_now(websocket_reboot_lease_t *lease);
