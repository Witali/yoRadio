#pragma once

#include <stdbool.h>
#include <stdio.h>
#include "esp_http_server.h"

esp_err_t web_upload_storage_init(void);
FILE *web_upload_open_file(const char *path);
bool web_upload_publish_file(const char *temporary, const char *live);
bool web_upload_publish_playlist(const char *csv_temporary,
                                 const char *index_temporary);

esp_err_t web_upload_handler(httpd_req_t *request);
esp_err_t web_board_upload_handler(httpd_req_t *request);
esp_err_t web_wifi_upload_handler(httpd_req_t *request);

// HTTP routes remain closed until startup has prepared every service.
void web_upload_activate(void);
void web_upload_deactivate(void);
