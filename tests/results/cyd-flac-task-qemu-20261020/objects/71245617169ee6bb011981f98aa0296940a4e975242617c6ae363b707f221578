#pragma once

#include "esp_http_server.h"

// Start before exposing routes; abort is only valid before activation.
esp_err_t web_static_start(void);
void web_static_activate(void);
void web_static_abort(void);
esp_err_t web_static_handler(httpd_req_t *request);
