#include "native_audio_settings.h"

#include <stdatomic.h>

#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "nvs.h"

#define AUDIO_NVS_NAMESPACE "audio"
#define AUDIO_NVS_VOLUME "volume"
#define AUDIO_NVS_BALANCE "balance"

static const char *const TAG = "audio_settings";
static atomic_uchar s_volume = NATIVE_AUDIO_DEFAULT_VOLUME;
static atomic_schar s_balance = NATIVE_AUDIO_DEFAULT_BALANCE;
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
    nvs_handle_t handle;
    esp_err_t result = nvs_open(AUDIO_NVS_NAMESPACE, NVS_READONLY, &handle);
    if (result == ESP_OK) {
        uint8_t saved_volume = volume;
        int8_t saved_balance = balance;
        esp_err_t volume_result =
            nvs_get_u8(handle, AUDIO_NVS_VOLUME, &saved_volume);
        esp_err_t balance_result =
            nvs_get_i8(handle, AUDIO_NVS_BALANCE, &saved_balance);
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
    } else if (result != ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGW(TAG, "Audio settings unavailable: %s",
                 esp_err_to_name(result));
    }

    atomic_store(&s_volume, volume);
    atomic_store(&s_balance, balance);
    atomic_store(&s_volume_dirty, false);
    if (!s_volume_timer) {
        const esp_timer_create_args_t timer = {
            .callback = save_volume_callback,
            .name = "save_volume",
        };
        ESP_RETURN_ON_ERROR(esp_timer_create(&timer, &s_volume_timer), TAG,
                            "Create delayed volume timer");
    }
    ESP_LOGI(TAG, "Restored volume %u, balance %d", volume, balance);
    return ESP_OK;
}

uint8_t native_audio_settings_get_volume(void) {
    return atomic_load(&s_volume);
}

int8_t native_audio_settings_get_balance(void) {
    return atomic_load(&s_balance);
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
