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

/* PRODUCTION */

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
