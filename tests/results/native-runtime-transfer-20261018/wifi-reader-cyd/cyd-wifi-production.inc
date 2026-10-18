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
