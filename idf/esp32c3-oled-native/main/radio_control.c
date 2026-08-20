#include "radio_control.h"

#include <stdio.h>
#include <string.h>

#include "audio_service.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

#define PLAYLIST_PATH "/spiffs/data/playlist.csv"

static const char *const TAG = "radio_control";
static SemaphoreHandle_t s_lock;
static native_state_t *s_state;
static uint16_t s_current_item = 1;
static char s_current_name[144] = "yoRadio native";
static char s_current_url[512];
// Playlist access is serialized by s_lock. Keep the parsing and candidate
// station buffers off caller task stacks: BOOT has to remain safe while the
// single-core C3 is also decoding audio.
static char s_playlist_line[768];
static char s_candidate_name[144];
static char s_candidate_url[512];

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
    s_current_item = item;
    strlcpy(s_current_name, s_candidate_name, sizeof(s_current_name));
    strlcpy(s_current_url, s_candidate_url, sizeof(s_current_url));
    ESP_LOGI(TAG, "Selected station %u: %s", item, s_candidate_name);
    return ESP_OK;
}

esp_err_t radio_control_init(native_state_t *state) {
    ESP_RETURN_ON_FALSE(state, ESP_ERR_INVALID_ARG, TAG, "missing state");
    if (!s_lock) s_lock = xSemaphoreCreateMutex();
    ESP_RETURN_ON_FALSE(s_lock, ESP_ERR_NO_MEM, TAG, "control mutex allocation");
    s_state = state;
    if (playlist_station(s_current_item, s_candidate_name,
                         sizeof(s_candidate_name), s_candidate_url,
                         sizeof(s_candidate_url))) {
        strlcpy(s_current_name, s_candidate_name, sizeof(s_current_name));
        strlcpy(s_current_url, s_candidate_url, sizeof(s_current_url));
        native_state_set_station(s_state, s_current_name);
    } else {
        ESP_LOGW(TAG, "Initial station %u is absent from playlist",
                 s_current_item);
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
    } else if (s_current_url[0]) {
        result = audio_service_play(s_current_url, NATIVE_CODEC_AUTO);
        if (result == ESP_OK) {
            native_state_set_station(s_state, s_current_name);
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
