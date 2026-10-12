#pragma once
#include <stddef.h>
#include <stdbool.h>
#include "esp_err.h"
#define HTTPD_RESP_USE_STRLEN -1
#define HTTPD_SOCK_ERR_TIMEOUT -2
typedef enum {HTTP_GET=1,HTTP_POST=3} httpd_method_t;
typedef enum {HTTPD_400_BAD_REQUEST=400,HTTPD_404_NOT_FOUND=404,HTTPD_500_INTERNAL_SERVER_ERROR=500} httpd_err_code_t;
typedef void *httpd_handle_t;
typedef struct {
    const char *uri,*input,*content_type,*host,*origin;
    size_t content_len,position,response_length;
    unsigned status;
    char response[12289];
} httpd_req_t;
typedef struct {const char *uri;httpd_method_t method;esp_err_t (*handler)(httpd_req_t *);} httpd_uri_t;
typedef struct {unsigned max_uri_handlers,stack_size,max_open_sockets,recv_wait_timeout,send_wait_timeout;bool lru_purge_enable;} httpd_config_t;
#define HTTPD_DEFAULT_CONFIG() {0}
esp_err_t httpd_resp_set_status(httpd_req_t *req,const char *status);
esp_err_t httpd_resp_set_type(httpd_req_t *req,const char *type);
esp_err_t httpd_resp_set_hdr(httpd_req_t *req,const char *name,const char *value);
esp_err_t httpd_resp_send(httpd_req_t *req,const char *data,int length);
esp_err_t httpd_resp_send_err(httpd_req_t *req,httpd_err_code_t code,const char *message);
size_t httpd_req_get_hdr_value_len(httpd_req_t *req,const char *name);
esp_err_t httpd_req_get_hdr_value_str(httpd_req_t *req,const char *name,char *out,size_t capacity);
int httpd_req_recv(httpd_req_t *req,char *out,size_t length);
esp_err_t httpd_req_get_url_query_str(httpd_req_t *req,char *out,size_t capacity);
esp_err_t httpd_query_key_value(const char *query,const char *key,char *out,size_t capacity);
esp_err_t httpd_start(httpd_handle_t *server,const httpd_config_t *config);
esp_err_t httpd_stop(httpd_handle_t server);
esp_err_t httpd_register_uri_handler(httpd_handle_t server,const httpd_uri_t *uri);
esp_err_t httpd_register_err_handler(httpd_handle_t server,httpd_err_code_t code,esp_err_t (*handler)(httpd_req_t *,httpd_err_code_t));
