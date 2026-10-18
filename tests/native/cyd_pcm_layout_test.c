/* PLATFORM */
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

/* PRODUCTION */

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
