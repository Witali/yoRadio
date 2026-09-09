#pragma once

#include <stdint.h>

#include "esp_err.h"
#include "esp_http_server.h"

esp_err_t web_service_start(void);
void web_service_poll(void);
void web_service_notify_playlist_changed(void);
void web_service_notify_assets_changed(void);
esp_err_t web_service_finish_response(httpd_req_t *request, esp_err_t result);

#define WEB_UPLOAD_RECEIVE_BYTES 512U
/* HTTP-task handlers only. Borrowed until the handler returns; do not retain
 * it or invoke another scratch-using handler from a multipart callback. */
uint8_t *web_service_upload_buffer(void);
