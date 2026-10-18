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
