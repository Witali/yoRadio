#pragma once
#define _GNU_SOURCE
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <setjmp.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>

#include "websocket_message.h"
#include "json_buffer.h"

typedef int esp_err_t;
typedef void *httpd_handle_t;
typedef void *SemaphoreHandle_t;
typedef uint32_t TickType_t;
typedef enum {HTTPD_WS_TYPE_TEXT=1,HTTPD_WS_TYPE_CLOSE=8} httpd_ws_type_t;
typedef struct {bool final,fragmented;httpd_ws_type_t type;uint8_t *payload;size_t len;} httpd_ws_frame_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_INVALID_ARG 0x102
#define HTTPD_WS_CLIENT_WEBSOCKET 2
#define CONFIG_LWIP_MAX_SOCKETS 4
#define CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT 1
#define CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT 1
#define CONFIG_HTTPD_QUEUE_WORK_BLOCKING 0
#define pdMS_TO_TICKS(ms) ((TickType_t)(ms))
static unsigned profile_logs;
static void host_log(const char *tag,const char *format,...){assert(tag&&format);if(strstr(format,"PERF WS:"))profile_logs++;}
#define ESP_LOGI(...) host_log(__VA_ARGS__)
static size_t strlcpy(char *out,const char *in,size_t cap){size_t n=strlen(in);if(cap){size_t take=n<cap-1?n:cap-1;memcpy(out,in,take);out[take]=0;}return n;}

static TickType_t ticks;
static int64_t monotonic_us;
static unsigned reboot_polls,probe_polls;
static unsigned cycle,budget;
static void(*before_cycle)(unsigned);
static jmp_buf loop_exit;
static bool in_httpd;
static TickType_t xTaskGetTickCount(void){return ticks;}
static int64_t esp_timer_get_time(void){return monotonic_us;}
static void vTaskDelay(TickType_t delay){assert(delay==100&&!in_httpd);if(++cycle>budget)longjmp(loop_exit,1);ticks+=delay;monotonic_us+=INT64_C(100000);if(before_cycle)before_cycle(cycle);}
static void poll_reboot(void){reboot_polls++;}
static void web_tcp_probe_poll(void){probe_polls++;}

static uint8_t fixture_volume=80,fixture_fill=37;
static int8_t fixture_balance=-2;
static uint16_t fixture_item=1;
static bool fixture_uppercase;
static char fixture_name[144]="station one";
static uint8_t native_audio_output_get_volume(void){return fixture_volume;}
static int8_t native_audio_output_get_balance(void){return fixture_balance;}
static uint8_t audio_service_buffer_fill_percent(void){return fixture_fill;}
static uint16_t radio_control_current_item(void){return fixture_item;}
static bool display_settings_get_station_uppercase(void){return fixture_uppercase;}
static void radio_control_current_name(char *out,size_t cap){strlcpy(out,fixture_name,cap);}

static esp_err_t httpd_queue_work(httpd_handle_t server,void(*callback)(void*),void *arg);
static esp_err_t httpd_get_client_list(httpd_handle_t server,size_t *count,int *sockets);
static int httpd_ws_get_fd_info(httpd_handle_t server,int socket);
static void *httpd_sess_get_ctx(httpd_handle_t server,int socket);
static esp_err_t httpd_ws_send_frame_async(httpd_handle_t server,int socket,httpd_ws_frame_t *frame);
static void native_web_transport_shutdown(httpd_handle_t server,int socket,bool graceful);
