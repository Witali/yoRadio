#pragma once
#include "esp_http_server.h"

#define WEB_OTA_MAX_IMAGE_BYTES 0x1B0000U
#define WEB_OTA_MAX_BODY_BYTES (WEB_OTA_MAX_IMAGE_BYTES + 4096U)
void web_ota_activate(void);
void web_ota_deactivate(void);
esp_err_t web_ota_handler(httpd_req_t *request);
esp_err_t web_ota_info_handler(httpd_req_t *request);
