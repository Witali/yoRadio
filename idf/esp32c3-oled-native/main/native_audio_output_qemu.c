#include "native_audio_output.h"

#include <limits.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#include "audio_level_led.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_audio_normalizer.h"
#include "native_audio_settings.h"

#define QEMU_PCM_BASE 0x6002d000U
#define QEMU_PCM_VERSION_REG (*(volatile uint32_t *)(QEMU_PCM_BASE + 0x00U))
#define QEMU_PCM_CONTROL_REG (*(volatile uint32_t *)(QEMU_PCM_BASE + 0x04U))
#define QEMU_PCM_FREE_REG (*(volatile uint32_t *)(QEMU_PCM_BASE + 0x08U))
#define QEMU_PCM_DATA_REG (*(volatile uint32_t *)(QEMU_PCM_BASE + 0x0cU))
#define QEMU_PCM_DROPPED_REG (*(volatile uint32_t *)(QEMU_PCM_BASE + 0x10U))
#define QEMU_PCM_VERSION 0x00010000U
#define QEMU_PCM_ENABLE 1U

#define OUTPUT_SAMPLE_RATE 48000U
#define RESAMPLER_SCALE 32768U
#define RESAMPLER_FRACTION_MULTIPLIER_Q16 44739U
#define SAMPLE_GAIN_SCALE 32768U
#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U

static const char *const TAG = "audio_output";
static uint32_t s_input_sample_rate;
static bool s_resampler_has_previous;
static int16_t s_previous_left;
static int16_t s_previous_right;
static uint32_t s_resampler_next_phase;
static atomic_bool s_normalizer_reset_pending = ATOMIC_VAR_INIT(false);

typedef struct {
    bool valid;
    bool enabled;
    uint8_t max_gain_db;
    int8_t target_dbfs;
    uint16_t time_ms;
    uint32_t sample_rate;
} normalizer_config_cache_t;

static normalizer_config_cache_t s_normalizer_config;

static int16_t scale_sample_q15(int16_t sample, uint32_t gain_q15) {
    int32_t scaled = (int32_t)sample * (int32_t)gain_q15;
    if (scaled >= 0) {
        return (int16_t)((scaled + SAMPLE_GAIN_SCALE / 2U) /
                         SAMPLE_GAIN_SCALE);
    }
    return (int16_t)-(((-scaled) + SAMPLE_GAIN_SCALE / 2U) /
                      SAMPLE_GAIN_SCALE);
}

static uint32_t channel_gain_q15(uint8_t volume, uint8_t balance_gain) {
    const uint32_t denominator =
        VOLUME_DENOMINATOR * BALANCE_DENOMINATOR;
    uint32_t numerator = (uint32_t)volume * balance_gain;
    return (numerator * SAMPLE_GAIN_SCALE + denominator / 2U) / denominator;
}

static void decode_pcm_frame(const uint8_t *frame, uint8_t channels,
                             int16_t *left, int16_t *right) {
    memcpy(left, frame, sizeof(*left));
    if (channels > 1) {
        memcpy(right, frame + sizeof(*left), sizeof(*right));
    } else {
        *right = *left;
    }
}

static void reset_resampler(void) {
    s_resampler_has_previous = false;
    s_previous_left = 0;
    s_previous_right = 0;
    s_resampler_next_phase = 0;
}

static esp_err_t qemu_queue_frame(int16_t left, int16_t right) {
    unsigned waits = 0;
    while (QEMU_PCM_FREE_REG == 0) {
        if (++waits > 2000U) return ESP_ERR_TIMEOUT;
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    QEMU_PCM_DATA_REG = (uint16_t)left | ((uint32_t)(uint16_t)right << 16);
    return ESP_OK;
}

static int16_t interpolate_sample(int16_t previous, int16_t current,
                                  uint32_t fraction) {
    int32_t delta = (int32_t)current - previous;
    int32_t scaled = delta * (int32_t)fraction;
    scaled += scaled >= 0 ? RESAMPLER_SCALE / 2U
                          : -(int32_t)(RESAMPLER_SCALE / 2U);
    return (int16_t)((int32_t)previous +
                     scaled / (int32_t)RESAMPLER_SCALE);
}

static esp_err_t qemu_write_resampled(int16_t left, int16_t right) {
    if (s_input_sample_rate == OUTPUT_SAMPLE_RATE) {
        return qemu_queue_frame(left, right);
    }
    if (!s_resampler_has_previous) {
        s_resampler_has_previous = true;
        s_previous_left = left;
        s_previous_right = right;
        s_resampler_next_phase = s_input_sample_rate;
        return qemu_queue_frame(left, right);
    }

    uint32_t phase = s_resampler_next_phase;
    while (phase <= OUTPUT_SAMPLE_RATE) {
        uint32_t fraction =
            (phase * RESAMPLER_FRACTION_MULTIPLIER_Q16 + 32768U) >> 16;
        ESP_RETURN_ON_ERROR(
            qemu_queue_frame(
                interpolate_sample(s_previous_left, left, fraction),
                interpolate_sample(s_previous_right, right, fraction)),
            TAG, "write QEMU PCM");
        phase += s_input_sample_rate;
    }
    s_resampler_next_phase = phase - OUTPUT_SAMPLE_RATE;
    s_previous_left = left;
    s_previous_right = right;
    return ESP_OK;
}

static void sync_normalizer_configuration(void) {
    normalizer_config_cache_t next = {
        .valid = true,
        .enabled = native_audio_settings_get_normalization(),
        .max_gain_db = native_audio_settings_get_normalization_gain_db(),
        .target_dbfs = native_audio_settings_get_normalization_target_dbfs(),
        .time_ms = native_audio_settings_get_normalization_time_ms(),
        .sample_rate = s_input_sample_rate,
    };
    if (s_normalizer_config.valid &&
        next.enabled == s_normalizer_config.enabled &&
        next.max_gain_db == s_normalizer_config.max_gain_db &&
        next.target_dbfs == s_normalizer_config.target_dbfs &&
        next.time_ms == s_normalizer_config.time_ms &&
        next.sample_rate == s_normalizer_config.sample_rate) {
        return;
    }
    native_audio_normalizer_configure(
        next.enabled, next.max_gain_db, next.target_dbfs, next.time_ms,
        next.sample_rate);
    s_normalizer_config = next;
}

esp_err_t native_audio_output_init(void) {
    ESP_RETURN_ON_FALSE(QEMU_PCM_VERSION_REG == QEMU_PCM_VERSION,
                        ESP_ERR_NOT_SUPPORTED, TAG,
                        "QEMU PCM device is unavailable");
    QEMU_PCM_CONTROL_REG = QEMU_PCM_ENABLE;
    ESP_LOGI(TAG, "QEMU stereo PCM ready at 48000 Hz");
    return ESP_OK;
}

esp_err_t native_audio_output_configure(uint32_t input_sample_rate) {
    if (input_sample_rate < 8000U || input_sample_rate > 48000U) {
        return ESP_ERR_INVALID_ARG;
    }
    if (input_sample_rate != s_input_sample_rate) {
        s_input_sample_rate = input_sample_rate;
        reset_resampler();
        native_audio_normalizer_set_sample_rate(input_sample_rate);
        ESP_LOGI(TAG, "QEMU PCM resampler input changed to %lu Hz",
                 (unsigned long)input_sample_rate);
    }
    return ESP_OK;
}

void native_audio_output_request_normalizer_reset(void) {
    if (native_audio_settings_get_normalization()) {
        atomic_store(&s_normalizer_reset_pending, true);
    }
}

esp_err_t native_audio_output_write_pcm(uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels) {
    if (!data || bits_per_sample != 16 || channels == 0 ||
        !s_input_sample_rate) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    sync_normalizer_configuration();
    if (atomic_exchange(&s_normalizer_reset_pending, false)) {
        native_audio_normalizer_reset();
    }

    size_t frame_bytes = (size_t)channels * sizeof(int16_t);
    size_t frames = size / frame_bytes;
    native_audio_normalizer_process_block((int16_t *)data, frames, channels);
    uint16_t peak = 0;
    uint8_t volume = native_audio_settings_get_volume();
    int8_t balance = native_audio_settings_get_balance();
    uint8_t left_balance =
        balance < 0 ? (uint8_t)((int)BALANCE_DENOMINATOR + balance)
                    : BALANCE_DENOMINATOR;
    uint8_t right_balance =
        balance > 0 ? (uint8_t)(BALANCE_DENOMINATOR - balance)
                    : BALANCE_DENOMINATOR;
    uint32_t left_gain_q15 = channel_gain_q15(volume, left_balance);
    uint32_t right_gain_q15 = channel_gain_q15(volume, right_balance);

    for (size_t frame = 0; frame < frames; ++frame) {
        int16_t left;
        int16_t right;
        decode_pcm_frame(data + frame * frame_bytes, channels, &left, &right);
        left = scale_sample_q15(left, left_gain_q15);
        right = scale_sample_q15(right, right_gain_q15);
        uint16_t left_peak = left == INT16_MIN ? 32768U : (uint16_t)abs(left);
        uint16_t right_peak =
            right == INT16_MIN ? 32768U : (uint16_t)abs(right);
        if (left_peak > peak) peak = left_peak;
        if (right_peak > peak) peak = right_peak;
        ESP_RETURN_ON_ERROR(qemu_write_resampled(left, right), TAG,
                            "write virtual stereo PCM");
    }
    audio_level_led_update_peak(peak);
    return QEMU_PCM_DROPPED_REG == 0 ? ESP_OK : ESP_FAIL;
}

void native_audio_output_set_volume(uint8_t volume) {
    ESP_ERROR_CHECK_WITHOUT_ABORT(native_audio_settings_set_volume(volume));
}

uint8_t native_audio_output_get_volume(void) {
    return native_audio_settings_get_volume();
}

void native_audio_output_set_balance(int8_t balance) {
    ESP_ERROR_CHECK_WITHOUT_ABORT(native_audio_settings_set_balance(balance));
}

int8_t native_audio_output_get_balance(void) {
    return native_audio_settings_get_balance();
}

void native_audio_output_idle(void) {
    audio_level_led_update_peak(0);
}

const char *native_audio_output_name(void) {
    return "QEMU 48 kHz stereo PCM";
}
