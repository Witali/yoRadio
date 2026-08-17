#include "idf6_i2s_compat.h"

#include <algorithm>
#include <cstring>
#include "driver/dac_continuous.h"

namespace {

struct DacState {
    i2s_config_t config{};
    dac_continuous_handle_t handle = nullptr;
    i2s_dac_mode_t mode = I2S_DAC_CHANNEL_LEFT_EN;
    bool installed = false;
    bool enabled = false;
    uint8_t pending[128]{};
    size_t pendingSize = 0;
};

DacState state;

dac_channel_mask_t channelMask() {
    switch (state.mode) {
        case I2S_DAC_CHANNEL_RIGHT_EN: return DAC_CHANNEL_MASK_CH0;
        case I2S_DAC_CHANNEL_BOTH_EN: return DAC_CHANNEL_MASK_ALL;
        case I2S_DAC_CHANNEL_LEFT_EN:
        default: return DAC_CHANNEL_MASK_CH1;
    }
}

esp_err_t flushPending(int timeoutMs) {
    if (!state.pendingSize) return ESP_OK;
    if (!state.handle || !state.enabled) {
        state.pendingSize = 0;
        return ESP_OK;
    }
    size_t loaded = 0;
    const esp_err_t result = dac_continuous_write(
        state.handle, state.pending, state.pendingSize, &loaded, timeoutMs);
    if (result == ESP_OK && loaded == state.pendingSize) {
        state.pendingSize = 0;
        return ESP_OK;
    }
    if (loaded && loaded < state.pendingSize) {
        memmove(state.pending, state.pending + loaded, state.pendingSize - loaded);
        state.pendingSize -= loaded;
    }
    return result == ESP_OK ? ESP_ERR_TIMEOUT : result;
}

esp_err_t releaseHardware() {
    esp_err_t result = ESP_OK;
    if (state.handle && state.enabled) {
        flushPending(-1);
        result = dac_continuous_disable(state.handle);
        state.enabled = false;
    }
    if (state.handle) {
        const esp_err_t deleted = dac_continuous_del_channels(state.handle);
        if (result == ESP_OK) result = deleted;
        state.handle = nullptr;
    }
    state.pendingSize = 0;
    return result;
}

}  // namespace

extern "C" esp_err_t idf6_dac_output_configure(
    const i2s_config_t *config, i2s_dac_mode_t mode) {
    if (!config || mode < I2S_DAC_CHANNEL_RIGHT_EN ||
        mode > I2S_DAC_CHANNEL_BOTH_EN) return ESP_ERR_INVALID_ARG;
    state.config = *config;
    state.mode = mode;
    state.installed = true;
    return ESP_OK;
}

extern "C" esp_err_t idf6_dac_output_begin(void) {
    if (!state.installed) return ESP_ERR_INVALID_STATE;
    if (state.handle) return ESP_OK;

    const dac_continuous_config_t config = {
        .chan_mask = channelMask(),
        .desc_num = static_cast<uint32_t>(std::max(2, state.config.dma_buf_count)),
        .buf_size = static_cast<size_t>(std::clamp(state.config.dma_buf_len, 32, 4092)),
        .freq_hz = state.config.sample_rate ? state.config.sample_rate : 16000U,
        .offset = 0,
        .clk_src = DAC_DIGI_CLK_SRC_APLL,
        .chan_mode = DAC_CHANNEL_MODE_SIMUL,
    };
    esp_err_t result = dac_continuous_new_channels(&config, &state.handle);
    if (result != ESP_OK) return result;
    result = dac_continuous_enable(state.handle);
    if (result != ESP_OK) {
        dac_continuous_del_channels(state.handle);
        state.handle = nullptr;
        return result;
    }
    state.enabled = true;
    return ESP_OK;
}

extern "C" esp_err_t idf6_dac_output_end(void) {
    const esp_err_t result = releaseHardware();
    state.installed = false;
    return result;
}

extern "C" esp_err_t idf6_dac_output_start(void) {
    if (!state.handle) return idf6_dac_output_begin();
    if (state.enabled) return ESP_OK;
    const esp_err_t result = dac_continuous_enable(state.handle);
    if (result == ESP_OK) state.enabled = true;
    return result;
}

extern "C" esp_err_t idf6_dac_output_stop(void) {
    if (!state.handle || !state.enabled) return ESP_OK;
    flushPending(-1);
    const esp_err_t result = dac_continuous_disable(state.handle);
    if (result == ESP_OK) state.enabled = false;
    return result;
}

extern "C" esp_err_t idf6_dac_output_clear(void) {
    state.pendingSize = 0;
    return ESP_OK;
}

extern "C" esp_err_t idf6_dac_output_set_sample_rate(uint32_t sampleRate) {
    if (!sampleRate) return ESP_ERR_INVALID_ARG;
    if (state.config.sample_rate == sampleRate) return ESP_OK;
    state.config.sample_rate = sampleRate;
    if (!state.handle) return ESP_OK;
    const esp_err_t released = releaseHardware();
    return released == ESP_OK ? idf6_dac_output_begin() : released;
}

extern "C" esp_err_t idf6_dac_output_write(
    const void *source, size_t size, size_t *bytesWritten,
    TickType_t timeoutTicks) {
    if (bytesWritten) *bytesWritten = 0;
    if (!source || size % sizeof(uint32_t)) {
        return ESP_ERR_INVALID_ARG;
    }
    if (!state.handle) {
        if (bytesWritten) *bytesWritten = size;
        return ESP_OK;
    }

    const uint8_t *input = static_cast<const uint8_t *>(source);
    const int timeoutMs = timeoutTicks == portMAX_DELAY
        ? -1
        : static_cast<int>(timeoutTicks * portTICK_PERIOD_MS);
    for (size_t offset = 0; offset < size; offset += sizeof(uint32_t)) {
        if (state.pendingSize == sizeof(state.pending)) {
            const esp_err_t result = flushPending(timeoutMs);
            if (result != ESP_OK) return result;
        }
        // Gain() packs left in bits 31..16 and right in bits 15..0. GPIO26 is
        // the legacy left DAC, so its unsigned high byte is byte 3 on ESP32.
        state.pending[state.pendingSize++] =
            input[offset + (state.mode == I2S_DAC_CHANNEL_RIGHT_EN ? 1 : 3)];
    }
    if (bytesWritten) *bytesWritten = size;
    return ESP_OK;
}
