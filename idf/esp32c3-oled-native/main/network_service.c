#include "network_service.h"

#include <stdio.h>
#include <stdatomic.h>
#include <string.h>

#include "board_config.h"
#include "esp_event.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_random.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "runtime_settings.h"
#include "time_service.h"
#include "web_tcp_probe.h"
#include "web_upload.h"
#include "file_transaction.h"
#include "credential_line.h"
#include "native_wifi_file.h"
#include "native_network_power.h"
#include "deep_sleep_clock.h"
#include "websocket_service.h"

#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAILED_BIT BIT1
#define WIFI_RETRIES_PER_CREDENTIAL 2
#define WIFI_MAX_CREDENTIALS 5
#define WIFI_RSSI_INTERVAL_MS 2000

static const char *const TAG = "network";
static EventGroupHandle_t s_wifi_events;
static esp_netif_t *s_station_netif;
static esp_netif_t *s_ap_netif;
static native_state_t *s_state;
static wifi_config_t s_station_config;
static wifi_config_t s_credentials[WIFI_MAX_CREDENTIALS];
static size_t s_credential_count;
static size_t s_credential_index;
static int s_retries;
static bool s_have_credentials;
static atomic_bool s_stopping_for_sleep;

// AP expiry has one deadline owner: the existing RSSI task. These short facts
// describe concurrent SDK operations; SDK calls never run under this mux.
typedef struct {
    uint64_t version;
    unsigned operations;
    bool valid, started, enabled, online, pending;
    int64_t pending_until;
} softap_facts_t;
typedef struct {
    bool armed, saturated;
    uint32_t revision;
    uint64_t version;
    int64_t deadline;
} softap_policy_t;
static portMUX_TYPE s_softap_lock = portMUX_INITIALIZER_UNLOCKED;
static softap_facts_t s_softap = {.valid = true};

static int64_t softap_after(int64_t now, int64_t interval) {
    return now > INT64_MAX - interval ? INT64_MAX : now + interval;
}
static void softap_changed_locked(void) {
    if (s_softap.version == UINT64_MAX) s_softap.valid = false;
    else ++s_softap.version;
}
static void softap_operation(bool begin) {
    portENTER_CRITICAL(&s_softap_lock);
    if (begin) ++s_softap.operations; else --s_softap.operations;
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
}
static softap_facts_t softap_snapshot(void) {
    portENTER_CRITICAL(&s_softap_lock);
    softap_facts_t facts = s_softap;
    portEXIT_CRITICAL(&s_softap_lock);
    return facts;
}
static void softap_link(bool online, bool pending) {
    int64_t now = esp_timer_get_time();
    portENTER_CRITICAL(&s_softap_lock);
    s_softap.online = online;
    s_softap.pending = pending;
    s_softap.pending_until = softap_after(now, 20000000LL);
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
}
static esp_err_t connect_station(void) {
    softap_link(false, true);
    esp_err_t result = esp_wifi_connect();
    if (result != ESP_OK) softap_link(false, false);
    return result;
}
static bool softap_current(const softap_facts_t *facts, uint32_t revision) {
    softap_facts_t current = softap_snapshot();
    runtime_softap_settings_t desired = runtime_settings_get_softap_snapshot();
    return facts->version == current.version && current.valid &&
        current.started && current.enabled && !current.online && !current.operations &&
        !atomic_load(&s_stopping_for_sleep) && desired.revision == revision && desired.delay_min;
}
static bool softap_disconnected(const softap_facts_t *facts, uint32_t revision) {
    if (!softap_current(facts, revision)) return false;
    wifi_ap_record_t ap = {0};
    wifi_mode_t mode = WIFI_MODE_NULL;
    esp_netif_ip_info_t info = {0};
    return esp_wifi_get_mode(&mode) == ESP_OK && mode == WIFI_MODE_APSTA &&
        esp_wifi_sta_get_ap_info(&ap) == ESP_ERR_WIFI_NOT_CONNECT &&
        !esp_netif_is_netif_up(s_station_netif) &&
        esp_netif_get_ip_info(s_station_netif, &info) == ESP_OK && !info.ip.addr &&
        softap_current(facts, revision);
}
static bool softap_live(const softap_facts_t *facts, uint32_t revision, int64_t now) {
    return now >= 0 && !facts->pending && softap_disconnected(facts, revision);
}
static void softap_cancel_pending(const softap_facts_t *facts, uint32_t revision, int64_t now) {
    // A grace deadline is not proof that the SDK finished an async connect.
    // Cancel only after live disconnected proof, then require a fresh interval.
    if (now < facts->pending_until || !softap_disconnected(facts, revision)) return;
    portENTER_CRITICAL(&s_softap_lock);
    bool admitted = s_softap.version == facts->version && !s_softap.operations &&
        s_softap.started && s_softap.enabled && !s_softap.online &&
        !atomic_load(&s_stopping_for_sleep);
    uint64_t operation = 0;
    if (admitted) {
        ++s_softap.operations;
        softap_changed_locked();
        operation = s_softap.version;
    }
    portEXIT_CRITICAL(&s_softap_lock);
    if (!admitted) return;
    runtime_softap_settings_t desired = runtime_settings_get_softap_snapshot();
    esp_err_t result = ESP_ERR_INVALID_STATE;
    if (desired.revision == revision && desired.delay_min && !atomic_load(&s_stopping_for_sleep))
        result = esp_wifi_disconnect();
    portENTER_CRITICAL(&s_softap_lock);
    // A newer callback/retry owns its own intent. Never clear it with the
    // completion of an older SDK cancellation; subsequent RF events remain
    // asynchronous and are reconciled again before any restart admission.
    if (s_softap.version == operation && s_softap.operations == 1 && result == ESP_OK)
        s_softap.pending = false;
    --s_softap.operations;
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
}
static void softap_arm(softap_policy_t *policy, const softap_facts_t *facts,
                       runtime_softap_settings_t desired, int64_t now) {
    int64_t interval = (int64_t)desired.delay_min * 60000000LL;
    policy->armed = true;
    policy->revision = desired.revision;
    policy->version = facts->version;
    policy->saturated = now > INT64_MAX - interval;
    policy->deadline = softap_after(now, interval);
}
static void softap_poll(softap_policy_t *policy, int64_t now) {
    softap_facts_t facts = softap_snapshot();
    runtime_softap_settings_t desired = runtime_settings_get_softap_snapshot();
    if (now < 0 || !facts.valid || !facts.started || !facts.enabled || facts.online ||
        facts.operations || !desired.delay_min || atomic_load(&s_stopping_for_sleep)) {
        policy->armed = false;
        return;
    }
    if (!policy->armed || policy->revision != desired.revision || policy->version != facts.version)
        softap_arm(policy, &facts, desired, now);
    if (policy->saturated || now < policy->deadline) return;
    // An active AP decision excludes the deep-sleep activity CAS. OTA already
    // owns activity and its reboot lease; the exact reservation arbitrates it.
    if (deep_sleep_clock_begin_activity()) {
        websocket_reboot_lease_t lease = {0};
        if (facts.pending) softap_cancel_pending(&facts, desired.revision, now);
        else if (softap_live(&facts, desired.revision, now) &&
            websocket_service_reboot_reserve(&lease) == ESP_OK) {
            // Final application arbitration; later RF/config events cannot be
            // atomically excluded by the SDK restart operation.
            if (softap_live(&facts, desired.revision, esp_timer_get_time()))
                (void)websocket_service_reboot_restart_reserved_now(&lease);
            if (lease.epoch) (void)websocket_service_reboot_cancel(&lease);
        }
        deep_sleep_clock_end_activity();
    }
    // Keep no ordinary pending AP reboot. Failed/held admission (including a
    // failed OTA later cancelled) receives a fresh full interval after return.
    int64_t rearm = esp_timer_get_time();
    if (rearm < now || rearm < 0) policy->armed = false;
    else softap_arm(policy, &facts, desired, rearm);
}

// Desired next-boot credential owner. Runtime profiles are loaded once at boot:
// HTTP edits cannot race an event handler reading/retrying that active table.
static SemaphoreHandle_t s_wifi_save_lock;
static native_wifi_store_t s_wifi_store;
static const native_wifi_file_t s_wifi_paths = {
    .live = "/spiffs/data/wifi.csv",
    .temporary = "/spiffs/data/wifi.csv.tmp",
    .backup = "/spiffs/data/wifi.csv.bak",
};

static native_wifi_result_t wifi_store_lock(void *context) {
    (void)context;
    return s_wifi_save_lock &&
           xSemaphoreTake(s_wifi_save_lock, pdMS_TO_TICKS(1000)) == pdTRUE ?
           NATIVE_WIFI_OK : NATIVE_WIFI_BUSY;
}

static void wifi_store_unlock(void *context) {
    (void)context;
    xSemaphoreGive(s_wifi_save_lock);
}

static native_wifi_result_t wifi_store_read(void *context, uint8_t *data,
                                           size_t capacity, size_t *size) {
    (void)context;
    return native_wifi_file_read(&s_wifi_paths, data, capacity, size);
}

static native_wifi_result_t wifi_store_publish(void *context,
                                              const uint8_t *data, size_t size) {
    (void)context;
    return native_wifi_file_publish(&s_wifi_paths, data, size);
}

esp_err_t network_service_storage_init(void) {
    ESP_RETURN_ON_ERROR(web_upload_storage_init(), TAG,
                        "Wi-Fi file storage initialization failed");
    if (!s_wifi_save_lock) s_wifi_save_lock = xSemaphoreCreateMutex();
    ESP_RETURN_ON_FALSE(s_wifi_save_lock, ESP_ERR_NO_MEM, TAG,
                        "Wi-Fi owner lock allocation failed");
    if (!s_wifi_store.ready) {
        uint64_t epoch = ((uint64_t)esp_random() << 32) | esp_random();
        const native_wifi_store_ops_t ops = {
            .lock = wifi_store_lock, .unlock = wifi_store_unlock,
            .read_live = wifi_store_read, .publish_csv = wifi_store_publish,
        };
        ESP_RETURN_ON_FALSE(native_wifi_store_init(&s_wifi_store, &ops, NULL,
                                                   epoch ? epoch : 1),
                            ESP_ERR_INVALID_STATE, TAG,
                            "Wi-Fi owner initialization failed");
    }
    return ESP_OK;
}

native_wifi_result_t network_service_wifi_metadata(native_wifi_metadata_t *out) {
    return native_wifi_store_metadata(&s_wifi_store, out);
}

native_wifi_result_t network_service_wifi_edit(const native_wifi_edit_t *edit) {
    return native_wifi_store_edit(&s_wifi_store, edit);
}

static esp_err_t wifi_store_error(native_wifi_result_t result) {
    switch (result) {
    case NATIVE_WIFI_OK: return ESP_OK;
    case NATIVE_WIFI_INVALID: return ESP_ERR_INVALID_ARG;
    case NATIVE_WIFI_BUSY: return ESP_ERR_TIMEOUT;
    case NATIVE_WIFI_NO_MEMORY: return ESP_ERR_NO_MEM;
    case NATIVE_WIFI_NOT_READY: return ESP_ERR_INVALID_STATE;
    default: return ESP_FAIL;
    }
}
// End desired next-boot credential owner.

static esp_err_t apply_power(void *context, bool active) {
    (void)context;
    return esp_wifi_set_ps(active ? WIFI_PS_NONE : WIFI_PS_MIN_MODEM);
}

static void rssi_task(void *argument) {
    (void)argument;
    int64_t rssi_next = 0;
    softap_policy_t softap = {0};
    while (true) {
        int64_t now = esp_timer_get_time();
        if (!atomic_load(&s_stopping_for_sleep)) {
            native_network_power_poll(now, apply_power, NULL);
            softap_poll(&softap, now);
            if (now >= rssi_next) {
                wifi_ap_record_t access_point = {0};
                if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK)
                    native_state_set_wifi_rssi(s_state, access_point.rssi);
                rssi_next = now > INT64_MAX - (int64_t)WIFI_RSSI_INTERVAL_MS * 1000
                    ? INT64_MAX : now + (int64_t)WIFI_RSSI_INTERVAL_MS * 1000;
            }
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

static void prepare_station_config(wifi_config_t *config) {
    config->sta.threshold.authmode = WIFI_AUTH_OPEN;
    config->sta.pmf_cfg.capable = true;
    config->sta.pmf_cfg.required = false;
}

static bool next_credential_row(FILE *file, char *line, size_t capacity) {
    return native_credential_next_row(file, line, capacity);
}

static bool read_credentials(wifi_config_t *config) {
    memset(s_credentials, 0, sizeof(s_credentials));
    s_credential_count = 0;
    s_credential_index = 0;
    if (!native_file_recover("/spiffs/data/wifi.csv", "/spiffs/data/wifi.csv.bak")) return false;
    FILE *file = fopen("/spiffs/data/wifi.csv", "r");
    if (!file) return false;
    char line[160];
    bool found = false;
    while (next_credential_row(file, line, sizeof(line))) {
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab++ = '\0';
        if (!line[0] || strlen(line) >= sizeof(config->sta.ssid) ||
            strlen(tab) >= sizeof(config->sta.password) || strchr(line, '\r') ||
            strpbrk(tab, "\t\r")) {
            continue;
        }
        if (s_credential_count >= WIFI_MAX_CREDENTIALS) continue;
        wifi_config_t *saved = &s_credentials[s_credential_count++];
        strlcpy((char *)saved->sta.ssid, line, sizeof(saved->sta.ssid));
        strlcpy((char *)saved->sta.password, tab,
                sizeof(saved->sta.password));
        prepare_station_config(saved);
    }
    bool read_ok = ferror(file) == 0;
    fclose(file);
    if (!read_ok) s_credential_count = 0;
    found = s_credential_count > 0;
    if (found) {
        *config = s_credentials[0];
        ESP_LOGI(TAG, "Loaded %u Wi-Fi network(s) from /data/wifi.csv",
                 (unsigned)s_credential_count);
    }
    return found;
}

static esp_err_t select_credential(size_t index) {
    ESP_RETURN_ON_FALSE(index < s_credential_count, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi network index is invalid");
    s_credential_index = index;
    s_station_config = s_credentials[index];
    return esp_wifi_set_config(WIFI_IF_STA, &s_station_config);
}

static void event_handler(void *arg, esp_event_base_t base, int32_t id,
                          void *event_data) {
    (void)arg;
    if (atomic_load(&s_stopping_for_sleep)) return;
    if (!((base == WIFI_EVENT && (id == WIFI_EVENT_STA_START ||
            id == WIFI_EVENT_STA_CONNECTED || id == WIFI_EVENT_STA_DISCONNECTED)) ||
          (base == IP_EVENT && (id == IP_EVENT_STA_GOT_IP || id == IP_EVENT_STA_LOST_IP)))) return;
    softap_operation(true);
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        if (s_have_credentials) connect_station();
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_CONNECTED) {
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_CONNECTED, 0);
#endif
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        softap_link(false, false);
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
        const wifi_event_sta_disconnected_t *event = event_data;
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_DISCONNECTED,
                                  event ? event->reason : 0);
#endif
        if (s_have_credentials &&
            s_retries++ < WIFI_RETRIES_PER_CREDENTIAL) {
            ESP_LOGW(TAG, "Wi-Fi network %u/%u retry %d/%d",
                     (unsigned)(s_credential_index + 1U),
                     (unsigned)s_credential_count, s_retries,
                     WIFI_RETRIES_PER_CREDENTIAL);
            connect_station();
        } else if (s_have_credentials &&
                   s_credential_index + 1U < s_credential_count) {
            ++s_credential_index;
            s_retries = 0;
            if (select_credential(s_credential_index) == ESP_OK) {
                ESP_LOGI(TAG, "Trying saved Wi-Fi network %u/%u",
                         (unsigned)(s_credential_index + 1U),
                         (unsigned)s_credential_count);
                connect_station();
            } else {
                xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
            }
        } else {
            xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        softap_link(true, false);
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_GOT_IP, 0);
#endif
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        wifi_ap_record_t access_point = {0};
        s_retries = 0;
        native_state_set_network(s_state, NATIVE_NETWORK_CLIENT,
                                 event->ip_info.ip.addr);
        if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK) {
            native_state_set_wifi_rssi(s_state, access_point.rssi);
        }
        time_service_notify_network_ready();
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Client address: " IPSTR, IP2STR(&event->ip_info.ip));
    } else if (base == IP_EVENT && id == IP_EVENT_STA_LOST_IP) {
        softap_link(false, false);
    }
    softap_operation(false);
}

static esp_err_t start_access_point(void) {
    uint8_t mac[6];
    wifi_config_t ap = {0};
    ESP_RETURN_ON_ERROR(esp_read_mac(mac, ESP_MAC_WIFI_SOFTAP), TAG,
                        "MAC read failed");
    snprintf((char *)ap.ap.ssid, sizeof(ap.ap.ssid), "yoRadio-%02X%02X%02X",
             mac[3], mac[4], mac[5]);
    ap.ap.ssid_len = strlen((char *)ap.ap.ssid);
    ap.ap.channel = 1;
    ap.ap.max_connection = 4;
    ap.ap.authmode = WIFI_AUTH_OPEN;
    if (!s_ap_netif) s_ap_netif = esp_netif_create_default_wifi_ap();
    ESP_RETURN_ON_FALSE(s_ap_netif, ESP_ERR_NO_MEM, TAG,
                        "AP network interface allocation failed");
    ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_APSTA), TAG,
                        "AP/client mode failed");
    ESP_RETURN_ON_ERROR(esp_wifi_set_config(WIFI_IF_AP, &ap), TAG,
                        "AP configuration failed");
    portENTER_CRITICAL(&s_softap_lock);
    s_softap.enabled = true;
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
    native_state_set_network(s_state, NATIVE_NETWORK_ACCESS_POINT, 0);
    ESP_LOGW(TAG, "Access point enabled: %s", ap.ap.ssid);
    return ESP_OK;
}

esp_err_t network_service_prepare_sleep(void) {
    softap_operation(true);
    atomic_store(&s_stopping_for_sleep, true);
    esp_err_t result = esp_wifi_stop();
    if (result != ESP_OK) atomic_store(&s_stopping_for_sleep, false);
    else {
        portENTER_CRITICAL(&s_softap_lock);
        s_softap.started = s_softap.enabled = false;
        portEXIT_CRITICAL(&s_softap_lock);
    }
    softap_operation(false);
    return result;
}

esp_err_t network_service_start(native_state_t *state) {
    ESP_RETURN_ON_ERROR(network_service_storage_init(), TAG,
                        "Wi-Fi credential owner initialization failed");
    s_state = state;
    s_wifi_events = xEventGroupCreate();
    ESP_RETURN_ON_FALSE(s_wifi_events, ESP_ERR_NO_MEM, TAG,
                        "Wi-Fi event group allocation failed");
    ESP_RETURN_ON_ERROR(esp_netif_init(), TAG, "TCP/IP stack failed");
    ESP_RETURN_ON_ERROR(esp_event_loop_create_default(), TAG,
                        "Default event loop failed");
    s_station_netif = esp_netif_create_default_wifi_sta();
    ESP_RETURN_ON_FALSE(s_station_netif, ESP_ERR_NO_MEM, TAG,
                        "Station network interface allocation failed");
    char hostname[24];
    runtime_settings_get_mdns_name(hostname, sizeof(hostname));
    if (hostname[0]) {
        ESP_RETURN_ON_ERROR(esp_netif_set_hostname(s_station_netif, hostname),
                            TAG, "Station hostname failed");
    }
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_RETURN_ON_ERROR(esp_wifi_init(&init), TAG, "Wi-Fi init failed");
    // wifi.csv is the only persistent source of credentials. Keep the
    // driver's working copy in RAM so it cannot silently override the file.
    ESP_RETURN_ON_ERROR(esp_wifi_set_storage(WIFI_STORAGE_RAM), TAG,
                        "Wi-Fi RAM storage selection failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_register(
                            WIFI_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL),
                        TAG, "Wi-Fi event registration failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_register(
                            IP_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL),
                        TAG, "IP event registration failed");

    memset(&s_station_config, 0, sizeof(s_station_config));
    s_have_credentials = read_credentials(&s_station_config);
    if (s_have_credentials) {
        ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                            "Station mode failed");
        ESP_RETURN_ON_ERROR(select_credential(0), TAG,
                            "Station configuration failed");
    } else {
        ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                            "Station mode failed");
    }
    ESP_RETURN_ON_ERROR(esp_wifi_start(), TAG, "Wi-Fi start failed");
    portENTER_CRITICAL(&s_softap_lock);
    s_softap.started = true;
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
    // Preserve audio intent if it arrived before networking was ready. The
    // existing RSSI task is the sole power-policy driver caller.
    native_network_power_invalidate();

    ESP_RETURN_ON_FALSE(xTaskCreate(rssi_task, "wifi_rssi",
                                    BOARD_TASK_STACK_WIFI_RSSI, NULL, 2,
                                    NULL) == pdPASS,
                        ESP_ERR_NO_MEM, TAG, "RSSI task allocation failed");

    if (s_have_credentials) {
        EventBits_t bits = xEventGroupWaitBits(
            s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT, pdTRUE,
            pdFALSE, pdMS_TO_TICKS(20000));
        if (bits & WIFI_CONNECTED_BIT) return ESP_OK;
    }
    return start_access_point();
}

void network_service_audio_accept(uint32_t generation, bool active) {
    native_network_power_accept(generation, active);
}

void network_service_audio_receive(uint32_t generation) {
    native_network_power_receive(generation);
}

void network_service_audio_finish(uint32_t generation) {
    native_network_power_finish(generation);
}

esp_err_t network_service_retry_client(void) {
    ESP_RETURN_ON_FALSE(s_have_credentials, ESP_ERR_NOT_FOUND, TAG,
                        "No saved Wi-Fi credentials");
    softap_operation(true);
    s_retries = 0;
    s_credential_index = 0;
    xEventGroupClearBits(s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT);
    esp_err_t result = esp_wifi_set_mode(WIFI_MODE_STA);
    if (result == ESP_OK) {
        portENTER_CRITICAL(&s_softap_lock);
        s_softap.enabled = s_softap.online = false;
        portEXIT_CRITICAL(&s_softap_lock);
        result = select_credential(0);
    }
    if (result == ESP_OK) {
        native_state_set_network(s_state, NATIVE_NETWORK_STARTING, 0);
        result = connect_station();
    }
    softap_operation(false);
    return result;
}

esp_err_t network_service_save_credentials(const char *ssid,
                                           const char *password) {
    ESP_RETURN_ON_FALSE(ssid && password, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi credentials are missing");
    size_t ssid_size = strnlen(ssid, sizeof(s_station_config.sta.ssid));
    size_t password_size = strnlen(password, sizeof(s_station_config.sta.password));
    ESP_RETURN_ON_FALSE(ssid_size && ssid_size < sizeof(s_station_config.sta.ssid) &&
                            password_size < sizeof(s_station_config.sta.password) &&
                            !strpbrk(ssid, "\t\r\n") && !strpbrk(password, "\t\r\n"),
                        ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi fields");
    char line[sizeof(s_station_config.sta.ssid) +
              sizeof(s_station_config.sta.password)];
    memcpy(line, ssid, ssid_size);
    line[ssid_size] = '\t';
    memcpy(line + ssid_size + 1U, password, password_size);
    size_t size = ssid_size + 1U + password_size;
    line[size++] = '\n';
    esp_err_t result = network_service_save_credentials_file((const uint8_t *)line, size);
    native_wifi_erase(line, sizeof(line));
    return result;
}

esp_err_t network_service_validate_credentials_file(const uint8_t *data,
                                                    size_t size) {
    ESP_RETURN_ON_FALSE(data && size && size < 800U, ESP_ERR_INVALID_SIZE, TAG,
                        "Wi-Fi file is empty or too large");
    return wifi_store_error(native_wifi_validate_csv(data, size));
}

esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size) {
    ESP_RETURN_ON_ERROR(network_service_validate_credentials_file(data, size),
                        TAG, "Invalid Wi-Fi file");
    return wifi_store_error(native_wifi_store_import(&s_wifi_store, data, size));
}
