#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_NOT_SUPPORTED -2
#define ESP_ERR_INVALID_STATE -3
#define pdMS_TO_TICKS(t) (t)
#define ESP_RETURN_ON_ERROR(call, tag, message) do { \
    esp_err_t result_ = (call); if (result_ != ESP_OK) return result_; \
} while (0)

static uint8_t volume;
static int8_t balance;
static unsigned gain_calls, volume_reads, balance_reads;
static uint8_t captured[3072 * 16 * 4], expected[sizeof(captured)];
static size_t captured_size, expected_size;
static uint8_t dac_storage[3072];
static uint8_t *s_dac_data = dac_storage;
static int s_dac;
static bool s_legacy_installed = true;
static uint32_t legacy_storage[1536];
static uint32_t *s_legacy_frames = legacy_storage;
static uint16_t s_legacy_fractional_error;
static uint8_t native_audio_settings_get_volume(void) { ++volume_reads; return volume; }
static int8_t native_audio_settings_get_balance(void) { ++balance_reads; return balance; }
static bool native_audio_settings_get_normalization(void) { return false; }
static uint8_t native_audio_settings_get_normalization_gain_db(void) { return 20; }
static int8_t native_audio_settings_get_normalization_target_dbfs(void) { return -3; }
static uint16_t native_audio_settings_get_normalization_time_ms(void) { return 5000; }
static void native_audio_normalizer_configure(bool enabled, uint8_t gain,
    int8_t target, uint16_t time, uint32_t rate) {
    (void)gain; (void)target; (void)time; (void)rate; assert(!enabled);
}
static void native_audio_normalizer_reset(void) {}
static void native_audio_normalizer_process_block(int16_t *pcm, size_t frames,
                                                   uint8_t channels) {
    (void)pcm; (void)frames; (void)channels;
    assert(!"disabled normalization must not process or copy PCM");
}

static int capture(const void *data, size_t size) {
    assert(size <= sizeof(captured) - captured_size);
    memcpy(captured + captured_size, data, size);
    captured_size += size;
    return ESP_OK;
}
static int pdm_write_resampled(int16_t sample) { return capture(&sample, sizeof(sample)); }
static int dac_continuous_write(int handle, const void *data, size_t size,
                                 size_t *written, unsigned timeout) {
    (void)handle; (void)timeout; *written = size;
    return capture(data, size);
}
static int idf6_dac_output_write(const void *data, size_t size,
                                 size_t *written, unsigned timeout) {
    return dac_continuous_write(0, data, size, written, timeout);
}

#define OUTPUT_PACKET_BYTES 3072
#define SAMPLE_GAIN_SCALE 32768U
#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U
#define NORMALIZER_CHUNK_FRAMES 128U
#define LEGACY_OUTPUT_BYTES (OUTPUT_PACKET_BYTES * 2)
#define LEGACY_OVERSAMPLE_FACTOR 16U
static int16_t scale_sample_q15(int16_t sample, uint32_t gain_q15) {
    int32_t scaled = (int32_t)sample * (int32_t)gain_q15;
    if (scaled >= 0) {
        return (int16_t)((scaled + SAMPLE_GAIN_SCALE / 2U) /
                         SAMPLE_GAIN_SCALE);
    }
    return (int16_t)-(((-scaled) + SAMPLE_GAIN_SCALE / 2U) /
                      SAMPLE_GAIN_SCALE);
}

static uint32_t production_channel_gain_q15(uint8_t volume, uint8_t balance_gain) {
    const uint32_t denominator =
        VOLUME_DENOMINATOR * BALANCE_DENOMINATOR;
    uint32_t numerator = (uint32_t)volume * balance_gain;
    return (numerator * SAMPLE_GAIN_SCALE + denominator / 2U) / denominator;
}

typedef struct {
    uint32_t left;
    uint32_t right;
} pcm_gains_t;


static uint32_t channel_gain_q15(uint8_t volume, uint8_t balance) {
    ++gain_calls;
    return production_channel_gain_q15(volume, balance);
}
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
    size_t buffered = 0;
    for (size_t frame = 0; frame < frames; ++frame) {
        int32_t value = (pcm_reader_next(&reader) >> 8) + 128;
        if (value < 0) value = 0;
        if (value > 255) value = 255;
        s_dac_data[buffered++] = (uint8_t)value;
        if (buffered == OUTPUT_PACKET_BYTES) {
            if (atomic_load(&s_pause_requested)) return ESP_ERR_INVALID_STATE;
            size_t written = 0;
            esp_err_t result = dac_continuous_write(s_dac, s_dac_data, buffered,
                                                    &written, 1000);
            if (result != ESP_OK) return result;
            if (written != buffered) return ESP_FAIL;
            buffered = 0;
        }
    }
    if (!buffered) return ESP_OK;
    if (atomic_load(&s_pause_requested)) return ESP_ERR_INVALID_STATE;
    size_t written = 0;
    esp_err_t result = dac_continuous_write(s_dac, s_dac_data, buffered,
                                            &written, 1000);
    if (result != ESP_OK) return result;
    return written == buffered ? ESP_OK : ESP_FAIL;
}


static int16_t reference_scaled(int16_t sample, unsigned v, unsigned b) {
    /* The public Q15 law has one coefficient rounding and symmetric sample
       rounding. Use wide arithmetic independently of the production helpers. */
    int64_t coefficient = ((int64_t)v * b * 32768 + 2032) / 4064;
    int64_t value = (int64_t)sample * coefficient;
    return (int16_t)(value < 0 ? -((-value + 16384) / 32768)
                               : (value + 16384) / 32768);
}
static int16_t reference_mono(const uint8_t *p, unsigned channels,
                              unsigned v, int b) {
    int16_t samples[2];
    memcpy(samples, p, channels > 1 ? sizeof(samples) : sizeof(samples[0]));
    if (channels == 1) return reference_scaled(samples[0], v, 16);
    int left = reference_scaled(samples[0], v, b < 0 ? (unsigned)(16 + b) : 16);
    int right = reference_scaled(samples[1], v, b > 0 ? (unsigned)(16 - b) : 16);
    return (int16_t)((left + right) / 2);
}

static unsigned long long arithmetic_cases;
static void check_sample(int16_t left, int16_t right, uint8_t channels,
                         unsigned v, int b) {
    uint8_t unaligned[8];
    memcpy(unaligned + 1, &left, sizeof(left));
    memcpy(unaligned + 3, &right, sizeof(right));
    pcm_gains_t gains = pcm_channel_gains(channels, (uint8_t)v, (int8_t)b);
    unsigned calls = gain_calls;
    assert(pcm_mono_sample(unaligned + 1, channels, &gains) ==
           reference_mono(unaligned + 1, channels, v, b));
    assert(gain_calls == calls); /* Coefficients are not evaluated per frame. */
    ++arithmetic_cases;
}

static void append_expected(const void *data, size_t bytes) {
    assert(bytes <= sizeof(expected) - expected_size);
    memcpy(expected + expected_size, data, bytes);
    expected_size += bytes;
}
static void reference_output(const uint8_t *data, size_t frames, uint8_t channels,
                               unsigned *fraction) {
    for (size_t index = 0; index < frames; ++index) {
        int16_t sample = reference_mono(data + index * channels * 2, channels,
                                       volume, balance);
#if TEST_PDM
        (void)fraction;
        append_expected(&sample, sizeof(sample));
#elif TEST_DAC
        (void)fraction;
        int value = sample < 0 ? -((-(int)sample + 255) / 256) : sample / 256;
        uint8_t code = (uint8_t)(value + 128);
        append_expected(&code, sizeof(code));
#else
        unsigned value = (unsigned)((int)sample + 32768);
        for (unsigned phase = 0; phase < 16; ++phase) {
            unsigned code = value / 256;
            if (code == 255) {
                *fraction = 0;
            } else {
                unsigned sum = *fraction + value % 256;
                code += sum / 256;
                *fraction = sum % 256;
            }
            uint32_t packed = code * 0x01000100U;
            append_expected(&packed, sizeof(packed));
        }
#endif
    }
}

static void check_output(uint8_t channels, size_t frames, unsigned v, int b) {
    uint8_t storage[3072 * 6 + 2];
    uint8_t *data = storage + 1; /* The real producer must tolerate unaligned PCM. */
    for (size_t index = 0; index < frames * channels; ++index) {
        int16_t sample = (int16_t)(index * 9973U + v * 17U + (unsigned)(b + 16));
        memcpy(data + index * 2, &sample, sizeof(sample));
    }
    volume = (uint8_t)v; balance = (int8_t)b;
    captured_size = expected_size = 0;
    s_legacy_fractional_error = 0;
    unsigned fraction = 0;
    const size_t split = frames / 3;
    const size_t sizes[] = {split, frames - split};
    size_t offset = 0;
    for (unsigned part = 0; part < 2; ++part) {
        gain_calls = volume_reads = balance_reads = 0;
        /* A trailing byte is not a complete frame and must not produce PCM. */
        assert(native_audio_output_write_pcm(data + offset * channels * 2,
                   sizes[part] * channels * 2 + 1, 16, channels) == ESP_OK);
        assert(gain_calls == (channels > 1 ? 2u : 1u));
        assert(volume_reads == 1 && balance_reads == 1);
        reference_output(data + offset * channels * 2, sizes[part], channels, &fraction);
        offset += sizes[part];
    }
    assert(captured_size == expected_size);
    assert(!memcmp(captured, expected, captured_size));
}

int main(void) {
    const int16_t edge[] = {INT16_MIN, -32767, -30001, -1234, -1, 0, 1, 1234, 30001, INT16_MAX};
    for (unsigned v = 0; v <= 254; ++v)
        for (int b = -16; b <= 16; ++b)
            for (unsigned channels = 1; channels <= 3; ++channels)
                for (size_t l = 0; l < sizeof(edge) / sizeof(*edge); ++l)
                    for (size_t r = 0; r < sizeof(edge) / sizeof(*edge); ++r)
                        check_sample(edge[l], edge[r], (uint8_t)channels, v, b);
    const unsigned volumes[] = {0, 1, 127, 192, 254};
    const int balances[] = {-16, -1, 0, 1, 16};
    for (size_t v = 0; v < sizeof(volumes) / sizeof(*volumes); ++v)
        for (size_t b = 0; b < sizeof(balances) / sizeof(*balances); ++b)
            for (int sample = INT16_MIN; sample <= INT16_MAX; ++sample) {
                int16_t right = (int16_t)(sample ^ 0x5a5a);
                check_sample((int16_t)sample, right, 1, volumes[v], balances[b]);
                check_sample((int16_t)sample, right, 2, volumes[v], balances[b]);
            }
    unsigned output_cases = 0;
    const size_t frames[] = {0, 1, 97, 1024, 3072};
    for (unsigned channels = 1; channels <= 3; ++channels)
        for (size_t v = 0; v < sizeof(volumes) / sizeof(*volumes); ++v)
            for (size_t b = 0; b < sizeof(balances) / sizeof(*balances); ++b)
                for (size_t count = 0; count < sizeof(frames) / sizeof(*frames); ++count) {
                    check_output((uint8_t)channels, frames[count], volumes[v], balances[b]);
                    ++output_cases;
                }
    gain_calls = volume_reads = balance_reads = 0;
    uint8_t data[8] = {0};
    assert(native_audio_output_write_pcm(NULL, 4, 16, 1) == ESP_ERR_NOT_SUPPORTED);
    assert(native_audio_output_write_pcm(data, 4, 20, 1) == ESP_ERR_NOT_SUPPORTED);
    assert(native_audio_output_write_pcm(data, 4, 16, 0) == ESP_ERR_NOT_SUPPORTED);
    assert(!gain_calls && !volume_reads && !balance_reads);
    printf("PASS PCM gain: %llu arithmetic cases, %u output cases, bounded coefficient evaluations\n",
           arithmetic_cases, output_cases);
    return 0;
}
