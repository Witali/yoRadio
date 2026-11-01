/* PLATFORM */
#include <math.h>
#include <float.h>
#include <stdlib.h>
#include <unistd.h>

static unsigned pow_calls;
static double pow_result = 1.0;
static bool pow_fault;
static double observed_pow(double base, double exponent) {
    ++pow_calls;
    return pow_fault ? pow_result : pow(base, exponent);
}
#define PCM_HEADER_GAIN_POW observed_pow

static size_t short_write_bytes = SIZE_MAX;
static unsigned driver_writes;
static int pause_result;
static int test_driver_write(const void *data, size_t size, size_t *written) {
    ++driver_writes;
    if (write_result != ESP_OK) { *written = 0; return write_result; }
    *written = size > short_write_bytes ? short_write_bytes : size;
    return capture(data, *written);
}
static int pdm_release(bool ramp) { (void)ramp; return pause_result; }
static int idf6_dac_output_end(void) { return pause_result; }
#if TEST_PDM
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

/* PRODUCTION */
#include "reference_vectors.h"

void reference_owner(void);
void reference_configure(bool, uint8_t, int8_t, uint16_t, uint32_t);
void reference_reset(void);
void reference_process(int16_t stereo[2]);

static FILE *trace;
static unsigned vector_cases, stream_cases, cache_cases, refusal_cases;
static unsigned reference_fraction;
static uint64_t reference_frames, reference_next_output;
static int16_t reference_previous;
static uint32_t reference_rate = 48000;

static void append_expected(const void *data, size_t bytes) {
    assert(bytes <= sizeof(expected) - expected_size);
    memcpy(expected + expected_size, data, bytes); expected_size += bytes;
}
static int32_t round_signed(int64_t value, int64_t divisor) {
    return (int32_t)(value < 0 ? -((-value + divisor / 2) / divisor)
                               : (value + divisor / 2) / divisor);
}
static void reference_output(int16_t sample) {
#if TEST_PDM
    if (!reference_frames) {
        append_expected(&sample, 2); reference_next_output = 1;
    } else {
        while (reference_next_output * reference_rate <= reference_frames * 48000U) {
            uint64_t phase = reference_next_output * reference_rate -
                             (reference_frames - 1U) * 48000U;
            int64_t fraction = (int64_t)(phase * 44739U + 32768U) / 65536;
            int16_t interpolated = (int16_t)(reference_previous +
                round_signed(((int32_t)sample - reference_previous) * fraction, 32768));
            append_expected(&interpolated, 2); ++reference_next_output;
        }
    }
    reference_previous = sample; ++reference_frames;
#elif TEST_DAC
    int shifted = sample < 0 ? -((-(int)sample + 255) / 256) : sample / 256;
    uint8_t code = (uint8_t)(shifted + 128); append_expected(&code, 1);
#else
    unsigned value = (unsigned)((int)sample + 32768);
    for (unsigned phase = 0; phase < 16; ++phase) {
        unsigned code = value / 256;
        if (code == 255) reference_fraction = 0;
        else { unsigned sum = reference_fraction + value % 256;
               code += sum / 256; reference_fraction = sum % 256; }
        uint32_t packed = code * 0x01000100U; append_expected(&packed, 4);
    }
#endif
}
static void reset_stream(void) {
    native_audio_output_discard_pcm();
    reference_configure(enabled, gain_db, target_dbfs, time_ms, reference_rate);
    reference_reset(); reference_fraction = 0;
    reference_frames = reference_next_output = 0;
    captured_size = expected_size = 0; driver_writes = 0;
}
static void finish_compare(void) {
#if TEST_PDM
    int16_t zero = 0;
    while ((expected_size / 2) % 512) append_expected(&zero, 2);
#endif
    assert(native_audio_output_flush_pcm() == ESP_OK);
    assert(!s_header_gain.active);
    assert(captured_size == expected_size);
    if (memcmp(captured, expected, captured_size)) {
        size_t at = 0;
        while (at < captured_size && captured[at] == expected[at]) ++at;
        fprintf(stderr, "vectors=%u streams=%u mismatch=%zu actual=%u expected=%u\n",
                vector_cases, stream_cases, at, captured[at], expected[at]);
        assert(!"header gain output mismatch");
    }
}
static int16_t project(const uint8_t *p, unsigned bits) {
    uint64_t raw = 0;
    for (unsigned byte = 0; byte < bits / 8; ++byte)
        raw += (uint64_t)p[byte] << (byte * 8);
    int64_t sample = raw & (UINT64_C(1) << (bits - 1))
        ? (int64_t)raw - (INT64_C(1) << bits) : (int64_t)raw;
    if (bits == 8) return (int16_t)(sample * 256);
    int64_t divisor = INT64_C(1) << (bits - 16);
    return (int16_t)(sample < 0 ? -((-sample + divisor - 1) / divisor) : sample / divisor);
}
static int coefficient(unsigned v, unsigned b) {
    return (int)(((int64_t)v * b * 32768 + 2032) / 4064);
}
static int16_t legacy_scale(int16_t sample, unsigned gain) {
    int64_t value = (int64_t)sample * gain;
    return (int16_t)round_signed(value, 32768);
}
static int16_t reference_mono(int16_t left, int16_t right, unsigned channels,
                             int16_t header) {
    unsigned gl = coefficient(volume, channels > 1 && balance < 0 ? 16 + balance : 16);
    unsigned gr = coefficient(volume, balance > 0 ? 16 - balance : 16);
    int16_t result;
    if (!header) {
        int l = legacy_scale(left, gl), r = legacy_scale(right, gr);
        result = (int16_t)(channels > 1 ? (l + r) / 2 : l);
    } else {
        long double factor = powl(10.0L, (long double)header / 5120.0L);
        long double value = ((long double)left * gl +
            (channels > 1 ? (long double)right * gr : 0)) * factor /
            (channels > 1 ? 65536.0L : 32768.0L);
        result = value >= INT16_MAX ? INT16_MAX : value <= INT16_MIN ? INT16_MIN :
            (int16_t)(value >= 0 ? (int32_t)(value + 0.5L) : -(int32_t)(-value + 0.5L));
    }
    fprintf(trace, "%d,%d,%d,%u,%u,%d,%d\n", header, left, right,
            channels, volume, balance, result);
    return result;
}
static void vectors(void) {
    for (size_t n = 0; n < sizeof(vectors_data) / sizeof(*vectors_data); ++n) {
        const gain_vector *v = &vectors_data[n];
        enabled = false; volume = v->volume; balance = v->balance;
        reset_stream();
        uint8_t bytes[255 * 4 + 2] = {0};
        for (unsigned c = 0; c < v->channels; ++c) {
            int64_t projected = c ? v->right : v->left;
            int64_t scalar = v->bits == 8 ? projected / 256 :
                projected * (INT64_C(1) << (v->bits - 16));
            if (v->bits > 16) scalar += (INT64_C(1) << (v->bits - 16)) - 1;
            for (unsigned b = 0; b < v->bits / 8; ++b)
                bytes[1 + c * (v->bits / 8) + b] = (uint8_t)((uint64_t)scalar >> (8 * b));
        }
        assert(native_audio_output_set_header_gain(v->gain) == ESP_OK);
        reference_output(v->expected);
        assert(native_audio_output_write_pcm(bytes + 1,
            v->channels * (v->bits / 8) + (v->channels * (v->bits / 8) > 1 ? 1 : 0),
            v->bits, v->channels) == ESP_OK);
        finish_compare(); ++vector_cases;
    }
}
static void stream_packet(const uint8_t *input, size_t frames, unsigned bits,
                           unsigned channels, int16_t header) {
    assert(native_audio_output_set_header_gain(header) == ESP_OK);
    unsigned calls = pow_calls;
    assert(native_audio_output_set_header_gain(header) == ESP_OK && pow_calls == calls);
    for (size_t frame = 0; frame < frames; ++frame) {
        const uint8_t *p = input + frame * channels * (bits / 8);
        int16_t stereo[2] = {project(p, bits), channels > 1 ? project(p + bits / 8, bits) : project(p, bits)};
        reference_process(stereo);
        reference_output(reference_mono(stereo[0], stereo[1], channels, header));
    }
    assert(native_audio_output_write_pcm(input, frames * channels * (bits / 8), bits, channels) == ESP_OK);
    ++stream_cases;
}
static void streams(void) {
    uint8_t *mapping = mmap(NULL, 32768, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(mapping != MAP_FAILED); uint8_t *input = mapping + 1;
    for (size_t n = 0; n < 32760; ++n) input[n] = (uint8_t)(n * 137U + n / 11U);
    assert(!mprotect(mapping, 32768, PROT_READ));
    const unsigned widths[] = {8, 16, 24, 32};
    const unsigned layouts[] = {1, 2, 3};
    for (unsigned normalize = 0; normalize < 2; ++normalize)
        for (unsigned width = 0; width < 4; ++width)
            for (unsigned layout = 0; layout < 3; ++layout) {
                enabled = normalize; volume = 1; balance = -7;
                unsigned bits = widths[width], channels = layouts[layout];
                reset_stream();
                stream_packet(input, 513, bits, channels, 48 * 256);
                stream_packet(input, 129, bits, channels, -6 * 256);
                volume = 127; balance = 11;
                stream_packet(input, 513, bits, channels, 0);
                stream_packet(input, 129, bits, channels, INT16_MIN);
                volume = 0; stream_packet(input, 129, bits, channels, INT16_MAX);
                finish_compare();
                /* Whole/split writes preserve DSP, resampler and diffusion history. */
                volume = 127; balance = 0;
                for (unsigned split = 0; split < 2; ++split) {
                    reset_stream();
                    if (!split) stream_packet(input, 513, bits, channels, 6 * 256);
                    else { stream_packet(input, 127, bits, channels, 6 * 256);
                           stream_packet(input + 127 * channels * (bits / 8), 386, bits, channels, 6 * 256); }
                    finish_compare();
                }
            }
    assert(!munmap(mapping, 32768));
}
static void cache_and_failures(void) {
    enabled = false; reset_stream();
    assert(!s_header_gain.active);
    for (int gain = INT16_MIN; gain <= INT16_MAX; ++gain) {
        unsigned before = pow_calls;
        assert(native_audio_output_set_header_gain((int16_t)gain) == ESP_OK);
        assert(isfinite(s_header_gain.factor) && s_header_gain.factor > 0);
        assert(pow_calls == before + (gain != 0));
        assert(native_audio_output_set_header_gain((int16_t)gain) == ESP_OK);
        assert(pow_calls == before + (gain != 0)); ++cache_cases;
    }
    assert(native_audio_output_set_header_gain(6 * 256) == ESP_OK);
    const double refusals[] = {NAN, INFINITY, -INFINITY, 0.0, -1.0, DBL_MAX};
    pcm_header_gain saved = s_header_gain;
    for (unsigned n = 0; n < sizeof(refusals) / sizeof(*refusals); ++n) {
        pow_fault = true; pow_result = refusals[n];
        assert(native_audio_output_set_header_gain(7 * 256) == ESP_FAIL);
        assert(!memcmp(&saved, &s_header_gain, sizeof(saved))); ++refusal_cases;
    }
    pow_fault = false;
    /* A refused calibration must leave the previous gain usable for PCM. */
    volume = 127; balance = 0;
    const int16_t previous[2] = {25000, 25000};
    captured_size = expected_size = 0;
    reference_frames = reference_next_output = 0; reference_fraction = 0;
    reference_output(reference_mono(previous[0], previous[1], 2, 6 * 256));
    assert(native_audio_output_write_pcm((const uint8_t *)previous, sizeof(previous), 16, 2) == ESP_OK);
    finish_compare();
    native_audio_output_discard_pcm(); assert(!s_header_gain.active);
    assert(native_audio_output_set_header_gain(0) == ESP_OK && s_header_gain.factor == 1);
    uint8_t pcm[2048] = {0};
    assert(native_audio_output_set_header_gain(6 * 256) == ESP_OK);
    atomic_store(&s_pause_requested, true);
    assert(native_audio_output_write_pcm(pcm, 4, 16, 2) == ESP_ERR_INVALID_STATE);
    assert(s_header_gain.gain_q8 == 6 * 256); atomic_store(&s_pause_requested, false);
    assert(native_audio_output_write_pcm(NULL, 4, 16, 2) == ESP_ERR_NOT_SUPPORTED);
    assert(s_header_gain.gain_q8 == 6 * 256);
    write_result = ESP_FAIL;
    assert(native_audio_output_write_pcm(pcm, sizeof(pcm), 16, 1) == ESP_FAIL);
    assert(s_header_gain.gain_q8 == 6 * 256);
    native_audio_output_discard_pcm(); assert(!s_header_gain.active);
    write_result = ESP_OK;
    assert(native_audio_output_set_header_gain(6 * 256) == ESP_OK);
    short_write_bytes = 1;
    assert(native_audio_output_write_pcm(pcm, sizeof(pcm), 16, 1) == ESP_FAIL);
    assert(s_header_gain.gain_q8 == 6 * 256);
    short_write_bytes = SIZE_MAX; native_audio_output_discard_pcm();
#if TEST_PDM
    assert(native_audio_output_set_header_gain(6 * 256) == ESP_OK);
    assert(native_audio_output_write_pcm(pcm, 2, 16, 1) == ESP_OK);
    write_result = ESP_FAIL;
    assert(native_audio_output_flush_pcm() == ESP_FAIL);
    assert(!s_header_gain.active); write_result = ESP_OK;
#endif
    assert(native_audio_output_set_header_gain(6 * 256) == ESP_OK);
    pause_result = ESP_FAIL;
    assert(native_audio_output_pause() == ESP_FAIL); assert(!s_header_gain.active);
    pause_result = ESP_OK;
    assert(native_audio_output_set_header_gain(6 * 256) == ESP_OK);
    assert(native_audio_output_pause() == ESP_OK); assert(!s_header_gain.active);
}
int main(int argc, char **argv) {
    assert(argc == 2); trace = fopen(argv[1], "w"); assert(trace);
    reference_owner();
    assert(native_audio_output_configure(48000) == ESP_OK);
    vectors(); streams(); cache_and_failures();
    assert(!fclose(trace));
    printf("PASS header gain: %u Decimal vectors, %u stream packets, %u cached gain transitions, "
           "%u transactional math refusals; immutable PCM, preserved normalization, split/order/lifecycle/failure controls\n",
           vector_cases, stream_cases, cache_cases, refusal_cases);
    return 0;
}
