#pragma once
#include "esp_http_server.h"

esp_err_t web_ota_handler(httpd_req_t *request);
esp_err_t web_ota_info_handler(httpd_req_t *request);
