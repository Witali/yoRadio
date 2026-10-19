/* Deterministic function-body seams, not SDK layout or RTOS implementation. */
#include <assert.h>
#include <setjmp.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_NOT_FOUND 0x105
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_RETURN_ON_FALSE(v, e, ...) do { if (!(v)) return (e); } while (0)
#define ESP_RETURN_ON_ERROR(v, ...) do { int r_ = (v); if (r_) return r_; } while (0)
#define pdMS_TO_TICKS(x) (x)
#define pdTRUE 1
#define pdFALSE 0
#define pdPASS 1
#define BIT0 1U
#define BIT1 2U
#define BOARD_TASK_STACK_WIFI_RSSI 3072
#define WIFI_EVENT_STA_START 1
#define WIFI_EVENT_STA_DISCONNECTED 2
#define IP_EVENT_STA_GOT_IP 3
#define IP_EVENT_STA_LOST_IP 4
#define ESP_EVENT_ANY_ID (-1)
#define WIFI_IF_STA 0
#define WIFI_IF_AP 1
#define WIFI_AUTH_OPEN 0
#define WIFI_STORAGE_RAM 1
#define ESP_MAC_WIFI_SOFTAP 0

typedef int esp_err_t;
typedef const char *esp_event_base_t;
static const char wifi_base[] = "wifi", ip_base[] = "ip";
#define WIFI_EVENT wifi_base
#define IP_EVENT ip_base
typedef enum { WIFI_MODE_NULL, WIFI_MODE_STA, WIFI_MODE_AP,
               WIFI_MODE_APSTA } wifi_mode_t;
typedef enum { WIFI_PS_NONE, WIFI_PS_MIN_MODEM } wifi_ps_type_t;
typedef enum { NATIVE_NETWORK_STARTING, NATIVE_NETWORK_CLIENT,
               NATIVE_NETWORK_ACCESS_POINT } native_network_mode_t;
typedef struct { native_network_mode_t mode; uint32_t ip; int rssi; } native_state_t;
typedef union {
    struct {
        uint8_t ssid[32], password[64];
        struct { int authmode; } threshold;
        struct { bool capable, required; } pmf_cfg;
    } sta;
    struct { uint8_t ssid[32]; size_t ssid_len; int channel, max_connection,
             authmode; } ap;
} wifi_config_t;
typedef struct { struct { struct { uint32_t addr; } ip; } ip_info; } ip_event_got_ip_t;
typedef struct { int8_t rssi; } wifi_ap_record_t;
typedef struct { int unused; } wifi_init_config_t;
#define WIFI_INIT_CONFIG_DEFAULT() ((wifi_init_config_t){0})
typedef unsigned EventBits_t;
typedef struct { void (*callback)(void *); const char *name; } esp_timer_create_args_t;

static native_state_t state, *s_state;
static int s_wifi_events, s_retries;
static void *s_station_netif, *s_ap_netif, *s_softap_reboot_timer;
static bool s_have_credentials;
static wifi_config_t s_station_config, s_credentials[5], driver_config;
static size_t s_credential_count, s_credential_index;
static atomic_bool s_stopping_for_sleep;
static unsigned event_bits, connects, ap_calls, delays, waits, starts;
static unsigned rssi_tasks, restart_calls, timer_starts, timer_stops;
static unsigned power_calls, hostname_calls;
static wifi_mode_t driver_mode;
static wifi_ps_type_t driver_ps;
static int query_result, config_result;
static uint8_t configured_ap_delay;
static bool driver_ram, time_ready, task_polling;
static bool startup_timeout;
static jmp_buf poll_exit;
static void event_handler(void *, esp_event_base_t, int32_t, void *);

static void native_state_set_network(native_state_t *s, native_network_mode_t mode,
                                     uint32_t ip) { s->mode = mode; s->ip = ip; }
static void native_state_set_wifi_rssi(native_state_t *s, int rssi) { s->rssi = rssi; }
static void time_service_notify_network(bool ready) { time_ready = ready; }
static void time_service_notify_network_ready(void) { time_ready = true; }
static const char *esp_err_to_name(int e) { (void)e; return "modeled"; }
static esp_err_t network_service_storage_init(void) { return ESP_OK; }
static int xEventGroupCreate(void) { return 1; }
static void xEventGroupClearBits(int handle, unsigned bits) {
    assert(handle == 1); event_bits &= ~bits;
}
static void xEventGroupSetBits(int handle, unsigned bits) {
    assert(handle == 1); event_bits |= bits;
}
static EventBits_t xEventGroupWaitBits(int handle, unsigned bits, int clear,
                                     int all, unsigned timeout) {
    assert(handle == 1 && bits == 3U && clear == pdTRUE && all == pdFALSE);
    assert(timeout == 20000U); ++waits;
    if (startup_timeout) return 0;
    ip_event_got_ip_t ip = {.ip_info.ip.addr = 0x01020304};
    event_handler(NULL, IP_EVENT, IP_EVENT_STA_GOT_IP, &ip);
    unsigned result = event_bits & bits;
    event_bits &= ~bits;
    return result;
}
static esp_err_t esp_netif_init(void) { return ESP_OK; }
static esp_err_t esp_event_loop_create_default(void) { return ESP_OK; }
static void *esp_netif_create_default_wifi_sta(void) { return &s_station_netif; }
static void *esp_netif_create_default_wifi_ap(void) { return &s_ap_netif; }
static esp_err_t esp_netif_set_hostname(void *netif, const char *hostname) {
    assert(netif && !strcmp(hostname, "yoradio")); ++hostname_calls; return ESP_OK;
}
static esp_err_t esp_event_handler_register(esp_event_base_t base, int id,
    void (*handler)(void *, esp_event_base_t, int32_t, void *), void *argument) {
    assert(handler == event_handler && !argument);
    assert((base == WIFI_EVENT && id == ESP_EVENT_ANY_ID) ||
           (base == IP_EVENT && (id == ESP_EVENT_ANY_ID || id == IP_EVENT_STA_GOT_IP)));
    return ESP_OK;
}
static esp_err_t esp_wifi_init(const wifi_init_config_t *init) { assert(init); return ESP_OK; }
static esp_err_t esp_wifi_set_storage(int storage) {
    assert(storage == WIFI_STORAGE_RAM); driver_ram = true; return ESP_OK;
}
static esp_err_t esp_wifi_connect(void) { ++connects; return ESP_OK; }
static esp_err_t esp_wifi_get_mode(wifi_mode_t *mode) { *mode = driver_mode; return ESP_OK; }
static esp_err_t esp_wifi_set_mode(wifi_mode_t mode) {
    if (mode == WIFI_MODE_APSTA) ++ap_calls;
    driver_mode = mode; return ESP_OK;
}
static esp_err_t esp_wifi_set_config(int interface, wifi_config_t *config) {
    assert(interface == WIFI_IF_STA || interface == WIFI_IF_AP);
    if (interface == WIFI_IF_STA && !config_result) driver_config = *config;
    return interface == WIFI_IF_STA ? config_result : ESP_OK;
}
static esp_err_t esp_wifi_set_ps(wifi_ps_type_t mode) {
    ++power_calls; driver_ps = mode; return ESP_OK;
}
static esp_err_t esp_wifi_sta_get_ap_info(wifi_ap_record_t *record) {
    if (!query_result) record->rssi = -55;
    return query_result;
}
static esp_err_t esp_wifi_start(void) {
    ++starts; event_handler(NULL, WIFI_EVENT, WIFI_EVENT_STA_START, NULL); return ESP_OK;
}
static esp_err_t esp_read_mac(uint8_t *mac, int type) {
    assert(type == ESP_MAC_WIFI_SOFTAP); memset(mac, 0, 6); return ESP_OK;
}
static void runtime_settings_get_mdns_name(char *out, size_t capacity) {
    assert(capacity >= sizeof("yoradio")); memcpy(out, "yoradio", sizeof("yoradio"));
}
static uint8_t runtime_settings_get_softap_delay_min(void) { return configured_ap_delay; }
static esp_err_t esp_timer_create(const esp_timer_create_args_t *args, void **timer) {
    assert(args && args->callback && !strcmp(args->name, "softap_reboot"));
    *timer = &s_softap_reboot_timer; return ESP_OK;
}
static esp_err_t esp_timer_start_once(void *timer, uint64_t delay) {
    assert(timer && delay == (uint64_t)configured_ap_delay * 60U * 1000000U);
    ++timer_starts; return ESP_OK;
}
static void esp_restart(void) { ++restart_calls; }
static int xTaskCreate(void (*task)(void *), const char *name, unsigned stack,
                       void *argument, unsigned priority, void *handle) {
    assert(task && !strcmp(name, "wifi_rssi") && stack == BOARD_TASK_STACK_WIFI_RSSI);
    assert(!argument && priority == 2U && !handle); ++rssi_tasks; return pdPASS;
}
static void vTaskDelay(unsigned delay) {
    assert(task_polling && delay == 2000U);
    if (delays++) longjmp(poll_exit, 1);
}
static bool read_credentials(wifi_config_t *config) {
    /* Loader is a seam: profile parsing and private storage have separate suites. */
    assert(s_credential_count > 0); *config = s_credentials[0]; return true;
}
