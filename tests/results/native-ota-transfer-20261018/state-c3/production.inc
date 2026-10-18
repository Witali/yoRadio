static void publish_icy_title(uint32_t generation, const char *title) {
    if (!title) return;
    if (generation != atomic_load(&s_generation)) return;
    native_state_set_stream_title(s_state, generation, title);
    ESP_LOGI(TAG, "Stream title: %s", title);
}
