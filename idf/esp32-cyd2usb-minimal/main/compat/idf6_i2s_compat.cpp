#include "idf6_i2s_compat.h"

#include <algorithm>
#include <atomic>
#include <cstring>
#include "driver/dac_continuous.h"
#include "freertos/stream_buffer.h"
#include "freertos/task.h"

namespace {

constexpr size_t kPendingSamples = 128;
constexpr size_t kAudioQueueStorageBytes = 8193;  // 8192 usable bytes
constexpr size_t kOutputBlockSamples = 512;
constexpr uint32_t kDefaultClockMinimumHz = 19600;

struct DacState {
    i2s_config_t config{};
    dac_continuous_handle_t handle = nullptr;
    i2s_dac_mode_t mode = I2S_DAC_CHANNEL_LEFT_EN;
    bool installed = false;
    bool enabled = false;
    uint8_t pending[kPendingSamples]{};
    size_t pendingSize = 0;
    StaticStreamBuffer_t streamControl{};
    uint8_t streamStorage[kAudioQueueStorageBytes]{};
    StreamBufferHandle_t stream = nullptr;
    TaskHandle_t volatile outputTask = nullptr;
    std::atomic<bool> stopRequested{false};
    std::atomic<uint32_t> clearRequest{0};
    std::atomic<uint32_t> clearApplied{0};
    std::atomic<uint32_t> underruns{0};
    std::atomic<uint32_t> driverErrors{0};
    uint8_t outputBlock[kOutputBlockSamples]{};
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

esp_err_t flushPending(TickType_t timeoutTicks) {
    if (!state.pendingSize) return ESP_OK;
    if (!state.stream || !state.handle || !state.enabled) {
        state.pendingSize = 0;
        return ESP_OK;
    }
    const size_t loaded = xStreamBufferSend(
        state.stream, state.pending, state.pendingSize, timeoutTicks);
    if (loaded == state.pendingSize) {
        state.pendingSize = 0;
        return ESP_OK;
    }
    if (loaded && loaded < state.pendingSize) {
        memmove(state.pending, state.pending + loaded, state.pendingSize - loaded);
        state.pendingSize -= loaded;
    }
    return ESP_ERR_TIMEOUT;
}

void resetQueuedSamples() {
    state.pendingSize = 0;
    if (!state.stream) return;
    (void)xStreamBufferReset(state.stream);
}

esp_err_t requestQueueClear() {
    state.pendingSize = 0;
    if (!state.stream) return ESP_OK;
    if (!state.outputTask) {
        resetQueuedSamples();
        return ESP_OK;
    }

    const uint32_t request =
        state.clearRequest.fetch_add(1, std::memory_order_relaxed) + 1;
    const TickType_t deadline = xTaskGetTickCount() + pdMS_TO_TICKS(250);
    while (state.clearApplied.load(std::memory_order_relaxed) != request &&
           static_cast<int32_t>(deadline - xTaskGetTickCount()) > 0) {
        vTaskDelay(1);
    }
    return state.clearApplied.load(std::memory_order_relaxed) == request
        ? ESP_OK : ESP_ERR_TIMEOUT;
}

void dacOutputTask(void *) {
    while (!state.stopRequested.load(std::memory_order_relaxed)) {
        const uint32_t clearRequest =
            state.clearRequest.load(std::memory_order_relaxed);
        if (state.clearApplied.load(std::memory_order_relaxed) != clearRequest) {
            while (xStreamBufferReceive(
                       state.stream, state.outputBlock,
                       sizeof(state.outputBlock), 0) != 0) {}
            state.clearApplied.store(clearRequest, std::memory_order_relaxed);
        }
        const uint32_t blockGeneration = clearRequest;

        size_t received = xStreamBufferReceive(
            state.stream, state.outputBlock, sizeof(state.outputBlock), 0);

        // Decoders produce PCM in bursts. Once a burst starts, briefly wait
        // for a complete output block instead of inserting silence between
        // the decoder's small producer blocks.
        if (received && received < sizeof(state.outputBlock)) {
            const uint32_t sampleRate = state.config.sample_rate
                ? state.config.sample_rate : 16000U;
            const uint32_t blockMs = std::clamp<uint32_t>(
                static_cast<uint32_t>(
                    (sizeof(state.outputBlock) * 1000U + sampleRate - 1U) /
                    sampleRate),
                1U, 50U);
            const TickType_t deadline =
                xTaskGetTickCount() + pdMS_TO_TICKS(blockMs);
            while (received < sizeof(state.outputBlock) &&
                   !state.stopRequested.load(std::memory_order_relaxed) &&
                   state.clearRequest.load(std::memory_order_relaxed) ==
                       blockGeneration) {
                const TickType_t now = xTaskGetTickCount();
                const int32_t remaining = static_cast<int32_t>(deadline - now);
                if (remaining <= 0) break;
                received += xStreamBufferReceive(
                    state.stream, state.outputBlock + received,
                    sizeof(state.outputBlock) - received,
                    static_cast<TickType_t>(remaining));
            }
        }

        if (state.clearRequest.load(std::memory_order_relaxed) !=
            blockGeneration) {
            continue;
        }

        if (received < sizeof(state.outputBlock)) {
            if (received) {
                state.underruns.fetch_add(1, std::memory_order_relaxed);
            }
            memset(state.outputBlock + received, 0x80,
                   sizeof(state.outputBlock) - received);
        }

        size_t offset = 0;
        while (offset < sizeof(state.outputBlock) &&
               !state.stopRequested.load(std::memory_order_relaxed)) {
            size_t loaded = 0;
            const esp_err_t result = dac_continuous_write(
                state.handle, state.outputBlock + offset,
                sizeof(state.outputBlock) - offset, &loaded, 50);
            offset += loaded;
            if (result == ESP_ERR_TIMEOUT) continue;
            if (result != ESP_OK) {
                state.driverErrors.fetch_add(1, std::memory_order_relaxed);
                vTaskDelay(1);
                break;
            }
        }
    }

    state.outputTask = nullptr;
    vTaskDelete(nullptr);
}

esp_err_t startOutputTask() {
    if (state.outputTask) return ESP_OK;
    state.stopRequested.store(false, std::memory_order_relaxed);
    TaskHandle_t task = nullptr;
    const BaseType_t created = xTaskCreatePinnedToCore(
        dacOutputTask, "dac-output", 4096, nullptr, 4, &task,
        CONFIG_ARDUINO_RUNNING_CORE);
    if (created != pdPASS) return ESP_ERR_NO_MEM;
    state.outputTask = task;
    return ESP_OK;
}

esp_err_t stopOutputTask() {
    if (!state.outputTask) return ESP_OK;
    state.stopRequested.store(true, std::memory_order_relaxed);
    const TickType_t deadline = xTaskGetTickCount() + pdMS_TO_TICKS(250);
    while (state.outputTask &&
           static_cast<int32_t>(deadline - xTaskGetTickCount()) > 0) {
        vTaskDelay(1);
    }
    return state.outputTask ? ESP_ERR_TIMEOUT : ESP_OK;
}

esp_err_t releaseHardware() {
    esp_err_t result = stopOutputTask();
    if (result != ESP_OK) return result;
    if (state.handle && state.enabled) {
        result = dac_continuous_disable(state.handle);
        state.enabled = false;
    }
    if (state.handle) {
        const esp_err_t deleted = dac_continuous_del_channels(state.handle);
        if (result == ESP_OK) result = deleted;
        state.handle = nullptr;
    }
    resetQueuedSamples();
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

    if (!state.stream) {
        state.stream = xStreamBufferCreateStatic(
            sizeof(state.streamStorage), 1, state.streamStorage,
            &state.streamControl);
        if (!state.stream) return ESP_ERR_NO_MEM;
    } else if (xStreamBufferReset(state.stream) != pdPASS) {
        return ESP_ERR_INVALID_STATE;
    }
    state.pendingSize = 0;
    state.clearRequest.store(0, std::memory_order_relaxed);
    state.clearApplied.store(0, std::memory_order_relaxed);
    state.underruns.store(0, std::memory_order_relaxed);
    state.driverErrors.store(0, std::memory_order_relaxed);

    const dac_continuous_config_t config = {
        .chan_mask = channelMask(),
        // The legacy ring stores 32-bit stereo frames. The new single-channel
        // DAC stores 16-bit DMA slots, and IDF's short-write splitter uses two
        // descriptors per 512-sample producer block. Doubling both dimensions
        // restores the old ring's duration without increasing its byte count.
        .desc_num = static_cast<uint32_t>(
            std::max(4, state.config.dma_buf_count * 2)),
        .buf_size = static_cast<size_t>(
            std::clamp(state.config.dma_buf_len * 2, 64, 4092)),
        .freq_hz = state.config.sample_rate ? state.config.sample_rate : 16000U,
        .offset = 0,
        .clk_src = state.config.sample_rate >= kDefaultClockMinimumHz
            ? DAC_DIGI_CLK_SRC_DEFAULT : DAC_DIGI_CLK_SRC_APLL,
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
    result = startOutputTask();
    if (result == ESP_OK) return ESP_OK;
    dac_continuous_disable(state.handle);
    dac_continuous_del_channels(state.handle);
    state.handle = nullptr;
    state.enabled = false;
    return result;
}

extern "C" esp_err_t idf6_dac_output_end(void) {
    const esp_err_t result = releaseHardware();
    state.installed = false;
    return result;
}

extern "C" esp_err_t idf6_dac_output_start(void) {
    if (!state.handle) return idf6_dac_output_begin();
    return state.enabled ? startOutputTask() : ESP_ERR_INVALID_STATE;
}

extern "C" esp_err_t idf6_dac_output_stop(void) {
    return releaseHardware();
}

extern "C" esp_err_t idf6_dac_output_clear(void) {
    return requestQueueClear();
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
    for (size_t offset = 0; offset < size; offset += sizeof(uint32_t)) {
        if (state.pendingSize == sizeof(state.pending)) {
            const esp_err_t result = flushPending(timeoutTicks);
            if (result != ESP_OK) {
                if (bytesWritten) *bytesWritten = offset;
                return result;
            }
        }
        // Gain() packs left in bits 31..16 and right in bits 15..0. GPIO26 is
        // the legacy left DAC, so its unsigned high byte is byte 3 on ESP32.
        state.pending[state.pendingSize++] =
            input[offset + (state.mode == I2S_DAC_CHANNEL_RIGHT_EN ? 1 : 3)];
    }
    if (bytesWritten) *bytesWritten = size;
    // The sample is already accepted by the adapter even if the stream queue
    // is temporarily full; keep it in pending and back-pressure the next call.
    if (state.pendingSize == sizeof(state.pending)) {
        (void)flushPending(timeoutTicks);
    }
    return ESP_OK;
}
