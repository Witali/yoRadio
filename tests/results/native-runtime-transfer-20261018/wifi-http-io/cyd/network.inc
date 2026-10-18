static SemaphoreHandle_t s_wifi_save_lock;
static native_wifi_store_t s_wifi_store;
static const native_wifi_file_t s_wifi_paths = {
    .live = "/spiffs/data/wifi.csv",
    .temporary = "/spiffs/data/wifi.csv.tmp",
    .backup = "/spiffs/data/wifi.csv.bak",
};

static native_wifi_result_t wifi_store_lock(void *context) {
    (void)context;
    return xSemaphoreTake(s_wifi_save_lock, pdMS_TO_TICKS(1000)) == pdTRUE
        ? NATIVE_WIFI_OK : NATIVE_WIFI_BUSY;
}

static void wifi_store_unlock(void *context) {
    (void)context;
    xSemaphoreGive(s_wifi_save_lock);
}

static native_wifi_result_t wifi_store_read(void *context, uint8_t *data,
                                            size_t capacity, size_t *size) {
    (void)context;
    return native_wifi_file_read(&s_wifi_paths, data, capacity, size);
}

static native_wifi_result_t wifi_store_publish(void *context,
                                               const uint8_t *data, size_t size) {
    (void)context;
    return native_wifi_file_publish(&s_wifi_paths, data, size);
}

static esp_err_t wifi_store_error(native_wifi_result_t result) {
    switch (result) {
        case NATIVE_WIFI_OK: return ESP_OK;
        case NATIVE_WIFI_INVALID: return ESP_ERR_INVALID_ARG;
        case NATIVE_WIFI_BUSY: return ESP_ERR_TIMEOUT;
        case NATIVE_WIFI_NO_MEMORY: return ESP_ERR_NO_MEM;
        case NATIVE_WIFI_NOT_READY:
        case NATIVE_WIFI_EXHAUSTED: return ESP_ERR_INVALID_STATE;
        default: return ESP_FAIL;
    }
}

esp_err_t network_service_storage_init(void) {
    ESP_RETURN_ON_ERROR(web_upload_storage_init(), TAG,
                        "Wi-Fi file storage initialization failed");
    if (!s_wifi_save_lock) s_wifi_save_lock = xSemaphoreCreateMutex();
    ESP_RETURN_ON_FALSE(s_wifi_save_lock, ESP_ERR_NO_MEM, TAG,
                        "Wi-Fi save lock allocation failed");
    if (!s_wifi_store.ready) {
        uint64_t boot_epoch = 0;
        esp_fill_random(&boot_epoch, sizeof(boot_epoch));
        const native_wifi_store_ops_t ops = {
            .lock = wifi_store_lock,
            .unlock = wifi_store_unlock,
            .read_live = wifi_store_read,
            .publish_csv = wifi_store_publish,
        };
        ESP_RETURN_ON_FALSE(native_wifi_store_init(&s_wifi_store, &ops, NULL,
                                                    boot_epoch),
                            ESP_FAIL, TAG, "Wi-Fi store initialization failed");
    }
    return ESP_OK;
}

native_wifi_result_t network_service_wifi_metadata(native_wifi_metadata_t *out) {
    return native_wifi_store_metadata(&s_wifi_store, out);
}

native_wifi_result_t network_service_wifi_edit(const native_wifi_edit_t *edit) {
    return native_wifi_store_edit(&s_wifi_store, edit);
}

