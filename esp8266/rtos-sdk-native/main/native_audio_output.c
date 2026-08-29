#include "native_audio_output.h"

#include <stdbool.h>
#include <limits.h>
#include <stdlib.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s.h"
#include "esp_log.h"
#include "native_audio_normalizer.h"
#include "persistent_settings.h"

static const char *TAG = "audio_output";
static uint32_t s_sample_rate;
static uint8_t s_volume = 160;
static int8_t s_balance;
static bool s_normalization_enabled;
static uint8_t s_normalization_max_gain_db;
static int8_t s_normalization_target_db;
static uint16_t s_normalization_time_ms;

#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U
#define GAIN_Q15_ONE 32768U

static uint32_t channel_gain_q15(uint8_t volume, uint8_t balance_gain) {
    uint32_t denominator = VOLUME_DENOMINATOR * BALANCE_DENOMINATOR;
    uint32_t numerator = (uint32_t)volume * balance_gain;
    return (numerator * GAIN_Q15_ONE + denominator / 2U) / denominator;
}

static int16_t scale_sample(int16_t sample, uint32_t gain_q15) {
    int32_t value = (int32_t)sample * (int32_t)gain_q15;
    if (value >= 0) {
        value = (value + (int32_t)(GAIN_Q15_ONE / 2U)) >> 15;
    } else {
        value = -((-value + (int32_t)(GAIN_Q15_ONE / 2U)) >> 15);
    }
    if (value > INT16_MAX) value = INT16_MAX;
    if (value < INT16_MIN) value = INT16_MIN;
    return (int16_t)value;
}

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
    native_audio_output_reload_settings();
    ESP_LOGI(TAG, "I2S DMA: 6 x 128 stereo frames");
    return result;
}

esp_err_t native_audio_output_write(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate, uint8_t channels) {
    if (!samples || !sample_count || !sample_rate ||
        (channels != 1 && channels != 2)) return ESP_ERR_INVALID_ARG;
    size_t frames = sample_count / channels;
    native_audio_normalizer_configure(
        s_normalization_enabled, s_normalization_max_gain_db,
        s_normalization_target_db, s_normalization_time_ms, sample_rate);
    native_audio_normalizer_process(samples, frames, channels);
    uint8_t left_balance = s_balance < 0
        ? (uint8_t)(BALANCE_DENOMINATOR + s_balance) : BALANCE_DENOMINATOR;
    uint8_t right_balance = s_balance > 0
        ? (uint8_t)(BALANCE_DENOMINATOR - s_balance) : BALANCE_DENOMINATOR;
    uint32_t left_gain = channel_gain_q15(s_volume, left_balance);
    uint32_t right_gain = channel_gain_q15(s_volume, right_balance);
    for (size_t frame = 0; frame < frames; ++frame) {
        samples[frame * channels] =
            scale_sample(samples[frame * channels], left_gain);
        if (channels == 2) {
            samples[frame * 2U + 1U] =
                scale_sample(samples[frame * 2U + 1U], right_gain);
        }
    }
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

void native_audio_output_reload_settings(void) {
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    s_volume = settings.volume > VOLUME_DENOMINATOR
                   ? VOLUME_DENOMINATOR : settings.volume;
    s_balance = settings.balance < -BALANCE_DENOMINATOR
                    ? -BALANCE_DENOMINATOR
                    : (settings.balance > BALANCE_DENOMINATOR
                           ? BALANCE_DENOMINATOR : settings.balance);
    s_normalization_enabled = settings.normalization_enabled;
    s_normalization_max_gain_db = settings.normalization_max_gain_db;
    s_normalization_target_db = settings.normalization_target_db;
    s_normalization_time_ms = settings.normalization_time_ms;
}

void native_audio_output_reset_normalizer(void) {
    native_audio_normalizer_reset();
}

uint8_t native_audio_output_volume(void) { return s_volume; }

void native_audio_output_set_volume_runtime(uint8_t volume) {
    s_volume = volume > VOLUME_DENOMINATOR ? VOLUME_DENOMINATOR : volume;
}

void native_audio_output_set_balance_runtime(int8_t balance) {
    s_balance = balance < -BALANCE_DENOMINATOR
                    ? -BALANCE_DENOMINATOR
                    : (balance > BALANCE_DENOMINATOR
                           ? BALANCE_DENOMINATOR : balance);
}
