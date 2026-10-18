#pragma once
#include <pthread.h>
#include <fcntl.h>
#include <sys/stat.h>
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef struct {struct {uint8_t ssid[32],password[64];}sta;} wifi_config_t;
static wifi_config_t s_station_config;
typedef unsigned portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(p) assert(!(*(p))++)
#define portEXIT_CRITICAL(p) assert((*(p))--==1)
#define pdTRUE 1
#define pdMS_TO_TICKS(v) (v)
#define portMAX_DELAY UINT32_MAX
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_NOT_SUPPORTED 0x106
#define ESP_ERR_HTTPD_RESP_HDR 0x602
#define ESP_ERR_HTTPD_RESP_SEND 0x604
#define HTTPD_RESP_USE_STRLEN (-1)
#define HTTP_SERVER_EVENT_HEADERS_SENT 4
#define HTTP_SERVER_EVENT_SENT_DATA 5
#define CONFIG_SPIFFS_OBJ_NAME_LEN 32
#define CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES 1024
#define NATIVE_NETWORK_CLIENT 1
/* Host field model, deliberately not an ESP32 ABI model. Algorithms below
 * come from snapshotted production and generated SDK source without edits. */
#define _POSIX_C_SOURCE 200809L
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
#include <strings.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <time.h>
#include <unistd.h>
#include "http_parser.h"
#include "websocket_message.h"
#include "json_buffer.h"
#define CONFIG_HTTPD_WS_SUPPORT 1
#define CONFIG_HTTPD_WS_STRICTER_RFC6455 1
#define CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT 1
#define CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT 1
#define CONFIG_HTTPD_QUEUE_WORK_BLOCKING 0
#define CONFIG_HTTPD_PURGE_BUF_LEN 32
#define CONFIG_HTTPD_MAX_REQ_HDR_LEN 1024
#define CONFIG_HTTPD_MAX_URI_LEN 512
#define CONFIG_LWIP_MAX_SOCKETS 10
#define PARSER_BLOCK_SIZE 128
#define HTTP_SERVER_EVENT_ON_HEADER 1
#define HTTP_SERVER_EVENT_DISCONNECTED 2
#define HTTP_SERVER_EVENT_ON_DATA 3
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_INVALID_SIZE 0x104
#define ESP_ERR_INVALID_VERSION 4
#define ESP_ERR_NOT_FOUND 5
#define ESP_ERR_HTTPD_RESULT_TRUNC 6
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_HTTPD_HANDLER_EXISTS 8
#define ESP_ERR_HTTPD_ALLOC_MEM 9
#define ESP_ERR_HTTPD_HANDLERS_FULL 10
#define ESP_ERR_HTTPD_INVALID_REQ 11
#define HTTPD_RECV_OPT_NONE 0
#define HTTPD_RECV_OPT_HALT_AFTER_PENDING 1
#define HTTPD_RECV_OPT_BLOCKING 2
#define HTTPD_SOCK_ERR_INVALID (-1)
#define HTTPD_SOCK_ERR_FAIL (-2)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define HTTPD_200 "200 OK"
#define HTTPD_TYPE_TEXT "text/html"
#define HTTPD_400_BAD_REQUEST 400
#define HTTPD_404_NOT_FOUND 404
#define HTTPD_405_METHOD_NOT_ALLOWED 405
#define HTTPD_408_REQ_TIMEOUT 408
#define HTTPD_413_CONTENT_TOO_LARGE 413
#define HTTPD_414_URI_TOO_LONG 414
#define HTTPD_431_REQ_HDR_FIELDS_TOO_LARGE 431
#define HTTPD_500_INTERNAL_SERVER_ERROR 500
#define HTTPD_501_METHOD_NOT_IMPLEMENTED 501
#define HTTPD_505_VERSION_NOT_SUPPORTED 505
#define HTTP_ANY (-1)
#define pdPASS 1
#define BOARD_TASK_STACK_WEBSOCKET_STATUS 3072
#define ESP_LOGD(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define ESP_COMPILER_DIAGNOSTIC_PUSH_IGNORE(x)
#define ESP_COMPILER_DIAGNOSTIC_POP(x)
#define ESP_RETURN_ON_ERROR(v,...) do { esp_err_t error_=(v); if(error_!=ESP_OK)return error_; } while(0)
#define ESP_RETURN_ON_FALSE(v,e,...) do { if(!(v))return (e); } while(0)
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef int esp_err_t, httpd_err_code_t, httpd_method_t, httpd_recv_opt_t;
typedef void *httpd_handle_t;
typedef void (*httpd_free_ctx_fn_t)(void *);
typedef void (*httpd_work_fn_t)(void *);
typedef struct { int fd; size_t data_len; } esp_http_server_event_data;
typedef int (*httpd_send_func_t)(void *,int,const char *,size_t,int);
typedef int (*httpd_recv_func_t)(void *,int,char *,size_t,int);
typedef int (*httpd_pending_func_t)(void *,int);
typedef struct { int network_mode; } native_state_t;
typedef enum { HTTPD_WS_TYPE_CONTINUE=0, HTTPD_WS_TYPE_TEXT=1, HTTPD_WS_TYPE_BINARY=2,
    HTTPD_WS_TYPE_CLOSE=8, HTTPD_WS_TYPE_PING=9, HTTPD_WS_TYPE_PONG=10 } httpd_ws_type_t;
typedef enum { HTTPD_WS_CLIENT_INVALID, HTTPD_WS_CLIENT_HTTP, HTTPD_WS_CLIENT_WEBSOCKET } httpd_ws_client_info_t;
typedef struct { bool final,fragmented; httpd_ws_type_t type; uint8_t *payload; size_t len,left_len; } httpd_ws_frame_t;
typedef struct httpd_req { void *handle,*aux,*sess_ctx,*user_ctx; httpd_free_ctx_fn_t free_ctx;
    bool ignore_sess_ctx_changes; int method; char uri[513]; size_t content_len; } httpd_req_t;
typedef struct { const char *uri; int method; esp_err_t (*handler)(httpd_req_t *); void *user_ctx;
    bool is_websocket,handle_ws_control_frames; const char *supported_subprotocol;
    esp_err_t (*ws_pre_handshake_cb)(httpd_req_t *),(*ws_post_handshake_cb)(httpd_req_t *); } httpd_uri_t;
struct resp_hdr { const char *field,*value; };
struct sock_db { bool ws_close,ws_handshake_done,ws_control_frames,ignore_sess_ctx_changes;
    int fd; void *ctx,*handle,*transport_ctx,*ws_user_ctx;
    httpd_free_ctx_fn_t free_ctx,free_transport_ctx; httpd_send_func_t send_fn;
    httpd_recv_func_t recv_fn; uint8_t pending_data[128]; size_t pending_len;
    esp_err_t (*ws_handler)(httpd_req_t *); int (*pending_fn)(httpd_handle_t,int); uint64_t lru_counter; };
struct httpd_req_aux { struct sock_db *sd; char *scratch; size_t scratch_cur_size,scratch_size_limit;
    size_t remaining_len; unsigned req_hdrs_count,resp_hdrs_count; bool ws_final; httpd_ws_type_t ws_type;
    uint8_t mask_key[4]; bool ws_handshake_detect; size_t max_uri_len,max_req_hdr_len;
    struct http_parser_url url_parse_res; char *status,*content_type; bool first_chunk_sent; struct resp_hdr resp_hdrs[8]; };
typedef struct { int max_req_hdr_len,max_uri_len,max_resp_headers,max_uri_handlers;
    bool enable_so_linger; int linger_timeout; void (*close_fn)(httpd_handle_t,int);
    bool (*uri_match_fn)(const char *,const char *,size_t); } httpd_config_t;
struct httpd_data { httpd_req_t hd_req; struct httpd_req_aux hd_req_aux; httpd_config_t config;
    httpd_uri_t *hd_calls[8]; int http_server_state; unsigned hd_sd_active_count; uint64_t lru_counter; };

static struct httpd_data server;
static struct sock_db session={.fd=-1};
static native_state_t state;
static unsigned cases,command_calls,queued_close_calls,activity_count,delete_count;
static uint8_t command_bytes[256];
static size_t command_size;
static size_t io_chunk=4096;
static char response_status[64],response_version[8];
static unsigned send_calls,recv_calls;

/* Public transport API is a POSIX adapter in this integration test. TLS is
 * exercised separately; no copied ESP-TLS or HTTPD-private TLS context here. */
#ifdef INTEGRATION_TLS
ssize_t native_web_transport_send(httpd_handle_t,int,const void *,size_t,int,bool *);
ssize_t native_web_transport_recv(httpd_handle_t,int,void *,size_t,int,bool *);
void native_web_transport_shutdown(httpd_handle_t,int,bool);
#else
static ssize_t native_web_transport_send(httpd_handle_t,int,const void *,size_t,int,bool *);
static ssize_t native_web_transport_recv(httpd_handle_t,int,void *,size_t,int,bool *);
static void native_web_transport_shutdown(httpd_handle_t,int,bool);
#endif
static int lwip_select(int,fd_set *,fd_set *,fd_set *,struct timeval *);
static void vTaskDelay(unsigned);
static int64_t esp_timer_get_time(void);
static bool deep_sleep_clock_begin_activity(void);
static void deep_sleep_clock_end_activity(void);
static int xTaskCreate(void (*)(void *),const char *,unsigned,void *,unsigned,TaskHandle_t *);
static void status_task(void *);
static bool httpd_valid_req(httpd_req_t *);
static struct sock_db *httpd_sess_get(httpd_handle_t,int);
void *httpd_sess_get_ctx(httpd_handle_t,int);
void httpd_sess_set_ctx(httpd_handle_t,int,void *,httpd_free_ctx_fn_t);
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
static esp_err_t httpd_sess_trigger_close(httpd_handle_t,int);
static esp_err_t httpd_queue_work(httpd_handle_t,httpd_work_fn_t,void *);
esp_err_t httpd_ws_send_frame(httpd_req_t *,httpd_ws_frame_t *);
esp_err_t httpd_ws_send_frame_async(httpd_handle_t,int,httpd_ws_frame_t *);
esp_err_t httpd_ws_recv_frame(httpd_req_t *,httpd_ws_frame_t *,size_t);
int httpd_req_to_sockfd(httpd_req_t *);
int httpd_req_recv(httpd_req_t *,char *,size_t);
int httpd_recv_with_opt(httpd_req_t *,char *,size_t,httpd_recv_opt_t);
int httpd_send(httpd_req_t *,const char *,size_t);
void httpd_sess_free_ctx(void **,httpd_free_ctx_fn_t);
static size_t strlcpy(char *,const char *,size_t);
static int httpd_req_handle_err(httpd_req_t *,int);
static int httpd_resp_set_hdr(httpd_req_t *,const char *,const char *);
static int httpd_resp_send_custom_err(httpd_req_t *,const char *,const char *);
static int httpd_resp_send_err(httpd_req_t *,httpd_err_code_t,const char *);
static void esp_http_server_dispatch_event(int,const void *,size_t);
esp_err_t httpd_uri(struct httpd_data *);
esp_err_t httpd_register_uri_handler(httpd_handle_t,const httpd_uri_t *);
static size_t httpd_req_get_hdr_value_len(httpd_req_t *,const char *);
static esp_err_t httpd_req_get_hdr_value_str(httpd_req_t *,const char *,char *,size_t);
#ifdef TARGET_C3
static atomic_bool s_reboot_ready;
static void handle_command(httpd_req_t *,char *);
#else
static bool prepare_status(void);
/* CYD's status formatter/radio operations are outside this protocol gate. */
struct ws_client_placeholder;
#endif

#define httpd_resp_sendstr(r,s) httpd_resp_send(r,s,HTTPD_RESP_USE_STRLEN)
static native_state_t *s_state=&state;
static TickType_t xTaskGetTickCount(void);
static void xTaskNotifyGive(TaskHandle_t);
static unsigned ulTaskNotifyTake(int,TickType_t);
static void vTaskDelete(TaskHandle_t);
static void esp_restart(void);
static void display_settings_note_activity(void);
static void *response_malloc(size_t);
static void *workspace_calloc(size_t,size_t);
static void workspace_free(void *);
static void observed_prepare_close(httpd_handle_t,int,bool);
static SemaphoreHandle_t xSemaphoreCreateMutex(void);
static int xSemaphoreTake(SemaphoreHandle_t,unsigned);
static void xSemaphoreGive(SemaphoreHandle_t);
static uint32_t esp_random(void);
static void esp_fill_random(void *,size_t);
static FILE *mapped_open(const char *,const char *);
static int mapped_fd_open(const char *,int,int);
static int mapped_stat(const char *,struct stat *);
static int mapped_remove(const char *);
static int mapped_rename(const char *,const char *);
static esp_err_t radio_control_publish_playlist(const char *,bool (*)(const char *,const char *));
static void websocket_service_notify_playlist_changed(void);
static void observed_upload_erase(void *,size_t);
static esp_err_t httpd_req_async_handler_begin(httpd_req_t *,httpd_req_t **);
static esp_err_t httpd_req_async_handler_complete(httpd_req_t *);
static int xQueueSend(void *,const void *,unsigned);
static esp_err_t serve_static_boundary(httpd_req_t *);
static const char *web_native_page(void);
static bool web_ui_available(void);
static const char *yoradio_index_html(void);
static esp_err_t send_recovery_page(httpd_req_t *);
static const char *esp_get_idf_version(void);
static void native_state_snapshot(native_state_t *,native_state_t *);
esp_err_t httpd_resp_send(httpd_req_t *,const char *,ssize_t);
esp_err_t httpd_resp_set_status(httpd_req_t *,const char *);
esp_err_t httpd_resp_set_type(httpd_req_t *,const char *);
esp_err_t httpd_resp_send_chunk(httpd_req_t *,const char *,ssize_t);
#ifdef INTEGRATION_TLS
void native_web_transport_prepare_close(httpd_handle_t,int,bool);
#else
static void native_web_transport_prepare_close(httpd_handle_t,int,bool);
#endif
