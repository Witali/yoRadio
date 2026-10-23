#pragma once

#include "esp_http_server.h"

esp_err_t web_network_settings_info_handler(httpd_req_t *request);
esp_err_t web_network_settings_edit_handler(httpd_req_t *request);
