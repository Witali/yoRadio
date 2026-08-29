#include "network_service.h"

#include <stdio.h>
#include <string.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"
#include "lwip/inet.h"
#include "native_state.h"
#include "tcpip_adapter.h"
#include "time_service.h"

#define WIFI_PATH "/spiffs/data/wifi.csv"
#define WIFI_MAX_CREDENTIALS 5U
#define WIFI_RETRIES_PER_CREDENTIAL 2U
#define WIFI_CONNECT_TIMEOUT_MS 20000U
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAILED_BIT BIT1

static const char *TAG = "network";
static EventGroupHandle_t s_events;
static uint32_t s_credential_offsets[WIFI_MAX_CREDENTIALS];
static uint8_t s_credential_count;
static uint8_t s_credential_index;
static uint8_t s_retries;
static bool s_connected;
static bool s_access_point;
/* Shared by indexing and credential loading; no array of wifi_config_t is
 * retained in RAM. */
static char s_wifi_line[128];

static bool has_edge_space(const char *text) {
    size_t length = strlen(text);
    return length && (text[0] == ' ' || text[length - 1] == ' ');
}

static bool index_credentials(void) {
    FILE *file = fopen(WIFI_PATH, "rb");
    s_credential_count = 0;
    if (!file) return false;
    while (s_credential_count < WIFI_MAX_CREDENTIALS) {
        long position = ftell(file);
        if (position < 0 || !fgets(s_wifi_line, sizeof(s_wifi_line), file))
            break;
        char *tab = strchr(s_wifi_line, '\t');
        if (!tab) continue;
        *tab++ = '\0';
        tab[strcspn(tab, "\r\n")] = '\0';
        if (!s_wifi_line[0] || strlen(s_wifi_line) >= 32 ||
            strlen(tab) >= 64) {
            continue;
        }
        if (has_edge_space(s_wifi_line)) {
            ESP_LOGW(TAG, "Wi-Fi SSID %u has leading/trailing space",
                     (unsigned)s_credential_count + 1U);
        }
        s_credential_offsets[s_credential_count++] = (uint32_t)position;
    }
    fclose(file);
    ESP_LOGI(TAG, "Indexed %u Wi-Fi network(s)", s_credential_count);
    return s_credential_count != 0;
}

static esp_err_t select_credential(uint8_t index) {
    if (index >= s_credential_count) return ESP_ERR_INVALID_ARG;
    FILE *file = fopen(WIFI_PATH, "rb");
    if (!file) return ESP_ERR_NOT_FOUND;
    bool read = fseek(file, (long)s_credential_offsets[index], SEEK_SET) == 0 &&
                fgets(s_wifi_line, sizeof(s_wifi_line), file);
    fclose(file);
    if (!read) return ESP_FAIL;
    char *password = strchr(s_wifi_line, '\t');
    if (!password) return ESP_ERR_INVALID_ARG;
    *password++ = '\0';
    password[strcspn(password, "\r\n")] = '\0';
    wifi_config_t config;
    memset(&config, 0, sizeof(config));
    memcpy(config.sta.ssid, s_wifi_line, strlen(s_wifi_line) + 1U);
    memcpy(config.sta.password, password, strlen(password) + 1U);
    config.sta.threshold.authmode = WIFI_AUTH_OPEN;
    s_credential_index = index;
    return esp_wifi_set_config(ESP_IF_WIFI_STA, &config);
}

static esp_err_t start_access_point(void) {
    uint8_t mac[6];
    wifi_config_t config;
    memset(&config, 0, sizeof(config));
    esp_err_t result = esp_wifi_get_mac(ESP_IF_WIFI_AP, mac);
    if (result != ESP_OK) return result;
    snprintf((char *)config.ap.ssid, sizeof(config.ap.ssid),
             "yoRadio-%02X%02X%02X", mac[3], mac[4], mac[5]);
    config.ap.ssid_len = strlen((char *)config.ap.ssid);
    config.ap.channel = 1;
    config.ap.max_connection = 4;
    config.ap.authmode = WIFI_AUTH_OPEN;
    result = esp_wifi_set_mode(WIFI_MODE_APSTA);
    if (result == ESP_OK)
        result = esp_wifi_set_config(ESP_IF_WIFI_AP, &config);
    if (result != ESP_OK) return result;
    s_access_point = true;
    native_state_set_network(NETWORK_ACCESS_POINT);
    tcpip_adapter_ip_info_t info;
    if (tcpip_adapter_get_ip_info(TCPIP_ADAPTER_IF_AP, &info) == ESP_OK) {
        native_state_set_ip(ip4addr_ntoa(&info.ip));
    }
    ESP_LOGW(TAG, "Recovery AP enabled: %s", config.ap.ssid);
    return ESP_OK;
}

static void event_handler(void *argument, esp_event_base_t base,
                          int32_t id, void *data) {
    (void)argument;
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        if (s_credential_count) esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        s_connected = false;
        if (s_access_point || !s_credential_count) return;
        if (++s_retries <= WIFI_RETRIES_PER_CREDENTIAL) {
            esp_wifi_connect();
        } else if (s_credential_index + 1U < s_credential_count) {
            s_retries = 0;
            if (select_credential(s_credential_index + 1U) == ESP_OK)
                esp_wifi_connect();
            else
                xEventGroupSetBits(s_events, WIFI_FAILED_BIT);
        } else {
            xEventGroupSetBits(s_events, WIFI_FAILED_BIT);
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)data;
        s_connected = true;
        s_retries = 0;
        native_state_set_network(NETWORK_CLIENT);
        native_state_set_ip(ip4addr_ntoa(&event->ip_info.ip));
        time_service_notify_connected();
        xEventGroupSetBits(s_events, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Client address: %s", ip4addr_ntoa(&event->ip_info.ip));
    }
}

static void supervisor_task(void *argument) {
    (void)argument;
    EventBits_t bits = xEventGroupWaitBits(
        s_events, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT, pdFALSE, pdFALSE,
        pdMS_TO_TICKS(WIFI_CONNECT_TIMEOUT_MS));
    if (!(bits & WIFI_CONNECTED_BIT)) {
        esp_err_t result = start_access_point();
        if (result != ESP_OK) {
            native_state_set_network(NETWORK_ERROR);
            ESP_LOGE(TAG, "Recovery AP failed: %s", esp_err_to_name(result));
        }
    }
    while (true) {
        if (s_connected) {
            wifi_ap_record_t access_point;
            if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK)
                native_state_set_wifi_rssi(access_point.rssi);
        }
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}

esp_err_t network_service_start(void) {
    s_events = xEventGroupCreate();
    if (!s_events) return ESP_ERR_NO_MEM;
    tcpip_adapter_init();
    esp_err_t result = esp_event_loop_create_default();
    if (result != ESP_OK) return result;
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    result = esp_wifi_init(&init);
    if (result != ESP_OK) return result;
    result = esp_wifi_set_storage(WIFI_STORAGE_RAM);
    if (result != ESP_OK) return result;
    result = esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
                                        event_handler, NULL);
    if (result != ESP_OK) return result;
    result = esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP,
                                        event_handler, NULL);
    if (result != ESP_OK) return result;
    index_credentials();
    result = esp_wifi_set_mode(WIFI_MODE_STA);
    if (result == ESP_OK && s_credential_count)
        result = select_credential(0);
    if (result == ESP_OK) result = esp_wifi_start();
    if (result != ESP_OK) return result;
    if (xTaskCreate(supervisor_task, "wifi", 2304, NULL, 2, NULL) != pdPASS)
        return ESP_ERR_NO_MEM;
    return ESP_OK;
}

bool network_service_connected(void) { return s_connected; }

esp_err_t network_service_set_streaming(bool active) {
    return esp_wifi_set_ps(active ? WIFI_PS_NONE : WIFI_PS_MIN_MODEM);
}
