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
static bool read_credentials(wifi_config_t *config) {
    FILE *file = web_upload_open_file("/spiffs/data/wifi.csv");
    if (!file) return false;
    char line[160];
    wifi_config_t selected = {0};
    bool found = false;
    while (native_credential_next_row(file, line, sizeof(line))) {
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab++ = '\0';
        if (!line[0] || strlen(line) >= sizeof(config->sta.ssid) ||
            strlen(tab) >= sizeof(config->sta.password) || strchr(line, '\r') ||
            strpbrk(tab, "\t\r")) {
            continue;
        }
        strlcpy((char *)selected.sta.ssid, line, sizeof(selected.sta.ssid));
        strlcpy((char *)selected.sta.password, tab,
                sizeof(selected.sta.password));
        found = true;
        break;
    }
    if (fclose(file) != 0) found = false;
    if (found) *config = selected;
    native_wifi_erase(line, sizeof(line));
    native_wifi_erase(&selected, sizeof(selected));
    return found;
}
esp_err_t network_service_validate_credentials_file(const uint8_t *data,
                                                    size_t size) {
    if (!data || !size || size >= NATIVE_WIFI_FILE_BYTES)
        return ESP_ERR_INVALID_SIZE;
    return wifi_store_error(native_wifi_validate_csv(data, size));
}
esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size) {
    ESP_RETURN_ON_ERROR(network_service_validate_credentials_file(data, size),
                        TAG, "Invalid Wi-Fi file");
    return wifi_store_error(native_wifi_store_import(&s_wifi_store, data, size));
}
esp_err_t network_service_save_credentials(const char *ssid,
                                           const char *password) {
    ESP_RETURN_ON_FALSE(ssid && password, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi credentials are missing");
    size_t ssid_size = strnlen(ssid, sizeof(s_station_config.sta.ssid));
    size_t password_size = strnlen(password, sizeof(s_station_config.sta.password));
    ESP_RETURN_ON_FALSE(ssid_size && ssid_size < sizeof(s_station_config.sta.ssid) &&
                            password_size < sizeof(s_station_config.sta.password),
                        ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi field size");
    ESP_RETURN_ON_FALSE(!strpbrk(ssid, "\t\r\n") && !strpbrk(password, "\t\r\n"),
                        ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi field");
    char line[sizeof(s_station_config.sta.ssid) +
              sizeof(s_station_config.sta.password)];
    memcpy(line, ssid, ssid_size);
    line[ssid_size] = '\t';
    memcpy(line + ssid_size + 1U, password, password_size);
    size_t size = ssid_size + 1U + password_size;
    line[size++] = '\n';
    esp_err_t result = network_service_save_credentials_file((const uint8_t *)line, size);
    native_wifi_erase(line, sizeof(line));
    return result;
}
