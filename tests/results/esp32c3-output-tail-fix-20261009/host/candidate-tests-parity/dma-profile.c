#include "stubs.h"
#define CONFIG_YORADIO_DIRECT_DMA_PCM 1
#define CONFIG_YORADIO_PIPELINE_PROFILE 1
#pragma once

// Task-local wall time, including time spent ready but preempted. These are
// queue-availability observations, not FreeRTOS blocked CPU-cycle counters.
typedef struct {
    uint64_t us;
    uint32_t count, timeouts, max_us;
} pipeline_wait_t;

static inline void pipeline_wait_record(pipeline_wait_t *stats,
                                        uint32_t us, bool timeout) {
    stats->us += us;
    ++stats->count;
    stats->timeouts += timeout;
    if (us > stats->max_us) stats->max_us = us;
}
#pragma once



#if defined(CONFIG_YORADIO_PIPELINE_PROFILE) || defined(CONFIG_YORADIO_STAGED_DMA_PROFILE)
// Monotonic counter; one ISR writer, aligned word read on the single-core C3.
// Queue overrun means a completed descriptor was discarded before reuse.
uint32_t native_audio_output_dma_overruns(void);
#endif

#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
// Embedded in the PCM queue item. The output task owns the item until release;
// neither the decoder nor the DMA ISR may modify it during this interval.
typedef struct native_audio_pcm_lease native_audio_pcm_lease_t;
struct native_audio_pcm_lease {
    native_audio_pcm_lease_t *next;
    void (*release)(native_audio_pcm_lease_t *);
    const uint8_t *data;
    size_t frame_bytes, output_frames;
    uint32_t left_gain, right_gain;
    uint16_t peak;
    uint8_t channels;
    bool current_valid;
    int16_t left, right;
};
esp_err_t native_audio_output_submit_pcm(native_audio_pcm_lease_t *lease,
    uint8_t *data, size_t size, uint8_t bits_per_sample, uint8_t channels,
    void (*release)(native_audio_pcm_lease_t *));
#endif

// Owned by the output task. Flush submits a zero-padded final DMA block; it
// does not wait for the hardware to play it. Discard drops software PCM
// and resampler history on Stop/new stream without draining old samples.
esp_err_t native_audio_output_flush_pcm(void);
void native_audio_output_discard_pcm(void);

esp_err_t native_audio_output_init(void);
esp_err_t native_audio_output_configure(uint32_t input_sample_rate);
esp_err_t native_audio_output_write_pcm(uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels);
void native_audio_output_set_volume(uint8_t volume);
uint8_t native_audio_output_get_volume(void);
void native_audio_output_set_balance(int8_t balance);
int8_t native_audio_output_get_balance(void);
void native_audio_output_request_normalizer_reset(void);
void native_audio_output_idle(void);
esp_err_t native_audio_output_suspend(void);
const char *native_audio_output_name(void);
#define native_i2s_write_generated tested_i2s_write_generated
#define native_i2s_write_full_block tested_i2s_write_full_block
// DMA acquisition adapted from ESP-IDF 6.0.2 i2s_common.c.
// SPDX-FileCopyrightText: 2022-2026 Espressif Systems (Shanghai) CO LTD
// SPDX-License-Identifier: Apache-2.0

#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
static pipeline_wait_t s_dma_wait;

pipeline_wait_t native_i2s_take_wait_profile(void) {
    pipeline_wait_t result = s_dma_wait;
    s_dma_wait = (pipeline_wait_t){0};
    return result;
}
#endif

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
            BaseType_t received;
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
            received = xQueueReceive(channel->msg_queue, &channel->dma.curr_ptr, 0);
            if (received != pdTRUE && !preload) {
                int64_t start = esp_timer_get_time();
                received = xQueueReceive(channel->msg_queue, &channel->dma.curr_ptr, timeout);
                pipeline_wait_record(&s_dma_wait,
                    (uint32_t)(esp_timer_get_time() - start), received != pdTRUE);
            }
#else
            received = xQueueReceive(channel->msg_queue, &channel->dma.curr_ptr,
                                       preload ? 0 : timeout);
#endif
            if (received != pdTRUE) {
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

#undef native_i2s_write_generated
#undef native_i2s_write_full_block



#if SOC_I2S_PDM_MAX_TX_LINES < 2
#error ESP32-C3 stereo PDM requires two hardware TX data lines
#endif

#define PDM_OUTPUT_SAMPLE_RATE 48000U
#define PDM_DMA_FRAMES 512U
#define PDM_DMA_DESCRIPTORS 4U
#define PDM_START_BLOCKS 3U
#define PDM_START_MAX_WAIT_US 32000LL
#define PDM_BIAS_RAMP_MS 100U
#define PDM_BIAS_SETTLE_MS 2U
#define RESAMPLER_SCALE 32768U
#define RESAMPLER_FRACTION_MULTIPLIER_Q16 44739U
#define SAMPLE_GAIN_SCALE 32768U
#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U
#define OUTPUT_STATS_INTERVAL_US 5000000LL

static const char *const TAG = "audio_output";
static i2s_chan_handle_t s_pdm;
static bool s_pdm_running;
static uint32_t s_input_sample_rate;
static bool s_resampler_has_previous;
static int16_t s_previous_left;
static int16_t s_previous_right;
static uint32_t s_resampler_next_phase;
static int64_t s_stats_started_us;
static uint64_t s_stats_audio_us;
static uint64_t s_stats_normalize_us;
static uint32_t s_stats_packets;

#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
static DRAM_ATTR volatile uint32_t s_dma_overruns;

static bool IRAM_ATTR dma_queue_overrun(i2s_chan_handle_t channel,
    i2s_event_data_t *event, void *context) {
    (void)channel;
    (void)event;
    (void)context;
    // No atomic RMW helper, logging, clock or allocation in the ISR. Only this
    // ISR writes the counter; the output task never resets it.
    ++s_dma_overruns;
    return false;
}

uint32_t native_audio_output_dma_overruns(void) {
    return s_dma_overruns;
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

typedef struct { uint32_t first, count; bool up; } ramp_context_t;
static void fill_ramp(void *context, int16_t *dma, size_t frames) {
    ramp_context_t *ramp = context;
    for (size_t frame = 0; frame < frames; ++frame) {
        int16_t value = ramp->first < ramp->count
                            ? ramp_sample(ramp->first, ramp->count, ramp->up)
                            : (ramp->up ? 0 : INT16_MIN);
        dma[frame * 2] = value;
        dma[frame * 2 + 1] = value;
        ++ramp->first;
    }
}

static esp_err_t pdm_generate(size_t frames, native_i2s_fill_t fill,
                               void *context, bool preload) {
    if (!s_pdm || (!preload && !s_pdm_running)) return ESP_ERR_INVALID_STATE;
    size_t written = 0;
    esp_err_t result = native_i2s_write_generated(s_pdm, frames, fill, context,
                                                   preload, &written);
    if (result != ESP_OK) return result;
    return written == frames ? ESP_OK : ESP_FAIL;
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
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
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

    reset_resampler();
    uint32_t count = ramp_frames();
    ramp_context_t ramp = {.count = count, .up = true};
    for (uint32_t descriptor = 0; descriptor < PDM_DMA_DESCRIPTORS;
         ++descriptor) {
        result = pdm_generate(PDM_DMA_FRAMES, fill_ramp, &ramp, true);
        if (result != ESP_OK) {
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

    while (ramp.first < count) {
        size_t chunk = count - ramp.first;
        if (chunk > PDM_DMA_FRAMES) chunk = PDM_DMA_FRAMES;
        ESP_RETURN_ON_ERROR(pdm_generate(chunk, fill_ramp, &ramp, false), TAG,
                            "write stereo PDM bias ramp");
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

typedef native_audio_pcm_lease_t pcm_context_t;
static pcm_context_t *s_pending_head, *s_pending_tail;
static size_t s_pending_frames;
static bool s_stream_started;
static int64_t s_prefill_started_us;
static bool s_predicted_previous;
static uint32_t s_predicted_phase;

static void read_scaled_frame(pcm_context_t *pcm) {
    decode_pcm_frame(pcm->data, pcm->channels, &pcm->left, &pcm->right);
    pcm->data += pcm->frame_bytes;
    pcm->left = scale_sample_q15(pcm->left, pcm->left_gain);
    pcm->right = scale_sample_q15(pcm->right, pcm->right_gain);
    uint16_t left_peak = pcm->left == INT16_MIN ? 32768U : (uint16_t)abs(pcm->left);
    uint16_t right_peak = pcm->right == INT16_MIN ? 32768U : (uint16_t)abs(pcm->right);
    if (left_peak > pcm->peak) pcm->peak = left_peak;
    if (right_peak > pcm->peak) pcm->peak = right_peak;
}

static size_t resampled_frames(size_t input_frames) {
    if (!input_frames || s_input_sample_rate == PDM_OUTPUT_SAMPLE_RATE) return input_frames;
    size_t first = s_resampler_has_previous ? 0 : 1;
    uint32_t phase = s_resampler_has_previous ? s_resampler_next_phase : s_input_sample_rate;
    uint64_t end = (uint64_t)(input_frames - first) * PDM_OUTPUT_SAMPLE_RATE;
    return first + (end >= phase ? (end - phase) / s_input_sample_rate + 1 : 0);
}

static void fill_pcm(void *context, int16_t *dma, size_t frames) {
    pcm_context_t *pcm = context;
    for (size_t frame = 0; frame < frames; ++frame) {
        if (!pcm->current_valid) {
            read_scaled_frame(pcm);
            pcm->current_valid = true;
        }
        int16_t left = pcm->left, right = pcm->right;
        if (s_input_sample_rate == PDM_OUTPUT_SAMPLE_RATE) {
            pcm->current_valid = false;
        } else if (!s_resampler_has_previous) {
            s_resampler_has_previous = true;
            s_previous_left = left;
            s_previous_right = right;
            s_resampler_next_phase = s_input_sample_rate;
            pcm->current_valid = false;
        } else {
            uint32_t fraction = (s_resampler_next_phase *
                RESAMPLER_FRACTION_MULTIPLIER_Q16 + 32768U) >> 16;
            left = interpolate_sample(s_previous_left, pcm->left, fraction);
            right = interpolate_sample(s_previous_right, pcm->right, fraction);
            s_resampler_next_phase += s_input_sample_rate;
            if (s_resampler_next_phase > PDM_OUTPUT_SAMPLE_RATE) {
                s_resampler_next_phase -= PDM_OUTPUT_SAMPLE_RATE;
                s_previous_left = pcm->left;
                s_previous_right = pcm->right;
                pcm->current_valid = false;
            }
        }
        dma[frame * 2] = left;
        dma[frame * 2 + 1] = right;
    }
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
        s_predicted_previous = false;
        s_predicted_phase = 0;
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

static esp_err_t prepare_pcm(pcm_context_t *pcm, uint8_t *data, size_t size,
                              uint8_t bits_per_sample, uint8_t channels) {
    if (!data || bits_per_sample != 16 || channels == 0 || !s_input_sample_rate ||
        size % ((size_t)channels * sizeof(int16_t))) {
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
    *pcm = (pcm_context_t){.data = data, .frame_bytes = frame_bytes,
        .channels = channels, .left_gain = left_gain_q15, .right_gain = right_gain_q15};
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
        s_stats_started_us = now_us;
        s_stats_audio_us = 0;
        s_stats_normalize_us = 0;
        s_stats_packets = 0;
    }
    return ESP_OK;
}

// Gather original PCM queue items until a complete DMA descriptor can be
// generated. No partial descriptor or DMA pointer survives an input wait.
static void fill_pending(void *unused, int16_t *dma, size_t frames) {
    (void)unused;
    pcm_context_t *item = s_pending_head;
    while (frames && item) {
        size_t count = item->output_frames < frames ? item->output_frames : frames;
        fill_pcm(item, dma, count);
        item->output_frames -= count;
        s_pending_frames -= count;
        frames -= count;
        dma += count * 2;
        item = item->next;
    }
    // Only EOF/format boundaries pad the final descriptor, never packet gaps.
    if (frames) memset(dma, 0, frames * 2 * sizeof(*dma));
}

static void release_completed(void) {
    while (s_pending_head && !s_pending_head->output_frames) {
        pcm_context_t *item = s_pending_head;
        s_pending_head = item->next;
        if (!s_pending_head) s_pending_tail = NULL;
        audio_level_led_update_peak(item->peak);
        // Returning a queue item can wake the higher-priority decoder. Do it
        // after the complete DMA block is filled and the driver lock released.
        item->release(item);
    }
}

void native_audio_output_discard_pcm(void) {
    while (s_pending_head) {
        pcm_context_t *item = s_pending_head;
        s_pending_head = item->next;
        item->release(item);
    }
    s_pending_tail = NULL;
    s_pending_frames = 0;
    s_stream_started = false;
    s_prefill_started_us = 0;
    s_predicted_previous = false;
    s_predicted_phase = 0;
    reset_resampler();
}

static esp_err_t drain_pending(bool force_start) {
    if (!s_stream_started) {
        if (!force_start && s_pending_frames < PDM_START_BLOCKS * PDM_DMA_FRAMES)
            return ESP_OK;
        s_stream_started = true;
    }
    esp_err_t result = ESP_OK;
    while (s_pending_frames >= PDM_DMA_FRAMES) {
        result = native_i2s_write_full_block(s_pdm, fill_pending, NULL);
        if (result != ESP_OK) break;
    }
    // At startup, submit the prepared three blocks before returning source
    // items: returning an item can preempt us to run another decoder frame.
    release_completed();
    if (result != ESP_OK) native_audio_output_discard_pcm();
    return result;
}

esp_err_t native_audio_output_flush_pcm(void) {
    esp_err_t result = drain_pending(true);
    if (result == ESP_OK && s_pending_frames) {
        result = native_i2s_write_full_block(s_pdm, fill_pending, NULL);
        release_completed();
    }
    if (result != ESP_OK) native_audio_output_discard_pcm();
    s_stream_started = false;
    return result;
}

// Count output frames using the phase after all already queued source frames,
// independently of the actual resampler, which can still be partway through
// the preceding item. Rates <= 48 kHz produce at least one output per input.
static size_t predict_frames(size_t frames) {
    if (!frames || s_input_sample_rate == PDM_OUTPUT_SAMPLE_RATE) return frames;
    size_t first = s_predicted_previous ? 0 : 1;
    uint32_t phase = s_predicted_previous ? s_predicted_phase : s_input_sample_rate;
    uint64_t span = (uint64_t)(frames - first) * PDM_OUTPUT_SAMPLE_RATE;
    size_t rest = span >= phase ? (span - phase) / s_input_sample_rate + 1 : 0;
    s_predicted_previous = true;
    s_predicted_phase = phase + (uint64_t)rest * s_input_sample_rate - span;
    return first + rest;
}

esp_err_t native_audio_output_submit_pcm(pcm_context_t *item, uint8_t *data,
    size_t size, uint8_t bits_per_sample, uint8_t channels,
    void (*release)(native_audio_pcm_lease_t *)) {
    if (!item || !release) return ESP_ERR_INVALID_ARG;
    esp_err_t result = prepare_pcm(item, data, size, bits_per_sample, channels);
    if (result != ESP_OK) { release(item); return result; }
    item->release = release;
    item->output_frames = predict_frames(size / item->frame_bytes);
    if (s_pending_tail) s_pending_tail->next = item;
    else s_pending_head = item;
    s_pending_tail = item;
    s_pending_frames += item->output_frames;
    if (!s_stream_started && s_pending_head == item)
        s_prefill_started_us = esp_timer_get_time();
    return drain_pending(false);
}

// Synchronous borrowed-buffer API used by the bring-up tone only. Streaming
// uses submit_pcm, because a borrowed caller buffer cannot outlive this call.
esp_err_t native_audio_output_write_pcm(uint8_t *data, size_t size,
                                        uint8_t bits_per_sample, uint8_t channels) {
    ESP_RETURN_ON_ERROR(native_audio_output_flush_pcm(), TAG, "flush leased PCM");
    pcm_context_t pcm;
    ESP_RETURN_ON_ERROR(prepare_pcm(&pcm, data, size, bits_per_sample, channels),
                        TAG, "prepare PCM");
    ESP_RETURN_ON_ERROR(pdm_generate(resampled_frames(size / pcm.frame_bytes),
                                    fill_pcm, &pcm, false), TAG, "write PCM");
    s_predicted_previous = s_resampler_has_previous;
    s_predicted_phase = s_resampler_next_phase;
    audio_level_led_update_peak(pcm.peak);
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

void native_audio_output_idle(void) {
    // A short file, tiny packets or source backpressure must not deadlock
    // startup while waiting for three blocks. EOF flushes immediately; a
    // temporarily empty source queue can start after one 32 ms reserve period.
    if (!s_stream_started && s_pending_frames &&
        esp_timer_get_time() - s_prefill_started_us >= PDM_START_MAX_WAIT_US) {
        esp_err_t result = drain_pending(true);
        if (result != ESP_OK) ESP_LOGW(TAG, "PCM prefill failed: %s", esp_err_to_name(result));
    }
    audio_level_led_update_peak(0);
}

esp_err_t native_audio_output_suspend(void) {
    native_audio_output_discard_pcm();
    if (!s_pdm) return ESP_OK;
    uint32_t count = ramp_frames();
    ramp_context_t ramp = {.count = count, .up = false};
    for (uint32_t first = 0; first < count; first += PDM_DMA_FRAMES) {
        ESP_RETURN_ON_ERROR(pdm_generate(PDM_DMA_FRAMES, fill_ramp, &ramp, false),
                            TAG, "sleep bias ramp");
    }
    // Pad with constant-low PDM. Stop while this tail is still queued so
    // DMA auto-clear cannot restore 50% duty after the downward ramp.
    for (unsigned tail = 0; tail < 2; ++tail) {
        ESP_RETURN_ON_ERROR(pdm_generate(PDM_DMA_FRAMES, fill_ramp, &ramp, false),
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

#include "test.c"
