#pragma once
#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define CHECK(c, tag) do { if (!(c)) { fprintf(stderr, "SEMANTIC_FAILURE:%s:%u\n", tag, __LINE__); exit(80); } } while (0)
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_NOT_FOUND 0x105
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_WIFI_NOT_CONNECT 0x300f
#define ESP_ERR_WIFI_STATE 0x3006
typedef int esp_err_t;
typedef int BaseType_t;
typedef unsigned UBaseType_t;
typedef uint32_t TickType_t;
#define BIT0 1U
#define BIT1 2U
#define pdTRUE 1
#define pdFALSE 0
#define pdPASS 1
#define pdMS_TO_TICKS(t) (t)
#define portMAX_DELAY UINT32_MAX
typedef struct test_sem *SemaphoreHandle_t;
typedef struct test_queue *QueueHandle_t;
typedef struct test_event *EventGroupHandle_t;
typedef struct test_task *TaskHandle_t;
typedef unsigned EventBits_t;
QueueHandle_t xQueueCreate(unsigned count, size_t size);
BaseType_t xQueueSend(QueueHandle_t queue, const void *value, TickType_t timeout);
BaseType_t xQueueReceive(QueueHandle_t queue, void *value, TickType_t timeout);
void vQueueDelete(QueueHandle_t queue);
SemaphoreHandle_t xSemaphoreCreateMutex(void);
BaseType_t xSemaphoreTake(SemaphoreHandle_t sem, TickType_t timeout);
BaseType_t xSemaphoreGive(SemaphoreHandle_t sem);
void vSemaphoreDelete(SemaphoreHandle_t sem);
EventGroupHandle_t xEventGroupCreate(void);
EventBits_t xEventGroupSetBits(EventGroupHandle_t group, EventBits_t bits);
EventBits_t xEventGroupWaitBits(EventGroupHandle_t group, EventBits_t bits,
    BaseType_t clear, BaseType_t all, TickType_t timeout);
void vEventGroupDelete(EventGroupHandle_t group);
BaseType_t xTaskCreatePinnedToCore(void (*entry)(void *), const char *name,
    unsigned stack, void *argument, unsigned priority, TaskHandle_t *out, int core);
void vTaskDelay(TickType_t ticks);
void vTaskDelete(TaskHandle_t task);

typedef const char *esp_event_base_t;
extern const char fixture_wifi_base[], fixture_ip_base[];
#define WIFI_EVENT fixture_wifi_base
#define IP_EVENT fixture_ip_base
#define ESP_EVENT_ANY_ID (-1)
#define WIFI_EVENT_STA_START 1
#define WIFI_EVENT_STA_CONNECTED 2
#define WIFI_EVENT_STA_DISCONNECTED 3
#define IP_EVENT_STA_GOT_IP 4
#define IP_EVENT_STA_LOST_IP 5
typedef void (*esp_event_handler_t)(void *, esp_event_base_t, int32_t, void *);
typedef void *esp_event_handler_instance_t;
typedef struct { uint32_t addr; } esp_ip4_addr_t;
typedef struct { esp_ip4_addr_t ip; } esp_netif_ip_info_t;
typedef struct esp_netif { unsigned identity; } esp_netif_t;
typedef struct { bool ap; } esp_netif_config_t;
#define ESP_NETIF_DEFAULT_WIFI_AP() {.ap = true}
#define ESP_NETIF_DEFAULT_WIFI_STA() {.ap = false}
typedef struct { esp_netif_t *esp_netif; esp_netif_ip_info_t ip_info; } ip_event_got_ip_t;
typedef struct { uint16_t reason; } wifi_event_sta_disconnected_t;
typedef struct { uint8_t ssid[33], bssid[6]; int8_t rssi; } wifi_ap_record_t;
typedef enum { WIFI_MODE_NULL, WIFI_MODE_STA, WIFI_MODE_AP, WIFI_MODE_APSTA } wifi_mode_t;
#define WIFI_IF_STA 0
#define WIFI_IF_AP 1
#define WIFI_AUTH_OPEN 0
#define ESP_MAC_WIFI_SOFTAP 0
typedef union {
    struct { uint8_t ssid[32], password[64]; struct { int authmode; } threshold;
             struct { bool capable, required; } pmf_cfg; } sta;
    struct { uint8_t ssid[32], ssid_len, channel, max_connection; int authmode; } ap;
} wifi_config_t;
int64_t esp_timer_get_time(void);
esp_err_t esp_read_mac(uint8_t *mac, int type);
esp_netif_t *esp_netif_create_default_wifi_ap(void);
void esp_netif_destroy_default_wifi(esp_netif_t *netif);
esp_netif_t *esp_netif_new(const esp_netif_config_t *config);
void esp_netif_destroy(esp_netif_t *netif);
esp_err_t esp_netif_attach_wifi_ap(esp_netif_t *netif);
esp_err_t esp_netif_attach_wifi_station(esp_netif_t *netif);
esp_err_t esp_wifi_set_default_wifi_ap_handlers(void);
esp_err_t esp_wifi_set_default_wifi_sta_handlers(void);
esp_err_t esp_wifi_clear_default_wifi_driver_and_handlers(esp_netif_t *netif);
bool esp_netif_is_netif_up(esp_netif_t *netif);
esp_err_t esp_netif_get_ip_info(esp_netif_t *netif, esp_netif_ip_info_t *info);
esp_err_t esp_wifi_set_mode(wifi_mode_t mode);
esp_err_t esp_wifi_set_config(int interface, wifi_config_t *config);
esp_err_t esp_wifi_connect(void);
esp_err_t esp_wifi_disconnect(void);
esp_err_t esp_wifi_sta_get_ap_info(wifi_ap_record_t *ap);
esp_err_t esp_event_handler_instance_register(esp_event_base_t base, int32_t id,
    esp_event_handler_t handler, void *arg, esp_event_handler_instance_t *instance);
esp_err_t esp_event_handler_instance_unregister(esp_event_base_t base, int32_t id,
    esp_event_handler_instance_t instance);
void time_service_notify_network(bool online);
size_t strlcpy(char *out, const char *in, size_t capacity);

enum fixture_api { API_MAC, API_MODE, API_STA_CONFIG, API_AP_CONFIG, API_CONNECT,
    API_DISCONNECT, API_AP_INFO, API_IP_INFO, API_REGISTER, API_UNREGISTER,
    API_ATTACH, API_DEFAULT_HANDLERS, API_CLEAR, API_COUNT };
typedef struct {
    unsigned queues, semaphores, events, ap_netifs, registrations;
    unsigned tasks, joins, api_calls[API_COUNT], config_rows[512], configs, connects;
    unsigned requested_stack, requested_priority;
    int requested_core;
    wifi_mode_t mode;
    bool started, associated, netif_up, time_online;
    unsigned time_true, time_false;
} fixture_stats_t;
void fixture_init(void);
void fixture_step(int64_t delta_us);
void fixture_release_step(int64_t delta_us);
void fixture_wait_parked(void);
void fixture_join(void);
fixture_stats_t fixture_stats(void);
void fixture_fail_alloc(unsigned nth);
void fixture_fail_api(enum fixture_api api, unsigned nth, esp_err_t error);
void fixture_fail_task(bool fail);
void fixture_hold_disconnect(bool hold);
void fixture_driver_stopped(void);
void fixture_set_clock(int64_t now);
void fixture_observe(bool associated, bool up, uint32_t ip, int8_t rssi, unsigned profile);
void fixture_emit(esp_event_base_t base, int id, esp_netif_t *netif, uint32_t ip);
void fixture_lock_snapshot(bool lock);
void fixture_block_ap_info(void);
void fixture_wait_ap_info(void);
void fixture_release_ap_info(void);
void fixture_block_send(void);
void fixture_wait_send(void);
void fixture_release_send(void);
void fixture_block_unregister(void);
void fixture_wait_unregister(void);
void fixture_release_unregister(void);
