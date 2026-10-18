#pragma once
#include <stdio.h>
#include <stdbool.h>
#include "esp_http_server.h"

esp_err_t web_upload_handler(httpd_req_t *request);
esp_err_t web_board_upload_handler(httpd_req_t *request);
esp_err_t web_wifi_upload_handler(httpd_req_t *request);

// Initialize before exposing HTTP routes/workers. Recovery/open and single-file
// replacement share a mutex; slow downloads do not hold it after fopen.
esp_err_t web_upload_storage_init(void);
FILE *web_upload_open_file(const char *path);
bool web_upload_publish_file(const char *temporary, const char *live);
bool web_upload_publish_playlist(const char *csv_temporary,
                                 const char *index_temporary);
