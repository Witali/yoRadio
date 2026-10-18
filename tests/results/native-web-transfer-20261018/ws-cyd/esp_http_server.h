#pragma once
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
typedef void *httpd_handle_t;
typedef void (*httpd_free_ctx_fn_t)(void *);
typedef void (*httpd_work_fn_t)(void *);
typedef enum { HTTP_DELETE=0, HTTP_GET=1, HTTP_POST=3 } httpd_method_t;
typedef enum { HTTPD_WS_TYPE_CONTINUE=0,HTTPD_WS_TYPE_TEXT=1,HTTPD_WS_TYPE_BINARY=2,HTTPD_WS_TYPE_CLOSE=8,HTTPD_WS_TYPE_PING=9,HTTPD_WS_TYPE_PONG=10 } httpd_ws_type_t;
typedef enum { HTTPD_WS_CLIENT_INVALID,HTTPD_WS_CLIENT_HTTP,HTTPD_WS_CLIENT_WEBSOCKET } httpd_ws_client_info_t;
typedef struct { bool final,fragmented;httpd_ws_type_t type;uint8_t *payload;size_t len; } httpd_ws_frame_t;
typedef struct { int socket;httpd_method_t method;const char *payload;size_t length;httpd_ws_type_t type;bool final,fragmented,receive_error,transport_reads; } httpd_req_t;
typedef struct { const char *uri;httpd_method_t method;esp_err_t (*handler)(httpd_req_t *);bool is_websocket,handle_ws_control_frames;esp_err_t (*ws_post_handshake_cb)(httpd_req_t *);esp_err_t (*ws_pre_handshake_cb)(httpd_req_t *); } httpd_uri_t;
typedef int (*httpd_send_func_t)(httpd_handle_t,int,const char *,size_t,int);
typedef int (*httpd_recv_func_t)(httpd_handle_t,int,char *,size_t,int);
#define HTTPD_SOCK_ERR_FAIL (-1)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
esp_err_t httpd_register_uri_handler(httpd_handle_t,const httpd_uri_t *);
esp_err_t httpd_get_client_list(httpd_handle_t,size_t *,int *);
httpd_ws_client_info_t httpd_ws_get_fd_info(httpd_handle_t,int);
void *httpd_sess_get_ctx(httpd_handle_t,int);
void httpd_sess_set_ctx(httpd_handle_t,int,void *,httpd_free_ctx_fn_t);
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_queue_work(httpd_handle_t,httpd_work_fn_t,void *);
esp_err_t httpd_ws_send_frame_async(httpd_handle_t,int,httpd_ws_frame_t *);
int httpd_req_to_sockfd(httpd_req_t *);
esp_err_t httpd_ws_recv_frame(httpd_req_t *,httpd_ws_frame_t *,size_t);
