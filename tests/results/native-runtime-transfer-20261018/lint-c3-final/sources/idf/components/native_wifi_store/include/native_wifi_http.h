#pragma once

#include "esp_http_server.h"
#include "native_wifi_store.h"

typedef struct {
    native_wifi_result_t (*edit)(const native_wifi_edit_t *edit);
    // Pins a preallocated reboot before any durable credential mutation.
    esp_err_t (*admit)(void *context);
    // Once after response+bounded TLS close preparation+workspace detach.
    // A durable commit MUST commit that reservation even on response failure.
    void (*finish)(void *context, bool committed);
    void *context;
} native_wifi_http_config_t;

esp_err_t native_wifi_http_info(httpd_req_t *request,
    native_wifi_result_t (*metadata)(native_wifi_metadata_t *out));
// Terminal session: always ESP_FAIL, avoiding SDK unread-body purge. Uses actual
// httpd_req_recv so pending parser bytes survive. 10s idle/30s total receive,
// 1s response and bounded TLS-aware rejection/close; SDK owns final socket free.
esp_err_t native_wifi_http_edit(httpd_req_t *request,
                               const native_wifi_http_config_t *config);
