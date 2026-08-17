#include "idf6_i2s_compat.h"
#include "driver/adc_i2s_legacy.h"

namespace {

i2s_config_t config{};
i2s_dac_mode_t dacMode = I2S_DAC_CHANNEL_LEFT_EN;
bool configured = false;
bool installed = false;

}  // namespace

// i2s_legacy.c keeps the ADC switch call in code shared by RX and DAC-only TX.
// ESP-IDF 6 no longer exports that deprecated ADC helper. This backend never
// enables RX, so the call is unreachable for its supported mode and a no-op is
// the correct compatibility implementation.
extern "C" esp_err_t adc_set_i2s_data_source(adc_i2s_source_t) {
    return ESP_OK;
}

extern "C" esp_err_t idf6_dac_output_configure(
    const i2s_config_t *newConfig, i2s_dac_mode_t mode) {
    if (!newConfig) return ESP_ERR_INVALID_ARG;
    if (installed) return ESP_ERR_INVALID_STATE;
    config = *newConfig;
    dacMode = mode;
    configured = true;
    return ESP_OK;
}

extern "C" esp_err_t idf6_dac_output_begin(void) {
    if (installed) return ESP_OK;
    if (!configured) return ESP_ERR_INVALID_STATE;
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &config, 0, nullptr);
    if (result != ESP_OK) return result;
    result = i2s_set_dac_mode(dacMode);
    if (result != ESP_OK) {
        i2s_driver_uninstall(I2S_NUM_0);
        return result;
    }
    installed = true;
    return ESP_OK;
}

extern "C" esp_err_t idf6_dac_output_end(void) {
    if (!installed) return ESP_OK;
    const esp_err_t result = i2s_driver_uninstall(I2S_NUM_0);
    if (result == ESP_OK) installed = false;
    return result;
}

extern "C" esp_err_t idf6_dac_output_start(void) {
    return installed ? i2s_start(I2S_NUM_0) : idf6_dac_output_begin();
}

extern "C" esp_err_t idf6_dac_output_stop(void) {
    return installed ? i2s_stop(I2S_NUM_0) : ESP_OK;
}

extern "C" esp_err_t idf6_dac_output_clear(void) {
    if (!installed) return ESP_OK;
    // The old helper writes raw zeroes (the lower DAC rail), so midpoint
    // silence is supplied by Audio::fillDacSilence() instead.
    return ESP_OK;
}

extern "C" esp_err_t idf6_dac_output_set_sample_rate(uint32_t sampleRate) {
    if (!sampleRate) return ESP_ERR_INVALID_ARG;
    config.sample_rate = sampleRate;
    if (!installed) return ESP_OK;
    return i2s_set_clk(I2S_NUM_0, sampleRate, I2S_BITS_PER_SAMPLE_16BIT,
                       I2S_CHANNEL_STEREO);
}

extern "C" esp_err_t idf6_dac_output_write(
    const void *source, size_t size, size_t *bytesWritten,
    TickType_t timeoutTicks) {
    if (!installed) return ESP_ERR_INVALID_STATE;
    return i2s_write(I2S_NUM_0, source, size, bytesWritten, timeoutTicks);
}
