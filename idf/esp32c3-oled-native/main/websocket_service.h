#pragma once

#include "esp_err.h"
#include "esp_http_server.h"
#include "native_state.h"

esp_err_t websocket_service_register(httpd_handle_t server,
                                     native_state_t *state);
void websocket_service_notify_playlist_changed(void);

// Served by the existing status task; readiness must precede OTA activation.
bool websocket_service_reboot_ready(void);
void websocket_service_request_reboot(unsigned delay_ms);
