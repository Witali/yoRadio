static void reset_resampler(void) {
    s_resampler_has_previous = false;
    s_resampler_previous = 0;
    s_resampler_next_phase = 0;
}

static esp_err_t pdm_flush(void) {
    if (!s_buffered_samples) return ESP_OK;
    memset(s_sample_buffer + s_buffered_samples, 0,
           (PDM_DMA_SAMPLES - s_buffered_samples) * sizeof(int16_t));
    esp_err_t result = pdm_write_block(s_sample_buffer, PDM_DMA_SAMPLES);
    s_buffered_samples = 0;
    return result;
}

void native_audio_output_discard_pcm(void) {
    s_buffered_samples = 0;
    reset_resampler();
    reset_pcm_normalizer();
}

esp_err_t native_audio_output_flush_pcm(void) {
    esp_err_t result = pdm_flush();
    reset_resampler();
    reset_pcm_normalizer();
    return result;
}
