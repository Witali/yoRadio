#pragma once
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <assert.h>
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <setjmp.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <stdatomic.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/types.h>
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_NOT_FOUND 0x105
#define ESP_ERR_NOT_SUPPORTED 0x106
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_HTTPD_INVALID_REQ 0x601
#define ESP_ERR_HTTPD_RESP_HDR 0x602
#define ESP_ERR_HTTPD_ALLOC_MEM 0x603
#define ESP_ERR_HTTPD_RESP_SEND 0x604
#define HTTPD_SOCK_ERR_FAIL (-1)
#define HTTPD_SOCK_ERR_INVALID (-2)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define HTTPD_RESP_USE_STRLEN (-1)
#define HTTPD_500_INTERNAL_SERVER_ERROR 500
#define HTTP_SERVER_EVENT_HEADERS_SENT 1
#define HTTP_SERVER_EVENT_SENT_DATA 2
#define HTTP_SERVER_EVENT_ON_DATA 3
#define ESP_IMAGE_HASH_LEN 32
#define OTA_WITH_SEQUENTIAL_WRITES 0xfffffffeU
#define ESP_STATIC_ASSERT _Static_assert
#define FORCE_INLINE_ATTR static inline
#define ESP_LOGD(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef int esp_err_t;
typedef unsigned esp_ota_handle_t;
typedef struct {uint32_t address,size;int type,subtype;void *flash_chip;char label[17];} esp_partition_t;
#define ESP_PARTITION_TYPE_APP 0
#define ESP_PARTITION_TYPE_DATA 1
#define ESP_PARTITION_SUBTYPE_APP_OTA_MIN 0x10
#define ESP_PARTITION_SUBTYPE_APP_OTA_MAX 0x20
typedef struct {uint32_t offset,size;} esp_partition_pos_t;
#include "sdk-app-format.h"
#include "sdk-app-desc.h"
#include "sdk-image-types.inc"
const esp_partition_t *esp_ota_get_running_partition(void);
const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *);
const esp_app_desc_t *esp_app_get_description(void);
esp_err_t esp_ota_begin(const esp_partition_t *,size_t,esp_ota_handle_t *);
esp_err_t esp_ota_write(esp_ota_handle_t,const void *,size_t);
esp_err_t esp_ota_end(esp_ota_handle_t);
esp_err_t esp_ota_abort(esp_ota_handle_t);
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *);
esp_err_t esp_image_verify(esp_image_load_mode_t,const esp_partition_pos_t *,esp_image_metadata_t *);
typedef void *httpd_handle_t;
typedef void (*httpd_free_ctx_fn_t)(void *);
typedef int (*httpd_send_func_t)(httpd_handle_t,int,const char *,size_t,int);
typedef int (*httpd_recv_func_t)(httpd_handle_t,int,char *,size_t,int);
struct sock_db {
    httpd_handle_t handle;int fd;httpd_send_func_t send_fn;httpd_recv_func_t recv_fn;
    uint8_t pending_data[2048];size_t pending_len;void *ctx;httpd_free_ctx_fn_t free_ctx;bool ignore_sess_ctx_changes;
};
typedef struct httpd_req {httpd_handle_t handle;void *aux;size_t content_len;void *sess_ctx;httpd_free_ctx_fn_t free_ctx;bool ignore_sess_ctx_changes;void *user_ctx;} httpd_req_t;
struct httpd_req_aux {
    struct sock_db *sd;size_t remaining_len,max_req_hdr_len;unsigned req_hdrs_count,resp_hdrs_count;
    struct {const char *field,*value;} resp_hdrs[8];char *status,*content_type;
    char *scratch;size_t scratch_size_limit,scratch_cur_size;
};
struct httpd_data {
    struct {unsigned max_resp_headers;} config;int http_server_state;
    httpd_req_t hd_req;struct httpd_req_aux hd_req_aux;
};
typedef struct {int fd;ssize_t data_len;} esp_http_server_event_data;
typedef enum {HTTPD_RECV_OPT_NONE,HTTPD_RECV_OPT_HALT_AFTER_PENDING,HTTPD_RECV_OPT_BLOCKING} httpd_recv_opt_t;
struct sock_db *httpd_sess_get(httpd_handle_t,int);
bool httpd_valid_req(httpd_req_t *);
void esp_http_server_dispatch_event(int,void *,size_t);
int httpd_req_to_sockfd(httpd_req_t *);
esp_err_t httpd_req_get_hdr_value_str(httpd_req_t *,const char *,char *,size_t);
void *httpd_sess_get_ctx(httpd_handle_t,int);
void httpd_sess_set_ctx(httpd_handle_t,int,void *,httpd_free_ctx_fn_t);
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
int httpd_req_recv(httpd_req_t *,char *,size_t);
esp_err_t httpd_resp_set_type(httpd_req_t *,const char *);
esp_err_t httpd_resp_set_hdr(httpd_req_t *,const char *,const char *);
esp_err_t httpd_resp_set_status(httpd_req_t *,const char *);
esp_err_t httpd_resp_send(httpd_req_t *,const char *,ssize_t);
#define httpd_resp_sendstr(r,s) httpd_resp_send(r,s,HTTPD_RESP_USE_STRLEN)
esp_err_t httpd_resp_send_err(httpd_req_t *,int,const char *);
ssize_t native_web_transport_send(httpd_handle_t,int,const void *,size_t,int,bool *);
ssize_t native_web_transport_recv(httpd_handle_t,int,void *,size_t,int,bool *);
void native_web_transport_prepare_close(httpd_handle_t,int,bool);
int64_t esp_timer_get_time(void);
int lwip_select(int,fd_set *,fd_set *,fd_set *,struct timeval *);
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
typedef unsigned portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(p) assert(!(*(p))++)
#define portEXIT_CRITICAL(p) assert((*(p))--==1)
#define pdPASS 1
#define pdTRUE 1
#define pdMS_TO_TICKS(v) (v)
#define portMAX_DELAY UINT32_MAX
void vTaskDelay(TickType_t);
TickType_t xTaskGetTickCount(void);
int xTaskCreate(void (*)(void *),const char *,unsigned,void *,unsigned,TaskHandle_t *);
void xTaskNotifyGive(TaskHandle_t);
unsigned ulTaskNotifyTake(int,TickType_t);
void vTaskDelete(TaskHandle_t);
void esp_restart(void);
typedef struct {uint64_t epoch;} audio_maintenance_token_t;
esp_err_t audio_service_maintenance_begin(uint32_t,audio_maintenance_token_t *);
esp_err_t audio_service_maintenance_end(audio_maintenance_token_t *,bool);
bool deep_sleep_clock_begin_activity(void);
void deep_sleep_clock_end_activity(void);
void display_settings_note_activity(void);
void *host_malloc(size_t);
void *host_calloc(size_t,size_t);
