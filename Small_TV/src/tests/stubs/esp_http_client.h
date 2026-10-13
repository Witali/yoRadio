#pragma once
#include <stdbool.h>
#include "esp_err.h"
enum
{
    HTTP_EVENT_ON_DATA = 1
};
typedef struct
{
    int event_id, data_len;
    void *data, *user_data;
} esp_http_client_event_t;
typedef struct
{
    const char *url;
    int timeout_ms, buffer_size, buffer_size_tx;
    bool disable_auto_redirect;
    esp_err_t (*event_handler)(esp_http_client_event_t *);
    void *user_data;
} esp_http_client_config_t;
typedef void *esp_http_client_handle_t;
esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t *config);
esp_err_t esp_http_client_perform(esp_http_client_handle_t client);
int esp_http_client_get_status_code(esp_http_client_handle_t client);
void esp_http_client_cleanup(esp_http_client_handle_t client);
