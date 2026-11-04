extern "C" esp_err_t audio_level_led_init(void) { return ESP_OK; }
extern "C" void audio_level_led_update_peak(uint16_t peak) { (void)peak; }
extern "C" void audio_level_led_update_pcm(const uint8_t *data, size_t size, uint8_t bits, uint8_t channels) {
    (void)data; (void)size; (void)bits; (void)channels;
}
extern "C" void network_service_audio_accept(uint32_t generation, bool active) { native_network_power_accept(generation, active); }
extern "C" void network_service_audio_receive(uint32_t generation) { native_network_power_receive(generation); }
extern "C" void network_service_audio_finish(uint32_t generation) { native_network_power_finish(generation); }

