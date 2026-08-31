#include "radio_control.h"

#include <stdbool.h>
#include <string.h>

#include "audio_service.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "native_audio_output.h"
#include "native_state.h"
#include "network_service.h"
#include "persistent_settings.h"
#include "playlist_service.h"

#define SETTINGS_SAVE_DELAY_MS 1000U

static const char *TAG = "radio";
static SemaphoreHandle_t s_lock;
static uint16_t s_current_station = 1;
static bool s_settings_dirty;
static bool s_resume_when_connected;
static TickType_t s_settings_changed_at;

static void mark_settings_dirty(void) {
    s_settings_dirty = true;
    s_settings_changed_at = xTaskGetTickCount();
}

static void update_smart_start(bool playing) {
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    if (settings.smart_start == 2U) return;
    uint8_t state = playing ? 1U : 0U;
    if (settings.smart_start != state) {
        persistent_settings_set_smart_start_runtime(state);
        mark_settings_dirty();
    }
}

static esp_err_t preview_station(uint16_t index, const char *name,
                                 const char *url, int8_t output_gain_db,
                                 void *context) {
    (void)url;
    (void)output_gain_db;
    (void)context;
    native_state_set_station(index, name);
    return ESP_OK;
}

static esp_err_t start_station(uint16_t index, const char *name,
                               const char *url, int8_t output_gain_db,
                               void *context) {
    (void)context;
    if (strncmp(url, "http://", 7) != 0) {
        native_state_set_audio(false, false, "HTTPS NOT SUPPORTED");
        return ESP_ERR_NOT_SUPPORTED;
    }
    esp_err_t result = audio_service_play(url);
    if (result != ESP_OK) return result;
    s_current_station = index;
    native_state_set_station(index, name);
    native_audio_output_reset_normalizer();
    /* Per-station gain is deliberately reset at every station change. The
     * optional playlist field is retained for compatibility but is not
     * allowed to leak an old station's boost into a new stream. */
    if (output_gain_db != 0)
        ESP_LOGI(TAG, "Station gain %d dB ignored/reset to 0 dB",
                 output_gain_db);
    persistent_settings_set_last_station_runtime(index);
    update_smart_start(true);
    mark_settings_dirty();
    ESP_LOGI(TAG, "Station %u: %s", index, name);
    return ESP_OK;
}

static esp_err_t play_locked(uint16_t station) {
    return playlist_service_visit(station, start_station, NULL);
}

esp_err_t radio_control_init(void) {
    s_lock = xSemaphoreCreateMutex();
    if (!s_lock) return ESP_ERR_NO_MEM;
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    native_audio_output_set_volume_runtime(settings.volume);
    native_audio_output_set_balance_runtime(settings.balance);
    native_state_set_volume(settings.volume);
    uint16_t count = playlist_service_count();
    native_state_set_station_count(count);
    uint16_t selected = settings.last_station;
    if (!selected || selected > count ||
        playlist_service_visit(selected, preview_station, NULL) != ESP_OK) {
        if (!playlist_service_find_http_index(1, 1, &selected)) {
            native_state_set_audio(false, false, "PLAYLIST EMPTY");
            return count ? ESP_ERR_NOT_SUPPORTED : ESP_ERR_NOT_FOUND;
        }
        playlist_service_visit(selected, preview_station, NULL);
    }
    s_current_station = selected;
    /* Network startup is asynchronous. Defer smart-start until DHCP has
     * completed instead of blocking/failing before the interface has an IP. */
    s_resume_when_connected = settings.smart_start == 1U;
#ifdef YORADIO_ESP8266_AUDIO_PROFILE_URL
    s_resume_when_connected = true;
#endif
    return ESP_OK;
}

esp_err_t radio_control_play(uint16_t station) {
    if (!s_lock) return ESP_ERR_INVALID_STATE;
    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(500)) != pdTRUE)
        return ESP_ERR_TIMEOUT;
    esp_err_t result = play_locked(station);
    xSemaphoreGive(s_lock);
    return result;
}

esp_err_t radio_control_stop(void) {
    if (!s_lock) return ESP_ERR_INVALID_STATE;
    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(500)) != pdTRUE)
        return ESP_ERR_TIMEOUT;
    esp_err_t result = audio_service_stop();
    if (result == ESP_OK) {
        update_smart_start(false);
        mark_settings_dirty();
    }
    xSemaphoreGive(s_lock);
    return result;
}

esp_err_t radio_control_toggle(void) {
    native_state_t state;
    native_state_snapshot(&state);
    return state.playing || state.connecting
               ? radio_control_stop()
               : radio_control_play(s_current_station);
}

static esp_err_t step_station(int direction) {
    if (!s_lock) return ESP_ERR_INVALID_STATE;
    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(500)) != pdTRUE)
        return ESP_ERR_TIMEOUT;
    uint16_t found = 0;
    esp_err_t result = playlist_service_find_http_index(
                           s_current_station, direction, &found)
                           ? play_locked(found)
                           : ESP_ERR_NOT_FOUND;
    xSemaphoreGive(s_lock);
    return result;
}

esp_err_t radio_control_next(void) { return step_station(1); }
esp_err_t radio_control_previous(void) { return step_station(-1); }

esp_err_t radio_control_adjust_volume(int delta) {
    if (!s_lock) return ESP_ERR_INVALID_STATE;
    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE)
        return ESP_ERR_TIMEOUT;
    int volume = (int)native_audio_output_volume() + delta;
    if (volume < 0) volume = 0;
    if (volume > 254) volume = 254;
    native_audio_output_set_volume_runtime((uint8_t)volume);
    native_state_set_volume((uint8_t)volume);
    persistent_settings_set_volume_runtime((uint8_t)volume);
    mark_settings_dirty();
    xSemaphoreGive(s_lock);
    return ESP_OK;
}

void radio_control_flush_pending(void) {
    if (s_resume_when_connected && network_service_connected()) {
        s_resume_when_connected = false;
#ifdef YORADIO_ESP8266_AUDIO_PROFILE_URL
        esp_err_t result = audio_service_play(
            YORADIO_ESP8266_AUDIO_PROFILE_URL);
        if (result == ESP_OK) {
            native_state_set_station(s_current_station, "PROFILE STREAM");
        }
#else
        esp_err_t result = radio_control_play(s_current_station);
#endif
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Deferred smart start failed: %s",
                     esp_err_to_name(result));
        }
    }
    if (!s_lock || !s_settings_dirty) return;
    TickType_t elapsed = xTaskGetTickCount() - s_settings_changed_at;
    if (elapsed < pdMS_TO_TICKS(SETTINGS_SAVE_DELAY_MS)) return;
    if (xSemaphoreTake(s_lock, 0) != pdTRUE) return;
    if (s_settings_dirty &&
        xTaskGetTickCount() - s_settings_changed_at >=
            pdMS_TO_TICKS(SETTINGS_SAVE_DELAY_MS)) {
        esp_err_t result = persistent_settings_commit();
        if (result == ESP_OK) s_settings_dirty = false;
        else ESP_LOGW(TAG, "Settings save failed: %s",
                      esp_err_to_name(result));
    }
    xSemaphoreGive(s_lock);
}

void radio_control_settings_changed(void) {
    if (!s_lock) return;
    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) return;
    mark_settings_dirty();
    xSemaphoreGive(s_lock);
}
