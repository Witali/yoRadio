#include "network_service.h"

#include <stdio.h>
#include <string.h>

#include "esp_event.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "credential_line.h"
#include "web_upload.h"

#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAILED_BIT BIT1
#define WIFI_MAX_RETRIES 8
#define WIFI_MAX_FILE_BYTES 800U
#define WIFI_MAX_FILE_NETWORKS 5U

static const char *const TAG = "network";
static EventGroupHandle_t s_wifi_events;
static esp_netif_t *s_station_netif;
static esp_netif_t *s_ap_netif;
static native_state_t *s_state;
static wifi_config_t s_station_config;
static int s_retries;
static bool s_have_credentials;
static SemaphoreHandle_t s_wifi_save_lock;

esp_err_t network_service_storage_init(void) {
    ESP_RETURN_ON_ERROR(web_upload_storage_init(), TAG,
                        "Wi-Fi file storage initialization failed");
    if (!s_wifi_save_lock) s_wifi_save_lock = xSemaphoreCreateMutex();
    ESP_RETURN_ON_FALSE(s_wifi_save_lock, ESP_ERR_NO_MEM, TAG,
                        "Wi-Fi save lock allocation failed");
    return ESP_OK;
}

static bool read_credentials(wifi_config_t *config) {
    FILE *file = web_upload_open_file("/spiffs/data/wifi.csv");
    if (!file) return false;
    char line[160];
    wifi_config_t selected = {0};
    bool found = false;
    while (native_credential_next_row(file, line, sizeof(line))) {
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab++ = '\0';
        if (!line[0] || strlen(line) >= sizeof(config->sta.ssid) ||
            strlen(tab) >= sizeof(config->sta.password) || strchr(line, '\r') ||
            strpbrk(tab, "\t\r")) {
            continue;
        }
        strlcpy((char *)selected.sta.ssid, line, sizeof(selected.sta.ssid));
        strlcpy((char *)selected.sta.password, tab,
                sizeof(selected.sta.password));
        found = true;
        break;
    }
    if (fclose(file) != 0) found = false;
    if (found) *config = selected;
    return found;
}

static void event_handler(void *arg, esp_event_base_t base, int32_t id,
                          void *event_data) {
    (void)arg;
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_have_credentials && s_retries++ < WIFI_MAX_RETRIES) {
            ESP_LOGW(TAG, "Wi-Fi disconnected, retry %d/%d", s_retries,
                     WIFI_MAX_RETRIES);
            esp_wifi_connect();
        } else {
            xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        s_retries = 0;
        native_state_set_network(s_state, NATIVE_NETWORK_CLIENT,
                                 event->ip_info.ip.addr);
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Client address: " IPSTR, IP2STR(&event->ip_info.ip));
    }
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
    return ESP_OK;
}

esp_err_t network_service_start(native_state_t *state) {
    ESP_RETURN_ON_ERROR(network_service_storage_init(), TAG,
                        "Wi-Fi file storage initialization failed");
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
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_RETURN_ON_ERROR(esp_wifi_init(&init), TAG, "Wi-Fi init failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_register(
                            WIFI_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL),
                        TAG, "Wi-Fi event registration failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_register(
                            IP_EVENT, IP_EVENT_STA_GOT_IP, event_handler, NULL),
                        TAG, "IP event registration failed");

    memset(&s_station_config, 0, sizeof(s_station_config));
    s_have_credentials = read_credentials(&s_station_config);
    if (s_have_credentials) {
        s_station_config.sta.threshold.authmode = WIFI_AUTH_OPEN;
        s_station_config.sta.pmf_cfg.capable = true;
        s_station_config.sta.pmf_cfg.required = false;
        ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                            "Station mode failed");
        ESP_RETURN_ON_ERROR(
            esp_wifi_set_config(WIFI_IF_STA, &s_station_config), TAG,
            "Station configuration failed");
    } else {
        ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                            "Station mode failed");
    }
    ESP_RETURN_ON_ERROR(esp_wifi_start(), TAG, "Wi-Fi start failed");

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
    xEventGroupClearBits(s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT);
    ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                        "Station mode restore failed");
    ESP_RETURN_ON_ERROR(esp_wifi_set_config(WIFI_IF_STA, &s_station_config),
                        TAG, "Station configuration restore failed");
    native_state_set_network(s_state, NATIVE_NETWORK_STARTING, 0);
    return esp_wifi_connect();
}

esp_err_t network_service_validate_credentials_file(const uint8_t *data,
                                                    size_t size) {
    ESP_RETURN_ON_FALSE(data && size && size < WIFI_MAX_FILE_BYTES,
                        ESP_ERR_INVALID_SIZE, TAG,
                        "Wi-Fi file is empty or too large");
    size_t count = 0;
    size_t offset = 0;
    while (offset < size) {
        size_t end = offset;
        while (end < size && data[end] != '\n') ++end;
        size_t row_end = end;
        if (row_end > offset && data[row_end - 1U] == '\r') --row_end;
        if (row_end > offset) {
            size_t tab = offset;
            while (tab < row_end && data[tab] != '\t') ++tab;
            ESP_RETURN_ON_FALSE(tab > offset && tab < row_end &&
                                    tab - offset < sizeof(s_station_config.sta.ssid) &&
                                    row_end - tab - 1U < sizeof(s_station_config.sta.password),
                                ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi row");
            for (size_t index = offset; index < row_end; ++index) {
                ESP_RETURN_ON_FALSE(data[index] && data[index] != '\r' &&
                                        (data[index] != '\t' || index == tab),
                                    ESP_ERR_INVALID_ARG, TAG,
                                    "Invalid Wi-Fi field");
            }
            ESP_RETURN_ON_FALSE(++count <= WIFI_MAX_FILE_NETWORKS,
                                ESP_ERR_INVALID_SIZE, TAG,
                                "Too many Wi-Fi networks");
        }
        offset = end < size ? end + 1U : end;
    }
    ESP_RETURN_ON_FALSE(count, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi file has no networks");
    return ESP_OK;
}

esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size) {
    ESP_RETURN_ON_ERROR(network_service_validate_credentials_file(data, size),
                        TAG, "Invalid Wi-Fi file");
    ESP_RETURN_ON_FALSE(s_wifi_save_lock, ESP_ERR_INVALID_STATE, TAG,
                        "Wi-Fi storage is not initialized");
    ESP_RETURN_ON_FALSE(xSemaphoreTake(s_wifi_save_lock, pdMS_TO_TICKS(1000)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "Wi-Fi save is busy");
    const char *path = "/spiffs/data/wifi.csv";
    const char *temporary_path = "/spiffs/data/wifi.csv.tmp";
    FILE *file = fopen(temporary_path, "wb");
    esp_err_t result = ESP_FAIL;
    if (file) {
        bool written = fwrite(data, 1, size, file) == size;
        bool flushed = fflush(file) == 0;
        bool closed = fclose(file) == 0;
        if (written && flushed && closed &&
            web_upload_publish_file(temporary_path, path)) {
            result = ESP_OK;
        } else {
            (void)remove(temporary_path);
        }
    }
    xSemaphoreGive(s_wifi_save_lock);
    return result;
}

esp_err_t network_service_save_credentials(const char *ssid,
                                           const char *password) {
    ESP_RETURN_ON_FALSE(ssid && password, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi credentials are missing");
    size_t ssid_size = strnlen(ssid, sizeof(s_station_config.sta.ssid));
    size_t password_size = strnlen(password, sizeof(s_station_config.sta.password));
    ESP_RETURN_ON_FALSE(ssid_size && ssid_size < sizeof(s_station_config.sta.ssid) &&
                            password_size < sizeof(s_station_config.sta.password),
                        ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi field size");
    ESP_RETURN_ON_FALSE(!strpbrk(ssid, "\t\r\n") && !strpbrk(password, "\t\r\n"),
                        ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi field");
    char line[sizeof(s_station_config.sta.ssid) +
              sizeof(s_station_config.sta.password)];
    memcpy(line, ssid, ssid_size);
    line[ssid_size] = '\t';
    memcpy(line + ssid_size + 1U, password, password_size);
    size_t size = ssid_size + 1U + password_size;
    line[size++] = '\n';
    return network_service_save_credentials_file((const uint8_t *)line, size);
}
