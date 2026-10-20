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
static uint8_t captured[3072 * 16 * 4], expected[sizeof(captured)];
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
static int pdm_write_resampled(int16_t sample) { return capture(&sample, sizeof(sample)); }
static int pdm_begin(void) { return config_result; }
static int pdm_flush(void) { return ESP_OK; }
static void reset_resampler(void) {}
static int dac_continuous_write(void *handle, const void *data, size_t size,
                                 size_t *written, unsigned timeout) {
    (void)handle; (void)timeout;
    if (write_result != ESP_OK) { *written = 0; return write_result; }
    *written = size;
    return capture(data, size);
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

#define OUTPUT_PACKET_BYTES 3072
#define SAMPLE_GAIN_SCALE 32768U
#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U
#define NORMALIZER_CHUNK_FRAMES 128U
#define LEGACY_OUTPUT_BYTES (OUTPUT_PACKET_BYTES * 2)
#define LEGACY_OVERSAMPLE_FACTOR 16U
#define LEGACY_DMA_DESCRIPTORS 8
#define LEGACY_DMA_FRAMES 512
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
unsigned normalizer_configure_calls(void);
unsigned normalizer_reset_calls(void);
unsigned normalizer_process_calls(void);

static unsigned reference_fraction;
static uint8_t reference_channels;
static uint32_t reference_rate = 16000;
static void configure_reference(void) {
    reference_configure(enabled, gain_db, target_dbfs, time_ms, reference_rate);
}
static void reset_reference(void) {
    reference_reset(); reference_channels = 0;
}
static void configure_output(uint32_t rate) {
    bool changed = rate != reference_rate;
    assert(native_audio_output_configure(rate) == ESP_OK);
    assert(s_pcm_sample_rate == rate);
    reference_rate = rate;
    configure_reference();
    if (changed) { reset_reference(); reference_fraction = 0; }
    captured_size = 0; /* Ignore backend silence priming. */
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
static void reference_output(const uint8_t *data, size_t frames, uint8_t channels) {
    if (channels != reference_channels) reference_reset();
    reference_channels = channels;
    for (size_t frame = 0; frame < frames; ++frame) {
        int16_t stereo[2];
        memcpy(stereo, data + frame * channels * 2, channels > 1 ? 4 : 2);
        if (channels == 1) stereo[1] = stereo[0];
        reference_process(stereo);
        int left = reference_scaled(stereo[0], volume,
                                    channels > 1 && balance < 0 ? 16 + balance : 16);
        int right = reference_scaled(stereo[1], volume, balance > 0 ? 16 - balance : 16);
        int16_t sample = (int16_t)(channels > 1 ? (left + right) / 2 : left);
#if TEST_PDM
        append_expected(&sample, sizeof(sample));
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
}

static void check_packet(const uint8_t *data, size_t frames, uint8_t channels) {
    configure_reference();
    captured_size = expected_size = 0; setting_reads = 0;
    unsigned processes = normalizer_process_calls();
    reference_output(data, frames, channels);
    assert(native_audio_output_write_pcm(data, frames * channels * 2 + 1,
                                         16, channels) == ESP_OK);
    assert(setting_reads == 4);
    assert(captured_size == expected_size);
    if (memcmp(captured, expected, captured_size)) {
        size_t first = 0;
        while (first < captured_size && captured[first] == expected[first]) ++first;
        fprintf(stderr, "packet=%u frames=%zu channels=%u mismatch=%zu actual=%u expected=%u\n",
                cases, frames, channels, first, captured[first], expected[first]);
        assert(!"PCM differs from normalizer reference");
    }
    assert(normalizer_process_calls() - processes ==
           (enabled ? (frames + 127) / 128 : 0));
    ++cases;
}

static void reset_output(void) {
    native_audio_output_discard_pcm(); reset_reference(); reference_fraction = 0;
}
static void *request_thread(void *unused) {
    (void)unused;
    for (unsigned index = 0; index < 10000; ++index)
        native_audio_output_request_normalizer_reset();
    return NULL;
}

int main(void) {
    reference_owner();
    assert(sizeof(s_normalizer_scratch) == 512);
    uint8_t *mapping = mmap(NULL, 16384, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(mapping != MAP_FAILED);
    uint8_t *data = mapping + 1;
    for (size_t index = 0; index < 7000; ++index) {
        int16_t value = (int16_t)((index * 157U) % 12000U - 6000);
        memcpy(data + index * 2, &value, 2);
    }
    assert(!mprotect(mapping, 16384, PROT_READ));
    configure_output(16000);
    for (unsigned channel = 1; channel <= 3; ++channel) {
        check_packet(data, 0, (uint8_t)channel);
        check_packet(data, 1, (uint8_t)channel);
        check_packet(data, 129, (uint8_t)channel);
        check_packet(data, 1536, (uint8_t)channel);
    }
    assert(normalizer_process_calls() == 0);
    enabled = true;
    for (unsigned channel = 1; channel <= 3; ++channel) {
        reset_output();
        const size_t frames[] = {0, 1, 127, 128, 129, 500, 1536};
        for (unsigned pass = 0; pass < 8; ++pass)
            for (size_t index = 0; index < sizeof(frames) / sizeof(*frames); ++index)
                check_packet(data, frames[index], (uint8_t)channel);
    }
    /* Independent packet partitioning must preserve the same DSP history. */
    for (uint8_t channel = 1; channel <= 3; ++channel) {
        reset_output(); check_packet(data, 1536, channel);
        uint8_t whole[sizeof(captured)]; size_t whole_size = captured_size;
        memcpy(whole, captured, whole_size);
        reset_output();
        uint8_t pieces[sizeof(captured)]; size_t piece_size = 0, offset = 0;
        const size_t splits[] = {1, 127, 128, 129, 3, 648, 500};
        for (size_t split = 0; split < sizeof(splits) / sizeof(*splits); ++split) {
            check_packet(data + offset * channel * 2, splits[split], channel);
            memcpy(pieces + piece_size, captured, captured_size);
            piece_size += captured_size; offset += splits[split];
        }
        assert(offset == 1536 && piece_size == whole_size);
        assert(!memcmp(pieces, whole, whole_size));
    }
    unsigned configurations = normalizer_configure_calls();
    check_packet(data, 1000, 2); check_packet(data, 1000, 2);
    assert(normalizer_configure_calls() == configurations);
    gain_db = 6; target_dbfs = -12; time_ms = 10000;
    check_packet(data, 1536, 2);
    assert(normalizer_configure_calls() == configurations + 1);
    volume = 127; balance = -7; check_packet(data, 1536, 2);
    balance = 11; check_packet(data, 1536, 2);
    enabled = false; check_packet(data, 1536, 2);
    enabled = true; check_packet(data, 1536, 2);
    /* Control requests never mutate DSP. Only the output thread consumes them. */
    unsigned resets = normalizer_reset_calls();
    native_audio_output_request_normalizer_reset();
    native_audio_output_request_normalizer_reset();
    assert(normalizer_reset_calls() == resets);
    reset_reference(); check_packet(data, 1536, 2);
    assert(normalizer_reset_calls() == resets + 1);
    check_packet(data, 1536, 2);
    assert(normalizer_reset_calls() == resets + 1);
    pthread_t requester;
    assert(!pthread_create(&requester, NULL, request_thread, NULL));
    for (unsigned index = 0; index < 1000; ++index)
        assert(native_audio_output_write_pcm(data, 0, 16, 2) == ESP_OK);
    assert(!pthread_join(requester, NULL));
    native_audio_output_request_normalizer_reset(); reset_reference();
    check_packet(data, 1536, 2);
    /* New rates/layouts, discarded generations and ordered EOF all restart. */
    const uint32_t rates[] = {8000, 11025, 44100, 48000, 16000};
    for (size_t index = 0; index < sizeof(rates) / sizeof(*rates); ++index) {
        configure_output(rates[index]); check_packet(data, 1536, 2);
        check_packet(data, 1536, 1); check_packet(data, 1536, 2);
        reset_output(); check_packet(data, 1536, 2);
        assert(native_audio_output_flush_pcm() == ESP_OK);
        reset_reference(); reference_fraction = 0; check_packet(data, 1536, 2);
    }
    uint32_t before_rate = s_pcm_sample_rate;
    config_result = ESP_FAIL;
    assert(native_audio_output_configure(24000) == ESP_FAIL);
    assert(s_pcm_sample_rate == before_rate);
    config_result = ESP_OK;
#if TEST_DAC
    unsigned allocations = dac_allocations;
    write_result = ESP_FAIL;
    assert(native_audio_output_configure(24000) == ESP_FAIL);
    assert(s_dac_sample_rate == 0 && s_pcm_sample_rate == before_rate);
    write_result = ESP_OK;
    configure_output(24000);
    assert(dac_allocations == allocations + 2);
    assert(s_dac_sample_rate == 24000);
    check_packet(data, 1536, 2);
#endif
    setting_reads = 0;
    unsigned processes = normalizer_process_calls(); resets = normalizer_reset_calls();
    assert(native_audio_output_write_pcm(NULL, 8, 16, 1) == ESP_ERR_NOT_SUPPORTED);
    assert(native_audio_output_write_pcm(data, 8, 20, 1) == ESP_ERR_NOT_SUPPORTED);
    assert(native_audio_output_write_pcm(data, 8, 16, 0) == ESP_ERR_NOT_SUPPORTED);
    assert(!setting_reads && normalizer_process_calls() == processes &&
           normalizer_reset_calls() == resets);
    assert(!munmap(mapping, 16384));
    printf("PASS normalizer: %u packets, mono/stereo/wider layouts, immutable unaligned PCM, "
           "split identity, cached settings, owner-only reset, rate/layout/discard/EOF, scratch=512 bytes\n", cases);
    return 0;
}
