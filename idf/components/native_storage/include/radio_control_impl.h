#pragma once
#include "radio_control.h"
#include "radio_control_platform.h"

#include <stdio.h>
#include <string.h>

#include "audio_service.h"
#include "native_audio_output.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "file_transaction.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "nvs.h"

#define PLAYLIST_PATH "/spiffs/data/playlist.csv"
#define PLAYLIST_BACKUP_PATH "/spiffs/data/playlist.csv.bak"
#define PLAYLIST_INDEX_PATH "/spiffs/data/index.dat"
#define PLAYLIST_INDEX_TEMP_PATH "/spiffs/data/index.dat.tmp"
#define PLAYLIST_INDEX_BACKUP_PATH "/spiffs/data/index.dat.bak"
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
static uint16_t s_playlist_count;
static char s_current_name[144] = "yoRadio native";
static char s_current_url[512];
// Playlist access is serialized by s_lock. Keep the parsing and candidate
// station buffers off caller task stacks. Both targets serialize all accesses
// through s_lock; this storage is never shared outside that ownership.
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

static bool parse_playlist_line(char *line, char **name, char **url) {
    char *first_tab = strchr(line, '\t');
    if (!first_tab) return false;
    char *second_tab = strchr(first_tab + 1, '\t');
    if (!second_tab) return false;
    *first_tab = '\0';
    *second_tab = '\0';
    if (!line[0] || !first_tab[1]) return false;
    *name = line;
    *url = first_tab + 1;
    return true;
}

// One row walk defines both cache validation and index construction. Return
// one valid row, clean EOF, or an I/O/unsupported-offset error, respectively.
static int next_playlist_row(FILE *playlist, uint32_t *offset) {
    for (;;) {
        long position = ftell(playlist);
        if (position < 0 || (unsigned long)position > INT32_MAX) return -1;
        if (!fgets(s_playlist_line, sizeof(s_playlist_line), playlist))
            return ferror(playlist) ? -1 : 0;
        long end = ftell(playlist);
        if (end <= position || (unsigned long)(end-position) >= sizeof(s_playlist_line)) return -1;
        size_t bytes = (size_t)(end-position);
        bool embedded_zero = memchr(s_playlist_line, '\0', bytes) != NULL;
        if (bytes == sizeof(s_playlist_line)-1U && s_playlist_line[bytes-1U] != '\n') {
            int next = fgetc(playlist);
            if (next != EOF) {
                while (next != '\n' && next != EOF) next = fgetc(playlist);
                if (ferror(playlist)) return -1;
                continue; // Continuation chunks are never independent rows.
            }
            if (ferror(playlist)) return -1;
        }
        if (embedded_zero) continue;
        char *name, *url;
        if (!parse_playlist_line(s_playlist_line, &name, &url)) continue;
        // Never turn a truncated URL into a different station request.
        if (strlen(url) >= sizeof(s_candidate_url)) continue;
        *offset = (uint32_t)position;
        return 1;
    }
}

static esp_err_t load_playlist_index_locked(void) {
    if (!native_file_recover(PLAYLIST_PATH, PLAYLIST_BACKUP_PATH)) return ESP_FAIL;
    if (!native_file_recover(PLAYLIST_INDEX_PATH, PLAYLIST_INDEX_BACKUP_PATH)) return ESP_FAIL;
    FILE *playlist = fopen(PLAYLIST_PATH, "rb");
    if (!playlist) return ESP_ERR_NOT_FOUND;
    FILE *index = fopen(PLAYLIST_INDEX_PATH, "rb");
    if (!index) { fclose(playlist); return ESP_ERR_NOT_FOUND; }
    uint16_t count = 0;
    esp_err_t result = ESP_OK;
    for (;;) {
        uint32_t expected = 0, actual = 0;
        int row = next_playlist_row(playlist, &expected);
        if (row < 0) { result = ESP_FAIL; break; }
        if (!row) {
            if (fgetc(index) != EOF || ferror(index)) result = ESP_ERR_INVALID_SIZE;
            break;
        }
        if (count == UINT16_MAX || fread(&actual,sizeof(actual),1,index) != 1 || actual != expected) {
            result = ESP_ERR_INVALID_SIZE;
            break;
        }
        ++count;
    }
    fclose(index);
    fclose(playlist);
    if (result == ESP_OK) {
        s_playlist_count = count;
        ESP_LOGI(TAG, "Validated playlist index: %u stations", s_playlist_count);
    }
    return result;
}

static esp_err_t write_playlist_index_candidate_locked(const char *csv,
                                                        uint16_t *count_out) {
    FILE *playlist = fopen(csv, "rb");
    if (!playlist) {
        return ESP_ERR_NOT_FOUND;
    }
    FILE *index = fopen(PLAYLIST_INDEX_TEMP_PATH, "wb");
    if (!index) {
        fclose(playlist);
        return ESP_FAIL;
    }
    esp_err_t result = ESP_OK;
    uint16_t count = 0;
    while (true) {
        uint32_t offset = 0;
        int row = next_playlist_row(playlist, &offset);
        if (row < 0) { result = ESP_FAIL; break; }
        if (!row) break;
        if (count == UINT16_MAX) {
            result = ESP_ERR_INVALID_SIZE;
            break;
        }
        if (fwrite(&offset, sizeof(offset), 1, index) != 1) {
            result = ESP_FAIL;
            break;
        }
        ++count;
    }
    if (ferror(playlist) && result == ESP_OK) result = ESP_FAIL;
    if (fflush(index) != 0 && result == ESP_OK) result = ESP_FAIL;
    if (fclose(index) != 0 && result == ESP_OK) result = ESP_FAIL;
    if (fclose(playlist) != 0 && result == ESP_OK) result = ESP_FAIL;
    if (result != ESP_OK) {
        remove(PLAYLIST_INDEX_TEMP_PATH);
        return result;
    }
    *count_out = count;
    return ESP_OK;
}

static esp_err_t build_playlist_index_locked(void) {
    int64_t started_us = esp_timer_get_time();
    uint16_t count;
    esp_err_t result = write_playlist_index_candidate_locked(PLAYLIST_PATH, &count);
    if (result != ESP_OK) return result;
    if (!native_file_replace(PLAYLIST_INDEX_TEMP_PATH, PLAYLIST_INDEX_PATH,
                              PLAYLIST_INDEX_BACKUP_PATH)) {
        return ESP_FAIL;
    }
    s_playlist_count = count;
    uint64_t elapsed_ms =
        (uint64_t)(esp_timer_get_time() - started_us + 999) / 1000U;
    ESP_LOGI(TAG, "Built playlist index: %u stations in %llu ms",
             s_playlist_count, (unsigned long long)elapsed_ms);
    return ESP_OK;
}

static bool playlist_station(uint16_t requested, char *name,
                             size_t name_size, char *url, size_t url_size) {
    if (!requested || requested > s_playlist_count) return false;
    FILE *index = fopen(PLAYLIST_INDEX_PATH, "rb");
    if (!index) return false;
    long index_position = (long)(requested - 1U) * (long)sizeof(uint32_t);
    uint32_t offset = 0;
    bool indexed = fseek(index, index_position, SEEK_SET) == 0 &&
                   fread(&offset, sizeof(offset), 1, index) == 1;
    fclose(index);
    if (!indexed || offset > INT32_MAX) return false;
    FILE *playlist = fopen(PLAYLIST_PATH, "rb");
    if (!playlist) return false;
    if (offset && (fseek(playlist,(long)offset-1L,SEEK_SET) != 0 || fgetc(playlist) != '\n')) {
        fclose(playlist);
        return false;
    }
    bool found = fseek(playlist, (long)offset, SEEK_SET) == 0 &&
                 fgets(s_playlist_line, sizeof(s_playlist_line), playlist);
    fclose(playlist);
    if (!found) return false;
    char *indexed_name;
    char *indexed_url;
    if (!parse_playlist_line(s_playlist_line, &indexed_name, &indexed_url)) {
        return false;
    }
    if (strlen(indexed_url) >= url_size) return false;
    strlcpy(name, indexed_name, name_size);
    strlcpy(url, indexed_url, url_size);
    return name[0] && url[0];
}

static uint16_t playlist_count(void) {
    return s_playlist_count;
}

static esp_err_t play_locked(uint16_t item) {
    ESP_RETURN_ON_FALSE(playlist_station(item, s_candidate_name,
                                         sizeof(s_candidate_name),
                                         s_candidate_url,
                                         sizeof(s_candidate_url)),
                        ESP_ERR_NOT_FOUND, TAG,
                        "Station %u is absent from playlist", item);
    const bool station_changed = item != s_current_item;
    ESP_RETURN_ON_ERROR(
        audio_service_play(s_candidate_url, NATIVE_CODEC_AUTO), TAG,
        "start station %u", item);
    if (station_changed) radio_control_reset_normalizer();
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
    esp_err_t index_result = load_playlist_index_locked();
    if (index_result != ESP_OK) {
        index_result = build_playlist_index_locked();
    }
    if (index_result != ESP_OK) {
        ESP_LOGW(TAG, "Playlist index unavailable: %s",
                 esp_err_to_name(index_result));
    }
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

static void clamp_current_station_locked(void) {
    if (s_playlist_count && s_current_item > s_playlist_count) {
        s_current_item = 1;
        esp_err_t result = save_last_station(s_current_item);
        if (result != ESP_OK)
            ESP_LOGW(TAG, "Could not clamp saved station: %s", esp_err_to_name(result));
    }
}

esp_err_t radio_control_reindex_playlist(void) {
    ESP_RETURN_ON_FALSE(s_state && s_lock, ESP_ERR_INVALID_STATE, TAG,
                        "radio is not ready");
    ESP_RETURN_ON_FALSE(xSemaphoreTake(s_lock, pdMS_TO_TICKS(1000)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "radio control lock");
    esp_err_t result = build_playlist_index_locked();
    if (result != ESP_OK && load_playlist_index_locked() != ESP_OK) {
        // Retain files for recovery, but never expose offsets from another
        // CSV after an interrupted/failed playlist publication.
        s_playlist_count = 0;
    }
    if (result == ESP_OK) clamp_current_station_locked();
    xSemaphoreGive(s_lock);
    return result;
}

esp_err_t radio_control_publish_playlist(const char *csv_temporary,
                                         radio_playlist_publisher_t publisher) {
    if (!csv_temporary || !*csv_temporary || !publisher ||
        !strcmp(csv_temporary, PLAYLIST_PATH) ||
        !strcmp(csv_temporary, PLAYLIST_BACKUP_PATH) ||
        !strcmp(csv_temporary, PLAYLIST_INDEX_PATH) ||
        !strcmp(csv_temporary, PLAYLIST_INDEX_TEMP_PATH) ||
        !strcmp(csv_temporary, PLAYLIST_INDEX_BACKUP_PATH)) return ESP_ERR_INVALID_ARG;
    if (!s_state || !s_lock) return ESP_ERR_INVALID_STATE;
    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return ESP_ERR_TIMEOUT;
    // Hold the catalog lock through preparation and pair publication. Readers
    // can never select an old offset from a newly published CSV in between.
    uint16_t count = 0;
    esp_err_t result = write_playlist_index_candidate_locked(csv_temporary, &count);
    if (result == ESP_OK && !count) result = ESP_ERR_INVALID_ARG;
    if (result == ESP_OK) {
        if (publisher(csv_temporary, PLAYLIST_INDEX_TEMP_PATH)) {
            s_playlist_count = count;
            clamp_current_station_locked();
        } else {
            result = ESP_FAIL;
            // Rollback can itself fail. Advertise only a verified live pair;
            // keep backups for recovery instead of guessing its generation.
            if (load_playlist_index_locked() != ESP_OK) s_playlist_count = 0;
        }
    }
    (void)remove(PLAYLIST_INDEX_TEMP_PATH);
    xSemaphoreGive(s_lock);
    return result;
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
    if (state.audio_running || state.audio_pending) {
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
                       ? (state.audio_running || state.audio_pending ? SMARTSTART_PLAYING
                                              : SMARTSTART_STOPPED)
                       : SMARTSTART_DISABLED;
    esp_err_t result = ESP_OK;
    if (next != s_smartstart) {
        uint8_t previous = s_smartstart;
        s_smartstart = next;
        result = save_smartstart();
        if (result != ESP_OK) s_smartstart = previous;
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

uint16_t radio_control_playlist_count(void) {
    if (!s_lock || xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) return 0;
    uint16_t count = s_playlist_count;
    xSemaphoreGive(s_lock);
    return count;
}

void radio_control_current_name(char *name, size_t name_size) {
    if (!name || !name_size) return;
    name[0] = '\0';
    if (!s_lock || xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) return;
    strlcpy(name, s_current_name, name_size);
    xSemaphoreGive(s_lock);
}

bool radio_control_snapshot(radio_control_snapshot_t *snapshot) {
    if (!snapshot) return false;
    memset(snapshot, 0, sizeof(*snapshot));
    if (!s_lock || xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) return false;
    snapshot->item = s_current_item;
    snapshot->count = s_playlist_count;
    snapshot->smartstart = s_smartstart != SMARTSTART_DISABLED;
    strlcpy(snapshot->name, s_current_name, sizeof(snapshot->name));
    xSemaphoreGive(s_lock);
    return true;
}
