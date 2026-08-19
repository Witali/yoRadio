#pragma once

#include "esp_err.h"
#include "esp_http_server.h"
#include "native_state.h"

esp_err_t websocket_service_register(httpd_handle_t server,
                                     native_state_t *state);
