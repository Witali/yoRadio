#pragma once
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <time.h>
#define CHECK(c,m) do { if (!(c)) { fprintf(stderr,"SEMANTIC_FAILURE:%s:%u\n",m,__LINE__); exit(80); } } while(0)
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_NOT_FOUND 0x105
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_NVS_NOT_FOUND 0x1102
#define ESP_ERR_WIFI_NOT_CONNECT 0x300f
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_RETURN_ON_ERROR(c,...) do { int e_=(c); if(e_)return e_; } while(0)
#define ESP_RETURN_ON_FALSE(c,e,...) do { if(!(c))return (e); } while(0)
typedef uint32_t TickType_t;
typedef unsigned EventBits_t;
typedef int EventGroupHandle_t;
typedef void *SemaphoreHandle_t;
#define pdMS_TO_TICKS(t) (t)
#define configTICK_RATE_HZ 1000U
#define portMAX_DELAY UINT32_MAX
#define pdTRUE 1
#define pdFALSE 0
#define pdPASS 1
#define BIT0 1U
#define BIT1 2U
#define BOARD_TASK_STACK_WIFI_RSSI 2048
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(l) CHECK(!pthread_mutex_lock(l),"critical_enter")
#define portEXIT_CRITICAL(l) CHECK(!pthread_mutex_unlock(l),"critical_leave")
SemaphoreHandle_t xSemaphoreCreateMutex(void);
int xSemaphoreTake(SemaphoreHandle_t sem,TickType_t ticks);
void xSemaphoreGive(SemaphoreHandle_t sem);
int xEventGroupCreate(void);
void xEventGroupSetBits(int handle,unsigned bits);
void xEventGroupClearBits(int handle,unsigned bits);
unsigned xEventGroupWaitBits(int handle,unsigned bits,int clear,int all,unsigned timeout);
int xTaskCreate(void (*entry)(void *),const char *name,unsigned stack,void *arg,unsigned priority,void *handle);
void vTaskDelay(unsigned ticks);
typedef const char *esp_event_base_t;
extern const char wifi_base[],ip_base[];
#define WIFI_EVENT wifi_base
#define IP_EVENT ip_base
#define WIFI_EVENT_STA_START 1
#define WIFI_EVENT_STA_CONNECTED 2
#define WIFI_EVENT_STA_DISCONNECTED 3
#define IP_EVENT_STA_GOT_IP 4
#define IP_EVENT_STA_LOST_IP 5
#define ESP_EVENT_ANY_ID (-1)
#define WIFI_IF_STA 0
#define WIFI_IF_AP 1
#define WIFI_AUTH_OPEN 0
#define WIFI_STORAGE_RAM 1
#define ESP_MAC_WIFI_SOFTAP 0
typedef struct { unsigned identity; } esp_netif_t;
typedef struct { struct {uint32_t addr;} ip; } esp_netif_ip_info_t;
typedef struct {esp_netif_ip_info_t ip_info;} ip_event_got_ip_t;
typedef struct {int8_t rssi;} wifi_ap_record_t;
typedef enum {WIFI_MODE_NULL,WIFI_MODE_STA,WIFI_MODE_AP,WIFI_MODE_APSTA} wifi_mode_t;
typedef enum {WIFI_PS_NONE,WIFI_PS_MIN_MODEM} wifi_ps_type_t;
typedef union {
 struct {uint8_t ssid[32],password[64];struct{int authmode;}threshold;struct{bool capable,required;}pmf_cfg;}sta;
 struct {uint8_t ssid[32];size_t ssid_len;int channel,max_connection,authmode;}ap;
} wifi_config_t;
typedef struct {int unused;}wifi_init_config_t;
#define WIFI_INIT_CONFIG_DEFAULT() ((wifi_init_config_t){0})
typedef enum {NATIVE_NETWORK_STARTING,NATIVE_NETWORK_CLIENT,NATIVE_NETWORK_ACCESS_POINT}native_network_mode_t;
typedef struct {native_network_mode_t mode;uint32_t ip;int rssi;}native_state_t;
void native_state_set_network(native_state_t *s,native_network_mode_t mode,uint32_t ip);
void native_state_set_wifi_rssi(native_state_t *s,int rssi);
void time_service_notify_network_ready(void);
void native_network_power_poll(int64_t now,esp_err_t(*apply)(void *,bool),void *context);
void native_network_power_invalidate(void);
int64_t esp_timer_get_time(void);
esp_err_t esp_netif_init(void);
esp_err_t esp_event_loop_create_default(void);
esp_netif_t *esp_netif_create_default_wifi_sta(void);
esp_netif_t *esp_netif_create_default_wifi_ap(void);
esp_err_t esp_netif_set_hostname(esp_netif_t *netif,const char *hostname);
bool esp_netif_is_netif_up(esp_netif_t *netif);
esp_err_t esp_netif_get_ip_info(esp_netif_t *netif,esp_netif_ip_info_t *info);
esp_err_t esp_wifi_init(const wifi_init_config_t *config);
esp_err_t esp_wifi_set_storage(int storage);
esp_err_t esp_wifi_set_mode(wifi_mode_t mode);
esp_err_t esp_wifi_get_mode(wifi_mode_t *mode);
esp_err_t esp_wifi_set_config(int iface,wifi_config_t *config);
esp_err_t esp_wifi_start(void);
esp_err_t esp_wifi_stop(void);
esp_err_t esp_wifi_connect(void);
esp_err_t esp_wifi_disconnect(void);
esp_err_t esp_wifi_set_ps(wifi_ps_type_t mode);
esp_err_t esp_wifi_sta_get_ap_info(wifi_ap_record_t *ap);
esp_err_t esp_read_mac(uint8_t *mac,int type);
typedef void(*event_handler_t)(void *,esp_event_base_t,int32_t,void *);
esp_err_t esp_event_handler_register(esp_event_base_t base,int id,event_handler_t handler,void *arg);
typedef void*esp_timer_handle_t;
typedef struct {void(*callback)(void*);const char *name;}esp_timer_create_args_t;
esp_err_t esp_timer_create(const esp_timer_create_args_t *args,esp_timer_handle_t *timer);
esp_err_t esp_timer_start_once(esp_timer_handle_t timer,uint64_t delay);
void esp_restart(void);
bool deep_sleep_clock_begin_activity(void);
void deep_sleep_clock_end_activity(void);
typedef struct{uint64_t epoch;}websocket_reboot_lease_t;
esp_err_t websocket_service_reboot_reserve(websocket_reboot_lease_t *lease);
esp_err_t websocket_service_reboot_cancel(websocket_reboot_lease_t *lease);
esp_err_t websocket_service_reboot_restart_reserved_now(websocket_reboot_lease_t *lease);
typedef unsigned nvs_handle_t;
#define NVS_READWRITE 1
esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle);
void nvs_close(nvs_handle_t handle);
esp_err_t nvs_commit(nvs_handle_t handle);
esp_err_t nvs_set_u8(nvs_handle_t handle,const char *key,uint8_t value);
esp_err_t nvs_set_i8(nvs_handle_t handle,const char *key,int8_t value);
esp_err_t nvs_set_u16(nvs_handle_t handle,const char *key,uint16_t value);
esp_err_t nvs_set_str(nvs_handle_t handle,const char *key,const char *value);
esp_err_t nvs_get_u8(nvs_handle_t handle,const char *key,uint8_t *value);
esp_err_t nvs_get_i8(nvs_handle_t handle,const char *key,int8_t *value);
esp_err_t nvs_get_u16(nvs_handle_t handle,const char *key,uint16_t *value);
esp_err_t nvs_get_str(nvs_handle_t handle,const char *key,char *value,size_t *size);
size_t strlcpy(char *out,const char *in,size_t capacity);
enum api {QUERY,IP_QUERY,GET_MODE,AP_MODE,AP_CONFIG,CONNECT,DISCONNECT,STOP,RESERVE,API_COUNT};
typedef struct {unsigned restarts,reserves,cancels,immediates,connects,disconnects,power,rssi,activities;bool reserved,pending,sleep;uint8_t saved;}stats_t;
stats_t fixture_stats(void);
void fixture_init(void);
void fixture_step(int64_t delta);
void fixture_release_step(int64_t delta);
void fixture_parked(void);
void fixture_finish(void);
void fixture_emit(esp_event_base_t base,int id);
void fixture_observe(bool associated,bool up,uint32_t ip);
void fixture_failure(enum api api,bool fail);
void fixture_nvs_failure(unsigned stage);
void fixture_lock_failure(bool fail);
void fixture_lease(bool held);
bool fixture_sleep_claim(void);
void fixture_sleep_release(void);
void fixture_clock(int64_t now);
void fixture_block(enum api api);
void fixture_wait_blocked(void);
void fixture_release_blocked(void);
void fixture_fire_timer(void);
