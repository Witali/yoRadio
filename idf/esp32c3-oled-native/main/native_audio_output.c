#include "native_audio_output.h"

#include <limits.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#include "board_config.h"
#include "driver/gpio.h"
#include "driver/i2s_pdm.h"
#include "driver/ledc.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "soc/soc_caps.h"

#if SOC_I2S_PDM_MAX_TX_LINES < 2
#error ESP32-C3 stereo PDM requires two hardware TX data lines
#endif

#define PDM_OUTPUT_SAMPLE_RATE 48000U
#define PDM_DMA_FRAMES 512U
#define PDM_DMA_DESCRIPTORS 8U
#define PDM_BIAS_RAMP_MS 100U
#define PDM_BIAS_SETTLE_MS 2U
#define RESAMPLER_SCALE 32768U

static const char *const TAG = "audio_output";
static i2s_chan_handle_t s_pdm;
static bool s_pdm_running;
static uint32_t s_input_sample_rate;
static size_t s_buffered_frames;
static int16_t s_frame_buffer[PDM_DMA_FRAMES * 2];
static bool s_resampler_has_previous;
static int16_t s_previous_left;
static int16_t s_previous_right;
static uint32_t s_resampler_next_phase;
static uint8_t s_led_envelope;
static atomic_uchar s_volume;
static atomic_schar s_balance;

static int16_t scale_sample(int16_t sample, uint16_t numerator,
                            uint16_t denominator) {
    int32_t scaled = (int32_t)sample * numerator;
    scaled += scaled >= 0 ? denominator / 2 : -(int32_t)(denominator / 2);
    return (int16_t)(scaled / denominator);
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

static void hold_pdm_low(void) {
    const gpio_num_t pins[] = {
        BOARD_AUDIO_LEFT_DATA,
        BOARD_AUDIO_RIGHT_DATA,
    };
    for (size_t index = 0; index < sizeof(pins) / sizeof(pins[0]); ++index) {
        gpio_reset_pin(pins[index]);
        gpio_set_direction(pins[index], GPIO_MODE_OUTPUT);
        gpio_set_level(pins[index], 0);
    }
}

static void reset_resampler(void) {
    s_resampler_has_previous = false;
    s_previous_left = 0;
    s_previous_right = 0;
    s_resampler_next_phase = 0;
}

static uint32_t ramp_frames(void) {
    return (PDM_OUTPUT_SAMPLE_RATE * PDM_BIAS_RAMP_MS + 999U) / 1000U;
}

static int16_t ramp_sample(uint32_t index, uint32_t count, bool ramp_up) {
    int32_t offset = (int32_t)(((uint64_t)index * 32768U) / (count - 1U));
    return (int16_t)(ramp_up ? INT16_MIN + offset : -offset);
}

static void fill_ramp(size_t frames, uint32_t first, uint32_t count,
                      bool ramp_up) {
    for (size_t frame = 0; frame < frames; ++frame) {
        int16_t value = first + frame < count
                            ? ramp_sample(first + frame, count, ramp_up)
                            : 0;
        s_frame_buffer[frame * 2] = value;
        s_frame_buffer[frame * 2 + 1] = value;
    }
}

static esp_err_t pdm_write_block(const int16_t *samples, size_t frames) {
    if (!s_pdm || !s_pdm_running) return ESP_ERR_INVALID_STATE;
    size_t written = 0;
    size_t bytes = frames * 2U * sizeof(*samples);
    esp_err_t result = i2s_channel_write(s_pdm, samples, bytes, &written, 1000);
    if (result != ESP_OK) return result;
    return written == bytes ? ESP_OK : ESP_FAIL;
}

static esp_err_t pdm_queue_frame(int16_t left, int16_t right) {
    size_t offset = s_buffered_frames * 2U;
    s_frame_buffer[offset] = left;
    s_frame_buffer[offset + 1U] = right;
    ++s_buffered_frames;
    if (s_buffered_frames < PDM_DMA_FRAMES) return ESP_OK;
    esp_err_t result = pdm_write_block(s_frame_buffer, s_buffered_frames);
    s_buffered_frames = 0;
    return result;
}

static esp_err_t pdm_begin(void) {
    if (s_pdm) return ESP_OK;
    i2s_chan_config_t channel_config =
        I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    channel_config.dma_desc_num = PDM_DMA_DESCRIPTORS;
    channel_config.dma_frame_num = PDM_DMA_FRAMES;
    channel_config.auto_clear_after_cb = true;
    channel_config.auto_clear_before_cb = false;
    ESP_RETURN_ON_ERROR(i2s_new_channel(&channel_config, &s_pdm, NULL), TAG,
                        "allocate stereo PDM channel");

    i2s_pdm_tx_config_t pdm_config = {
        .clk_cfg = I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG(PDM_OUTPUT_SAMPLE_RATE),
        .slot_cfg = I2S_PDM_TX_SLOT_DAC_DEFAULT_CONFIG(
            I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .clk = I2S_GPIO_UNUSED,
            .dout = BOARD_AUDIO_LEFT_DATA,
            .dout2 = BOARD_AUDIO_RIGHT_DATA,
            .invert_flags = {
                .clk_inv = false,
            },
        },
    };
    esp_err_t result = i2s_channel_init_pdm_tx_mode(s_pdm, &pdm_config);
    if (result != ESP_OK) {
        i2s_del_channel(s_pdm);
        s_pdm = NULL;
        hold_pdm_low();
        return result;
    }

    s_buffered_frames = 0;
    reset_resampler();
    uint32_t count = ramp_frames();
    uint32_t index = 0;
    for (uint32_t descriptor = 0; descriptor < PDM_DMA_DESCRIPTORS;
         ++descriptor) {
        fill_ramp(PDM_DMA_FRAMES, index, count, true);
        if (index < count) {
            uint32_t remaining = count - index;
            index += remaining > PDM_DMA_FRAMES ? PDM_DMA_FRAMES : remaining;
        }
        size_t loaded = 0;
        size_t bytes = sizeof(s_frame_buffer);
        result = i2s_channel_preload_data(s_pdm, s_frame_buffer, bytes,
                                          &loaded);
        if (result != ESP_OK || loaded != bytes) {
            i2s_del_channel(s_pdm);
            s_pdm = NULL;
            hold_pdm_low();
            return result == ESP_OK ? ESP_FAIL : result;
        }
    }

    result = i2s_channel_enable(s_pdm);
    if (result != ESP_OK) {
        i2s_del_channel(s_pdm);
        s_pdm = NULL;
        hold_pdm_low();
        return result;
    }
    s_pdm_running = true;

    while (index < count) {
        size_t chunk = count - index;
        if (chunk > PDM_DMA_FRAMES) chunk = PDM_DMA_FRAMES;
        fill_ramp(chunk, index, count, true);
        ESP_RETURN_ON_ERROR(pdm_write_block(s_frame_buffer, chunk), TAG,
                            "write stereo PDM bias ramp");
        index += chunk;
    }
    vTaskDelay(pdMS_TO_TICKS(PDM_BIAS_SETTLE_MS));

    i2s_chan_info_t channel_info = {0};
    ESP_RETURN_ON_ERROR(i2s_channel_get_info(s_pdm, &channel_info), TAG,
                        "read PDM clock");
    ESP_LOGI(TAG,
             "Stereo PDM fixed at 48000 Hz, carrier %lu Hz, L=GPIO%d R=GPIO%d",
             (unsigned long)channel_info.bclk_hz, BOARD_AUDIO_LEFT_DATA,
             BOARD_AUDIO_RIGHT_DATA);
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

static esp_err_t pdm_write_resampled(int16_t left, int16_t right) {
    if (s_input_sample_rate == PDM_OUTPUT_SAMPLE_RATE) {
        return pdm_queue_frame(left, right);
    }
    if (!s_resampler_has_previous) {
        s_resampler_has_previous = true;
        s_previous_left = left;
        s_previous_right = right;
        s_resampler_next_phase = s_input_sample_rate;
        return pdm_queue_frame(left, right);
    }

    uint32_t phase = s_resampler_next_phase;
    while (phase <= PDM_OUTPUT_SAMPLE_RATE) {
        uint32_t fraction =
            (phase * RESAMPLER_SCALE + PDM_OUTPUT_SAMPLE_RATE / 2U) /
            PDM_OUTPUT_SAMPLE_RATE;
        ESP_RETURN_ON_ERROR(
            pdm_queue_frame(interpolate_sample(s_previous_left, left, fraction),
                            interpolate_sample(s_previous_right, right,
                                               fraction)),
            TAG, "write resampled stereo PDM");
        phase += s_input_sample_rate;
    }
    s_resampler_next_phase = phase - PDM_OUTPUT_SAMPLE_RATE;
    s_previous_left = left;
    s_previous_right = right;
    return ESP_OK;
}

static esp_err_t audio_led_init(void) {
    ledc_timer_config_t timer = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_8_BIT,
        .timer_num = LEDC_TIMER_0,
        .freq_hz = 5000,
        .clk_cfg = LEDC_AUTO_CLK,
    };
    ESP_RETURN_ON_ERROR(ledc_timer_config(&timer), TAG,
                        "audio LED timer setup");
    ledc_channel_config_t channel = {
        .gpio_num = BOARD_AUDIO_LED,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0,
        .intr_type = LEDC_INTR_DISABLE,
        .timer_sel = LEDC_TIMER_0,
        .duty = BOARD_AUDIO_LED_ACTIVE_LOW ? 255 : 0,
        .hpoint = 0,
    };
    return ledc_channel_config(&channel);
}

static void audio_led_update(uint16_t peak) {
    uint8_t target = (uint8_t)(((uint32_t)peak * 255U + 16384U) / 32768U);
    if (target >= s_led_envelope) {
        s_led_envelope = target;
    } else if (s_led_envelope > 4U) {
        s_led_envelope -= 4U;
    } else {
        s_led_envelope = 0;
    }
    uint32_t duty = BOARD_AUDIO_LED_ACTIVE_LOW
                        ? 255U - s_led_envelope
                        : s_led_envelope;
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

esp_err_t native_audio_output_init(void) {
    hold_pdm_low();
    s_led_envelope = 0;
    atomic_init(&s_volume, 192);
    atomic_init(&s_balance, 0);
    return audio_led_init();
}

esp_err_t native_audio_output_configure(uint32_t input_sample_rate) {
    if (input_sample_rate < 8000U || input_sample_rate > 48000U) {
        return ESP_ERR_INVALID_ARG;
    }
    ESP_RETURN_ON_ERROR(pdm_begin(), TAG, "start fixed-rate stereo PDM");
    if (input_sample_rate != s_input_sample_rate) {
        s_input_sample_rate = input_sample_rate;
        s_buffered_frames = 0;
        reset_resampler();
        ESP_LOGI(TAG, "Stereo PDM resampler input changed to %lu Hz",
                 (unsigned long)input_sample_rate);
    }
    return ESP_OK;
}

esp_err_t native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels) {
    if (!data || bits_per_sample != 16 || channels == 0) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    size_t frame_bytes = (size_t)channels * sizeof(int16_t);
    size_t frames = size / frame_bytes;
    uint16_t peak = 0;
    uint8_t volume = atomic_load(&s_volume);
    int8_t balance = atomic_load(&s_balance);
    for (size_t frame = 0; frame < frames; ++frame) {
        int16_t left;
        int16_t right;
        decode_pcm_frame(data + frame * frame_bytes, channels, &left, &right);
        left = scale_sample(left, volume, 254);
        right = scale_sample(right, volume, 254);
        if (balance < 0) {
            right = scale_sample(right, (uint16_t)(16 + balance), 16);
        } else if (balance > 0) {
            left = scale_sample(left, (uint16_t)(16 - balance), 16);
        }
        uint16_t left_peak = left == INT16_MIN ? 32768U
                                               : (uint16_t)abs(left);
        uint16_t right_peak = right == INT16_MIN ? 32768U
                                                 : (uint16_t)abs(right);
        if (left_peak > peak) peak = left_peak;
        if (right_peak > peak) peak = right_peak;
        ESP_RETURN_ON_ERROR(pdm_write_resampled(left, right), TAG,
                            "write stereo PDM PCM");
    }
    audio_led_update(peak);
    return ESP_OK;
}

void native_audio_output_set_volume(uint8_t volume) {
    atomic_store(&s_volume, volume);
}

uint8_t native_audio_output_get_volume(void) {
    return atomic_load(&s_volume);
}

void native_audio_output_set_balance(int8_t balance) {
    if (balance < -16) balance = -16;
    if (balance > 16) balance = 16;
    atomic_store(&s_balance, balance);
}

int8_t native_audio_output_get_balance(void) {
    return atomic_load(&s_balance);
}

void native_audio_output_idle(void) {
    // DMA descriptors auto-clear to PCM zero; only the level LED must decay.
    audio_led_update(0);
}

const char *native_audio_output_name(void) {
    return "stereo I2S PDM (GPIO10/GPIO3)";
}
