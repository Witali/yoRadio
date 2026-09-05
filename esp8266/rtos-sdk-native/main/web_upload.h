#pragma once
#include "esp_http_server.h"
esp_err_t web_upload_handler(httpd_req_t *request);
esp_err_t web_ota_handler(httpd_req_t *request);
void web_upload_poll(void);
void web_upload_request_reboot(void);
