#include "playlist_service.h"
#include "playlist_web_cache.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/stat.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "file_replace.h"

#define INDEX_MAGIC 0x58444959UL
#define INDEX_VERSION 2U
#define INDEX_TEMP_PATH PLAYLIST_INDEX_PATH ".tmp"

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint16_t count;
    uint32_t playlist_size;
} index_header_t;

static const char *TAG = "playlist";
static SemaphoreHandle_t s_lock;
static uint16_t s_count;
/* 144-byte name + tab + 512-byte URL + tab/gain/newline. */
static char s_line[672];

bool playlist_service_validate(const char *path) {
    if (!s_lock) return false;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    FILE *file = fopen(path, "rb");
    bool valid = file != NULL;
    unsigned supported = 0;
    while (file && fgets(s_line, sizeof(s_line), file)) {
        size_t n = strlen(s_line);
        if (!n || (s_line[n-1] != '\n' && !feof(file))) { valid = false; break; }
        if (playlist_service_entry_supported(s_line)) ++supported;
    }
    if (file) { valid = valid && !ferror(file); fclose(file); }
    xSemaphoreGive(s_lock);
    return valid && supported > 0;
}

static esp_err_t rebuild_locked(void);
static bool same_playlist_locked(const char *temporary) {
    struct stat a, b;
    if (stat(temporary, &a) || stat(PLAYLIST_PATH, &b) ||
        a.st_size != b.st_size) return false;
    FILE *left = fopen(temporary, "rb"), *right = fopen(PLAYLIST_PATH, "rb");
    bool same = left && right;
    /* Reuse the indexed-reader line buffer while holding its mutex. */
    const size_t half = sizeof(s_line) / 2U;
    while (same) {
        size_t n = fread(s_line, 1, half, left);
        size_t m = fread(s_line + half, 1, half, right);
        same = n == m && !memcmp(s_line, s_line + half, n);
        if (!n || !m) break;
    }
    if (left) { same = same && !ferror(left); fclose(left); }
    if (right) { same = same && !ferror(right); fclose(right); }
    return same;
}

esp_err_t playlist_service_install(const char *temporary, bool *changed) {
    if (changed) *changed = false;
    if (!s_lock) return ESP_ERR_INVALID_STATE;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    esp_err_t result = ESP_FAIL;
    if (same_playlist_locked(temporary)) {
        result = remove(temporary) == 0 ? ESP_OK : ESP_FAIL;
    } else if (file_recover(PLAYLIST_PATH)) {
        playlist_web_cache_invalidate();
        bool previous = file_exists(PLAYLIST_PATH);
        /* Invalidate even an equal-size old index before publishing new CSV.
         * Keep old CSV until the replacement's index has been built. */
        bool invalidated = !file_exists(PLAYLIST_INDEX_PATH) ||
                           remove(PLAYLIST_INDEX_PATH) == 0;
        if (invalidated && (!previous ||
            rename(PLAYLIST_PATH, PLAYLIST_PATH ".bak") == 0)) {
            result = rename(temporary, PLAYLIST_PATH) == 0
                         ? rebuild_locked() : ESP_FAIL;
            if (result == ESP_OK) {
                if (previous) (void)remove(PLAYLIST_PATH ".bak");
                if (changed) *changed = true;
            } else {
                (void)remove(PLAYLIST_PATH);
                if (previous) (void)rename(PLAYLIST_PATH ".bak", PLAYLIST_PATH);
                s_count = 0;
                (void)rebuild_locked();
            }
        } else if (invalidated) {
            (void)rebuild_locked(); /* Failed to rename old CSV: restore its index. */
        }
    }
    if (result == ESP_OK) playlist_web_cache_refresh();
    xSemaphoreGive(s_lock);
    return result;
}

static bool has_unsupported_extension(const char *url) {
    /* strpbrk/strncasecmp repeatedly byte-read flash literals (and libc's
     * ctype table) through LX106 LoadStoreError emulation. Scan the DRAM URL
     * once and compare immediate ASCII codes, with no new RAM table. */
    const char *end = url, *dot = NULL;
    while (*end && *end != '?' && *end != '#') {
        if (*end == '.') dot = end;
        ++end;
    }
    if (!dot || end - dot < 4 || end - dot > 5) return false;
    unsigned code = 0;
    for (const char *p = dot + 1; p < end; ++p) {
        unsigned c = (unsigned char)*p;
        if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
        code = (code << 8) | c;
    }
    switch (code) {
        case 0x6f6767U:   /* ogg */
        case 0x6f707573U: /* opus */
        case 0x666c6163U: /* flac */
        case 0x6d3375U:   /* m3u */
        case 0x6d337538U: /* m3u8 */
        case 0x706c73U:   /* pls */
        case 0x776176U:   /* wav */
            return true;
        default: return false;
    }
}

static bool station_supported(const char *name, const char *url) {
    /* The ESP8266 profile deliberately contains no TLS, Ogg, FLAC or WAV
     * decoder. The shared repository playlist remains unchanged; this board's
     * offset index contains only streams it can actually open and decode. */
    bool http = url[0] == 'h' && url[1] == 't' && url[2] == 't' &&
                url[3] == 'p' && url[4] == ':' && url[5] == '/' && url[6] == '/';
    bool ogg = (name[0] == 'O' || name[0] == 'o') &&
               (name[1] == 'G' || name[1] == 'g') &&
               (name[2] == 'G' || name[2] == 'g') && name[3] == ' ';
    return http && !ogg &&
           !has_unsupported_extension(url);
}

bool playlist_service_entry_supported(char *line) {
    if (!line) return false;
    char *name_end = strchr(line, '\t');
    if (!name_end) return false;
    char *url = name_end + 1;
    char *url_end = strchr(url, '\t');
    if (!url_end) url_end = url + strcspn(url, "\r\n");
    char saved_name_end = *name_end;
    char saved_url_end = *url_end;
    *name_end = '\0';
    *url_end = '\0';
    bool supported = line[0] && url[0] && station_supported(line, url);
    *name_end = saved_name_end;
    *url_end = saved_url_end;
    return supported;
}

static bool parse_line(char *line, playlist_station_t *station) {
    if (!playlist_service_entry_supported(line)) return false;
    char *name = line;
    char *url = strchr(name, '\t');
    if (!url) return false;
    *url++ = '\0';
    char *gain = strchr(url, '\t');
    if (gain) *gain++ = '\0';
    url[strcspn(url, "\r\n")] = '\0';
    if (!name[0] || !url[0]) return false;
    if (station) {
        strncpy(station->name, name, sizeof(station->name) - 1);
        station->name[sizeof(station->name) - 1] = '\0';
        strncpy(station->url, url, sizeof(station->url) - 1);
        station->url[sizeof(station->url) - 1] = '\0';
        station->output_gain_db = gain ? (int8_t)strtol(gain, NULL, 10) : 0;
    }
    return true;
}

static bool load_index_locked(void) {
    struct stat playlist_stat;
    if (stat(PLAYLIST_PATH, &playlist_stat) != 0 || playlist_stat.st_size < 0) {
        s_count = 0;
        return false;
    }
    FILE *file = fopen(PLAYLIST_INDEX_PATH, "rb");
    if (!file) return false;
    index_header_t header;
    bool valid = fread(&header, sizeof(header), 1, file) == 1 &&
                 header.magic == INDEX_MAGIC &&
                 header.version == INDEX_VERSION &&
                 header.playlist_size == (uint32_t)playlist_stat.st_size;
    if (valid) {
        valid = fseek(file, 0, SEEK_END) == 0 &&
                ftell(file) == (long)(sizeof(header) +
                                      header.count * sizeof(uint32_t));
    }
    fclose(file);
    if (!valid) return false;
    s_count = header.count;
    ESP_LOGI(TAG, "Loaded index: %u stations", s_count);
    return true;
}

static esp_err_t rebuild_locked(void) {
    playlist_web_cache_invalidate();
    struct stat playlist_stat;
    FILE *playlist = fopen(PLAYLIST_PATH, "rb");
    if (!playlist || stat(PLAYLIST_PATH, &playlist_stat) != 0 ||
        playlist_stat.st_size < 0 ||
        (unsigned long)playlist_stat.st_size > UINT32_MAX) {
        if (playlist) fclose(playlist);
        s_count = 0;
        remove(PLAYLIST_INDEX_PATH);
        return ESP_ERR_NOT_FOUND;
    }
    FILE *index = fopen(INDEX_TEMP_PATH, "wb+");
    if (!index) {
        fclose(playlist);
        return ESP_FAIL;
    }
    index_header_t header = {
        .magic = INDEX_MAGIC,
        .version = INDEX_VERSION,
        .count = 0,
        .playlist_size = (uint32_t)playlist_stat.st_size,
    };
    esp_err_t result = fwrite(&header, sizeof(header), 1, index) == 1
                           ? ESP_OK
                           : ESP_FAIL;
    while (result == ESP_OK) {
        long offset = ftell(playlist);
        if (offset < 0 || (unsigned long)offset > UINT32_MAX) {
            result = ESP_ERR_INVALID_SIZE;
            break;
        }
        if (!fgets(s_line, sizeof(s_line), playlist)) break;
        if (!parse_line(s_line, NULL)) continue;
        if (header.count == UINT16_MAX) {
            result = ESP_ERR_INVALID_SIZE;
            break;
        }
        uint32_t position = (uint32_t)offset;
        if (fwrite(&position, sizeof(position), 1, index) != 1) {
            result = ESP_FAIL;
            break;
        }
        ++header.count;
    }
    if (ferror(playlist) && result == ESP_OK) result = ESP_FAIL;
    if (result == ESP_OK && fseek(index, 0, SEEK_SET) != 0) result = ESP_FAIL;
    if (result == ESP_OK && fwrite(&header, sizeof(header), 1, index) != 1)
        result = ESP_FAIL;
    if (result == ESP_OK && fflush(index) != 0) result = ESP_FAIL;
    fclose(playlist);
    if (fclose(index) != 0 && result == ESP_OK) result = ESP_FAIL;
    if (result != ESP_OK) {
        remove(INDEX_TEMP_PATH);
        return result;
    }
    remove(PLAYLIST_INDEX_PATH);
    if (rename(INDEX_TEMP_PATH, PLAYLIST_INDEX_PATH) != 0) {
        remove(INDEX_TEMP_PATH);
        return ESP_FAIL;
    }
    s_count = header.count;
    ESP_LOGI(TAG, "Built index: %u stations", s_count);
    return ESP_OK;
}

esp_err_t playlist_service_init(void) {
    s_lock = xSemaphoreCreateMutex();
    if (!s_lock) return ESP_ERR_NO_MEM;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    esp_err_t result = load_index_locked() ? ESP_OK : rebuild_locked();
    if (result == ESP_OK) playlist_web_cache_refresh();
    xSemaphoreGive(s_lock);
    return result;
}

esp_err_t playlist_service_rebuild(void) {
    if (!s_lock) return ESP_ERR_INVALID_STATE;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    esp_err_t result = rebuild_locked();
    if (result == ESP_OK) playlist_web_cache_refresh();
    xSemaphoreGive(s_lock);
    return result;
}

uint16_t playlist_service_count(void) { return s_count; }

bool playlist_service_get(uint16_t one_based_index, playlist_station_t *station) {
    if (!s_lock || !station || !one_based_index) return false;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    bool found = false;
    if (one_based_index <= s_count) {
        FILE *index = fopen(PLAYLIST_INDEX_PATH, "rb");
        uint32_t offset = 0;
        long position = (long)sizeof(index_header_t) +
                        (long)(one_based_index - 1U) * sizeof(offset);
        if (index && fseek(index, position, SEEK_SET) == 0 &&
            fread(&offset, sizeof(offset), 1, index) == 1) {
            FILE *playlist = fopen(PLAYLIST_PATH, "rb");
            if (playlist && fseek(playlist, (long)offset, SEEK_SET) == 0 &&
                fgets(s_line, sizeof(s_line), playlist)) {
                found = parse_line(s_line, station);
            }
            if (playlist) fclose(playlist);
        }
        if (index) fclose(index);
    }
    xSemaphoreGive(s_lock);
    return found;
}

esp_err_t playlist_service_visit(uint16_t one_based_index,
                                 playlist_station_visitor_t visitor,
                                 void *context) {
    if (!s_lock || !visitor || !one_based_index) return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    esp_err_t result = ESP_ERR_NOT_FOUND;
    if (one_based_index <= s_count) {
        FILE *index = fopen(PLAYLIST_INDEX_PATH, "rb");
        uint32_t offset = 0;
        long position = (long)sizeof(index_header_t) +
                        (long)(one_based_index - 1U) * sizeof(offset);
        if (index && fseek(index, position, SEEK_SET) == 0 &&
            fread(&offset, sizeof(offset), 1, index) == 1) {
            FILE *playlist = fopen(PLAYLIST_PATH, "rb");
            if (playlist && fseek(playlist, (long)offset, SEEK_SET) == 0 &&
                fgets(s_line, sizeof(s_line), playlist)) {
                char *name = s_line;
                char *url = strchr(name, '\t');
                if (url) {
                    *url++ = '\0';
                    char *gain_text = strchr(url, '\t');
                    if (gain_text) *gain_text++ = '\0';
                    url[strcspn(url, "\r\n")] = '\0';
                    int8_t gain = gain_text
                        ? (int8_t)strtol(gain_text, NULL, 10) : 0;
                    if (name[0] && url[0])
                        result = visitor(one_based_index, name, url, gain,
                                         context);
                }
            }
            if (playlist) fclose(playlist);
        }
        if (index) fclose(index);
    }
    xSemaphoreGive(s_lock);
    return result;
}

static esp_err_t inspect_http(uint16_t index, const char *name,
                              const char *url, int8_t gain, void *context) {
    (void)index;
    (void)name;
    (void)gain;
    *(bool *)context = strncmp(url, "http://", 7) == 0;
    return ESP_OK;
}

bool playlist_service_find_http_index(uint16_t start, int direction,
                                      uint16_t *found_index) {
    uint16_t count = playlist_service_count();
    if (!count || !found_index) return false;
    uint16_t candidate = start >= 1 && start <= count ? start : 1;
    for (uint16_t checked = 0; checked < count; ++checked) {
        if (checked) {
            if (direction < 0)
                candidate = candidate == 1 ? count : candidate - 1;
            else
                candidate = candidate == count ? 1 : candidate + 1;
        }
        bool is_http = false;
        if (playlist_service_visit(candidate, inspect_http, &is_http) ==
                ESP_OK && is_http) {
            *found_index = candidate;
            return true;
        }
    }
    return false;
}

bool playlist_service_find_http(uint16_t start, int direction,
                                uint16_t *found_index,
                                playlist_station_t *station) {
    uint16_t count = playlist_service_count();
    if (!count || !found_index || !station) return false;
    uint16_t candidate = start >= 1 && start <= count ? start : 1;
    for (uint16_t checked = 0; checked < count; ++checked) {
        if (checked) {
            if (direction < 0)
                candidate = candidate == 1 ? count : candidate - 1;
            else
                candidate = candidate == count ? 1 : candidate + 1;
        }
        if (playlist_service_get(candidate, station) &&
            strncmp(station->url, "http://", 7) == 0) {
            *found_index = candidate;
            return true;
        }
    }
    return false;
}
