#include "network_service.h"

#include <stdio.h>
#include <string.h>

#include "board_config.h"
#include "esp_event.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"
#include "runtime_settings.h"

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
static esp_timer_handle_t s_softap_reboot_timer;
static int s_retries;
static bool s_have_credentials;

static void rssi_task(void *argument) {
    (void)argument;
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(WIFI_RSSI_INTERVAL_MS));
        wifi_ap_record_t access_point = {0};
        if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK) {
            native_state_set_wifi_rssi(s_state, access_point.rssi);
        }
    }
}

static void prepare_station_config(wifi_config_t *config) {
    config->sta.threshold.authmode = WIFI_AUTH_OPEN;
    config->sta.pmf_cfg.capable = true;
    config->sta.pmf_cfg.required = false;
}

static bool read_credentials(wifi_config_t *config) {
    memset(s_credentials, 0, sizeof(s_credentials));
    s_credential_count = 0;
    s_credential_index = 0;
    FILE *file = fopen("/spiffs/data/wifi.csv", "r");
    if (!file) return false;
    char line[160];
    bool found = false;
    while (fgets(line, sizeof(line), file)) {
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab++ = '\0';
        tab[strcspn(tab, "\r\n")] = '\0';
        if (!line[0] || strlen(line) >= sizeof(config->sta.ssid) ||
            strlen(tab) >= sizeof(config->sta.password)) {
            continue;
        }
        if (s_credential_count >= WIFI_MAX_CREDENTIALS) continue;
        wifi_config_t *saved = &s_credentials[s_credential_count++];
        strlcpy((char *)saved->sta.ssid, line, sizeof(saved->sta.ssid));
        strlcpy((char *)saved->sta.password, tab,
                sizeof(saved->sta.password));
        prepare_station_config(saved);
    }
    fclose(file);
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
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_have_credentials &&
            s_retries++ < WIFI_RETRIES_PER_CREDENTIAL) {
            ESP_LOGW(TAG, "Wi-Fi network %u/%u retry %d/%d",
                     (unsigned)(s_credential_index + 1U),
                     (unsigned)s_credential_count, s_retries,
                     WIFI_RETRIES_PER_CREDENTIAL);
            esp_wifi_connect();
        } else if (s_have_credentials &&
                   s_credential_index + 1U < s_credential_count) {
            ++s_credential_index;
            s_retries = 0;
            if (select_credential(s_credential_index) == ESP_OK) {
                ESP_LOGI(TAG, "Trying saved Wi-Fi network %u/%u",
                         (unsigned)(s_credential_index + 1U),
                         (unsigned)s_credential_count);
                esp_wifi_connect();
            } else {
                xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
            }
        } else {
            xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        wifi_ap_record_t access_point = {0};
        s_retries = 0;
        native_state_set_network(s_state, NATIVE_NETWORK_CLIENT,
                                 event->ip_info.ip.addr);
        if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK) {
            native_state_set_wifi_rssi(s_state, access_point.rssi);
        }
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Client address: " IPSTR, IP2STR(&event->ip_info.ip));
    }
}

static void softap_reboot_callback(void *argument) {
    (void)argument;
    ESP_LOGW(TAG, "SoftAP timeout reached; rebooting");
    esp_restart();
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
    native_state_set_network(s_state, NATIVE_NETWORK_ACCESS_POINT, 0);
    ESP_LOGW(TAG, "Access point enabled: %s", ap.ap.ssid);
    uint8_t delay_min = runtime_settings_get_softap_delay_min();
    if (delay_min) {
        if (!s_softap_reboot_timer) {
            const esp_timer_create_args_t timer = {
                .callback = softap_reboot_callback,
                .name = "softap_reboot",
            };
            ESP_RETURN_ON_ERROR(
                esp_timer_create(&timer, &s_softap_reboot_timer), TAG,
                "Create SoftAP reboot timer");
        }
        ESP_RETURN_ON_ERROR(esp_timer_start_once(
                                s_softap_reboot_timer,
                                (uint64_t)delay_min * 60U * 1000000U), TAG,
                            "Start SoftAP reboot timer");
    }
    return ESP_OK;
}

esp_err_t network_service_start(native_state_t *state) {
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
                            IP_EVENT, IP_EVENT_STA_GOT_IP, event_handler, NULL),
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

esp_err_t network_service_retry_client(void) {
    ESP_RETURN_ON_FALSE(s_have_credentials, ESP_ERR_NOT_FOUND, TAG,
                        "No saved Wi-Fi credentials");
    s_retries = 0;
    s_credential_index = 0;
    xEventGroupClearBits(s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT);
    ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                        "Station mode restore failed");
    ESP_RETURN_ON_ERROR(select_credential(0), TAG,
                        "Station configuration restore failed");
    native_state_set_network(s_state, NATIVE_NETWORK_STARTING, 0);
    return esp_wifi_connect();
}

esp_err_t network_service_save_credentials(const char *ssid,
                                           const char *password) {
    ESP_RETURN_ON_FALSE(ssid && password, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi credentials are missing");
    char line[160];
    int length = snprintf(line, sizeof(line), "%s\t%s\n", ssid, password);
    ESP_RETURN_ON_FALSE(length > 0 && (size_t)length < sizeof(line),
                        ESP_ERR_INVALID_SIZE, TAG,
                        "Wi-Fi credentials are too long");
    return network_service_save_credentials_file((const uint8_t *)line,
                                                 (size_t)length);
}

esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size) {
    ESP_RETURN_ON_FALSE(data && size && size < 800U, ESP_ERR_INVALID_SIZE, TAG,
                        "Wi-Fi file is empty or too large");
    char content[800];
    memcpy(content, data, size);
    content[size] = '\0';
    size_t count = 0;
    char *cursor = content;
    while (*cursor) {
        char *line_end = strpbrk(cursor, "\r\n");
        char line_break = line_end ? *line_end : '\0';
        if (line_end) *line_end = '\0';
        if (*cursor) {
            char *tab = strchr(cursor, '\t');
            ESP_RETURN_ON_FALSE(tab, ESP_ERR_INVALID_ARG, TAG,
                                "Wi-Fi row has no tab separator");
            *tab++ = '\0';
            ESP_RETURN_ON_FALSE(
                cursor[0] && strlen(cursor) < sizeof(s_station_config.sta.ssid) &&
                    strlen(tab) < sizeof(s_station_config.sta.password) &&
                    !strpbrk(cursor, "\t\r\n") && !strpbrk(tab, "\t\r\n"),
                ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi row");
            ESP_RETURN_ON_FALSE(++count <= WIFI_MAX_CREDENTIALS,
                                ESP_ERR_INVALID_SIZE, TAG,
                                "Too many Wi-Fi networks");
        }
        if (!line_end) break;
        cursor = line_end + 1;
        if (*cursor == '\n' && line_break == '\r') ++cursor;
    }
    ESP_RETURN_ON_FALSE(count > 0, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi file has no networks");

    const char *path = "/spiffs/data/wifi.csv";
    const char *temporary_path = "/spiffs/data/wifi.csv.tmp";
    FILE *file = fopen(temporary_path, "wb");
    ESP_RETURN_ON_FALSE(file, ESP_FAIL, TAG,
                        "Cannot create Wi-Fi credentials file");
    bool written = fwrite(data, 1, size, file) == size;
    bool flushed = fflush(file) == 0;
    bool closed = fclose(file) == 0;
    if (!written || !flushed || !closed) {
        remove(temporary_path);
        return ESP_FAIL;
    }
    remove(path);
    if (rename(temporary_path, path) != 0) {
        remove(temporary_path);
        return ESP_FAIL;
    }
    memset(&s_station_config, 0, sizeof(s_station_config));
    s_have_credentials = read_credentials(&s_station_config);
    ESP_RETURN_ON_FALSE(s_have_credentials, ESP_FAIL, TAG,
                        "Reload saved Wi-Fi networks");
    ESP_LOGI(TAG, "Saved %u Wi-Fi network(s)", (unsigned)count);
    return ESP_OK;
}
