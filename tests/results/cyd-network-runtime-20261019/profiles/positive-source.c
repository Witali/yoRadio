#include "network_profiles.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>

#include "credential_line.h"
#include "native_wifi_store.h"
#include "web_upload.h"

esp_err_t network_profiles_load(network_profiles_t *out) {
    if (!out) return ESP_ERR_INVALID_ARG;

    network_profiles_t staged = {0};
    char line[160] = {0};
    esp_err_t result;
    errno = 0;
    FILE *file = web_upload_open_file("/spiffs/data/wifi.csv");
    if (!file) {
        result = errno == ENOENT ? ESP_ERR_NOT_FOUND : ESP_FAIL;
        goto cleanup;
    }

    while (native_credential_next_row(file, line, sizeof(line))) {
        char *password = strchr(line, '\t');
        if (!password) continue;
        *password++ = '\0';
        size_t ssid_size = strlen(line);
        size_t password_size = strlen(password);
        if (!ssid_size || ssid_size >= sizeof(staged.rows[0].ssid) ||
            password_size >= sizeof(staged.rows[0].password) ||
            strchr(line, '\r') || strpbrk(password, "\t\r")) {
            continue;
        }
        if (staged.count < NETWORK_PROFILES_MAX) {
            network_profile_t *row = &staged.rows[staged.count];
            memcpy(row->ssid, line, ssid_size + 1U);
            memcpy(row->password, password, password_size + 1U);
            ++staged.count;
        }
    }
    result = ferror(file) ? ESP_FAIL : ESP_OK;
    if (fclose(file) != 0) result = ESP_FAIL;
    if (result == ESP_OK) *out = staged;

cleanup:
    native_wifi_erase(line, sizeof(line));
    native_wifi_erase(&staged, sizeof(staged));
    return result;
}
