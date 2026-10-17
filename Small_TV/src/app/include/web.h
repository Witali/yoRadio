#pragma once
#include <stddef.h>
#include "esp_http_server.h"
#include "cJSON.h"
esp_err_t web_start(void);
/* Registered callbacks receive their canonical static route string in user_ctx.
 * req->uri remains the complete SDK request target, including any query. */
esp_err_t web_settings_get(httpd_req_t *req);
esp_err_t web_settings_post(httpd_req_t *req);
esp_err_t web_scan(httpd_req_t *req);
esp_err_t web_photo_get(httpd_req_t *req);
esp_err_t web_photo_post(httpd_req_t *req);
esp_err_t web_error(httpd_req_t *req, const char *message);
esp_err_t web_json(httpd_req_t *req, cJSON *object);
esp_err_t web_ok(httpd_req_t *req);
char *web_body(httpd_req_t *req, size_t max_length);
cJSON *web_parse_json(httpd_req_t *req);
bool web_integer(const cJSON *object, const char *name, int minimum, int maximum, int *out);
