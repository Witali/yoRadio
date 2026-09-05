#include "persistent_settings.h"

#include <stddef.h>
#include <string.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "nvs.h"

#define SETTINGS_NAMESPACE "yoradio"
#define SETTINGS_KEY "settings"
#define SETTINGS_MAGIC 0x59523836UL
#define SETTINGS_VERSION 1U

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint16_t payload_size;
    persistent_settings_t payload;
    uint32_t checksum;
} settings_blob_t;

static const char *TAG = "settings";
static SemaphoreHandle_t s_lock;
static persistent_settings_t s_settings;
static persistent_web_settings_t s_web = {.audio_info = true};

void persistent_settings_get_web(persistent_web_settings_t *output) {
    xSemaphoreTake(s_lock, portMAX_DELAY);
    *output = s_web;
    xSemaphoreGive(s_lock);
}

esp_err_t persistent_settings_update_web(const persistent_web_settings_t *settings) {
    if (!settings || settings->softap_delay_min > 30U)
        return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_web = *settings;
    xSemaphoreGive(s_lock);
    return ESP_OK;
}

static uint32_t checksum_bytes(const void *data, size_t length) {
    const uint8_t *bytes = (const uint8_t *)data;
    uint32_t value = 2166136261UL;
    while (length--) {
        value ^= *bytes++;
        value *= 16777619UL;
    }
    return value;
}

static void load_defaults(persistent_settings_t *settings) {
    memset(settings, 0, sizeof(*settings));
    settings->volume = 160;
    settings->last_station = 1;
    settings->smart_start = 2;
    settings->brightness = 38;
    settings->screensaver_enabled = true;
    settings->screensaver_timeout_s = 20;
    settings->normalization_target_db = -3;
    settings->normalization_max_gain_db = 12;
    settings->normalization_time_ms = 5000;
    settings->time_sync_interval_min = 60;
    settings->volume_steps = 2;
    strcpy(settings->mdns_name, "yoradio-esp8266");
    strcpy(settings->sntp1, "pool.ntp.org");
    strcpy(settings->sntp2, "time.nist.gov");
}

static bool settings_valid(const persistent_settings_t *settings) {
    return settings && settings->last_station > 0 &&
           settings->balance >= -16 && settings->balance <= 16 &&
           settings->smart_start <= 2 && settings->brightness <= 100 &&
           settings->normalization_target_db >= -24 &&
           settings->normalization_target_db <= 0 &&
           settings->normalization_max_gain_db <= 24 &&
           settings->normalization_time_ms >= 100 &&
           settings->normalization_time_ms <= 30000 &&
           settings->timezone_hour >= -12 && settings->timezone_hour <= 14 &&
           settings->timezone_minute <= 45 &&
           settings->timezone_minute % 15 == 0 &&
           settings->time_sync_interval_min >= 15 &&
           settings->time_sync_interval_min <= 1440 &&
           settings->volume_steps >= 1 && settings->volume_steps <= 10 &&
           settings->mdns_name[sizeof(settings->mdns_name) - 1] == '\0' &&
           settings->sntp1[sizeof(settings->sntp1) - 1] == '\0' &&
           settings->sntp2[sizeof(settings->sntp2) - 1] == '\0';
}

esp_err_t persistent_settings_reset_group(const char *group) {
    persistent_settings_t defaults, settings;
    load_defaults(&defaults);
    persistent_settings_get(&settings);
    persistent_web_settings_t web;
    persistent_settings_get_web(&web);
    if (strcmp(group, "1") == 0) {
        settings = defaults;
        web.audio_info = true; web.softap_delay_min = 0;
    } else if (strcmp(group, "system") == 0) {
        settings.smart_start = defaults.smart_start;
        settings.normalization_enabled = defaults.normalization_enabled;
        settings.normalization_max_gain_db = defaults.normalization_max_gain_db;
        settings.normalization_target_db = defaults.normalization_target_db;
        settings.normalization_time_ms = defaults.normalization_time_ms;
        web.audio_info = true; web.softap_delay_min = 0;
    } else if (strcmp(group, "screen") == 0) {
        settings.brightness = defaults.brightness;
        settings.station_uppercase = defaults.station_uppercase;
        settings.numbered_playlist = defaults.numbered_playlist;
        settings.screensaver_enabled = defaults.screensaver_enabled;
        settings.screensaver_blank = defaults.screensaver_blank;
        settings.screensaver_timeout_s = defaults.screensaver_timeout_s;
    } else if (strcmp(group, "timezone") == 0) {
        settings.timezone_hour = defaults.timezone_hour;
        settings.timezone_minute = defaults.timezone_minute;
        settings.time_sync_interval_min = defaults.time_sync_interval_min;
        memcpy(settings.sntp1, defaults.sntp1, sizeof(settings.sntp1));
        memcpy(settings.sntp2, defaults.sntp2, sizeof(settings.sntp2));
    } else if (strcmp(group, "controls") == 0) {
        settings.volume_steps = defaults.volume_steps;
        settings.encoder_acceleration = defaults.encoder_acceleration;
    } else return ESP_ERR_NOT_SUPPORTED;
    esp_err_t result = persistent_settings_update_runtime(&settings);
    if (result == ESP_OK) result = persistent_settings_update_web(&web);
    return result;
}

esp_err_t persistent_settings_init(void) {
    s_lock = xSemaphoreCreateMutex();
    if (!s_lock) return ESP_ERR_NO_MEM;
    load_defaults(&s_settings);
    nvs_handle handle;
    esp_err_t result = nvs_open(SETTINGS_NAMESPACE, NVS_READONLY, &handle);
    if (result == ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGI(TAG, "Using default settings");
        return ESP_OK;
    }
    if (result != ESP_OK) return result;
    settings_blob_t blob;
    size_t size = sizeof(blob);
    uint8_t audio_info = 1, ap_delay = 0;
    (void)nvs_get_u8(handle, "audioinfo", &audio_info);
    (void)nvs_get_u8(handle, "apdelay", &ap_delay);
    s_web.audio_info = audio_info != 0;
    s_web.softap_delay_min = ap_delay <= 30U ? ap_delay : 0U;
    result = nvs_get_blob(handle, SETTINGS_KEY, &blob, &size);
    nvs_close(handle);
    if (result == ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGI(TAG, "Using default settings");
        return ESP_OK;
    }
    if (result != ESP_OK) return result;
    bool valid = size == sizeof(blob) && blob.magic == SETTINGS_MAGIC &&
                 blob.version == SETTINGS_VERSION &&
                 blob.payload_size == sizeof(blob.payload) &&
                 blob.checksum == checksum_bytes(&blob.payload,
                                                 sizeof(blob.payload)) &&
                 settings_valid(&blob.payload);
    if (!valid) {
        ESP_LOGW(TAG, "Ignoring incompatible or damaged settings blob");
        return ESP_OK;
    }
    s_settings = blob.payload;
    ESP_LOGI(TAG, "Settings restored: station=%u volume=%u",
             s_settings.last_station, s_settings.volume);
    return ESP_OK;
}

void persistent_settings_get(persistent_settings_t *output) {
    if (!output || !s_lock) return;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    *output = s_settings;
    xSemaphoreGive(s_lock);
}

esp_err_t persistent_settings_save(const persistent_settings_t *settings) {
    if (!settings_valid(settings)) return ESP_ERR_INVALID_ARG;
    settings_blob_t blob = {
        .magic = SETTINGS_MAGIC,
        .version = SETTINGS_VERSION,
        .payload_size = sizeof(*settings),
        .payload = *settings,
    };
    blob.checksum = checksum_bytes(&blob.payload, sizeof(blob.payload));
    nvs_handle handle;
    esp_err_t result = nvs_open(SETTINGS_NAMESPACE, NVS_READWRITE, &handle);
    if (result != ESP_OK) return result;
    result = nvs_set_blob(handle, SETTINGS_KEY, &blob, sizeof(blob));
    persistent_web_settings_t web;
    persistent_settings_get_web(&web);
    if (result == ESP_OK) result = nvs_set_u8(handle, "audioinfo", web.audio_info);
    if (result == ESP_OK) result = nvs_set_u8(handle, "apdelay", web.softap_delay_min);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    if (result != ESP_OK) return result;
    /* Never overwrite newer runtime values with the older flash snapshot. */
    return ESP_OK;
}

esp_err_t persistent_settings_update_runtime(
    const persistent_settings_t *settings) {
    if (!settings_valid(settings)) return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_settings = *settings;
    xSemaphoreGive(s_lock);
    return ESP_OK;
}

esp_err_t persistent_settings_commit(void) {
    persistent_settings_t snapshot;
    persistent_settings_get(&snapshot);
    return persistent_settings_save(&snapshot);
}

void persistent_settings_set_volume_runtime(uint8_t volume) {
    if (!s_lock) return;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_settings.volume = volume > 254U ? 254U : volume;
    xSemaphoreGive(s_lock);
}

void persistent_settings_set_last_station_runtime(uint16_t station) {
    if (!s_lock || !station) return;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_settings.last_station = station;
    xSemaphoreGive(s_lock);
}

void persistent_settings_set_smart_start_runtime(uint8_t state) {
    if (!s_lock || state > 2U) return;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_settings.smart_start = state;
    xSemaphoreGive(s_lock);
}
