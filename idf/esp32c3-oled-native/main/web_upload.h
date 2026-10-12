#pragma once
#include "esp_http_server.h"

esp_err_t web_upload_handler(httpd_req_t *request);
esp_err_t web_board_upload_handler(httpd_req_t *request);
esp_err_t web_wifi_upload_handler(httpd_req_t *request);
