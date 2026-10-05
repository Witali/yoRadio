// DMA acquisition adapted from ESP-IDF 6.0.2 i2s_common.c.
// SPDX-FileCopyrightText: 2022-2026 Espressif Systems (Shanghai) CO LTD
// SPDX-License-Identifier: Apache-2.0
#include "native_i2s_generator.h"
#include "i2s_private.h"

// Built inside the pinned esp_driver_i2s component, using its actual types.
// Keep the stock writer's lock, timeout, stale-buffer avoidance and preload
// queue. Only replace memcpy with bounded PCM generation into the DMA block.
static esp_err_t write_generated(i2s_chan_handle_t channel, size_t frames,
    native_i2s_fill_t fill, void *context, bool preload, bool full_block,
    size_t *written) {
    enum { FRAME_BYTES = 2 * sizeof(int16_t), WRITE_TIMEOUT_MS = 1000 };
    if (written) *written = 0;
    if (!channel || !fill || !written || channel->dir != I2S_DIR_TX ||
        !channel->dma.buf_size || channel->dma.buf_size % FRAME_BYTES ||
        channel->dma.rw_pos % FRAME_BYTES) return ESP_ERR_INVALID_ARG;
    if (preload && channel->state != I2S_CHAN_STATE_READY)
        return ESP_ERR_INVALID_STATE;
    SemaphoreHandle_t lock = preload ? channel->mutex : channel->binary;
    TickType_t timeout = preload ? portMAX_DELAY : pdMS_TO_TICKS(WRITE_TIMEOUT_MS);
    if (xSemaphoreTake(lock, timeout) != pdTRUE) return ESP_ERR_INVALID_STATE;
    esp_err_t result = ESP_OK;
    if (full_block) {
        // Bias ramps may leave a partial descriptor. Audio never resumes a
        // partially filled DMA block across an input-queue wait.
        channel->dma.rw_pos = channel->dma.buf_size;
    }
    if (preload && !channel->dma.curr_ptr) {
        xQueueReset(channel->msg_queue);
        for (unsigned i = 1; i < channel->dma.desc_num; ++i) {
            if (xQueueSend(channel->msg_queue, &channel->dma.desc[i]->buf, 0) != pdTRUE) {
                result = ESP_FAIL;
                goto done;
            }
        }
        channel->dma.curr_ptr = (void *)channel->dma.desc[0]->buf;
        channel->dma.rw_pos = 0;
    }
    while (frames && (preload || channel->state == I2S_CHAN_STATE_RUNNING)) {
        if (channel->dma.rw_pos == channel->dma.buf_size || !channel->dma.curr_ptr ||
            (!preload && uxQueueSpacesAvailable(channel->msg_queue) <= 1)) {
            if (xQueueReceive(channel->msg_queue, &channel->dma.curr_ptr,
                              preload ? 0 : timeout) != pdTRUE) {
                if (!preload) result = ESP_ERR_TIMEOUT;
                break;
            }
            channel->dma.rw_pos = 0;
        }
        size_t count = (channel->dma.buf_size - channel->dma.rw_pos) / FRAME_BYTES;
        if (count > frames) count = frames;
        int16_t *target = (int16_t *)((uint8_t *)channel->dma.curr_ptr + channel->dma.rw_pos);
        fill(context, target, count);
        // C3 internal SRAM is DMA coherent. No PSRAM or cached SRAM is used.
        channel->dma.rw_pos += count * FRAME_BYTES;
        *written += count;
        frames -= count;
    }
    if (!preload && frames && result == ESP_OK) result = ESP_ERR_INVALID_STATE;
done:
    xSemaphoreGive(lock);
    return result;
}

esp_err_t native_i2s_write_generated(i2s_chan_handle_t channel, size_t frames,
    native_i2s_fill_t fill, void *context, bool preload, size_t *written) {
    return write_generated(channel, frames, fill, context, preload, false, written);
}

esp_err_t native_i2s_write_full_block(i2s_chan_handle_t channel,
    native_i2s_fill_t fill, void *context) {
    if (!channel) return ESP_ERR_INVALID_ARG;
    size_t frames = channel->dma.buf_size / (2 * sizeof(int16_t)), written = 0;
    esp_err_t result = write_generated(channel, frames, fill, context, false,
                                       true, &written);
    return result != ESP_OK ? result : written == frames ? ESP_OK : ESP_FAIL;
}
