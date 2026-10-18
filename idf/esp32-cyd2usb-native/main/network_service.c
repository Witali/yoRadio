#include "network_service.h"

#include <stdio.h>
#include <string.h>

#include "esp_event.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_random.h"
#include "esp_wifi.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "credential_line.h"
#include "web_upload.h"
#include "native_wifi_file.h"
#include "time_service.h"

#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAILED_BIT BIT1
#define WIFI_MAX_RETRIES 8

static const char *const TAG = "network";
static EventGroupHandle_t s_wifi_events;
static esp_netif_t *s_station_netif;
static esp_netif_t *s_ap_netif;
static native_state_t *s_state;
static wifi_config_t s_station_config;
static int s_retries;
static bool s_have_credentials;
static SemaphoreHandle_t s_wifi_save_lock;
static native_wifi_store_t s_wifi_store;
static const native_wifi_file_t s_wifi_paths = {
    .live = "/spiffs/data/wifi.csv",
    .temporary = "/spiffs/data/wifi.csv.tmp",
    .backup = "/spiffs/data/wifi.csv.bak",
};

static native_wifi_result_t wifi_store_lock(void *context) {
    (void)context;
    return xSemaphoreTake(s_wifi_save_lock, pdMS_TO_TICKS(1000)) == pdTRUE
        ? NATIVE_WIFI_OK : NATIVE_WIFI_BUSY;
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

static esp_err_t wifi_store_error(native_wifi_result_t result) {
    switch (result) {
        case NATIVE_WIFI_OK: return ESP_OK;
        case NATIVE_WIFI_INVALID: return ESP_ERR_INVALID_ARG;
        case NATIVE_WIFI_BUSY: return ESP_ERR_TIMEOUT;
        case NATIVE_WIFI_NO_MEMORY: return ESP_ERR_NO_MEM;
        case NATIVE_WIFI_NOT_READY:
        case NATIVE_WIFI_EXHAUSTED: return ESP_ERR_INVALID_STATE;
        default: return ESP_FAIL;
    }
}

esp_err_t network_service_storage_init(void) {
    ESP_RETURN_ON_ERROR(web_upload_storage_init(), TAG,
                        "Wi-Fi file storage initialization failed");
    if (!s_wifi_save_lock) s_wifi_save_lock = xSemaphoreCreateMutex();
    ESP_RETURN_ON_FALSE(s_wifi_save_lock, ESP_ERR_NO_MEM, TAG,
                        "Wi-Fi save lock allocation failed");
    if (!s_wifi_store.ready) {
        uint64_t boot_epoch = 0;
        esp_fill_random(&boot_epoch, sizeof(boot_epoch));
        const native_wifi_store_ops_t ops = {
            .lock = wifi_store_lock,
            .unlock = wifi_store_unlock,
            .read_live = wifi_store_read,
            .publish_csv = wifi_store_publish,
        };
        ESP_RETURN_ON_FALSE(native_wifi_store_init(&s_wifi_store, &ops, NULL,
                                                    boot_epoch),
                            ESP_FAIL, TAG, "Wi-Fi store initialization failed");
    }
    return ESP_OK;
}

native_wifi_result_t network_service_wifi_metadata(native_wifi_metadata_t *out) {
    return native_wifi_store_metadata(&s_wifi_store, out);
}

native_wifi_result_t network_service_wifi_edit(const native_wifi_edit_t *edit) {
    return native_wifi_store_edit(&s_wifi_store, edit);
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
    native_wifi_erase(line, sizeof(line));
    native_wifi_erase(&selected, sizeof(selected));
    return found;
}

static void station_lost_ip(void) {
    time_service_notify_network(false);
    xEventGroupClearBits(s_wifi_events, WIFI_CONNECTED_BIT);
    wifi_mode_t mode = WIFI_MODE_NULL;
    bool access_point = esp_wifi_get_mode(&mode) == ESP_OK &&
                        (mode == WIFI_MODE_AP || mode == WIFI_MODE_APSTA);
    native_state_set_network(s_state, access_point ? NATIVE_NETWORK_ACCESS_POINT
                                                   : NATIVE_NETWORK_STARTING, 0);
}

static void event_handler(void *arg, esp_event_base_t base, int32_t id,
                          void *event_data) {
    (void)arg;
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        if (s_have_credentials) esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        station_lost_ip();
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
        time_service_notify_network(true);
        xEventGroupClearBits(s_wifi_events, WIFI_FAILED_BIT);
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Client address: " IPSTR, IP2STR(&event->ip_info.ip));
    } else if (base == IP_EVENT && id == IP_EVENT_STA_LOST_IP) {
        station_lost_ip();
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
    // The desired file owns persistence; never create another driver NVS copy.
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
    if (!data || !size || size >= NATIVE_WIFI_FILE_BYTES)
        return ESP_ERR_INVALID_SIZE;
    return wifi_store_error(native_wifi_validate_csv(data, size));
}

esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size) {
    ESP_RETURN_ON_ERROR(network_service_validate_credentials_file(data, size),
                        TAG, "Invalid Wi-Fi file");
    return wifi_store_error(native_wifi_store_import(&s_wifi_store, data, size));
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
    esp_err_t result = network_service_save_credentials_file((const uint8_t *)line, size);
    native_wifi_erase(line, sizeof(line));
    return result;
}
