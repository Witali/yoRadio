#include "native_audio_settings.h"

#include <stdatomic.h>

#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "nvs.h"

#define AUDIO_NVS_NAMESPACE "audio"
#define AUDIO_NVS_VOLUME "volume"
#define AUDIO_NVS_BALANCE "balance"
#define AUDIO_NVS_NORMALIZATION "normalize"
#define AUDIO_NVS_NORMALIZATION_GAIN "normgain"
#define AUDIO_NVS_NORMALIZATION_TARGET "normtarget"
#define AUDIO_NVS_NORMALIZATION_TIME "normtime"

static const char *const TAG = "audio_settings";
static atomic_uchar s_volume = NATIVE_AUDIO_DEFAULT_VOLUME;
static atomic_schar s_balance = NATIVE_AUDIO_DEFAULT_BALANCE;
static atomic_bool s_normalization = NATIVE_AUDIO_DEFAULT_NORMALIZATION;
static atomic_uchar s_normalization_gain_db = NATIVE_AUDIO_DEFAULT_NORMALIZATION_GAIN_DB;
static atomic_schar s_normalization_target_dbfs = NATIVE_AUDIO_DEFAULT_NORMALIZATION_TARGET_DBFS;
static atomic_uint_least16_t s_normalization_time_ms = NATIVE_AUDIO_DEFAULT_NORMALIZATION_TIME_MS;
static atomic_bool s_volume_dirty;
static esp_timer_handle_t s_volume_timer;

static esp_err_t save_u8(const char *key, uint8_t value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(nvs_open(AUDIO_NVS_NAMESPACE, NVS_READWRITE, &handle),
                        TAG, "Open audio settings");
    esp_err_t result = nvs_set_u8(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static esp_err_t save_i8(const char *key, int8_t value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(nvs_open(AUDIO_NVS_NAMESPACE, NVS_READWRITE, &handle),
                        TAG, "Open audio settings");
    esp_err_t result = nvs_set_i8(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static esp_err_t save_u16(const char *key, uint16_t value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(nvs_open(AUDIO_NVS_NAMESPACE, NVS_READWRITE, &handle),
                        TAG, "Open audio settings");
    esp_err_t result = nvs_set_u16(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static void save_volume_callback(void *argument) {
    (void)argument;
    esp_err_t result = native_audio_settings_flush();
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Delayed volume save failed: %s",
                 esp_err_to_name(result));
    }
}

esp_err_t native_audio_settings_init(void) {
    uint8_t volume = NATIVE_AUDIO_DEFAULT_VOLUME;
    int8_t balance = NATIVE_AUDIO_DEFAULT_BALANCE;
    bool normalization = NATIVE_AUDIO_DEFAULT_NORMALIZATION;
    uint8_t normalization_gain_db = NATIVE_AUDIO_DEFAULT_NORMALIZATION_GAIN_DB;
    int8_t normalization_target_dbfs = NATIVE_AUDIO_DEFAULT_NORMALIZATION_TARGET_DBFS;
    uint16_t normalization_time_ms = NATIVE_AUDIO_DEFAULT_NORMALIZATION_TIME_MS;
    nvs_handle_t handle;
    esp_err_t result = nvs_open(AUDIO_NVS_NAMESPACE, NVS_READONLY, &handle);
    if (result == ESP_OK) {
        uint8_t saved_volume = volume;
        int8_t saved_balance = balance;
        uint8_t saved_normalization = normalization ? 1U : 0U;
        uint8_t saved_normalization_gain_db = normalization_gain_db;
        int8_t saved_normalization_target_dbfs = normalization_target_dbfs;
        uint16_t saved_normalization_time_ms = normalization_time_ms;
        esp_err_t volume_result =
            nvs_get_u8(handle, AUDIO_NVS_VOLUME, &saved_volume);
        esp_err_t balance_result =
            nvs_get_i8(handle, AUDIO_NVS_BALANCE, &saved_balance);
        esp_err_t normalization_result = nvs_get_u8(
            handle, AUDIO_NVS_NORMALIZATION, &saved_normalization);
        esp_err_t normalization_gain_result = nvs_get_u8(
            handle, AUDIO_NVS_NORMALIZATION_GAIN,
            &saved_normalization_gain_db);
        esp_err_t normalization_target_result = nvs_get_i8(
            handle, AUDIO_NVS_NORMALIZATION_TARGET,
            &saved_normalization_target_dbfs);
        esp_err_t normalization_time_result = nvs_get_u16(
            handle, AUDIO_NVS_NORMALIZATION_TIME,
            &saved_normalization_time_ms);
        nvs_close(handle);
        if (volume_result == ESP_OK && saved_volume <= 254U) {
            volume = saved_volume;
        } else if (volume_result != ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGW(TAG, "Ignoring invalid saved volume");
        }
        if (balance_result == ESP_OK && saved_balance >= -16 &&
            saved_balance <= 16) {
            balance = saved_balance;
        } else if (balance_result != ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGW(TAG, "Ignoring invalid saved balance");
        }
        if (normalization_result == ESP_OK && saved_normalization <= 1U) {
            normalization = saved_normalization != 0U;
        } else if (normalization_result != ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGW(TAG, "Ignoring invalid saved normalization state");
        }
        if (normalization_gain_result == ESP_OK &&
            saved_normalization_gain_db <= 20U) {
            normalization_gain_db = saved_normalization_gain_db;
        } else if (normalization_gain_result != ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGW(TAG, "Ignoring invalid saved normalization gain");
        }
        if (normalization_target_result == ESP_OK &&
            saved_normalization_target_dbfs >= -20 &&
            saved_normalization_target_dbfs <= 0) {
            normalization_target_dbfs = saved_normalization_target_dbfs;
        } else if (normalization_target_result != ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGW(TAG, "Ignoring invalid saved normalization target");
        }
        if (normalization_time_result == ESP_OK &&
            saved_normalization_time_ms >= 100U &&
            saved_normalization_time_ms <= 10000U) {
            normalization_time_ms = saved_normalization_time_ms;
        } else if (normalization_time_result != ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGW(TAG, "Ignoring invalid saved normalization time");
        }
    } else if (result != ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGW(TAG, "Audio settings unavailable: %s",
                 esp_err_to_name(result));
    }

    atomic_store(&s_volume, volume);
    atomic_store(&s_balance, balance);
    atomic_store(&s_normalization, normalization);
    atomic_store(&s_normalization_gain_db, normalization_gain_db);
    atomic_store(&s_normalization_target_dbfs, normalization_target_dbfs);
    atomic_store(&s_normalization_time_ms, normalization_time_ms);
    atomic_store(&s_volume_dirty, false);
    if (!s_volume_timer) {
        const esp_timer_create_args_t timer = {
            .callback = save_volume_callback,
            .name = "save_volume",
        };
        ESP_RETURN_ON_ERROR(esp_timer_create(&timer, &s_volume_timer), TAG,
                            "Create delayed volume timer");
    }
    ESP_LOGI(TAG,
             "Restored volume %u, balance %d, normalization %u/%u/%d/%u",
             volume, balance, normalization ? 1U : 0U,
             normalization_gain_db, normalization_target_dbfs,
             normalization_time_ms);
    return ESP_OK;
}

uint8_t native_audio_settings_get_volume(void) {
    return atomic_load(&s_volume);
}

int8_t native_audio_settings_get_balance(void) {
    return atomic_load(&s_balance);
}

bool native_audio_settings_get_normalization(void) {
    return atomic_load(&s_normalization);
}

uint8_t native_audio_settings_get_normalization_gain_db(void) {
    return atomic_load(&s_normalization_gain_db);
}

int8_t native_audio_settings_get_normalization_target_dbfs(void) {
    return atomic_load(&s_normalization_target_dbfs);
}

uint16_t native_audio_settings_get_normalization_time_ms(void) {
    return atomic_load(&s_normalization_time_ms);
}

esp_err_t native_audio_settings_set_volume(uint8_t volume) {
    if (volume > 254U) volume = 254U;
    atomic_store(&s_volume, volume);
    atomic_store(&s_volume_dirty, true);
    ESP_RETURN_ON_FALSE(s_volume_timer, ESP_ERR_INVALID_STATE, TAG,
                        "Audio settings are not initialized");
    esp_timer_stop(s_volume_timer);
    return esp_timer_start_once(
        s_volume_timer, (uint64_t)NATIVE_AUDIO_VOLUME_SAVE_DELAY_MS * 1000U);
}

esp_err_t native_audio_settings_set_balance(int8_t balance) {
    if (balance < -16) balance = -16;
    if (balance > 16) balance = 16;
    atomic_store(&s_balance, balance);
    esp_err_t result = save_i8(AUDIO_NVS_BALANCE, balance);
    if (result == ESP_OK) ESP_LOGI(TAG, "Saved balance %d", balance);
    return result;
}

esp_err_t native_audio_settings_set_normalization(bool enabled) {
    atomic_store(&s_normalization, enabled);
    esp_err_t result = save_u8(AUDIO_NVS_NORMALIZATION, enabled ? 1U : 0U);
    if (result == ESP_OK) ESP_LOGI(TAG, "Saved normalization %u", enabled);
    return result;
}

esp_err_t native_audio_settings_set_normalization_gain_db(uint8_t gain_db) {
    if (gain_db > 20U) gain_db = 20U;
    atomic_store(&s_normalization_gain_db, gain_db);
    esp_err_t result = save_u8(AUDIO_NVS_NORMALIZATION_GAIN, gain_db);
    if (result == ESP_OK) ESP_LOGI(TAG, "Saved normalization gain %u", gain_db);
    return result;
}

esp_err_t native_audio_settings_set_normalization_target_dbfs(int8_t target_dbfs) {
    if (target_dbfs < -20) target_dbfs = -20;
    if (target_dbfs > 0) target_dbfs = 0;
    atomic_store(&s_normalization_target_dbfs, target_dbfs);
    esp_err_t result = save_i8(AUDIO_NVS_NORMALIZATION_TARGET, target_dbfs);
    if (result == ESP_OK) ESP_LOGI(TAG, "Saved normalization target %d", target_dbfs);
    return result;
}

esp_err_t native_audio_settings_set_normalization_time_ms(uint16_t time_ms) {
    if (time_ms < 100U) time_ms = 100U;
    if (time_ms > 10000U) time_ms = 10000U;
    atomic_store(&s_normalization_time_ms, time_ms);
    esp_err_t result = save_u16(AUDIO_NVS_NORMALIZATION_TIME, time_ms);
    if (result == ESP_OK) ESP_LOGI(TAG, "Saved normalization time %u", time_ms);
    return result;
}

esp_err_t native_audio_settings_flush(void) {
    if (!atomic_exchange(&s_volume_dirty, false)) return ESP_OK;
    uint8_t volume = atomic_load(&s_volume);
    esp_err_t result = save_u8(AUDIO_NVS_VOLUME, volume);
    if (result != ESP_OK) {
        atomic_store(&s_volume_dirty, true);
        return result;
    }
    ESP_LOGI(TAG, "Saved volume %u", volume);
    return ESP_OK;
}
