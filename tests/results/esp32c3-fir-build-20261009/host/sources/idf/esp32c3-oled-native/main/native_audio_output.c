#include "native_audio_output.h"

#include <limits.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#include "audio_level_led.h"
#include "board_config.h"
#include "driver/gpio.h"
#include "driver/i2s_pdm.h"
#include "esp_check.h"
#include "esp_attr.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_audio_normalizer.h"
#include "native_audio_settings.h"
#include "soc/soc_caps.h"

#ifdef CONFIG_YORADIO_PDM_INTEGER_FIR
#ifndef CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION
#error FIR requires the audited integer-rate compensation configuration
#endif
#include "native_pcm_fir.h"
static pcm_fir_state_t s_pcm_fir;
#endif

#if SOC_I2S_PDM_MAX_TX_LINES < 2
#error ESP32-C3 stereo PDM requires two hardware TX data lines
#endif

#define PDM_OUTPUT_SAMPLE_RATE 48000U
#define PDM_DMA_FRAMES 512U
#define PDM_DMA_DESCRIPTORS 4U
#define PDM_BIAS_RAMP_MS 100U
#define PDM_BIAS_SETTLE_MS 2U
#define RESAMPLER_SCALE 32768U
#define RESAMPLER_FRACTION_MULTIPLIER_Q16 44739U
#ifdef CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION
#ifdef CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK
#error Integer-rate compensation must not be combined with the fractional PDM clock
#endif
// The audited integer DAC clock is 160 MHz / (2 * 13 * 128) = 625000/13 Hz.
// Keep rational phase units so every input rate follows that clock without
// a cumulative sample-count error or a new buffer. The driver validates it.
#define RESAMPLER_OUTPUT_RATE_NUMERATOR 625000U
#define RESAMPLER_OUTPUT_RATE_DENOMINATOR 13U
#define RESAMPLER_FRACTION_MULTIPLIER_Q32 225179981U
#else
#define RESAMPLER_OUTPUT_RATE_NUMERATOR PDM_OUTPUT_SAMPLE_RATE
#define RESAMPLER_OUTPUT_RATE_DENOMINATOR 1U
#endif
#define SAMPLE_GAIN_SCALE 32768U
#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U
#define OUTPUT_STATS_INTERVAL_US 5000000LL

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
static int64_t s_stats_started_us;
static uint64_t s_stats_audio_us;
static uint64_t s_stats_normalize_us;
static uint32_t s_stats_packets;

#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
static DRAM_ATTR volatile uint32_t s_dma_overruns;
static struct {
    uint64_t written_bytes, write_us, max_write_us;
    uint32_t writes, errors;
} s_dma_write_profile;

static bool IRAM_ATTR dma_queue_overrun(i2s_chan_handle_t channel,
    i2s_event_data_t *event, void *context) {
    (void)channel;
    (void)event;
    (void)context;
    // One ISR writer; never reset from the output task. No logging, heap,
    // clock access or atomic library calls while servicing the interrupt.
    ++s_dma_overruns;
    return false;
}

uint32_t native_audio_output_dma_overruns(void) {
    return s_dma_overruns;
}

static void staged_dma_report(void) {
    ESP_LOGI(TAG,
        "PERF STAGED_DMA: q_overruns=%lu writes=%lu written_bytes=%llu "
        "write_us=%llu max_write_us=%llu errors=%lu",
        (unsigned long)s_dma_overruns, (unsigned long)s_dma_write_profile.writes,
        (unsigned long long)s_dma_write_profile.written_bytes,
        (unsigned long long)s_dma_write_profile.write_us,
        (unsigned long long)s_dma_write_profile.max_write_us,
        (unsigned long)s_dma_write_profile.errors);
}
#endif

typedef struct {
    bool valid;
    bool enabled;
    uint8_t max_gain_db;
    int8_t target_dbfs;
    uint16_t time_ms;
    uint32_t sample_rate;
} normalizer_config_cache_t;

static normalizer_config_cache_t s_normalizer_config;
static atomic_bool s_normalizer_reset_pending = ATOMIC_VAR_INIT(false);

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
#ifdef CONFIG_YORADIO_PDM_INTEGER_FIR
    pcm_fir_reset(&s_pcm_fir);
#endif
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
                            : (ramp_up ? 0 : INT16_MIN);
        s_frame_buffer[frame * 2] = value;
        s_frame_buffer[frame * 2 + 1] = value;
    }
}

static esp_err_t pdm_write_block(const int16_t *samples, size_t frames) {
    if (!s_pdm || !s_pdm_running) return ESP_ERR_INVALID_STATE;
    size_t written = 0;
    size_t bytes = frames * 2U * sizeof(*samples);
#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
    int64_t started_us = esp_timer_get_time();
#endif
    esp_err_t result = i2s_channel_write(s_pdm, samples, bytes, &written, 1000);
#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
    uint64_t elapsed_us = (uint64_t)(esp_timer_get_time() - started_us);
    ++s_dma_write_profile.writes;
    s_dma_write_profile.written_bytes += written;
    s_dma_write_profile.write_us += elapsed_us;
    if (elapsed_us > s_dma_write_profile.max_write_us) {
        s_dma_write_profile.max_write_us = elapsed_us;
    }
    if (result != ESP_OK || written != bytes) ++s_dma_write_profile.errors;
#endif
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
#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
    if (result == ESP_OK) {
        const i2s_event_callbacks_t callbacks = {
            .on_send_q_ovf = dma_queue_overrun,
        };
        result = i2s_channel_register_event_callback(s_pdm, &callbacks, NULL);
    }
#endif
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

#ifndef CONFIG_YORADIO_PDM_INTEGER_FIR
static int16_t interpolate_sample(int16_t previous, int16_t current,
                                  uint32_t fraction) {
    int32_t delta = (int32_t)current - previous;
    int32_t scaled = delta * (int32_t)fraction;
    scaled += scaled >= 0 ? RESAMPLER_SCALE / 2U
                          : -(int32_t)(RESAMPLER_SCALE / 2U);
    return (int16_t)((int32_t)previous +
                     scaled / (int32_t)RESAMPLER_SCALE);
}
#endif

static esp_err_t pdm_write_resampled(int16_t left, int16_t right) {
#ifdef CONFIG_YORADIO_PDM_INTEGER_FIR
    return pcm_fir_push(&s_pcm_fir, left, right,
                        s_input_sample_rate * PCM_FIR_RATE_DENOMINATOR,
                        false, pdm_queue_frame);
#else
    const uint32_t input_step =
        s_input_sample_rate * RESAMPLER_OUTPUT_RATE_DENOMINATOR;
    if (input_step == RESAMPLER_OUTPUT_RATE_NUMERATOR) {
        return pdm_queue_frame(left, right);
    }
    if (!s_resampler_has_previous) {
        s_resampler_has_previous = true;
        s_previous_left = left;
        s_previous_right = right;
        s_resampler_next_phase = input_step;
        return pdm_queue_frame(left, right);
    }

    uint32_t phase = s_resampler_next_phase;
    while (phase <= RESAMPLER_OUTPUT_RATE_NUMERATOR) {
#ifdef CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION
        // round(phase * 32768 / 625000). A rounded Q32 reciprocal uses the
        // high half of the RV32 multiply, without a per-frame division.
        uint32_t fraction = (uint32_t)(
            ((uint64_t)phase * RESAMPLER_FRACTION_MULTIPLIER_Q32 +
             (UINT64_C(1) << 31)) >> 32);
#else
        // round(phase * 32768 / 48000), using a Q16 reciprocal. This hot path
        // runs once per 48 kHz output frame, so avoid a hardware division.
        uint32_t fraction =
            (phase * RESAMPLER_FRACTION_MULTIPLIER_Q16 + 32768U) >> 16;
#endif
        ESP_RETURN_ON_ERROR(
            pdm_queue_frame(interpolate_sample(s_previous_left, left, fraction),
                            interpolate_sample(s_previous_right, right,
                                               fraction)),
            TAG, "write resampled stereo PDM");
        phase += input_step;
    }
    s_resampler_next_phase = phase - RESAMPLER_OUTPUT_RATE_NUMERATOR;
    s_previous_left = left;
    s_previous_right = right;
    return ESP_OK;
#endif
}

esp_err_t native_audio_output_init(void) {
    hold_pdm_low();
    // Reserve the I2S channel and its DMA descriptors before the compressed
    // stream ring, decoder workspace, and TLS record buffers fragment the
    // small internal heap. The 48 kHz PDM resource remains allocated across
    // station changes; configure() only updates the source-rate resampler.
    ESP_RETURN_ON_ERROR(pdm_begin(), TAG, "reserve fixed-rate stereo PDM");
    return ESP_OK;
}

esp_err_t native_audio_output_configure(uint32_t input_sample_rate) {
    if (input_sample_rate < 8000U || input_sample_rate > 48000U) {
        return ESP_ERR_INVALID_ARG;
    }
    ESP_RETURN_ON_ERROR(pdm_begin(), TAG, "start fixed-rate stereo PDM");
    if (input_sample_rate != s_input_sample_rate) {
        ESP_RETURN_ON_ERROR(native_audio_output_flush_pcm(), TAG, "flush old PCM rate");
        s_input_sample_rate = input_sample_rate;
        reset_resampler();
        native_audio_normalizer_set_sample_rate(input_sample_rate);
        ESP_LOGI(TAG, "Stereo PDM resampler input changed to %lu Hz",
                 (unsigned long)input_sample_rate);
    }
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

void native_audio_output_request_normalizer_reset(void) {
    if (native_audio_settings_get_normalization()) {
        atomic_store(&s_normalizer_reset_pending, true);
    }
}

esp_err_t native_audio_output_write_pcm(uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels) {
    if (!data || bits_per_sample != 16 || channels == 0) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    sync_normalizer_configuration();
    if (atomic_exchange(&s_normalizer_reset_pending, false)) {
        native_audio_normalizer_reset();
    }

    size_t frame_bytes = (size_t)channels * sizeof(int16_t);
    size_t frames = size / frame_bytes;
    int64_t normalize_started_us = esp_timer_get_time();
    native_audio_normalizer_process_block((int16_t *)data, frames, channels);
    uint64_t normalize_us =
        (uint64_t)(esp_timer_get_time() - normalize_started_us);
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
        uint16_t left_peak = left == INT16_MIN ? 32768U
                                               : (uint16_t)abs(left);
        uint16_t right_peak = right == INT16_MIN ? 32768U
                                                 : (uint16_t)abs(right);
        if (left_peak > peak) peak = left_peak;
        if (right_peak > peak) peak = right_peak;
        ESP_RETURN_ON_ERROR(pdm_write_resampled(left, right), TAG,
                            "write stereo PDM PCM");
    }
    audio_level_led_update_peak(peak);
    int64_t now_us = esp_timer_get_time();
    if (!s_stats_started_us) s_stats_started_us = now_us;
    s_stats_audio_us += frames * 1000000ULL / s_input_sample_rate;
    s_stats_normalize_us += normalize_us;
    ++s_stats_packets;
    if (now_us - s_stats_started_us >= OUTPUT_STATS_INTERVAL_US) {
        uint64_t tenths = s_stats_audio_us
                              ? s_stats_normalize_us * 1000ULL /
                                    s_stats_audio_us
                              : 0;
        ESP_LOGI(TAG,
                 "PERF PCM: audio %llu ms, normalize %llu ms (%llu.%llu%%), "
                 "packets %lu",
                 (unsigned long long)(s_stats_audio_us / 1000ULL),
                 (unsigned long long)(s_stats_normalize_us / 1000ULL),
                 (unsigned long long)(tenths / 10ULL),
                 (unsigned long long)(tenths % 10ULL),
                 (unsigned long)s_stats_packets);
#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
        staged_dma_report();
#endif
        s_stats_started_us = now_us;
        s_stats_audio_us = 0;
        s_stats_normalize_us = 0;
        s_stats_packets = 0;
    }
    return ESP_OK;
}

void native_audio_output_set_volume(uint8_t volume) {
    esp_err_t result = native_audio_settings_set_volume(volume);
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Schedule volume save failed: %s",
                 esp_err_to_name(result));
    }
}

uint8_t native_audio_output_get_volume(void) {
    return native_audio_settings_get_volume();
}

void native_audio_output_set_balance(int8_t balance) {
    esp_err_t result = native_audio_settings_set_balance(balance);
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Balance save failed: %s", esp_err_to_name(result));
    }
}

int8_t native_audio_output_get_balance(void) {
    return native_audio_settings_get_balance();
}

void native_audio_output_discard_pcm(void) {
    s_buffered_frames = 0;
    reset_resampler();
}

esp_err_t native_audio_output_flush_pcm(void) {
    esp_err_t result = ESP_OK;
#ifdef CONFIG_YORADIO_PDM_INTEGER_FIR
    result = pcm_fir_drain(&s_pcm_fir,
                           s_input_sample_rate * PCM_FIR_RATE_DENOMINATOR,
                           pdm_queue_frame);
    if (result != ESP_OK) {
        s_buffered_frames = 0;
        reset_resampler();
    }
#endif
    size_t tail_frames = s_buffered_frames;
    if (tail_frames) {
        // The output task is the sole owner. Consume this tail once, even on
        // a partial/failed driver write, so a later stream cannot replay it.
        memset(s_frame_buffer + tail_frames * 2U, 0,
               (PDM_DMA_FRAMES - tail_frames) * 2U * sizeof(*s_frame_buffer));
        s_buffered_frames = 0;
        result = pdm_write_block(s_frame_buffer, PDM_DMA_FRAMES);
        if (result != ESP_OK) reset_resampler();
    }
#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
    ESP_LOGI(TAG, "PERF PCM_FLUSH: frames=%lu result=%d",
             (unsigned long)tail_frames, (int)result);
    staged_dma_report();
#endif
    return result;
}

void native_audio_output_idle(void) {
    // DMA descriptors auto-clear to PCM zero; only the level LED must decay.
    audio_level_led_update_peak(0);
}

esp_err_t native_audio_output_suspend(void) {
    if (!s_pdm) return ESP_OK;
    s_buffered_frames = 0;
#ifdef CONFIG_YORADIO_PDM_INTEGER_FIR
    pcm_fir_reset(&s_pcm_fir);
#endif
    uint32_t count = ramp_frames();
    for (uint32_t first = 0; first < count; first += PDM_DMA_FRAMES) {
        fill_ramp(PDM_DMA_FRAMES, first, count, false);
        ESP_RETURN_ON_ERROR(pdm_write_block(s_frame_buffer, PDM_DMA_FRAMES),
                            TAG, "sleep bias ramp");
    }
    // Pad with constant-low PDM. Stop while this tail is still queued so
    // DMA auto-clear cannot restore 50% duty after the downward ramp.
    fill_ramp(PDM_DMA_FRAMES, count, count, false);
    for (unsigned tail = 0; tail < 2; ++tail) {
        ESP_RETURN_ON_ERROR(pdm_write_block(s_frame_buffer, PDM_DMA_FRAMES),
                            TAG, "sleep bias tail");
    }
    vTaskDelay(pdMS_TO_TICKS((PDM_DMA_DESCRIPTORS - 2U) * PDM_DMA_FRAMES *
                              1000U / PDM_OUTPUT_SAMPLE_RATE +
                              PDM_BIAS_SETTLE_MS));
    ESP_RETURN_ON_ERROR(i2s_channel_disable(s_pdm), TAG, "stop PDM for sleep");
    s_pdm_running = false;
    ESP_ERROR_CHECK(i2s_del_channel(s_pdm));
    s_pdm = NULL;
    hold_pdm_low();
    return ESP_OK;
}

const char *native_audio_output_name(void) {
    return "stereo I2S PDM (GPIO10/GPIO3)";
}
