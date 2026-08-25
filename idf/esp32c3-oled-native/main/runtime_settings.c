#include "runtime_settings.h"

#include <stdatomic.h>
#include <string.h>

#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "nvs.h"

#define SETTINGS_NVS_NAMESPACE "runtime"
#define SETTINGS_NVS_AUDIO_INFO "audioinfo"
#define SETTINGS_NVS_SOFTAP_DELAY "softap"
#define SETTINGS_NVS_AUDIO_BUFFER "abuff"
#define SETTINGS_NVS_MDNS_NAME "mdns"
#define SETTINGS_NVS_WATCHDOG "watchdog"
#define SETTINGS_NVS_TZ_HOUR "tzh"
#define SETTINGS_NVS_TZ_MINUTE "tzm"
#define SETTINGS_NVS_SNTP1 "sntp1"
#define SETTINGS_NVS_SNTP2 "sntp2"
#define SETTINGS_NVS_TIME_INTERVAL "timeint"
#define SETTINGS_NVS_VOLUME_STEPS "volsteps"
#define SETTINGS_NVS_ENCODER_ACCELERATION "encacc"

#define MDNS_NAME_CAPACITY 24
#define SNTP_NAME_CAPACITY 35

static const char *const TAG = "runtime_settings";
static atomic_bool s_audio_info = RUNTIME_DEFAULT_AUDIO_INFO;
static atomic_uchar s_softap_delay_min = RUNTIME_DEFAULT_SOFTAP_DELAY_MIN;
static atomic_uchar s_audio_buffer_blocks =
    RUNTIME_DEFAULT_AUDIO_BUFFER_BLOCKS;
static atomic_bool s_watchdog = RUNTIME_DEFAULT_WATCHDOG;
static atomic_schar s_timezone_hour = RUNTIME_DEFAULT_TZ_HOUR;
static atomic_uchar s_timezone_minute = RUNTIME_DEFAULT_TZ_MINUTE;
static atomic_uint_least16_t s_time_sync_interval_min =
    RUNTIME_DEFAULT_TIME_SYNC_INTERVAL_MIN;
static atomic_uchar s_volume_steps = RUNTIME_DEFAULT_VOLUME_STEPS;
static atomic_uint_least16_t s_encoder_acceleration =
    RUNTIME_DEFAULT_ENCODER_ACCELERATION;
static SemaphoreHandle_t s_string_lock;
static char s_mdns_name[MDNS_NAME_CAPACITY] = RUNTIME_DEFAULT_MDNS_NAME;
static char s_sntp1[SNTP_NAME_CAPACITY] = RUNTIME_DEFAULT_SNTP1;
static char s_sntp2[SNTP_NAME_CAPACITY] = RUNTIME_DEFAULT_SNTP2;

static bool valid_host_text(const char *text, size_t capacity,
                            bool allow_empty) {
    if (!text) return false;
    size_t length = strlen(text);
    if (length >= capacity || (!allow_empty && !length)) return false;
    for (size_t index = 0; index < length; ++index) {
        unsigned char value = (unsigned char)text[index];
        if (value <= 0x20 || value == 0x7f || value == '"' || value == '/' ||
            value == '\\') {
            return false;
        }
    }
    return true;
}

static esp_err_t save_u8(const char *key, uint8_t value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(SETTINGS_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open runtime settings");
    esp_err_t result = nvs_set_u8(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static esp_err_t save_i8(const char *key, int8_t value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(SETTINGS_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open runtime settings");
    esp_err_t result = nvs_set_i8(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static esp_err_t save_u16(const char *key, uint16_t value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(SETTINGS_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open runtime settings");
    esp_err_t result = nvs_set_u16(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static esp_err_t save_string(const char *key, const char *value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(SETTINGS_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open runtime settings");
    esp_err_t result = nvs_set_str(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static void load_string(nvs_handle_t handle, const char *key, char *target,
                        size_t capacity, bool allow_empty) {
    char saved[SNTP_NAME_CAPACITY];
    size_t size = sizeof(saved);
    esp_err_t result = nvs_get_str(handle, key, saved, &size);
    if (result == ESP_OK && valid_host_text(saved, capacity, allow_empty)) {
        strlcpy(target, saved, capacity);
    } else if (result != ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGW(TAG, "Ignoring invalid saved %s", key);
    }
}

esp_err_t runtime_settings_init(void) {
    if (!s_string_lock) s_string_lock = xSemaphoreCreateMutex();
    ESP_RETURN_ON_FALSE(s_string_lock, ESP_ERR_NO_MEM, TAG,
                        "Runtime settings mutex allocation");
    nvs_handle_t handle;
    esp_err_t result =
        nvs_open(SETTINGS_NVS_NAMESPACE, NVS_READWRITE, &handle);
    if (result == ESP_ERR_NVS_NOT_FOUND) return ESP_OK;
    ESP_RETURN_ON_ERROR(result, TAG, "Open saved runtime settings");

    uint8_t u8;
    int8_t i8;
    uint16_t u16;
    if (nvs_get_u8(handle, SETTINGS_NVS_AUDIO_INFO, &u8) == ESP_OK &&
        u8 <= 1U) atomic_store(&s_audio_info, u8 != 0U);
    if (nvs_get_u8(handle, SETTINGS_NVS_SOFTAP_DELAY, &u8) == ESP_OK &&
        u8 <= 30U) atomic_store(&s_softap_delay_min, u8);
    if (nvs_get_u8(handle, SETTINGS_NVS_AUDIO_BUFFER, &u8) == ESP_OK &&
        u8 >= RUNTIME_MIN_AUDIO_BUFFER_BLOCKS) {
        uint8_t saved = u8;
        if (u8 > RUNTIME_MAX_AUDIO_BUFFER_BLOCKS) {
            u8 = RUNTIME_MAX_AUDIO_BUFFER_BLOCKS;
        }
        atomic_store(&s_audio_buffer_blocks, u8);
        if (saved != u8) {
            esp_err_t migration =
                nvs_set_u8(handle, SETTINGS_NVS_AUDIO_BUFFER, u8);
            if (migration == ESP_OK) migration = nvs_commit(handle);
            if (migration == ESP_OK) {
                ESP_LOGI(TAG, "Migrated audio buffer from %u to %u blocks",
                         saved, u8);
            } else {
                ESP_LOGW(TAG, "Audio buffer migration failed: %s",
                         esp_err_to_name(migration));
            }
        }
    }
    if (nvs_get_u8(handle, SETTINGS_NVS_WATCHDOG, &u8) == ESP_OK &&
        u8 <= 1U) atomic_store(&s_watchdog, u8 != 0U);
    if (nvs_get_i8(handle, SETTINGS_NVS_TZ_HOUR, &i8) == ESP_OK &&
        i8 >= -12 && i8 <= 14) atomic_store(&s_timezone_hour, i8);
    if (nvs_get_u8(handle, SETTINGS_NVS_TZ_MINUTE, &u8) == ESP_OK &&
        u8 <= 45U && u8 % 15U == 0U) atomic_store(&s_timezone_minute, u8);
    if (nvs_get_u16(handle, SETTINGS_NVS_TIME_INTERVAL, &u16) == ESP_OK &&
        u16 >= 15U && u16 <= 1440U) {
        atomic_store(&s_time_sync_interval_min, u16);
    }
    if (nvs_get_u8(handle, SETTINGS_NVS_VOLUME_STEPS, &u8) == ESP_OK &&
        u8 >= 1U && u8 <= 10U) atomic_store(&s_volume_steps, u8);
    if (nvs_get_u16(handle, SETTINGS_NVS_ENCODER_ACCELERATION, &u16) == ESP_OK &&
        u16 <= RUNTIME_MAX_ENCODER_ACCELERATION) {
        atomic_store(&s_encoder_acceleration, u16);
    }
    load_string(handle, SETTINGS_NVS_MDNS_NAME, s_mdns_name,
                sizeof(s_mdns_name), true);
    load_string(handle, SETTINGS_NVS_SNTP1, s_sntp1, sizeof(s_sntp1), false);
    load_string(handle, SETTINGS_NVS_SNTP2, s_sntp2, sizeof(s_sntp2), false);
    nvs_close(handle);
    ESP_LOGI(TAG,
             "Restored aif=%u softap=%u abuff=%u watchdog=%u tz=%d:%02u "
             "timeint=%u vols=%u enca=%u",
             runtime_settings_get_audio_info() ? 1U : 0U,
             runtime_settings_get_softap_delay_min(),
             runtime_settings_get_audio_buffer_blocks(),
             runtime_settings_get_watchdog() ? 1U : 0U,
             runtime_settings_get_timezone_hour(),
             runtime_settings_get_timezone_minute(),
             runtime_settings_get_time_sync_interval_min(),
             runtime_settings_get_volume_steps(),
             runtime_settings_get_encoder_acceleration());
    return ESP_OK;
}

bool runtime_settings_get_audio_info(void) { return atomic_load(&s_audio_info); }
uint8_t runtime_settings_get_softap_delay_min(void) {
    return atomic_load(&s_softap_delay_min);
}
uint8_t runtime_settings_get_audio_buffer_blocks(void) {
    return atomic_load(&s_audio_buffer_blocks);
}
bool runtime_settings_get_watchdog(void) { return atomic_load(&s_watchdog); }
int8_t runtime_settings_get_timezone_hour(void) {
    return atomic_load(&s_timezone_hour);
}
uint8_t runtime_settings_get_timezone_minute(void) {
    return atomic_load(&s_timezone_minute);
}
uint16_t runtime_settings_get_time_sync_interval_min(void) {
    return atomic_load(&s_time_sync_interval_min);
}
uint8_t runtime_settings_get_volume_steps(void) {
    return atomic_load(&s_volume_steps);
}
uint16_t runtime_settings_get_encoder_acceleration(void) {
    return atomic_load(&s_encoder_acceleration);
}

static void get_string(const char *source, char *output, size_t output_size) {
    if (!output || !output_size) return;
    if (s_string_lock &&
        xSemaphoreTake(s_string_lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        strlcpy(output, source, output_size);
        xSemaphoreGive(s_string_lock);
    } else {
        output[0] = '\0';
    }
}

void runtime_settings_get_mdns_name(char *output, size_t output_size) {
    get_string(s_mdns_name, output, output_size);
}
void runtime_settings_get_sntp1(char *output, size_t output_size) {
    get_string(s_sntp1, output, output_size);
}
void runtime_settings_get_sntp2(char *output, size_t output_size) {
    get_string(s_sntp2, output, output_size);
}

esp_err_t runtime_settings_set_audio_info(bool enabled) {
    ESP_RETURN_ON_ERROR(save_u8(SETTINGS_NVS_AUDIO_INFO, enabled ? 1U : 0U),
                        TAG, "Save audio-info setting");
    atomic_store(&s_audio_info, enabled);
    return ESP_OK;
}
esp_err_t runtime_settings_set_softap_delay_min(uint8_t minutes) {
    ESP_RETURN_ON_FALSE(minutes <= 30U, ESP_ERR_INVALID_ARG, TAG,
                        "SoftAP delay range");
    ESP_RETURN_ON_ERROR(save_u8(SETTINGS_NVS_SOFTAP_DELAY, minutes), TAG,
                        "Save SoftAP delay");
    atomic_store(&s_softap_delay_min, minutes);
    return ESP_OK;
}
esp_err_t runtime_settings_set_audio_buffer_blocks(uint8_t blocks) {
    ESP_RETURN_ON_FALSE(blocks >= RUNTIME_MIN_AUDIO_BUFFER_BLOCKS &&
                            blocks <= RUNTIME_MAX_AUDIO_BUFFER_BLOCKS,
                        ESP_ERR_INVALID_ARG, TAG, "Audio buffer range");
    ESP_RETURN_ON_ERROR(save_u8(SETTINGS_NVS_AUDIO_BUFFER, blocks), TAG,
                        "Save audio buffer");
    atomic_store(&s_audio_buffer_blocks, blocks);
    return ESP_OK;
}
esp_err_t runtime_settings_set_watchdog(bool enabled) {
    ESP_RETURN_ON_ERROR(save_u8(SETTINGS_NVS_WATCHDOG, enabled ? 1U : 0U), TAG,
                        "Save watchdog setting");
    atomic_store(&s_watchdog, enabled);
    return ESP_OK;
}
esp_err_t runtime_settings_set_timezone_hour(int8_t hour) {
    ESP_RETURN_ON_FALSE(hour >= -12 && hour <= 14, ESP_ERR_INVALID_ARG, TAG,
                        "Timezone hour range");
    ESP_RETURN_ON_ERROR(save_i8(SETTINGS_NVS_TZ_HOUR, hour), TAG,
                        "Save timezone hour");
    atomic_store(&s_timezone_hour, hour);
    return ESP_OK;
}
esp_err_t runtime_settings_set_timezone_minute(uint8_t minute) {
    ESP_RETURN_ON_FALSE(minute <= 45U && minute % 15U == 0U,
                        ESP_ERR_INVALID_ARG, TAG, "Timezone minute range");
    ESP_RETURN_ON_ERROR(save_u8(SETTINGS_NVS_TZ_MINUTE, minute), TAG,
                        "Save timezone minute");
    atomic_store(&s_timezone_minute, minute);
    return ESP_OK;
}
esp_err_t runtime_settings_set_time_sync_interval_min(uint16_t minutes) {
    ESP_RETURN_ON_FALSE(minutes >= 15U && minutes <= 1440U,
                        ESP_ERR_INVALID_ARG, TAG, "Time sync interval range");
    ESP_RETURN_ON_ERROR(save_u16(SETTINGS_NVS_TIME_INTERVAL, minutes), TAG,
                        "Save time sync interval");
    atomic_store(&s_time_sync_interval_min, minutes);
    return ESP_OK;
}
esp_err_t runtime_settings_set_volume_steps(uint8_t steps) {
    ESP_RETURN_ON_FALSE(steps >= 1U && steps <= 10U, ESP_ERR_INVALID_ARG, TAG,
                        "Volume step range");
    ESP_RETURN_ON_ERROR(save_u8(SETTINGS_NVS_VOLUME_STEPS, steps), TAG,
                        "Save volume steps");
    atomic_store(&s_volume_steps, steps);
    return ESP_OK;
}

esp_err_t runtime_settings_set_encoder_acceleration(uint16_t acceleration) {
    ESP_RETURN_ON_FALSE(acceleration <= RUNTIME_MAX_ENCODER_ACCELERATION,
                        ESP_ERR_INVALID_ARG, TAG,
                        "Encoder acceleration range");
    ESP_RETURN_ON_ERROR(
        save_u16(SETTINGS_NVS_ENCODER_ACCELERATION, acceleration), TAG,
        "Save encoder acceleration");
    atomic_store(&s_encoder_acceleration, acceleration);
    return ESP_OK;
}

static esp_err_t set_string(const char *key, const char *value, char *target,
                            size_t capacity, bool allow_empty) {
    ESP_RETURN_ON_FALSE(valid_host_text(value, capacity, allow_empty),
                        ESP_ERR_INVALID_ARG, TAG, "Invalid host setting");
    ESP_RETURN_ON_ERROR(save_string(key, value), TAG, "Save host setting");
    ESP_RETURN_ON_FALSE(s_string_lock &&
                            xSemaphoreTake(s_string_lock,
                                           pdMS_TO_TICKS(100)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "Runtime settings lock");
    strlcpy(target, value, capacity);
    xSemaphoreGive(s_string_lock);
    return ESP_OK;
}

esp_err_t runtime_settings_set_mdns_name(const char *name) {
    return set_string(SETTINGS_NVS_MDNS_NAME, name, s_mdns_name,
                      sizeof(s_mdns_name), true);
}
esp_err_t runtime_settings_set_sntp1(const char *server) {
    return set_string(SETTINGS_NVS_SNTP1, server, s_sntp1, sizeof(s_sntp1),
                      false);
}
esp_err_t runtime_settings_set_sntp2(const char *server) {
    return set_string(SETTINGS_NVS_SNTP2, server, s_sntp2, sizeof(s_sntp2),
                      false);
}
