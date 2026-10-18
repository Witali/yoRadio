static SemaphoreHandle_t s_storage_lock;

esp_err_t web_upload_storage_init(void) {
    if (!s_storage_lock) s_storage_lock = xSemaphoreCreateMutex();
    return s_storage_lock ? ESP_OK : ESP_ERR_NO_MEM;
}

static bool backup_name(const char *live, char *backup, size_t capacity) {
    if (!live || !*live) return false;
    int length = snprintf(backup, capacity, "%s.bak", live);
    return length > 0 && (size_t)length < capacity;
}

FILE *web_upload_open_file(const char *path) {
    char backup[256];
    if (!s_storage_lock || !backup_name(path, backup, sizeof(backup)) ||
        xSemaphoreTake(s_storage_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return NULL;
    FILE *file = native_file_recover(path, backup) ? fopen(path, "rb") : NULL;
    xSemaphoreGive(s_storage_lock);
    return file;
}

bool web_upload_publish_file(const char *temporary, const char *live) {
    char backup[256];
    if (!s_storage_lock || !backup_name(live, backup, sizeof(backup)) ||
        xSemaphoreTake(s_storage_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return false;
    bool replaced = native_file_replace(temporary, live, backup);
    xSemaphoreGive(s_storage_lock);
    return replaced;
}

bool web_upload_publish_playlist(const char *csv_temporary,
                                 const char *index_temporary) {
    if (!s_storage_lock ||
        xSemaphoreTake(s_storage_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return false;
    bool replaced = native_file_replace_pair(
        csv_temporary, "/spiffs/data/playlist.csv", "/spiffs/data/playlist.csv.bak",
        index_temporary, "/spiffs/data/index.dat", "/spiffs/data/index.dat.bak");
    xSemaphoreGive(s_storage_lock);
    return replaced;
}

static void temporary_path(unsigned slot, char *path, size_t capacity) {
    snprintf(path, capacity, "/spiffs/data/web-upload-%02u.tmp", slot);
}
static bool upload_destination(const char *name, bool playlist,
                               char *destination, size_t capacity) {
    char checked[WEB_FILE_FORM_NAME_BYTES];
    if (!name || !web_form_name(name, checked, sizeof(checked)) ||
        strcmp(checked, name)) return false;
    int length = snprintf(destination, capacity, "/spiffs/%s/%s",
                          playlist ? "data" : "www", name);
    if (length <= 0 || (size_t)length >= capacity) return false;
    size_t backup_bytes = (size_t)length - strlen("/spiffs") + sizeof(".bak");
    if (backup_bytes > WEB_FILE_FORM_NAME_BYTES) return false;
    if (!playlist && (length <= 3 || strcmp(destination + length - 3, ".gz") != 0)) return false;
    if (!playlist) {
        size_t raw = strlen(name) - 3U;
        if ((raw >= 3U && !memcmp(name + raw - 3U, ".gz", 3)) ||
            (raw >= 4U && (!memcmp(name + raw - 4U, ".bak", 4) ||
                           !memcmp(name + raw - 4U, ".tmp", 4)))) return false;
    }
    return !playlist || !strcmp(name, "playlist.csv");
}
static bool publish_file(unsigned slot, const char *name, bool playlist) {
    char temporary[64], destination[128];
    temporary_path(slot, temporary, sizeof(temporary));
    if (!upload_destination(name, playlist, destination, sizeof(destination))) return false;
    // Retain the previous file until the validated replacement has its live
    // name. Boot/read recovery can restore a retained backup after interruption.
    if (playlist) return web_upload_publish_file(temporary, destination);
    char backup[256];
    if (!s_storage_lock || !backup_name(destination, backup, sizeof(backup)) ||
        xSemaphoreTake(s_storage_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return false;
    bool replaced = native_file_replace(temporary, destination, backup);
    if (replaced) {
        destination[strlen(destination) - 3] = 0;
        if (remove(destination) != 0 && errno != ENOENT) replaced = false;
    }
    xSemaphoreGive(s_storage_lock);
    return replaced;
}
