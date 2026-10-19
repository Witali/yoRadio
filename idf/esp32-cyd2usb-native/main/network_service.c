#include "network_service.h"

#include <stdatomic.h>
#include <stdio.h>
#include <string.h>

#include "esp_event.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_random.h"
#include "esp_wifi.h"
#include "freertos/task.h"
#include "esp_wifi_default.h"
#include "freertos/semphr.h"
#include "web_upload.h"
#include "native_wifi_file.h"
#include "network_profiles.h"
#include "network_runtime.h"
#include "network_netif.h"

static const char *const TAG = "network";
static network_netif_t s_station_netif;
static native_state_t *s_state;
enum { NETWORK_OFF, NETWORK_STARTING, NETWORK_READY, NETWORK_RETAINED };
static atomic_uint s_network_start;
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

esp_err_t network_service_start(native_state_t *state) {
    if (!state || !state->lock) return ESP_ERR_INVALID_ARG;
    unsigned expected = NETWORK_OFF;
    if (!atomic_compare_exchange_strong(&s_network_start, &expected, NETWORK_STARTING))
        return expected == NETWORK_READY && s_state == state ? ESP_OK : ESP_ERR_INVALID_STATE;
    bool loop_owned = false, wifi_owned = false;
    network_profiles_t profiles = {0};
    esp_err_t result = network_service_storage_init();
    if (result != ESP_OK) goto failed;
    result = esp_netif_init();
    if (result != ESP_OK) goto failed;
    result = esp_event_loop_create_default();
    if (result == ESP_OK) loop_owned = true;
    else if (result != ESP_ERR_INVALID_STATE) goto failed;
    result = network_netif_create(&s_station_netif, false);
    if (result != ESP_OK) goto failed;
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    result = esp_wifi_init(&init);
    if (result != ESP_OK) goto failed;
    wifi_owned = true;
    // Desired CSV is the sole persistent source, including an explicit empty file.
    result = esp_wifi_set_storage(WIFI_STORAGE_RAM);
    if (result != ESP_OK) goto failed;
    result = esp_wifi_set_mode(WIFI_MODE_STA);
    if (result != ESP_OK) goto failed;
    esp_err_t loaded = network_profiles_load(&profiles);
    if (loaded != ESP_OK) {
        // A complete read failure is an empty active table, never a partial one.
        // The runtime snapshot exposes no private rows or passwords.
        native_wifi_erase(&profiles, sizeof(profiles));
        ESP_LOGW(TAG, "Active Wi-Fi profiles unavailable: %s", esp_err_to_name(loaded));
    }
    result = network_runtime_start(state, s_station_netif.handle, &profiles);
    native_wifi_erase(&profiles, sizeof(profiles));
    if (result != ESP_OK) goto failed;
    result = esp_wifi_start();
    if (result != ESP_OK) goto failed;
    s_state = state;
    atomic_store_explicit(&s_network_start, NETWORK_READY, memory_order_release);
    // Bound bootstrap waiting; the owner still services late loss/portal work.
    // Successful infrastructure startup does not imply station association.
    result = network_runtime_wait_initial(20000);
    if (result == ESP_ERR_TIMEOUT) return ESP_OK;
    return result;
failed:
    native_wifi_erase(&profiles, sizeof(profiles));
    // Never tear down a netif or driver while retained callbacks can read it.
    if (wifi_owned) {
        esp_err_t stopped = esp_wifi_stop();
        if (stopped != ESP_OK && stopped != ESP_ERR_WIFI_NOT_STARTED) {
            atomic_store(&s_network_start, NETWORK_RETAINED);
            return result;
        }
    }
    if (network_runtime_stop(2000) != ESP_OK ||
        (wifi_owned && esp_wifi_deinit() != ESP_OK)) {
        atomic_store(&s_network_start, NETWORK_RETAINED);
        return result;
    }
    if (network_netif_release(&s_station_netif) != ESP_OK) {
        atomic_store(&s_network_start, NETWORK_RETAINED);
        return result;
    }
    if (loop_owned) esp_event_loop_delete_default();
    atomic_store_explicit(&s_network_start, NETWORK_OFF, memory_order_release);
    return result;
}

esp_err_t network_service_retry_client(void) {
    return network_runtime_retry();
}

esp_err_t network_service_snapshot(network_snapshot_t *out, uint32_t timeout_ms) {
    return network_runtime_snapshot(out, timeout_ms);
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
    size_t ssid_size = strnlen(ssid, NATIVE_WIFI_SSID_BYTES);
    size_t password_size = strnlen(password, NATIVE_WIFI_PASSWORD_BYTES);
    ESP_RETURN_ON_FALSE(ssid_size && ssid_size < NATIVE_WIFI_SSID_BYTES &&
                            password_size < NATIVE_WIFI_PASSWORD_BYTES,
                        ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi field size");
    ESP_RETURN_ON_FALSE(!strpbrk(ssid, "\t\r\n") && !strpbrk(password, "\t\r\n"),
                        ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi field");
    char line[NATIVE_WIFI_SSID_BYTES +
              NATIVE_WIFI_PASSWORD_BYTES];
    memcpy(line, ssid, ssid_size);
    line[ssid_size] = '\t';
    memcpy(line + ssid_size + 1U, password, password_size);
    size_t size = ssid_size + 1U + password_size;
    line[size++] = '\n';
    esp_err_t result = network_service_save_credentials_file((const uint8_t *)line, size);
    native_wifi_erase(line, sizeof(line));
    return result;
}
