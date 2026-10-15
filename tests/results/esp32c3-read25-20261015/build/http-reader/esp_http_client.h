#pragma once
#include <stddef.h>
typedef int esp_err_t;
typedef struct fake_client *esp_http_client_handle_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_HTTP_EAGAIN 0x7007
int esp_http_client_read(esp_http_client_handle_t,char *,int);
esp_err_t esp_http_client_close(esp_http_client_handle_t);
esp_err_t esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t,int *,int *);
