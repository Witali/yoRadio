static network_netif_t s_station_netif;
static native_state_t *s_state;
enum { NETWORK_OFF, NETWORK_STARTING, NETWORK_READY, NETWORK_RETAINED };
static atomic_uint s_network_start;
esp_err_t network_service_start(native_state_t *state) {
    if (!state || !state->lock) return ESP_ERR_INVALID_ARG;
    unsigned expected = NETWORK_OFF;
    if (!atomic_compare_exchange_strong(&s_network_start, &expected, NETWORK_STARTING))
        return expected == NETWORK_READY && s_state == state ? ESP_OK : ESP_ERR_INVALID_STATE;
    bool loop_owned = false, wifi_owned = false;
    network_profiles_t profiles = {0};
    esp_err_t result = network_service_storage_init();
    if (result != ESP_OK) goto failed;
    result = esp_netif_init();
    if (result != ESP_OK) goto failed;
    result = esp_event_loop_create_default();
    if (result == ESP_OK) loop_owned = true;
    else if (result != ESP_ERR_INVALID_STATE) goto failed;
    result = network_netif_create(&s_station_netif, false);
    if (result != ESP_OK) goto failed;
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    result = esp_wifi_init(&init);
    if (result != ESP_OK) goto failed;
    wifi_owned = true;
    // Desired CSV is the sole persistent source, including an explicit empty file.
    result = esp_wifi_set_storage(WIFI_STORAGE_RAM);
    if (result != ESP_OK) goto failed;
    result = esp_wifi_set_mode(WIFI_MODE_STA);
    if (result != ESP_OK) goto failed;
    esp_err_t loaded = network_profiles_load(&profiles);
    if (loaded != ESP_OK) {
        // A complete read failure is an empty active table, never a partial one.
        // The runtime snapshot exposes no private rows or passwords.
        native_wifi_erase(&profiles, sizeof(profiles));
        ESP_LOGW(TAG, "Active Wi-Fi profiles unavailable: %s", esp_err_to_name(loaded));
    }
    result = network_runtime_start(state, s_station_netif.handle, &profiles);
    native_wifi_erase(&profiles, sizeof(profiles));
    if (result != ESP_OK) goto failed;
    result = esp_wifi_start();
    if (result != ESP_OK) goto failed;
    s_state = state;
    atomic_store_explicit(&s_network_start, NETWORK_READY, memory_order_release);
    // Bound bootstrap waiting; the owner still services late loss/portal work.
    // Successful infrastructure startup does not imply station association.
    result = network_runtime_wait_initial(20000);
    if (result == ESP_ERR_TIMEOUT) return ESP_OK;
    return result;
failed:
    native_wifi_erase(&profiles, sizeof(profiles));
    // Never tear down a netif or driver while retained callbacks can read it.
    if (wifi_owned) {
        esp_err_t stopped = esp_wifi_stop();
        if (stopped != ESP_OK && stopped != ESP_ERR_WIFI_NOT_STARTED) {
            atomic_store(&s_network_start, NETWORK_RETAINED);
            return result;
        }
    }
    if (network_runtime_stop(2000) != ESP_OK ||
        (wifi_owned && esp_wifi_deinit() != ESP_OK)) {
        atomic_store(&s_network_start, NETWORK_RETAINED);
        return result;
    }
    if (network_netif_release(&s_station_netif) != ESP_OK) {
        atomic_store(&s_network_start, NETWORK_RETAINED);
        return result;
    }
    if (loop_owned) esp_event_loop_delete_default();
    atomic_store_explicit(&s_network_start, NETWORK_OFF, memory_order_release);
    return result;
}
