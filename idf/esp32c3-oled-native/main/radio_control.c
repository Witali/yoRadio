#include "radio_control.h"

#include <stdio.h>
#include <string.h>

#include "audio_service.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "nvs.h"

#define PLAYLIST_PATH "/spiffs/data/playlist.csv"
#define RADIO_NVS_NAMESPACE "radio"
#define RADIO_NVS_LAST_STATION "last_station"
#define RADIO_NVS_SMARTSTART "smartstart"
#define SMARTSTART_STOPPED 0U
#define SMARTSTART_PLAYING 1U
#define SMARTSTART_DISABLED 2U

static const char *const TAG = "radio_control";
static SemaphoreHandle_t s_lock;
static native_state_t *s_state;
static uint16_t s_current_item = 1;
static uint8_t s_smartstart = SMARTSTART_DISABLED;
static char s_current_name[144] = "yoRadio native";
static char s_current_url[512];
// Playlist access is serialized by s_lock. Keep the parsing and candidate
// station buffers off caller task stacks: BOOT has to remain safe while the
// single-core C3 is also decoding audio.
static char s_playlist_line[768];
static char s_candidate_name[144];
static char s_candidate_url[512];

static bool load_last_station(uint16_t *item) {
    nvs_handle_t handle;
    esp_err_t result = nvs_open(RADIO_NVS_NAMESPACE, NVS_READONLY, &handle);
    if (result == ESP_ERR_NVS_NOT_FOUND) return false;
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Last station storage unavailable: %s",
                 esp_err_to_name(result));
        return false;
    }

    uint16_t saved = 0;
    result = nvs_get_u16(handle, RADIO_NVS_LAST_STATION, &saved);
    nvs_close(handle);
    if (result == ESP_ERR_NVS_NOT_FOUND) return false;
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Could not read last station: %s",
                 esp_err_to_name(result));
        return false;
    }
    if (!saved) {
        ESP_LOGW(TAG, "Ignoring invalid saved station 0");
        return false;
    }
    *item = saved;
    return true;
}

static esp_err_t save_last_station(uint16_t item) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(RADIO_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open last station storage");
    esp_err_t result = nvs_set_u16(handle, RADIO_NVS_LAST_STATION, item);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    ESP_RETURN_ON_ERROR(result, TAG, "Save last station");
    ESP_LOGI(TAG, "Saved last station: %u", item);
    return ESP_OK;
}

static void load_smartstart(void) {
    nvs_handle_t handle;
    esp_err_t result = nvs_open(RADIO_NVS_NAMESPACE, NVS_READONLY, &handle);
    if (result == ESP_ERR_NVS_NOT_FOUND) return;
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Smart Start storage unavailable: %s",
                 esp_err_to_name(result));
        return;
    }
    uint8_t saved = SMARTSTART_DISABLED;
    result = nvs_get_u8(handle, RADIO_NVS_SMARTSTART, &saved);
    nvs_close(handle);
    if (result == ESP_ERR_NVS_NOT_FOUND) return;
    if (result != ESP_OK || saved > SMARTSTART_DISABLED) {
        ESP_LOGW(TAG, "Ignoring invalid Smart Start state");
        return;
    }
    s_smartstart = saved;
}

static esp_err_t save_smartstart(void) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(RADIO_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open Smart Start storage");
    esp_err_t result =
        nvs_set_u8(handle, RADIO_NVS_SMARTSTART, s_smartstart);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    ESP_RETURN_ON_ERROR(result, TAG, "Save Smart Start");
    return ESP_OK;
}

static void update_smartstart_play_state(bool playing) {
    if (s_smartstart == SMARTSTART_DISABLED) return;
    uint8_t next = playing ? SMARTSTART_PLAYING : SMARTSTART_STOPPED;
    if (s_smartstart == next) return;
    s_smartstart = next;
    esp_err_t result = save_smartstart();
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Could not save Smart Start state: %s",
                 esp_err_to_name(result));
    }
}

static bool playlist_station(uint16_t requested, char *name,
                             size_t name_size, char *url, size_t url_size) {
    FILE *file = fopen(PLAYLIST_PATH, "r");
    if (!file) return false;
    uint16_t item = 0;
    bool found = false;
    while (fgets(s_playlist_line, sizeof(s_playlist_line), file)) {
        char *first_tab = strchr(s_playlist_line, '\t');
        if (!first_tab) continue;
        char *second_tab = strchr(first_tab + 1, '\t');
        if (!second_tab) continue;
        ++item;
        if (item != requested) continue;
        *first_tab = '\0';
        *second_tab = '\0';
        strlcpy(name, s_playlist_line, name_size);
        strlcpy(url, first_tab + 1, url_size);
        found = name[0] && url[0];
        break;
    }
    fclose(file);
    return found;
}

static uint16_t playlist_count(void) {
    FILE *file = fopen(PLAYLIST_PATH, "r");
    if (!file) return 0;
    uint16_t count = 0;
    while (fgets(s_playlist_line, sizeof(s_playlist_line), file)) {
        char *first_tab = strchr(s_playlist_line, '\t');
        if (first_tab && strchr(first_tab + 1, '\t')) ++count;
    }
    fclose(file);
    return count;
}

static esp_err_t play_locked(uint16_t item) {
    ESP_RETURN_ON_FALSE(playlist_station(item, s_candidate_name,
                                         sizeof(s_candidate_name),
                                         s_candidate_url,
                                         sizeof(s_candidate_url)),
                        ESP_ERR_NOT_FOUND, TAG,
                        "Station %u is absent from playlist", item);
    ESP_RETURN_ON_ERROR(
        audio_service_play(s_candidate_url, NATIVE_CODEC_AUTO), TAG,
        "start station %u", item);
    native_state_set_station(s_state, s_candidate_name);
    update_smartstart_play_state(true);
    s_current_item = item;
    strlcpy(s_current_name, s_candidate_name, sizeof(s_current_name));
    strlcpy(s_current_url, s_candidate_url, sizeof(s_current_url));
    esp_err_t save_result = save_last_station(item);
    if (save_result != ESP_OK) {
        // Playback has already started successfully. Keep it running and make
        // the persistence failure visible in the diagnostic log.
        ESP_LOGW(TAG, "Station %u is playing but was not saved: %s", item,
                 esp_err_to_name(save_result));
    }
    ESP_LOGI(TAG, "Selected station %u: %s", item, s_candidate_name);
    return ESP_OK;
}

esp_err_t radio_control_init(native_state_t *state) {
    ESP_RETURN_ON_FALSE(state, ESP_ERR_INVALID_ARG, TAG, "missing state");
    if (!s_lock) s_lock = xSemaphoreCreateMutex();
    ESP_RETURN_ON_FALSE(s_lock, ESP_ERR_NO_MEM, TAG, "control mutex allocation");
    s_state = state;
    load_smartstart();
    ESP_LOGI(TAG, "Smart Start state: %u", s_smartstart);
    uint16_t saved_item = 0;
    if (load_last_station(&saved_item)) {
        s_current_item = saved_item;
        ESP_LOGI(TAG, "Restoring last station: %u", s_current_item);
    }
    if (playlist_station(s_current_item, s_candidate_name,
                         sizeof(s_candidate_name), s_candidate_url,
                         sizeof(s_candidate_url))) {
        strlcpy(s_current_name, s_candidate_name, sizeof(s_current_name));
        strlcpy(s_current_url, s_candidate_url, sizeof(s_current_url));
        native_state_set_station(s_state, s_current_name);
    } else {
        ESP_LOGW(TAG, "Saved station %u is absent from playlist; using 1",
                 s_current_item);
        s_current_item = 1;
        if (playlist_station(s_current_item, s_candidate_name,
                             sizeof(s_candidate_name), s_candidate_url,
                             sizeof(s_candidate_url))) {
            strlcpy(s_current_name, s_candidate_name, sizeof(s_current_name));
            strlcpy(s_current_url, s_candidate_url, sizeof(s_current_url));
            native_state_set_station(s_state, s_current_name);
        }
    }
    if (s_smartstart == SMARTSTART_PLAYING && s_current_url[0]) {
        esp_err_t result = play_locked(s_current_item);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Smart Start could not resume station %u: %s",
                     s_current_item, esp_err_to_name(result));
        }
    }
    return ESP_OK;
}

esp_err_t radio_control_play(uint16_t item) {
    ESP_RETURN_ON_FALSE(s_state && s_lock, ESP_ERR_INVALID_STATE, TAG,
                        "radio is not ready");
    ESP_RETURN_ON_FALSE(xSemaphoreTake(s_lock, pdMS_TO_TICKS(1000)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "radio control lock");
    esp_err_t result = play_locked(item);
    xSemaphoreGive(s_lock);
    return result;
}

esp_err_t radio_control_stop(void) {
    ESP_RETURN_ON_FALSE(s_state && s_lock, ESP_ERR_INVALID_STATE, TAG,
                        "radio is not ready");
    ESP_RETURN_ON_FALSE(xSemaphoreTake(s_lock, pdMS_TO_TICKS(1000)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "radio control lock");
    audio_service_stop();
    update_smartstart_play_state(false);
    xSemaphoreGive(s_lock);
    return ESP_OK;
}

esp_err_t radio_control_toggle(void) {
    ESP_RETURN_ON_FALSE(s_state && s_lock, ESP_ERR_INVALID_STATE, TAG,
                        "radio is not ready");
    ESP_RETURN_ON_FALSE(xSemaphoreTake(s_lock, pdMS_TO_TICKS(1000)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "radio control lock");
    native_state_t state;
    native_state_snapshot(s_state, &state);
    esp_err_t result = ESP_OK;
    if (state.audio_running) {
        audio_service_stop();
        update_smartstart_play_state(false);
    } else if (s_current_url[0]) {
        result = audio_service_play(s_current_url, NATIVE_CODEC_AUTO);
        if (result == ESP_OK) {
            native_state_set_station(s_state, s_current_name);
            update_smartstart_play_state(true);
        }
    } else {
        result = play_locked(s_current_item);
    }
    xSemaphoreGive(s_lock);
    return result;
}

static esp_err_t step_station(bool forward) {
    ESP_RETURN_ON_FALSE(s_state && s_lock, ESP_ERR_INVALID_STATE, TAG,
                        "radio is not ready");
    ESP_RETURN_ON_FALSE(xSemaphoreTake(s_lock, pdMS_TO_TICKS(1000)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "radio control lock");
    uint16_t count = playlist_count();
    esp_err_t result = ESP_ERR_NOT_FOUND;
    if (count) {
        uint16_t item;
        if (forward) {
            item = s_current_item < count ? s_current_item + 1 : 1;
        } else {
            item = s_current_item > 1 ? s_current_item - 1 : count;
        }
        result = play_locked(item);
    }
    xSemaphoreGive(s_lock);
    return result;
}

esp_err_t radio_control_next(void) { return step_station(true); }

esp_err_t radio_control_previous(void) { return step_station(false); }

bool radio_control_smartstart_enabled(void) {
    if (!s_lock || xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) {
        return false;
    }
    bool enabled = s_smartstart != SMARTSTART_DISABLED;
    xSemaphoreGive(s_lock);
    return enabled;
}

esp_err_t radio_control_set_smartstart_enabled(bool enabled) {
    ESP_RETURN_ON_FALSE(s_state && s_lock, ESP_ERR_INVALID_STATE, TAG,
                        "radio is not ready");
    ESP_RETURN_ON_FALSE(xSemaphoreTake(s_lock, pdMS_TO_TICKS(1000)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "radio control lock");
    native_state_t state;
    native_state_snapshot(s_state, &state);
    uint8_t next = enabled
                       ? (state.audio_running ? SMARTSTART_PLAYING
                                              : SMARTSTART_STOPPED)
                       : SMARTSTART_DISABLED;
    esp_err_t result = ESP_OK;
    if (next != s_smartstart) {
        s_smartstart = next;
        result = save_smartstart();
    }
    xSemaphoreGive(s_lock);
    return result;
}

uint16_t radio_control_current_item(void) {
    if (!s_lock || xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) {
        return 1;
    }
    uint16_t item = s_current_item;
    xSemaphoreGive(s_lock);
    return item;
}

void radio_control_current_name(char *name, size_t name_size) {
    if (!name || !name_size) return;
    name[0] = '\0';
    if (!s_lock || xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) return;
    strlcpy(name, s_current_name, name_size);
    xSemaphoreGive(s_lock);
}
