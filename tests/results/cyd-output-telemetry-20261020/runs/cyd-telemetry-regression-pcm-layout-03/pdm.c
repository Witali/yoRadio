#define _GNU_SOURCE
#include <assert.h>
#include <limits.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

#include "native_audio_normalizer.h"

typedef int esp_err_t;
#include "cyd_output_metrics_noop.h"
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_NOT_SUPPORTED -2
#define ESP_ERR_INVALID_ARG -3
#define ESP_ERR_INVALID_STATE -4
#define pdMS_TO_TICKS(t) (t)
#define ESP_RETURN_ON_ERROR(call, tag, message) do { \
    esp_err_t result_ = (call); if (result_ != ESP_OK) return result_; \
} while (0)
#define ESP_LOGI(...) ((void)0)

static bool enabled;
static uint8_t volume = 254, gain_db = 20;
static int8_t balance, target_dbfs = -3;
static uint16_t time_ms = 100;
static unsigned setting_reads, cases;
static uint8_t captured[8192 * 16 * 4], expected[sizeof(captured)];
static size_t captured_size, expected_size;
static uint8_t dac_storage[3072];
static uint8_t *s_dac_data = dac_storage;
static void *s_dac;
static bool s_dac_enabled;
esp_err_t native_audio_output_pause(void);
static uint32_t s_dac_sample_rate;
static bool s_legacy_installed;
static uint32_t s_legacy_sample_rate, s_legacy_output_sample_rate;
static uint32_t legacy_storage[1536];
static uint32_t *s_legacy_frames = legacy_storage;
static uint16_t s_legacy_fractional_error;
static uint32_t s_input_sample_rate;
static size_t s_buffered_samples;
static esp_err_t config_result;
static esp_err_t write_result;
static unsigned dac_allocations;
static bool native_audio_settings_get_normalization(void) { ++setting_reads; return enabled; }
static uint8_t native_audio_settings_get_normalization_gain_db(void) { ++setting_reads; return gain_db; }
static int8_t native_audio_settings_get_normalization_target_dbfs(void) { ++setting_reads; return target_dbfs; }
static uint16_t native_audio_settings_get_normalization_time_ms(void) { ++setting_reads; return time_ms; }
static uint8_t native_audio_settings_get_volume(void) { return volume; }
static int8_t native_audio_settings_get_balance(void) { return balance; }
static int capture(const void *data, size_t size) {
    assert(size <= sizeof(captured) - captured_size);
    memcpy(captured + captured_size, data, size);
    captured_size += size;
    return ESP_OK;
}

static int pdm_begin(void) { return config_result; }



static int test_driver_write(const void *, size_t, size_t *);
static int dac_continuous_write(void *handle, const void *data, size_t size,
                                 size_t *written, unsigned timeout) {
    (void)handle; (void)timeout;
    return test_driver_write(data, size, written);
}
static int idf6_dac_output_write(const void *data, size_t size,
                                 size_t *written, unsigned timeout) {
    return dac_continuous_write(0, data, size, written, timeout);
}
enum { DAC_CHANNEL_MASK_CH1, DAC_DIGI_CLK_SRC_APLL, DAC_CHANNEL_MODE_SIMUL,
       I2S_MODE_MASTER = 1, I2S_MODE_TX = 2, I2S_MODE_DAC_BUILT_IN = 4,
       I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_FMT_RIGHT_LEFT,
       I2S_COMM_FORMAT_STAND_MSB, ESP_INTR_FLAG_LEVEL1,
       I2S_PIN_NO_CHANGE, I2S_DAC_CHANNEL_LEFT_EN };
typedef struct {
    int chan_mask, desc_num, buf_size; uint32_t freq_hz;
    int offset, clk_src, chan_mode;
} dac_continuous_config_t;
typedef struct {
    int mode; uint32_t sample_rate; int bits_per_sample, channel_format,
        communication_format, intr_alloc_flags, dma_buf_count, dma_buf_len;
    bool use_apll, tx_desc_auto_clear; int fixed_mclk;
} i2s_config_t;
static int dac_continuous_disable(void *handle) { (void)handle; return ESP_OK; }
static int dac_continuous_del_channels(void *handle) { (void)handle; return ESP_OK; }
static int dac_continuous_new_channels(const dac_continuous_config_t *config,
                                        void **handle) {
    (void)config; ++dac_allocations;
    *handle = config_result == ESP_OK ? (void *)1 : NULL; return config_result;
}
static int dac_continuous_enable(void *handle) { (void)handle; return config_result; }
static int idf6_dac_output_set_sample_rate(uint32_t rate) { (void)rate; return config_result; }
static int idf6_dac_output_configure(const i2s_config_t *config, int channel) {
    (void)config; (void)channel; return config_result;
}
static int idf6_dac_output_begin(void) { return config_result; }


#include <unistd.h>

static size_t short_write_bytes = SIZE_MAX;
static unsigned driver_writes;
static int test_driver_write(const void *data, size_t size, size_t *written) {
    ++driver_writes;
    if (write_result != ESP_OK) { *written = 0; return write_result; }
    *written = size > short_write_bytes ? short_write_bytes : size;
    return capture(data, *written);
}
#if TEST_PDM
#define ESP_ERR_INVALID_STATE -4
static void *s_pdm = (void *)1;
static bool s_pdm_running = true;
static int16_t s_sample_buffer[512];
static bool s_resampler_has_previous;
static int16_t s_resampler_previous;
static uint32_t s_resampler_next_phase;
static int i2s_channel_write(void *handle, const void *data, size_t size,
                              size_t *written, unsigned timeout) {
    (void)handle; (void)timeout;
    return test_driver_write(data, size, written);
}
#endif

#define OUTPUT_PACKET_BYTES 3072
#define SAMPLE_GAIN_SCALE 32768U
#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U
#define NORMALIZER_CHUNK_FRAMES 128U
#define PDM_OUTPUT_SAMPLE_RATE 48000U
#define PDM_DMA_SAMPLES 512U
#define PDM_DMA_DESCRIPTORS 8U
#define PDM_BIAS_RAMP_MS 100U
#define PDM_BIAS_SETTLE_MS 2U
#define RESAMPLER_SCALE 32768U
#define RESAMPLER_FRACTION_MULTIPLIER_Q16 44739U
#define LEGACY_DMA_DESCRIPTORS 8
#define LEGACY_DMA_FRAMES 512
#define LEGACY_OUTPUT_BYTES (OUTPUT_PACKET_BYTES * 2)
#define LEGACY_OVERSAMPLE_FACTOR 16U
#define LEGACY_MIN_INPUT_SAMPLE_RATE 8000U
#define LEGACY_MAX_INPUT_SAMPLE_RATE 48000U
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

typedef struct {
    uint32_t left;
    uint32_t right;
} pcm_gains_t;

static pcm_gains_t pcm_channel_gains(uint8_t channels, uint8_t volume,
                                    int8_t balance) {
    uint8_t left_balance =
        channels > 1 && balance < 0
            ? (uint8_t)((int)BALANCE_DENOMINATOR + balance)
            : BALANCE_DENOMINATOR;
    uint8_t right_balance =
        balance > 0 ? (uint8_t)(BALANCE_DENOMINATOR - balance)
                    : BALANCE_DENOMINATOR;
    return (pcm_gains_t){
        .left = channel_gain_q15(volume, left_balance),
        .right = channels > 1 ? channel_gain_q15(volume, right_balance) : 0,
    };
}

static int16_t pcm_mono_values(int16_t left, int16_t right, uint8_t channels,
                               const pcm_gains_t *gains) {
    if (channels < 2) {
        return scale_sample_q15(left, gains->left);
    }
    left = scale_sample_q15(left, gains->left);
    right = scale_sample_q15(right, gains->right);
    return (int16_t)(((int32_t)left + (int32_t)right) / 2);
}

static int16_t pcm_mono_sample(const uint8_t *frame, uint8_t channels,
                               const pcm_gains_t *gains) {
    int16_t left, right = 0;
    memcpy(&left, frame, sizeof(left));
    if (channels > 1) memcpy(&right, frame + sizeof(right), sizeof(right));
    return pcm_mono_values(left, right, channels, gains);
}

bool native_audio_output_supports_pcm(uint8_t bits_per_sample,
                                      uint8_t channels) {
    return channels && (bits_per_sample == 8 || bits_per_sample == 16 ||
                        bits_per_sample == 24 || bits_per_sample == 32);
}

static int16_t pcm_sample_to_s16(const uint8_t *sample, uint8_t sample_bytes) {
    if (sample_bytes == 1) {
        int32_t value = sample[0] < 128U ? sample[0] : (int32_t)sample[0] - 256;
        return (int16_t)(value * 256);
    }
    // Keep the signed high 16 bits, with no unaligned load or negative shift.
    // Discarding the low bytes gives the same floor conversion as signed PCM
    // arithmetic shifts, including the negative values nearest to zero.
    uint16_t high = (uint16_t)sample[sample_bytes - 2U] |
                    ((uint16_t)sample[sample_bytes - 1U] << 8);
    int32_t value = high <= INT16_MAX ? high : (int32_t)high - 65536;
    return (int16_t)value;
}

typedef struct {
    bool valid;
    bool enabled;
    uint8_t max_gain_db;
    int8_t target_dbfs;
    uint16_t time_ms;
    uint32_t sample_rate;
} normalizer_config_cache_t;

// Only the output owner touches the cache, DSP instance and scratch. Settings
// getters are atomic; the controller can only publish a pending reset request.
static normalizer_config_cache_t s_normalizer_config;
static atomic_bool s_normalizer_reset_pending;
static atomic_bool s_pause_requested;
static uint32_t s_pcm_sample_rate = 16000U;
static uint8_t s_pcm_channels;
static uint8_t s_pcm_bits;
static int16_t s_normalizer_scratch[NORMALIZER_CHUNK_FRAMES * 2U];

static void reset_pcm_normalizer(void) {
    native_audio_normalizer_reset();
    s_pcm_channels = 0;
    s_pcm_bits = 0;
}

static void pcm_normalizer_set_sample_rate(uint32_t sample_rate) {
    if (sample_rate != s_pcm_sample_rate) {
        s_pcm_sample_rate = sample_rate;
        reset_pcm_normalizer();
    }
}

static bool sync_normalizer_configuration(uint8_t channels, uint8_t bits) {
    normalizer_config_cache_t next = {
        .valid = true,
        .enabled = native_audio_settings_get_normalization(),
        .max_gain_db = native_audio_settings_get_normalization_gain_db(),
        .target_dbfs = native_audio_settings_get_normalization_target_dbfs(),
        .time_ms = native_audio_settings_get_normalization_time_ms(),
        .sample_rate = s_pcm_sample_rate,
    };
    if (!s_normalizer_config.valid ||
        next.enabled != s_normalizer_config.enabled ||
        next.max_gain_db != s_normalizer_config.max_gain_db ||
        next.target_dbfs != s_normalizer_config.target_dbfs ||
        next.time_ms != s_normalizer_config.time_ms ||
        next.sample_rate != s_normalizer_config.sample_rate) {
        native_audio_normalizer_configure(
            next.enabled, next.max_gain_db, next.target_dbfs, next.time_ms,
            next.sample_rate);
        s_normalizer_config = next;
    }
    bool requested = atomic_exchange(&s_normalizer_reset_pending, false);
    if (requested || s_pcm_channels != channels || s_pcm_bits != bits) {
        native_audio_normalizer_reset();
    }
    s_pcm_channels = channels;
    s_pcm_bits = bits;
    return next.enabled;
}

void native_audio_output_request_normalizer_reset(void) {
    atomic_store(&s_normalizer_reset_pending, true);
}

void native_audio_output_request_pause(bool requested) {
    atomic_store(&s_pause_requested, requested);
}

typedef struct {
    const uint8_t *data;
    size_t frame_bytes;
    size_t frames;
    size_t position;
    size_t buffered_frames;
    size_t buffered_index;
    pcm_gains_t gains;
    uint8_t channels;
    uint8_t sample_bytes;
    bool normalize;
} pcm_reader_t;

static pcm_reader_t pcm_reader_begin(const uint8_t *data, size_t frames,
                                      uint8_t bits, uint8_t channels) {
    return (pcm_reader_t){
        .data = data,
        .frame_bytes = (size_t)channels * (bits / 8U),
        .frames = frames,
        .gains = pcm_channel_gains(channels,
            native_audio_settings_get_volume(),
            native_audio_settings_get_balance()),
        .channels = channels,
        .sample_bytes = bits / 8U,
        .normalize = sync_normalizer_configuration(channels, bits),
    };
}

static int16_t pcm_reader_next(pcm_reader_t *reader) {
    if (!reader->normalize) {
        const uint8_t *frame =
            reader->data + reader->position++ * reader->frame_bytes;
        if (reader->sample_bytes == sizeof(int16_t)) {
            return pcm_mono_sample(frame, reader->channels, &reader->gains);
        }
        int16_t left = pcm_sample_to_s16(frame, reader->sample_bytes);
        int16_t right = reader->channels > 1
            ? pcm_sample_to_s16(frame + reader->sample_bytes, reader->sample_bytes)
            : 0;
        return pcm_mono_values(left, right, reader->channels, &reader->gains);
    }

    uint8_t normalized_channels = reader->channels > 1 ? 2 : 1;
    if (reader->buffered_index == reader->buffered_frames) {
        size_t chunk = reader->frames - reader->position;
        if (chunk > NORMALIZER_CHUNK_FRAMES) chunk = NORMALIZER_CHUNK_FRAMES;
        // Keep the decoder's PCM read-only and tolerate unaligned input.
        // CYD's mono mixer consumes the first two channels of wider layouts.
        for (size_t frame = 0; frame < chunk; ++frame) {
            const uint8_t *input = reader->data +
                (reader->position + frame) * reader->frame_bytes;
            if (reader->sample_bytes == sizeof(int16_t)) {
                memcpy(s_normalizer_scratch + frame * normalized_channels,
                       input, normalized_channels * sizeof(int16_t));
            } else {
                for (uint8_t channel = 0; channel < normalized_channels; ++channel)
                    s_normalizer_scratch[frame * normalized_channels + channel] =
                        pcm_sample_to_s16(input + channel * reader->sample_bytes,
                                          reader->sample_bytes);
            }
        }
        native_audio_normalizer_process_block(
            s_normalizer_scratch, chunk, normalized_channels);
        reader->buffered_frames = chunk;
        reader->buffered_index = 0;
    }
    const uint8_t *frame = (const uint8_t *)(s_normalizer_scratch +
        reader->buffered_index++ * normalized_channels);
    ++reader->position;
    return pcm_mono_sample(frame, normalized_channels, &reader->gains);
}

static void reset_resampler(void) {
    s_resampler_has_previous = false;
    s_resampler_previous = 0;
    s_resampler_next_phase = 0;
}

static esp_err_t pdm_write_block(const int16_t *samples, size_t count) {
    if (atomic_load(&s_pause_requested)) return ESP_ERR_INVALID_STATE;
    if (!s_pdm || !s_pdm_running) return ESP_ERR_INVALID_STATE;
    size_t written = 0;
    size_t bytes = count * sizeof(*samples);
    int64_t started = native_output_metrics_begin_write();
    esp_err_t result = i2s_channel_write(s_pdm, samples, bytes, &written,
                                         1000);
    native_output_metrics_end_write(bytes, written, result, started);
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
        // round(phase * 32768 / 48000), using a Q16 reciprocal. This hot path
        // runs once per 48 kHz output sample, so avoid a hardware division.
        uint32_t fraction =
            (phase * RESAMPLER_FRACTION_MULTIPLIER_Q16 + 32768U) >> 16;
        int32_t scaled = delta * (int32_t)fraction;
        scaled += scaled >= 0 ? (int32_t)(RESAMPLER_SCALE / 2U)
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
esp_err_t native_audio_output_configure(uint32_t input_sample_rate) {
    if (input_sample_rate < 8000U || input_sample_rate > 48000U) {
        return ESP_ERR_INVALID_ARG;
    }
    ESP_RETURN_ON_ERROR(pdm_begin(), TAG, "start fixed-rate PDM");
    if (input_sample_rate != s_input_sample_rate) {
        ESP_RETURN_ON_ERROR(pdm_flush(), TAG, "flush old PDM rate");
        s_input_sample_rate = input_sample_rate;
        reset_resampler();
        ESP_LOGI(TAG, "PDM resampler input changed to %lu Hz",
                 (unsigned long)input_sample_rate);
    }
    pcm_normalizer_set_sample_rate(input_sample_rate);
    return ESP_OK;
}

esp_err_t native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels) {
    if (atomic_load(&s_pause_requested)) return ESP_ERR_INVALID_STATE;
    if (!data || !native_audio_output_supports_pcm(bits_per_sample, channels)) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    size_t frame_bytes = (size_t)channels * (bits_per_sample / 8U);
    size_t frames = size / frame_bytes;
    pcm_reader_t reader = pcm_reader_begin(data, frames, bits_per_sample, channels);
    for (size_t frame = 0; frame < frames; ++frame) {
        ESP_RETURN_ON_ERROR(
            pdm_write_resampled(pcm_reader_next(&reader)),
            TAG, "write PDM PCM");
    }
    return ESP_OK;
}

void native_audio_output_discard_pcm(void) {
    s_buffered_samples = 0;
    reset_resampler();
    reset_pcm_normalizer();
}

esp_err_t native_audio_output_flush_pcm(void) {
    esp_err_t result = pdm_flush();
    reset_resampler();
    reset_pcm_normalizer();
    return result;
}


void reference_owner(void);
void reference_configure(bool, uint8_t, int8_t, uint16_t, uint32_t);
void reference_reset(void);
void reference_process(int16_t stereo[2]);
unsigned normalizer_reset_calls(void);

static uint64_t reference_frames, reference_next_output;
static uint32_t reference_rate = 48000;
static int16_t reference_previous;
static unsigned reference_fraction, resampled_checks, max_rational_error;
static unsigned conversion_checks;
static uint8_t *input_mapping, *input;
static const size_t input_capacity = 256 * 1024;

static int16_t reference_decode(const uint8_t *sample, uint8_t bits) {
    uint64_t raw = 0;
    for (unsigned byte = 0; byte < bits / 8U; ++byte)
        raw += (uint64_t)sample[byte] << (byte * 8U);
    int64_t signed_value = raw & (UINT64_C(1) << (bits - 1U))
        ? (int64_t)raw - (INT64_C(1) << bits) : (int64_t)raw;
    if (bits == 8) return (int16_t)(signed_value * 256);
    int64_t divisor = INT64_C(1) << (bits - 16);
    return (int16_t)(signed_value < 0
        ? -((-signed_value + divisor - 1) / divisor) : signed_value / divisor);
}
static int16_t reference_scaled(int16_t sample, unsigned v, unsigned b) {
    int64_t gain = ((int64_t)v * b * 32768 + 2032) / 4064;
    int64_t result = (int64_t)sample * gain;
    return (int16_t)(result < 0 ? -((-result + 16384) / 32768)
                                : (result + 16384) / 32768);
}
static void append_expected(const void *data, size_t bytes) {
    assert(bytes <= sizeof(expected) - expected_size);
    memcpy(expected + expected_size, data, bytes); expected_size += bytes;
}
static int32_t round_signed(int64_t value, int64_t divisor) {
    return (int32_t)(value < 0 ? -((-value + divisor / 2) / divisor)
                               : (value + divisor / 2) / divisor);
}
static void reference_output_sample(int16_t sample) {
#if TEST_PDM
    if (reference_frames == 0) {
        append_expected(&sample, 2);
        reference_next_output = 1;
    } else {
        while (reference_next_output * reference_rate <= reference_frames * 48000U) {
            uint64_t phase = reference_next_output * reference_rate -
                             (reference_frames - 1U) * 48000U;
            /* The fixed CYD reciprocal is intentionally retained. Compare its
               exact integer output and bound error against a rational Q15 tap. */
            int64_t fraction = (int64_t)(phase * 44739U + 32768U) / 65536;
            int64_t exact_fraction = (int64_t)(phase * 32768U + 24000U) / 48000;
            int32_t delta = (int32_t)sample - reference_previous;
            int16_t interpolated = (int16_t)(reference_previous +
                round_signed((int64_t)delta * fraction, 32768));
            int16_t rational = (int16_t)(reference_previous +
                round_signed((int64_t)delta * exact_fraction, 32768));
            unsigned error = interpolated > rational
                ? (unsigned)(interpolated - rational) : (unsigned)(rational - interpolated);
            assert(error <= 2);
            if (error > max_rational_error) max_rational_error = error;
            ++resampled_checks;
            append_expected(&interpolated, 2);
            ++reference_next_output;
        }
    }
    reference_previous = sample;
    ++reference_frames;
#elif TEST_DAC
    int shifted = sample < 0 ? -((-(int)sample + 255) / 256) : sample / 256;
    uint8_t code = (uint8_t)(shifted + 128);
    append_expected(&code, 1);
#else
    unsigned value = (unsigned)((int)sample + 32768);
    for (unsigned phase = 0; phase < 16; ++phase) {
        unsigned code = value / 256;
        if (code == 255) reference_fraction = 0;
        else {
            unsigned sum = reference_fraction + value % 256;
            code += sum / 256; reference_fraction = sum % 256;
        }
        uint32_t packed = code * 0x01000100U;
        append_expected(&packed, sizeof(packed));
    }
#endif
}
static void reference_packet(const uint8_t *data, size_t frames,
                               uint8_t bits, uint8_t channels) {
    size_t bytes = bits / 8U;
    for (size_t frame = 0; frame < frames; ++frame) {
        const uint8_t *p = data + frame * channels * bytes;
        int16_t stereo[2] = {reference_decode(p, bits), 0};
        stereo[1] = channels > 1 ? reference_decode(p + bytes, bits) : stereo[0];
        reference_process(stereo);
        int left = reference_scaled(stereo[0], volume,
                                    channels > 1 && balance < 0 ? 16 + balance : 16);
        int right = reference_scaled(stereo[1], volume, balance > 0 ? 16 - balance : 16);
        reference_output_sample((int16_t)(channels > 1 ? (left + right) / 2 : left));
    }
}
static void expected_flush(void) {
#if TEST_PDM
    size_t samples = expected_size / 2;
    const int16_t zero = 0;
    while (samples % 512) { append_expected(&zero, 2); ++samples; }
#endif
}
static void compare_capture(void) {
    assert(captured_size == expected_size);
    if (memcmp(captured, expected, captured_size)) {
        size_t first = 0;
        while (first < captured_size && captured[first] == expected[first]) ++first;
        fprintf(stderr, "case=%u mismatch=%zu actual=%u expected=%u bytes=%zu\n",
                cases, first, captured[first], expected[first], captured_size);
        assert(!"PCM output differs from packed reference");
    }
}
static void reset_stream(void) {
    native_audio_output_discard_pcm();
    reference_configure(enabled, gain_db, target_dbfs, time_ms, reference_rate);
    reference_reset();
    reference_frames = 0; reference_next_output = 0;
    reference_fraction = 0; captured_size = expected_size = 0;
    driver_writes = 0;
}
static void configure_rate(uint32_t rate) {
    assert(native_audio_output_configure(rate) == ESP_OK);
    reference_rate = rate;
    reset_stream();
}
static void fill_input(size_t frames, uint8_t bits, uint8_t channels, unsigned seed) {
    assert(!mprotect(input_mapping, input_capacity, PROT_READ | PROT_WRITE));
    const int64_t edge[] = {INT64_MIN, -2147483648LL, -8388608, -32768, -129,
                           -128, -127, -2, -1, 0, 1, 2, 127, 128, 129,
                           32767, 8388607, 2147483647LL, INT64_MAX};
    uint64_t mask = (UINT64_C(1) << bits) - 1U;
    size_t sample_bytes = bits / 8U;
    assert(frames * channels * sample_bytes + 4 < input_capacity);
    for (size_t sample = 0; sample < frames * channels + 1; ++sample) {
        uint64_t value = sample < sizeof(edge) / sizeof(*edge)
            ? (uint64_t)edge[sample] & mask
            : (sample * UINT64_C(6364136223846793005) + seed * 1447U) & mask;
        for (unsigned byte = 0; byte < sample_bytes; ++byte)
            input[sample * sample_bytes + byte] = (uint8_t)(value >> (byte * 8));
    }
    assert(!mprotect(input_mapping, input_capacity, PROT_READ));
}
static void check_case(size_t frames, uint8_t bits, uint8_t channels, size_t trailing) {
    reset_stream(); fill_input(frames, bits, channels, cases);
    reference_packet(input, frames, bits, channels);
    size_t bytes = frames * channels * (bits / 8U);
    assert(native_audio_output_write_pcm(input, bytes + trailing, bits, channels) == ESP_OK);
    expected_flush();
    assert(native_audio_output_flush_pcm() == ESP_OK);
    compare_capture(); ++cases;
}
static void check_split(uint8_t bits, uint8_t channels) {
    const size_t frames = 4097;
    fill_input(frames, bits, channels, cases);
    reset_stream();
    reference_packet(input, frames, bits, channels);
    const size_t pieces[] = {1, 127, 129, 511, 1025, 7, 2297};
    size_t offset = 0;
    for (size_t part = 0; part < sizeof(pieces) / sizeof(*pieces); ++part) {
        assert(native_audio_output_write_pcm(input + offset * channels * (bits / 8U),
            pieces[part] * channels * (bits / 8U), bits, channels) == ESP_OK);
        offset += pieces[part];
    }
    assert(offset == frames);
    expected_flush(); assert(native_audio_output_flush_pcm() == ESP_OK);
    compare_capture(); ++cases;
}

static void check_conversion_boundaries(void) {
    uint8_t packed[4];
    for (unsigned raw = 0; raw <= UINT8_MAX; ++raw) {
        packed[0] = (uint8_t)raw;
        assert(pcm_sample_to_s16(packed, 1) == reference_decode(packed, 8));
        ++conversion_checks;
    }
    const unsigned low_bytes[] = {0, 1, 127, 128, 255};
    const unsigned low_words[] = {0, 1, 32767, 32768, 65535};
    for (unsigned high = 0; high <= UINT16_MAX; ++high) {
        packed[0] = (uint8_t)high; packed[1] = (uint8_t)(high / 256);
        assert(pcm_sample_to_s16(packed, 2) == reference_decode(packed, 16));
        ++conversion_checks;
        for (size_t low = 0; low < sizeof(low_bytes) / sizeof(*low_bytes); ++low) {
            packed[0] = (uint8_t)low_bytes[low];
            packed[1] = (uint8_t)high; packed[2] = (uint8_t)(high / 256);
            assert(pcm_sample_to_s16(packed, 3) == reference_decode(packed, 24));
            ++conversion_checks;
            packed[0] = (uint8_t)low_words[low];
            packed[1] = (uint8_t)(low_words[low] / 256);
            packed[2] = (uint8_t)high; packed[3] = (uint8_t)(high / 256);
            assert(pcm_sample_to_s16(packed, 4) == reference_decode(packed, 32));
            ++conversion_checks;
        }
    }
}

static void check_guard_boundary(uint8_t bits, uint8_t channels, size_t trailing) {
    size_t frame_bytes = channels * (bits / 8U);
    size_t bytes = frame_bytes + trailing;
    uint8_t *guarded = input_mapping + input_capacity - bytes;
    assert(!mprotect(input_mapping, input_capacity, PROT_READ | PROT_WRITE));
    for (size_t byte = 0; byte < bytes; ++byte) guarded[byte] = (uint8_t)(byte * 179U);
    assert(!mprotect(input_mapping, input_capacity, PROT_READ));
    reset_stream(); reference_packet(guarded, 1, bits, channels);
    assert(native_audio_output_write_pcm(guarded, bytes, bits, channels) == ESP_OK);
    expected_flush(); assert(native_audio_output_flush_pcm() == ESP_OK);
    compare_capture(); ++cases;
    /* No complete frame: even a pointer to the inaccessible page is valid
       for the mono8 zero-byte case, because no sample may be fetched. */
    reset_stream();
    assert(native_audio_output_write_pcm(input_mapping + input_capacity - (frame_bytes - 1),
                                         frame_bytes - 1, bits, channels) == ESP_OK);
    assert(native_audio_output_flush_pcm() == ESP_OK);
    assert(captured_size == 0); ++cases;
}

int main(void) {
    reference_owner();
    long page_size = sysconf(_SC_PAGESIZE);
    assert(page_size > 0 && input_capacity % (size_t)page_size == 0);
    size_t mapping_bytes = input_capacity + (size_t)page_size;
    input_mapping = mmap(NULL, mapping_bytes, PROT_NONE,
                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(input_mapping != MAP_FAILED); input = input_mapping + 1;
    check_conversion_boundaries();
    configure_rate(48000);
    for (unsigned bits = 0; bits <= UINT8_MAX; ++bits)
        for (unsigned channels = 0; channels <= UINT8_MAX; ++channels)
            assert(native_audio_output_supports_pcm((uint8_t)bits, (uint8_t)channels) ==
                (channels && (bits == 8 || bits == 16 || bits == 24 || bits == 32)));
    const uint8_t widths[] = {8, 16, 24, 32};
    const uint8_t layouts[] = {1, 2, 3, 8};
    const size_t lengths[] = {0, 1, 19, 127, 128, 129, 511, 512, 1025, 4097};
    for (unsigned mode = 0; mode < 2; ++mode) {
        enabled = mode != 0;
        for (size_t width = 0; width < sizeof(widths); ++width)
            for (size_t layout = 0; layout < sizeof(layouts); ++layout) {
                uint8_t bits = widths[width], channels = layouts[layout];
                size_t frame_bytes = channels * (bits / 8U);
                volume = 254; balance = 0;
                for (size_t length = 0; length < sizeof(lengths) / sizeof(*lengths); ++length)
                    check_case(lengths[length], bits, channels, frame_bytes - 1);
                const int8_t balances[] = {-16, -1, 0, 1, 16};
                const uint8_t volumes[] = {0, 1, 127, 192, 254};
                for (size_t v = 0; v < sizeof(volumes); ++v)
                    for (size_t b = 0; b < sizeof(balances); ++b) {
                        volume = volumes[v]; balance = balances[b];
                        check_case(521, bits, channels, 0);
                    }
                volume = 254; balance = 0; check_split(bits, channels);
                check_guard_boundary(bits, channels, 0);
                check_guard_boundary(bits, channels, frame_bytes - 1);
            }
    }
    /* Exercise non-integral PDM ratios, endpoint rails and packet boundaries. */
    const uint32_t rates[] = {8000, 11025, 16000, 22050, 24000, 32000, 44100, 47999, 48000};
    enabled = true;
    for (size_t rate = 0; rate < sizeof(rates) / sizeof(*rates); ++rate) {
        configure_rate(rates[rate]);
        for (size_t width = 0; width < sizeof(widths); ++width) {
            check_case(1025, widths[width], 2, 0);
            check_split(widths[width], 1);
        }
    }
    /* Layout changes restart DSP while resampling preserves the stream's
       physical sample timeline across packet and layout boundaries. */
    for (unsigned mode = 0; mode < 2; ++mode) {
        enabled = mode != 0;
        configure_rate(44100);
        for (size_t layout = 0; layout < sizeof(layouts); ++layout) {
            uint8_t bits = widths[layout], channels = layouts[layout];
            fill_input(513, bits, channels, (unsigned)layout);
            reference_reset(); reference_packet(input, 513, bits, channels);
            assert(native_audio_output_write_pcm(input, 513 * channels * (bits / 8U),
                                                 bits, channels) == ESP_OK);
        }
        expected_flush(); assert(native_audio_output_flush_pcm() == ESP_OK);
        compare_capture(); ++cases;
    }
#if TEST_PDM
    /* A coprime ratio visits every fractional phase of the fixed 48 kHz
       interpolation interval, including the final phase near its endpoint. */
    configure_rate(47999); check_case(48001, 32, 1, 0);
#endif
    /* Bit-depth changes restart normalization, even if rate/channels match. */
    configure_rate(48000); enabled = true; gain_db = 20; time_ms = 100;
    for (size_t width = 0; width < sizeof(widths); ++width) {
        fill_input(4096, widths[width], 2, (unsigned)width);
        captured_size = expected_size = 0;
        reference_reset(); reference_frames = 0; reference_next_output = 0;
        reference_packet(input, 4096, widths[width], 2);
        unsigned resets = normalizer_reset_calls();
        assert(native_audio_output_write_pcm(input, 4096 * 2 * (widths[width] / 8U),
                                             widths[width], 2) == ESP_OK);
        assert(normalizer_reset_calls() == resets + 1);
        compare_capture(); ++cases;
    }
    /* Unsupported formats are rejected before reading settings or PCM. */
    setting_reads = 0;
    const uint8_t unsupported[] = {0, 1, 7, 12, 20, 40, 64, 255};
    for (size_t i = 0; i < sizeof(unsupported); ++i)
        assert(native_audio_output_write_pcm(input, 32, unsupported[i], 2) == ESP_ERR_NOT_SUPPORTED);
    assert(native_audio_output_write_pcm(NULL, 32, 16, 2) == ESP_ERR_NOT_SUPPORTED);
    assert(native_audio_output_write_pcm(input, 32, 16, 0) == ESP_ERR_NOT_SUPPORTED);
    assert(!setting_reads);
    /* Driver failures and partial successes must reach the output owner. */
    configure_rate(48000); fill_input(1025, 16, 2, 1);
    write_result = ESP_FAIL;
    assert(native_audio_output_write_pcm(input, 1025 * 4, 16, 2) == ESP_FAIL);
    write_result = ESP_OK; reset_stream(); short_write_bytes = 1;
    assert(native_audio_output_write_pcm(input, 1025 * 4, 16, 2) == ESP_FAIL);
    short_write_bytes = SIZE_MAX; reset_stream();
#if TEST_PDM
    /* A format rate change drains the old partial block before new PCM. */
    fill_input(19, 16, 1, 9);
    reference_packet(input, 19, 16, 1);
    assert(native_audio_output_write_pcm(input, 38, 16, 1) == ESP_OK);
    expected_flush();
    assert(native_audio_output_configure(44100) == ESP_OK);
    compare_capture();
    reference_rate = 44100; reset_stream();
    reference_packet(input, 19, 16, 1);
    assert(native_audio_output_write_pcm(input, 38, 16, 1) == ESP_OK);
    expected_flush(); assert(native_audio_output_flush_pcm() == ESP_OK);
    compare_capture();
    reset_stream();
    assert(native_audio_output_write_pcm(input, 38, 16, 1) == ESP_OK);
    write_result = ESP_FAIL;
    assert(native_audio_output_configure(48000) == ESP_FAIL);
    assert(s_input_sample_rate == 44100 && s_pcm_sample_rate == 44100);
    write_result = ESP_OK; reset_stream();
    assert(native_audio_output_write_pcm(input, 38, 16, 1) == ESP_OK);
    short_write_bytes = 1;
    assert(native_audio_output_flush_pcm() == ESP_FAIL);
    assert(!s_resampler_has_previous && !s_pcm_channels && !s_pcm_bits);
    short_write_bytes = SIZE_MAX; reset_stream();
    assert(native_audio_output_configure(7999) == ESP_ERR_INVALID_ARG);
    assert(native_audio_output_configure(48001) == ESP_ERR_INVALID_ARG);
#else
    /* A failed/short prime cannot publish a ready rate or poison its retry. */
    uint32_t old_rate = s_pcm_sample_rate;
    write_result = ESP_FAIL;
    assert(native_audio_output_configure(24000) == ESP_FAIL);
    assert(s_pcm_sample_rate == old_rate);
    write_result = ESP_OK; short_write_bytes = 1;
    assert(native_audio_output_configure(24000) == ESP_FAIL);
    assert(s_pcm_sample_rate == old_rate);
    short_write_bytes = SIZE_MAX;
    assert(native_audio_output_configure(24000) == ESP_OK);
    assert(s_pcm_sample_rate == 24000);
#endif
    assert(!munmap(input_mapping, mapping_bytes));
    printf("PASS packed PCM: %u stream cases, signed LE8/16/24/32, immutable unaligned input, "
           "mono/stereo/first-two mix, split/partial frames, driver faults, rate/EOF; "
           "conversion checks=%u PDM checks=%u max rational error=%u LSB\n",
           cases, conversion_checks, resampled_checks, max_rational_error);
    return 0;
}
