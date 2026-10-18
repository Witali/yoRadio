#pragma once
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/types.h>
#ifndef OLD_BASELINE
#include "websocket_message.h"
#include "json_buffer.h"
#endif

typedef int esp_err_t;
typedef void *httpd_handle_t;
typedef struct { int unused; } native_state_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_INVALID_SIZE 0x104
#define HTTPD_SOCK_ERR_FAIL (-1)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define HTTP_GET 1
#define HTTPD_400_BAD_REQUEST 400
#define CONFIG_LWIP_MAX_SOCKETS 10
#define CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT 1
#define CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT 1
#define CONFIG_HTTPD_QUEUE_WORK_BLOCKING 0
#define CONFIG_HTTPD_WS_STRICTER_RFC6455 0
#define BOARD_TASK_STACK_WEBSOCKET_STATUS 3072
#define pdPASS 1
#define pdMS_TO_TICKS(x) (x)
#define HTTPD_RECV_OPT_NONE 0
#define HTTPD_RECV_OPT_BLOCKING 1
#define HTTPD_RECV_OPT_HALT_AFTER_PENDING 2
#define WS_SEND_OK 1
#define WS_SEND_FAILED 2
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef int httpd_recv_opt_t;
#define ESP_LOGD(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define ESP_RETURN_ON_ERROR(value,...) do { esp_err_t error_ = (value); if (error_ != ESP_OK) return error_; } while (0)
#define ESP_RETURN_ON_FALSE(value,error,...) do { if (!(value)) return (error); } while (0)
typedef enum { HTTPD_WS_TYPE_CONTINUE=0, HTTPD_WS_TYPE_TEXT=1,
    HTTPD_WS_TYPE_BINARY=2, HTTPD_WS_TYPE_CLOSE=8, HTTPD_WS_TYPE_PING=9,
    HTTPD_WS_TYPE_PONG=10 } httpd_ws_type_t;
typedef enum { HTTPD_WS_CLIENT_INVALID, HTTPD_WS_CLIENT_HTTP,
    HTTPD_WS_CLIENT_WEBSOCKET } httpd_ws_client_info_t;
typedef struct { bool final, fragmented; httpd_ws_type_t type;
    uint8_t *payload; size_t len, left_len; } httpd_ws_frame_t;
typedef int (*httpd_send_func_t)(httpd_handle_t,int,const char *,size_t,int);
typedef int (*httpd_recv_func_t)(httpd_handle_t,int,char *,size_t,int);
typedef void (*httpd_free_ctx_fn_t)(void *);
typedef void (*httpd_work_fn_t)(void *);
typedef void (*transfer_complete_cb)(esp_err_t,int,void *);
typedef void *EventGroupHandle_t;
typedef struct { httpd_ws_frame_t frame; httpd_handle_t handle; int socket;
    transfer_complete_cb callback; void *arg; bool blocking;
    EventGroupHandle_t transfer_done; } async_transfer_t;
struct sock_db { int fd; httpd_handle_t handle; bool live, ws_handshake_done, ws_close, ws_control_frames;
    unsigned incarnation; void *context; httpd_free_ctx_fn_t free_context;
    httpd_send_func_t send_fn; httpd_recv_func_t recv_fn; unsigned pending_len;
    char pending_data[128]; };
struct httpd_req_aux { struct sock_db *sd; bool ws_final; httpd_ws_type_t ws_type;
    uint8_t mask_key[4]; };
typedef struct { int method; httpd_handle_t handle; struct httpd_req_aux *aux; } httpd_req_t;
typedef struct { const char *uri; int method; esp_err_t (*handler)(httpd_req_t *);
    bool is_websocket, handle_ws_control_frames;
    esp_err_t (*ws_pre_handshake_cb)(httpd_req_t *);
    esp_err_t (*ws_post_handshake_cb)(httpd_req_t *); } httpd_uri_t;

int64_t esp_timer_get_time(void);
void vTaskDelay(unsigned);
int xTaskCreate(void (*)(void *),const char *,unsigned,void *,unsigned,void *);
int shutdown(int,int);
ssize_t lwip_send(int,const void *,size_t,int);
ssize_t lwip_recv(int,void *,size_t,int);
int lwip_select(int,fd_set *,fd_set *,fd_set *,struct timeval *);
ssize_t native_web_transport_send(httpd_handle_t,int,const void *,size_t,int,bool *);
ssize_t native_web_transport_recv(httpd_handle_t,int,void *,size_t,int,bool *);
void native_web_transport_shutdown(httpd_handle_t,int,bool);
void *httpd_sess_get_ctx(httpd_handle_t,int);
void httpd_sess_set_ctx(httpd_handle_t,int,void *,httpd_free_ctx_fn_t);
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_sess_trigger_close(httpd_handle_t,int);
struct sock_db *httpd_sess_get(httpd_handle_t,int);
int httpd_req_to_sockfd(httpd_req_t *);
esp_err_t httpd_get_client_list(httpd_handle_t,size_t *,int *);
httpd_ws_client_info_t httpd_ws_get_fd_info(httpd_handle_t,int);
esp_err_t httpd_queue_work(httpd_handle_t,httpd_work_fn_t,void *);
esp_err_t httpd_register_uri_handler(httpd_handle_t,const httpd_uri_t *);
esp_err_t httpd_ws_send_frame(httpd_req_t *,httpd_ws_frame_t *);
esp_err_t httpd_ws_send_frame_async(httpd_handle_t,int,httpd_ws_frame_t *);
esp_err_t httpd_ws_send_data_async(httpd_handle_t,int,httpd_ws_frame_t *,transfer_complete_cb,void *);
esp_err_t httpd_ws_recv_frame(httpd_req_t *,httpd_ws_frame_t *,size_t);
esp_err_t httpd_resp_send_err(httpd_req_t *,int,const char *);
bool deep_sleep_clock_begin_activity(void);
void deep_sleep_clock_end_activity(void);
static void handle_command(httpd_req_t *,char *);
static void format_status(char *,size_t);
static void status_task(void *);
static atomic_bool s_reboot_ready;
unsigned xEventGroupSetBits(EventGroupHandle_t,unsigned);
