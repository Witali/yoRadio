#include "native_audio_output.h"

#include <limits.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "board_config.h"
#include "driver/gpio.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

#define OUTPUT_PACKET_BYTES 3072

static const char *const TAG = "audio_output";

static int16_t pcm_mono_sample(const uint8_t *frame, uint8_t channels) {
    int16_t left;
    memcpy(&left, frame, sizeof(left));
    if (channels < 2) return left;

    int16_t right;
    memcpy(&right, frame + sizeof(right), sizeof(right));
    return (int16_t)(((int32_t)left + (int32_t)right) / 2);
}

#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM

#include "driver/i2s_pdm.h"

#define PDM_OUTPUT_SAMPLE_RATE 48000U
#define PDM_DMA_SAMPLES 512U
#define PDM_DMA_DESCRIPTORS 8U
#define PDM_BIAS_RAMP_MS 100U
#define PDM_BIAS_SETTLE_MS 2U
#define RESAMPLER_SCALE 32768U

static i2s_chan_handle_t s_pdm;
static bool s_pdm_running;
static uint32_t s_input_sample_rate;
static size_t s_buffered_samples;
static int16_t s_sample_buffer[PDM_DMA_SAMPLES];
static bool s_resampler_has_previous;
static int16_t s_resampler_previous;
static uint32_t s_resampler_next_phase;

static void hold_pdm_low(void) {
    gpio_reset_pin(BOARD_AUDIO_DATA);
    gpio_set_direction(BOARD_AUDIO_DATA, GPIO_MODE_OUTPUT);
    gpio_set_level(BOARD_AUDIO_DATA, 0);
}

static void reset_resampler(void) {
    s_resampler_has_previous = false;
    s_resampler_previous = 0;
    s_resampler_next_phase = 0;
}

static uint32_t ramp_samples(void) {
    return (PDM_OUTPUT_SAMPLE_RATE * PDM_BIAS_RAMP_MS + 999U) / 1000U;
}

static int16_t ramp_sample(uint32_t index, uint32_t count, bool ramp_up) {
    int32_t offset = (int32_t)(((uint64_t)index * 32768U) / (count - 1U));
    return (int16_t)(ramp_up ? INT16_MIN + offset : -offset);
}

static esp_err_t pdm_write_block(const int16_t *samples, size_t count) {
    if (!s_pdm || !s_pdm_running) return ESP_ERR_INVALID_STATE;
    size_t written = 0;
    size_t bytes = count * sizeof(*samples);
    esp_err_t result = i2s_channel_write(s_pdm, samples, bytes, &written,
                                         1000);
    if (result != ESP_OK) return result;
    return written == bytes ? ESP_OK : ESP_FAIL;
}

static esp_err_t pdm_flush(void) {
    if (!s_buffered_samples) return ESP_OK;
    memset(s_sample_buffer + s_buffered_samples, 0,
           (PDM_DMA_SAMPLES - s_buffered_samples) * sizeof(int16_t));
    esp_err_t result = pdm_write_block(s_sample_buffer, PDM_DMA_SAMPLES);
    s_buffered_samples = 0;
    return result;
}

static esp_err_t pdm_queue_sample(int16_t sample) {
    s_sample_buffer[s_buffered_samples++] = sample;
    if (s_buffered_samples < PDM_DMA_SAMPLES) return ESP_OK;
    esp_err_t result = pdm_write_block(s_sample_buffer, s_buffered_samples);
    s_buffered_samples = 0;
    return result;
}

static esp_err_t pdm_release(bool ramp_down) {
    esp_err_t first_error = ESP_OK;
    if (s_pdm && s_pdm_running && ramp_down) {
        esp_err_t result = pdm_flush();
        if (first_error == ESP_OK && result != ESP_OK) first_error = result;

        uint32_t count = ramp_samples();
        for (uint32_t index = 0; index < count; index += PDM_DMA_SAMPLES) {
            size_t chunk = count - index;
            if (chunk > PDM_DMA_SAMPLES) chunk = PDM_DMA_SAMPLES;
            for (size_t sample = 0; sample < chunk; ++sample) {
                s_sample_buffer[sample] =
                    ramp_sample(index + sample, count, false);
            }
            result = pdm_write_block(s_sample_buffer, chunk);
            if (first_error == ESP_OK && result != ESP_OK) first_error = result;
            if (result != ESP_OK) break;
        }
        uint32_t drain_ms =
            ((PDM_DMA_DESCRIPTORS + 1U) * PDM_DMA_SAMPLES * 1000ULL +
             PDM_OUTPUT_SAMPLE_RATE - 1U) /
            PDM_OUTPUT_SAMPLE_RATE;
        vTaskDelay(pdMS_TO_TICKS(PDM_BIAS_RAMP_MS + drain_ms +
                                PDM_BIAS_SETTLE_MS));
    }

    s_buffered_samples = 0;
    if (s_pdm && s_pdm_running) {
        esp_err_t result = i2s_channel_disable(s_pdm);
        if (first_error == ESP_OK && result != ESP_OK) first_error = result;
        s_pdm_running = false;
    }
    if (s_pdm) {
        esp_err_t result = i2s_del_channel(s_pdm);
        if (first_error == ESP_OK && result != ESP_OK) first_error = result;
        s_pdm = NULL;
    }
    s_input_sample_rate = 0;
    reset_resampler();
    hold_pdm_low();
    return first_error;
}

static esp_err_t pdm_begin(void) {
    if (s_pdm) return ESP_OK;
    i2s_chan_config_t channel_config =
        I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    channel_config.dma_desc_num = PDM_DMA_DESCRIPTORS;
    channel_config.dma_frame_num = PDM_DMA_SAMPLES;
    channel_config.auto_clear_after_cb = true;
    channel_config.auto_clear_before_cb = false;
    ESP_RETURN_ON_ERROR(i2s_new_channel(&channel_config, &s_pdm, NULL), TAG,
                        "allocate PDM channel");

    i2s_pdm_tx_config_t pdm_config = {
        .clk_cfg = I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG(PDM_OUTPUT_SAMPLE_RATE),
        .slot_cfg = I2S_PDM_TX_SLOT_DEFAULT_CONFIG(
            I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .clk = I2S_GPIO_UNUSED,
            .dout = BOARD_AUDIO_DATA,
            .invert_flags = {
                .clk_inv = false,
            },
        },
    };
    esp_err_t result = i2s_channel_init_pdm_tx_mode(s_pdm, &pdm_config);
    if (result != ESP_OK) {
        pdm_release(false);
        return result;
    }

    s_buffered_samples = 0;
    reset_resampler();

    uint32_t count = ramp_samples();
    uint32_t index = 0;
    for (uint32_t descriptor = 0; descriptor < PDM_DMA_DESCRIPTORS;
         ++descriptor) {
        for (size_t sample = 0; sample < PDM_DMA_SAMPLES; ++sample) {
            s_sample_buffer[sample] = index < count
                                          ? ramp_sample(index++, count, true)
                                          : 0;
        }
        size_t loaded = 0;
        result = i2s_channel_preload_data(s_pdm, s_sample_buffer,
                                          sizeof(s_sample_buffer), &loaded);
        if (result != ESP_OK || loaded != sizeof(s_sample_buffer)) {
            pdm_release(false);
            return result == ESP_OK ? ESP_FAIL : result;
        }
    }

    result = i2s_channel_enable(s_pdm);
    if (result != ESP_OK) {
        pdm_release(false);
        return result;
    }
    s_pdm_running = true;

    while (index < count) {
        size_t chunk = count - index;
        if (chunk > PDM_DMA_SAMPLES) chunk = PDM_DMA_SAMPLES;
        for (size_t sample = 0; sample < chunk; ++sample) {
            s_sample_buffer[sample] = ramp_sample(index + sample, count, true);
        }
        ESP_RETURN_ON_ERROR(pdm_write_block(s_sample_buffer, chunk), TAG,
                            "write PDM bias ramp");
        index += chunk;
    }
    vTaskDelay(pdMS_TO_TICKS(PDM_BIAS_SETTLE_MS));

    i2s_chan_info_t channel_info = {0};
    ESP_RETURN_ON_ERROR(i2s_channel_get_info(s_pdm, &channel_info), TAG,
                        "read PDM clock");
    ESP_LOGI(TAG, "PDM fixed at 48000 Hz, carrier %lu Hz on GPIO%d",
             (unsigned long)channel_info.bclk_hz, BOARD_AUDIO_DATA);
    return ESP_OK;
}

static esp_err_t pdm_write_resampled(int16_t sample) {
    if (s_input_sample_rate == PDM_OUTPUT_SAMPLE_RATE) {
        return pdm_queue_sample(sample);
    }
    if (!s_resampler_has_previous) {
        s_resampler_has_previous = true;
        s_resampler_previous = sample;
        s_resampler_next_phase = s_input_sample_rate;
        return pdm_queue_sample(sample);
    }

    uint32_t phase = s_resampler_next_phase;
    int32_t delta = (int32_t)sample - s_resampler_previous;
    while (phase <= PDM_OUTPUT_SAMPLE_RATE) {
        uint32_t fraction =
            (phase * RESAMPLER_SCALE + PDM_OUTPUT_SAMPLE_RATE / 2U) /
            PDM_OUTPUT_SAMPLE_RATE;
        int32_t scaled = delta * (int32_t)fraction;
        scaled += scaled >= 0 ? RESAMPLER_SCALE / 2U
                              : -(int32_t)(RESAMPLER_SCALE / 2U);
        int16_t interpolated = (int16_t)(
            (int32_t)s_resampler_previous + scaled / (int32_t)RESAMPLER_SCALE);
        ESP_RETURN_ON_ERROR(pdm_queue_sample(interpolated), TAG,
                            "write resampled PDM");
        phase += s_input_sample_rate;
    }
    s_resampler_next_phase = phase - PDM_OUTPUT_SAMPLE_RATE;
    s_resampler_previous = sample;
    return ESP_OK;
}

esp_err_t native_audio_output_init(void) {
    hold_pdm_low();
    return ESP_OK;
}

esp_err_t native_audio_output_configure(uint32_t input_sample_rate) {
    if (input_sample_rate < 8000U || input_sample_rate > 48000U) {
        return ESP_ERR_INVALID_ARG;
    }
    ESP_RETURN_ON_ERROR(pdm_begin(), TAG, "start fixed-rate PDM");
    if (input_sample_rate != s_input_sample_rate) {
        s_input_sample_rate = input_sample_rate;
        s_buffered_samples = 0;
        reset_resampler();
        ESP_LOGI(TAG, "PDM resampler input changed to %lu Hz",
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
    for (size_t frame = 0; frame < frames; ++frame) {
        ESP_RETURN_ON_ERROR(
            pdm_write_resampled(pcm_mono_sample(data + frame * frame_bytes,
                                                channels)),
            TAG, "write PDM PCM");
    }
    return ESP_OK;
}

void native_audio_output_idle(void) {
    // DMA descriptors are cleared after transmission, producing PCM zero on
    // an underrun instead of repeating the last block.
}

const char *native_audio_output_name(void) {
    return "I2S PDM";
}

#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC

#include "driver/dac_continuous.h"

static dac_continuous_handle_t s_dac;
static uint32_t s_dac_sample_rate;
static uint8_t *s_dac_data;

esp_err_t native_audio_output_init(void) {
    s_dac_data = malloc(OUTPUT_PACKET_BYTES);
    return s_dac_data ? ESP_OK : ESP_ERR_NO_MEM;
}

esp_err_t native_audio_output_configure(uint32_t input_sample_rate) {
    if (s_dac && input_sample_rate == s_dac_sample_rate) return ESP_OK;
    if (s_dac) {
        dac_continuous_disable(s_dac);
        dac_continuous_del_channels(s_dac);
        s_dac = NULL;
    }
    dac_continuous_config_t config = {
        .chan_mask = DAC_CHANNEL_MASK_CH1,
        .desc_num = 6,
        .buf_size = 1024,
        .freq_hz = input_sample_rate,
        .offset = 0,
        .clk_src = DAC_DIGI_CLK_SRC_APLL,
        .chan_mode = DAC_CHANNEL_MODE_SIMUL,
    };
    ESP_RETURN_ON_ERROR(dac_continuous_new_channels(&config, &s_dac), TAG,
                        "allocate DAC channel");
    ESP_RETURN_ON_ERROR(dac_continuous_enable(s_dac), TAG, "enable DAC");
    s_dac_sample_rate = input_sample_rate;
    memset(s_dac_data, 0x80, 1024);
    size_t written = 0;
    return dac_continuous_write(s_dac, s_dac_data, 1024, &written, 1000);
}

esp_err_t native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels) {
    if (!data || bits_per_sample != 16 || channels == 0) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    size_t frame_bytes = (size_t)channels * sizeof(int16_t);
    size_t frames = size / frame_bytes;
    if (frames > OUTPUT_PACKET_BYTES) frames = OUTPUT_PACKET_BYTES;
    for (size_t frame = 0; frame < frames; ++frame) {
        int32_t value = (pcm_mono_sample(data + frame * frame_bytes, channels)
                         >> 8) + 128;
        if (value < 0) value = 0;
        if (value > 255) value = 255;
        s_dac_data[frame] = (uint8_t)value;
    }
    size_t written = 0;
    return dac_continuous_write(s_dac, s_dac_data, frames, &written, 1000);
}

void native_audio_output_idle(void) {
    if (!s_dac) return;
    memset(s_dac_data, 0x80, 256);
    size_t written = 0;
    dac_continuous_write(s_dac, s_dac_data, 256, &written, 100);
}

const char *native_audio_output_name(void) {
    return "internal DAC";
}

#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC

#include "idf6_i2s_compat.h"

#define LEGACY_DMA_DESCRIPTORS 8
#define LEGACY_DMA_FRAMES 512
#define LEGACY_OUTPUT_BYTES (OUTPUT_PACKET_BYTES * 2)

static bool s_legacy_installed;
static uint32_t s_legacy_sample_rate;
static uint32_t *s_legacy_frames;

static esp_err_t legacy_write_silence(size_t frames) {
    size_t capacity = LEGACY_OUTPUT_BYTES / sizeof(uint32_t);
    for (size_t index = 0; index < capacity; ++index) {
        s_legacy_frames[index] = 0x80008000UL;
    }
    while (frames) {
        size_t chunk = frames > capacity ? capacity : frames;
        size_t written = 0;
        esp_err_t result = idf6_dac_output_write(
            s_legacy_frames, chunk * sizeof(uint32_t), &written,
            pdMS_TO_TICKS(1000));
        if (result != ESP_OK) return result;
        if (written != chunk * sizeof(uint32_t)) return ESP_FAIL;
        frames -= chunk;
    }
    return ESP_OK;
}

esp_err_t native_audio_output_init(void) {
    s_legacy_frames = malloc(LEGACY_OUTPUT_BYTES);
    return s_legacy_frames ? ESP_OK : ESP_ERR_NO_MEM;
}

esp_err_t native_audio_output_configure(uint32_t input_sample_rate) {
    if (!input_sample_rate) return ESP_ERR_INVALID_ARG;
    if (s_legacy_installed) {
        if (input_sample_rate == s_legacy_sample_rate) return ESP_OK;
        ESP_RETURN_ON_ERROR(idf6_dac_output_set_sample_rate(input_sample_rate),
                            TAG, "set legacy DAC clock");
        s_legacy_sample_rate = input_sample_rate;
        return ESP_OK;
    }

    i2s_config_t config = {
        .mode = I2S_MODE_MASTER | I2S_MODE_TX | I2S_MODE_DAC_BUILT_IN,
        .sample_rate = input_sample_rate,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_MSB,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = LEGACY_DMA_DESCRIPTORS,
        .dma_buf_len = LEGACY_DMA_FRAMES,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = I2S_PIN_NO_CHANGE,
    };
    ESP_RETURN_ON_ERROR(
        idf6_dac_output_configure(&config, I2S_DAC_CHANNEL_LEFT_EN), TAG,
        "configure legacy DAC adapter");
    ESP_RETURN_ON_ERROR(idf6_dac_output_begin(), TAG,
                        "start legacy DAC adapter");
    s_legacy_installed = true;
    s_legacy_sample_rate = input_sample_rate;
    ESP_RETURN_ON_ERROR(
        legacy_write_silence(LEGACY_DMA_DESCRIPTORS * LEGACY_DMA_FRAMES), TAG,
        "prime legacy DAC with midpoint");
    ESP_LOGI(TAG, "Legacy ESP-IDF 5.5 I2S/DAC at %lu Hz on GPIO26",
             (unsigned long)input_sample_rate);
    return ESP_OK;
}

esp_err_t native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels) {
    if (!data || !s_legacy_installed || bits_per_sample != 16 ||
        channels == 0) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    size_t frame_bytes = (size_t)channels * sizeof(int16_t);
    size_t frames = size / frame_bytes;
    size_t capacity = LEGACY_OUTPUT_BYTES / sizeof(uint32_t);
    if (frames > capacity) frames = capacity;
    for (size_t frame = 0; frame < frames; ++frame) {
        uint16_t unsigned_sample = (uint16_t)(
            (int32_t)pcm_mono_sample(data + frame * frame_bytes, channels) +
            32768);
        s_legacy_frames[frame] =
            ((uint32_t)unsigned_sample << 16) | unsigned_sample;
    }
    size_t written = 0;
    esp_err_t result = idf6_dac_output_write(
        s_legacy_frames, frames * sizeof(uint32_t), &written,
        pdMS_TO_TICKS(1000));
    if (result != ESP_OK) return result;
    return written == frames * sizeof(uint32_t) ? ESP_OK : ESP_FAIL;
}

void native_audio_output_idle(void) {
    if (s_legacy_installed) legacy_write_silence(128);
}

const char *native_audio_output_name(void) {
    return "legacy I2S/DAC";
}

#else
#error Select a yoRadio native audio output backend
#endif
