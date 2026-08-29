#include "native_audio_output.h"

#include <stdbool.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s.h"
#include "esp_log.h"

static const char *TAG = "audio_output";
static uint32_t s_sample_rate;

esp_err_t native_audio_output_init(void) {
    const i2s_config_t config = {
        .mode = I2S_MODE_MASTER | I2S_MODE_TX,
        .sample_rate = 44100,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB,
        .dma_buf_count = 6,
        .dma_buf_len = 128,
        .tx_desc_auto_clear = true,
    };
    const i2s_pin_config_t pins = {
        .bck_o_en = 1,
        .ws_o_en = 1,
        .data_out_en = 1,
        .data_in_en = 0,
    };
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &config, 0, NULL);
    if (result == ESP_OK) result = i2s_set_pin(I2S_NUM_0, &pins);
    if (result == ESP_OK) s_sample_rate = 44100;
    ESP_LOGI(TAG, "I2S DMA: 6 x 128 stereo frames");
    return result;
}

esp_err_t native_audio_output_write(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate, uint8_t channels) {
    if (!samples || !sample_count || !sample_rate ||
        (channels != 1 && channels != 2)) return ESP_ERR_INVALID_ARG;
    if (channels == 1) {
        if (sample_count > 1152) return ESP_ERR_INVALID_SIZE;
        for (size_t index = sample_count; index-- > 0;) {
            int16_t value = samples[index];
            samples[index * 2] = value;
            samples[index * 2 + 1] = value;
        }
        sample_count *= 2;
    }
    if (sample_rate != s_sample_rate) {
        esp_err_t result = i2s_set_clk(I2S_NUM_0, sample_rate,
                                       I2S_BITS_PER_SAMPLE_16BIT,
                                       I2S_CHANNEL_STEREO);
        if (result != ESP_OK) return result;
        s_sample_rate = sample_rate;
    }
    size_t bytes_written = 0;
    size_t bytes = sample_count * sizeof(*samples);
    esp_err_t result = i2s_write(I2S_NUM_0, samples, bytes, &bytes_written,
                                 pdMS_TO_TICKS(120));
    return result == ESP_OK && bytes_written == bytes ? ESP_OK : ESP_FAIL;
}

void native_audio_output_silence(void) {
    i2s_zero_dma_buffer(I2S_NUM_0);
}
