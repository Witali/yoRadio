#include "credential_line.h"
static void prepare_station_config(wifi_config_t *config) {
    config->sta.threshold.authmode = WIFI_AUTH_OPEN;
    config->sta.pmf_cfg.capable = true;
    config->sta.pmf_cfg.required = false;
}
static bool next_credential_row(FILE *file, char *line, size_t capacity) {
    return native_credential_next_row(file, line, capacity);
}
static bool read_credentials(wifi_config_t *config) {
    memset(s_credentials, 0, sizeof(s_credentials));
    s_credential_count = 0;
    s_credential_index = 0;
    if (!native_file_recover("/spiffs/data/wifi.csv", "/spiffs/data/wifi.csv.bak")) return false;
    FILE *file = fopen("/spiffs/data/wifi.csv", "r");
    if (!file) return false;
    char line[160];
    bool found = false;
    while (next_credential_row(file, line, sizeof(line))) {
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab++ = '\0';
        if (!line[0] || strlen(line) >= sizeof(config->sta.ssid) ||
            strlen(tab) >= sizeof(config->sta.password) || strchr(line, '\r') ||
            strpbrk(tab, "\t\r")) {
            continue;
        }
        if (s_credential_count >= WIFI_MAX_CREDENTIALS) continue;
        wifi_config_t *saved = &s_credentials[s_credential_count++];
        strlcpy((char *)saved->sta.ssid, line, sizeof(saved->sta.ssid));
        strlcpy((char *)saved->sta.password, tab,
                sizeof(saved->sta.password));
        prepare_station_config(saved);
    }
    bool read_ok = ferror(file) == 0;
    fclose(file);
    if (!read_ok) s_credential_count = 0;
    found = s_credential_count > 0;
    if (found) {
        *config = s_credentials[0];
        ESP_LOGI(TAG, "Loaded %u Wi-Fi network(s) from /data/wifi.csv",
                 (unsigned)s_credential_count);
    }
    return found;
}
esp_err_t network_service_validate_credentials_file(const uint8_t *data,
                                                    size_t size) {
    ESP_RETURN_ON_FALSE(data && size && size < 800U, ESP_ERR_INVALID_SIZE, TAG,
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
                                    ESP_ERR_INVALID_ARG, TAG, "Invalid Wi-Fi field");
            }
            ESP_RETURN_ON_FALSE(++count <= WIFI_MAX_CREDENTIALS,
                                ESP_ERR_INVALID_SIZE, TAG,
                                "Too many Wi-Fi networks");
        }
        offset = end < size ? end + 1U : end;
    }
    ESP_RETURN_ON_FALSE(count > 0, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi file has no networks");

    return ESP_OK;
}
static void load_validated_credentials(const uint8_t *data, size_t size) {
    // Validation has already proved the row count, field bounds and separators.
    // Apply the committed request directly: a second filesystem read could
    // fail after publication and destroy the running profile table.
    memset(s_credentials, 0, sizeof(s_credentials));
    s_credential_count = 0;
    s_credential_index = 0;
    for (size_t offset = 0; offset < size;) {
        size_t end = offset;
        while (end < size && data[end] != '\n') ++end;
        size_t row_end = end;
        if (row_end > offset && data[row_end - 1U] == '\r') --row_end;
        if (row_end > offset) {
            size_t tab = offset;
            while (data[tab] != '\t') ++tab;
            wifi_config_t *saved = &s_credentials[s_credential_count++];
            memcpy(saved->sta.ssid, data + offset, tab - offset);
            memcpy(saved->sta.password, data + tab + 1U, row_end - tab - 1U);
            prepare_station_config(saved);
        }
        offset = end < size ? end + 1U : end;
    }
    s_station_config = s_credentials[0];
    s_have_credentials = true;
}
esp_err_t network_service_save_credentials_file(const uint8_t *data,
                                                size_t size) {
    ESP_RETURN_ON_ERROR(network_service_validate_credentials_file(data, size),
                        TAG, "Invalid Wi-Fi file");
    const char *path = "/spiffs/data/wifi.csv";
    const char *temporary_path = "/spiffs/data/wifi.csv.tmp";
    FILE *file = fopen(temporary_path, "wb");
    ESP_RETURN_ON_FALSE(file, ESP_FAIL, TAG,
                        "Cannot create Wi-Fi credentials file");
    bool written = fwrite(data, 1, size, file) == size;
    bool flushed = fflush(file) == 0;
    bool closed = fclose(file) == 0;
    if (!written || !flushed || !closed) {
        remove(temporary_path);
        return ESP_FAIL;
    }
    if (!web_upload_publish_file(temporary_path, path)) {
        remove(temporary_path);
        return ESP_FAIL;
    }
    load_validated_credentials(data, size);
    ESP_LOGI(TAG, "Saved %u Wi-Fi network(s)", (unsigned)s_credential_count);
    return ESP_OK;
}
