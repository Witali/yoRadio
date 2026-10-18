esp_err_t network_service_storage_init(void) {
    ESP_RETURN_ON_ERROR(web_upload_storage_init(), TAG,
                        "Wi-Fi file storage initialization failed");
    if (!s_wifi_save_lock) s_wifi_save_lock = xSemaphoreCreateMutex();
    ESP_RETURN_ON_FALSE(s_wifi_save_lock, ESP_ERR_NO_MEM, TAG,
                        "Wi-Fi save lock allocation failed");
    return ESP_OK;
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
    return found;
}
esp_err_t network_service_validate_credentials_file(const uint8_t *data,
                                                    size_t size) {
    ESP_RETURN_ON_FALSE(data && size && size < WIFI_MAX_FILE_BYTES,
                        ESP_ERR_INVALID_SIZE, TAG,
                        "Wi-Fi file is empty or too large");
    size_t count = 0;
    size_t offset = 0;
    while (offset < size) {
        size_t end = offset;
        while (end < size && data[end] != '\n') ++end;
        size_t row_end = end;
        if (row_end > offset && data[row_end - 1U] == '\r') --row_end;
        if (row_end > offset) {
            size_t tab = offset;
            while (tab < row_end && data[tab] != '\t') ++tab;
            ESP_RETURN_ON_FALSE(tab > offset && tab < row_end &&
                                    tab - offset < sizeof(s_station_config.sta.ssid) &&
                                    row_end - tab - 1U < sizeof(s_station_config.sta.password),
                                ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi row");
            for (size_t index = offset; index < row_end; ++index) {
                ESP_RETURN_ON_FALSE(data[index] && data[index] != '\r' &&
                                        (data[index] != '\t' || index == tab),
                                    ESP_ERR_INVALID_ARG, TAG,
                                    "Invalid Wi-Fi field");
            }
            ESP_RETURN_ON_FALSE(++count <= WIFI_MAX_FILE_NETWORKS,
                                ESP_ERR_INVALID_SIZE, TAG,
                                "Too many Wi-Fi networks");
        }
        offset = end < size ? end + 1U : end;
    }
    ESP_RETURN_ON_FALSE(count, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi file has no networks");
    return ESP_OK;
}
esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size) {
    ESP_RETURN_ON_ERROR(network_service_validate_credentials_file(data, size),
                        TAG, "Invalid Wi-Fi file");
    ESP_RETURN_ON_FALSE(s_wifi_save_lock, ESP_ERR_INVALID_STATE, TAG,
                        "Wi-Fi storage is not initialized");
    ESP_RETURN_ON_FALSE(xSemaphoreTake(s_wifi_save_lock, pdMS_TO_TICKS(1000)) == pdTRUE,
                        ESP_ERR_TIMEOUT, TAG, "Wi-Fi save is busy");
    const char *path = "/spiffs/data/wifi.csv";
    const char *temporary_path = "/spiffs/data/wifi.csv.tmp";
    FILE *file = fopen(temporary_path, "wb");
    esp_err_t result = ESP_FAIL;
    if (file) {
        bool written = fwrite(data, 1, size, file) == size;
        bool flushed = fflush(file) == 0;
        bool closed = fclose(file) == 0;
        if (written && flushed && closed &&
            web_upload_publish_file(temporary_path, path)) {
            result = ESP_OK;
        } else {
            (void)remove(temporary_path);
        }
    }
    xSemaphoreGive(s_wifi_save_lock);
    return result;
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
    return network_service_save_credentials_file((const uint8_t *)line, size);
}
