static bool idle_clock(native_state_t *state) {
    native_state_t current;
    native_state_snapshot(state, &current);
    bool power_off = false;
    return !current.audio_running && current.web_ready &&
        current.network_mode == NATIVE_NETWORK_CLIENT &&
        (strcmp(current.stream_format, "stopped") == 0 ||
         strcmp(current.stream_format, "idle") == 0) &&
        display_settings_screensaver_active(false,
            (uint32_t)(esp_timer_get_time() / 1000U), &power_off) && !power_off &&
        gpio_get_level(BOARD_BOOT_BUTTON) != 0;
}
