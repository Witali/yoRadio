#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "board_config.h"

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_RETURN_ON_ERROR(expr, ...) do { int e_ = (expr); if (e_) return e_; } while (0)
#define ESP_RETURN_ON_FALSE(expr, err, ...) do { if (!(expr)) return (err); } while (0)
#define ESP_ERROR_CHECK(expr) assert((expr) == ESP_OK)
static void log_message(const char *tag, const char *format, ...) {(void)tag; (void)format;}
#define ESP_LOGI(...) log_message(__VA_ARGS__)
#define ESP_LOGW(...) log_message(__VA_ARGS__)
#define ESP_LOGE(...) log_message(__VA_ARGS__)
static const char *const TAG = "fixture";
static const char *esp_err_to_name(int error) {(void)error; return "fixture";}

typedef enum {NATIVE_NETWORK_STARTING, NATIVE_NETWORK_CLIENT,
              NATIVE_NETWORK_ACCESS_POINT, NATIVE_NETWORK_ERROR} native_network_mode_t;
typedef struct {native_network_mode_t mode; uint32_t ip;} native_state_t;
static native_state_t s_app_state, *s_network_state;
static int s_display;
static void native_state_init(native_state_t *state) {memset(state, 0, sizeof(*state));}
static void native_state_set_network(native_state_t *state, native_network_mode_t mode, uint32_t ip) {
    state->mode = mode; state->ip = ip;
}
typedef const char *esp_event_base_t;
static const char wifi_base[] = "wifi", ip_base[] = "ip";
#define WIFI_EVENT wifi_base
#define IP_EVENT ip_base
#define WIFI_EVENT_STA_START 1
#define WIFI_EVENT_STA_DISCONNECTED 2
#define IP_EVENT_STA_GOT_IP 3
#define IP_EVENT_STA_LOST_IP 4
#define ESP_EVENT_ANY_ID (-1)
typedef enum {WIFI_MODE_NULL, WIFI_MODE_STA, WIFI_MODE_AP, WIFI_MODE_APSTA} wifi_mode_t;
#define WIFI_IF_STA 0
#define WIFI_AUTH_OPEN 0
#define IPSTR "%u"
#define IP2STR(ip) ((unsigned)(ip)->addr)
typedef struct {struct {struct {uint32_t addr;} ip;} ip_info;} ip_event_got_ip_t;
typedef struct {struct {uint8_t ssid[32], password[64];
    struct {int authmode;} threshold; struct {bool capable, required;} pmf_cfg;} sta;} wifi_config_t;
typedef struct {int unused;} wifi_init_config_t;
#define WIFI_INIT_CONFIG_DEFAULT() ((wifi_init_config_t){0})
static wifi_config_t s_station_config;
static void *s_station_netif;
static bool s_have_credentials, configured_credentials;
static int s_retries;
#define WIFI_MAX_RETRIES 8
#define WIFI_CONNECTED_BIT 1U
#define WIFI_FAILED_BIT 2U
#define pdTRUE 1
#define pdFALSE 0
#define pdMS_TO_TICKS(ms) (ms)
typedef uint32_t EventBits_t;
static unsigned s_wifi_events, event_bits, startup_wait_bits;
static int sdk_calls, fail_sdk_at, registered_ip_id;
static unsigned connect_calls, ap_calls, time_notices, groups;
static bool time_ready, mode_error;
static wifi_mode_t mode;
static void event_handler(void *, esp_event_base_t, int32_t, void *);
static int sdk_result(void) {return ++sdk_calls == fail_sdk_at ? ESP_FAIL : ESP_OK;}
static int network_service_storage_init(void) {return sdk_result();}
static unsigned xEventGroupCreate(void) {return sdk_result() == ESP_OK ? 1U : 0U;}
static unsigned xEventGroupSetBits(unsigned handle, unsigned bits) {assert(handle == 1U); event_bits |= bits; return event_bits;}
static unsigned xEventGroupClearBits(unsigned handle, unsigned bits) {assert(handle == 1U); event_bits &= ~bits; return event_bits;}
static unsigned xEventGroupWaitBits(unsigned handle, unsigned bits, int clear, int all, unsigned timeout) {
    assert(handle == 1U && bits == 3U && clear == pdTRUE && all == pdFALSE && timeout == 20000U);
    return startup_wait_bits;
}
static int esp_netif_init(void) {return sdk_result();}
static int esp_event_loop_create_default(void) {return sdk_result();}
static void *esp_netif_create_default_wifi_sta(void) {return sdk_result() == ESP_OK ? &s_display : NULL;}
static int esp_wifi_init(const wifi_init_config_t *init) {assert(init); return sdk_result();}
static int esp_event_handler_register(esp_event_base_t base, int32_t id,
                                      void (*handler)(void *, esp_event_base_t, int32_t, void *), void *context) {
    assert(handler == event_handler && !context);
    if (base == IP_EVENT) registered_ip_id = id;
    else assert(base == WIFI_EVENT && id == ESP_EVENT_ANY_ID);
    return sdk_result();
}
static bool read_credentials(wifi_config_t *config) {memset(config, 0, sizeof(*config)); return configured_credentials;}
static int esp_wifi_set_mode(wifi_mode_t desired) {mode = desired; return sdk_result();}
static int esp_wifi_get_mode(wifi_mode_t *out) {*out = mode; return mode_error ? ESP_FAIL : ESP_OK;}
static int esp_wifi_set_config(int interface, const wifi_config_t *config) {assert(interface == WIFI_IF_STA && config); return sdk_result();}
static int esp_wifi_start(void) {return sdk_result();}
static int esp_wifi_connect(void) {++connect_calls; return ESP_OK;}
static int start_access_point(void) {++ap_calls; mode = WIFI_MODE_APSTA; return ESP_OK;}
static void time_service_notify_network(bool available) {time_ready = available; ++time_notices;}

#define s_state s_network_state
#include "network.inc"
#undef s_state

static unsigned startup_step, display_step, time_step, pinned_step[2], pinned_count;
static int time_start_error, nvs_error, spiffs_error;
static bool health_ok;
typedef struct {const char *base_path, *partition_label; int max_files; bool format_if_mount_failed;} esp_vfs_spiffs_conf_t;
static int esp_vfs_spiffs_register(const esp_vfs_spiffs_conf_t *config) {
    assert(!strcmp(config->base_path, "/spiffs") && !strcmp(config->partition_label, "spiffs"));
    assert(config->max_files == 8 && !config->format_if_mount_failed);
    return spiffs_error;
}
static int nvs_flash_init(void) {++startup_step; return nvs_error;}
static int native_audio_settings_init(void) {++startup_step; return ESP_OK;}
static bool native_health_start(void) {++startup_step; return health_ok;}
static int cyd_display_init(int *display) {assert(display == &s_display); display_step = ++startup_step; return ESP_OK;}
static int time_service_start(void) {time_step = ++startup_step; return time_start_error;}
static void display_task(void *context) {(void)context;}
static void network_task(void *context) {(void)context;}
static int xTaskCreatePinnedToCore(void (*task)(void *), const char *name,
                                  unsigned stack, void *context, unsigned priority, void *handle, int core) {
    assert(!context && !handle && pinned_count < 2U);
    pinned_step[pinned_count++] = ++startup_step;
    if (task == display_task) {
        assert(!strcmp(name, "display") && stack == BOARD_TASK_STACK_DISPLAY && priority == 1U && core == 0);
    } else {
        assert(task == network_task && !strcmp(name, "network") && stack == BOARD_TASK_STACK_NETWORK && priority == 3U && core == 0);
    }
    return pdTRUE;
}
#define s_state s_app_state
#include "startup.inc"
#undef s_state

static void reset(void) {
    sdk_calls = fail_sdk_at = s_retries = 0; registered_ip_id = 999;
    s_wifi_events = 1U; event_bits = startup_wait_bits = 0;
    connect_calls = ap_calls = time_notices = 0; time_ready = false;
    s_have_credentials = configured_credentials = mode_error = false; mode = WIFI_MODE_STA;
    s_network_state = &s_app_state; native_state_init(&s_app_state);
    startup_step = display_step = time_step = pinned_count = 0;
    time_start_error = nvs_error = spiffs_error = 0; health_ok = true;
}

int main(void) {
    reset();
    assert(network_service_start(&s_app_state) == ESP_OK && ap_calls == 1U);
    assert(registered_ip_id == ESP_EVENT_ANY_ID && !time_notices); ++groups;
    reset(); configured_credentials = true; startup_wait_bits = WIFI_CONNECTED_BIT;
    assert(network_service_start(&s_app_state) == ESP_OK && !ap_calls && !time_notices);
    assert(registered_ip_id == ESP_EVENT_ANY_ID); ++groups;
    reset(); configured_credentials = true; startup_wait_bits = WIFI_FAILED_BIT;
    assert(network_service_start(&s_app_state) == ESP_OK && ap_calls == 1U && !time_notices); ++groups;
    for (int failure = 1; failure <= 11; ++failure) {
        reset(); configured_credentials = true; fail_sdk_at = failure;
        assert(network_service_start(&s_app_state) != ESP_OK && !time_notices); ++groups;
    }
    const wifi_mode_t modes[] = {WIFI_MODE_STA, WIFI_MODE_AP, WIFI_MODE_APSTA, WIFI_MODE_NULL};
    for (unsigned i = 0; i < sizeof(modes) / sizeof(modes[0]); ++i) {
        reset(); mode = modes[i]; event_bits = WIFI_FAILED_BIT;
        ip_event_got_ip_t event = {.ip_info.ip.addr = UINT32_C(0x01020304)};
        event_handler(NULL, IP_EVENT, IP_EVENT_STA_GOT_IP, &event);
        assert(time_ready && time_notices == 1U && s_app_state.ip == event.ip_info.ip.addr);
        assert(s_app_state.mode == NATIVE_NETWORK_CLIENT && event_bits == WIFI_CONNECTED_BIT);
        event_handler(NULL, WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL);
        assert(!time_ready && time_notices == 2U && !s_app_state.ip);
        assert(!(event_bits & WIFI_CONNECTED_BIT));
        assert(s_app_state.mode == ((mode == WIFI_MODE_AP || mode == WIFI_MODE_APSTA)
                                   ? NATIVE_NETWORK_ACCESS_POINT : NATIVE_NETWORK_STARTING)); ++groups;
        event_handler(NULL, IP_EVENT, IP_EVENT_STA_GOT_IP, &event);
        event_handler(NULL, IP_EVENT, IP_EVENT_STA_LOST_IP, NULL);
        assert(!time_ready && !s_app_state.ip && !(event_bits & WIFI_CONNECTED_BIT)); ++groups;
    }
    reset(); mode_error = true; s_app_state.ip = UINT32_MAX;
    event_handler(NULL, IP_EVENT, IP_EVENT_STA_LOST_IP, NULL);
    assert(!time_ready && !s_app_state.ip && s_app_state.mode == NATIVE_NETWORK_STARTING); ++groups;
    reset(); s_have_credentials = true;
    event_handler(NULL, WIFI_EVENT, WIFI_EVENT_STA_START, NULL);
    for (unsigned i = 0; i < 9U; ++i) event_handler(NULL, WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL);
    assert(connect_calls == 9U && event_bits == WIFI_FAILED_BIT && !time_ready); ++groups;
    reset(); event_handler(NULL, IP_EVENT, 999, NULL);
    assert(!time_notices && !connect_calls && !event_bits); ++groups;
    for (unsigned failure = 0; failure < 5U; ++failure) {
        reset(); time_start_error = failure == 1U ? ESP_ERR_NO_MEM : 0;
        nvs_error = failure == 2U ? ESP_FAIL : 0; spiffs_error = failure == 3U ? ESP_FAIL : 0;
        health_ok = failure != 4U;
        app_main();
        assert(pinned_count == 2U && time_step > display_step && time_step < pinned_step[0]);
        assert(pinned_step[0] < pinned_step[1] && !time_notices); ++groups;
    }
    printf("PASS CYD time/network startup: %u groups; actual startup/events and SDK subscription, offline initialization, loss/reconnect/AP state, retained task affinity; platform seams only\n", groups);
    return 0;
}
