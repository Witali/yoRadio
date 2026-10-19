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
