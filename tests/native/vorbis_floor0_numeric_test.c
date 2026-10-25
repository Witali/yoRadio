// Binary host adapter for the real standalone floor0 numeric component.
// No copied arithmetic, decoder, vendor handle or target firmware is used.
#include "native_vorbis_floor0.h"
#include <assert.h>
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

_Static_assert(sizeof(double) == 8 && DBL_MANT_DIG == 53, "binary64 test adapter");
enum { MAX_ORDER = 255, MAX_BINS = 4096, CHECKS = 7 };
static const uint64_t CANARY = UINT64_C(0xa52d7e19d6034bc8);
typedef struct { uint64_t left; double values[MAX_ORDER]; uint64_t right; } doubles_t;
typedef struct { uint64_t left; native_vorbis_scaled_t value; uint64_t right; } scaled_t;
typedef struct { uint64_t left; native_vorbis_floor0_gain_t value; uint64_t right; } gain_t;
typedef struct { uint64_t left; uint16_t values[MAX_BINS]; uint64_t right; } maps_t;

static uint64_t get(FILE *file, unsigned bytes) {
    uint64_t value = 0;
    for (unsigned i = 0; i < bytes; ++i) {
        int c = fgetc(file); assert(c != EOF); value |= (uint64_t)(unsigned)c << (i * 8);
    }
    return value;
}
static void put(FILE *file, uint64_t value, unsigned bytes) {
    for (unsigned i = 0; i < bytes; ++i) assert(fputc((int)((value >> (i * 8)) & 255), file) != EOF);
}
static double number(uint64_t bits) { double value; memcpy(&value, &bits, 8); return value; }
static uint64_t bits(double value) { uint64_t result; memcpy(&result, &value, 8); return result; }
static native_vorbis_scaled_t get_scaled(FILE *file) {
    double value = number(get(file, 8)); uint32_t raw = (uint32_t)get(file, 4); int32_t exponent;
    memcpy(&exponent, &raw, 4); return (native_vorbis_scaled_t){value, exponent};
}
static void put_scaled(FILE *file, native_vorbis_scaled_t value) {
    put(file, bits(value.mantissa), 8); put(file, (uint32_t)value.exponent, 4);
}
static void arm_doubles(doubles_t *value) {
    memset(value, 0xa5, sizeof(*value)); value->left = value->right = CANARY;
}
static void arm_scaled(scaled_t *value) {
    memset(value, 0xa5, sizeof(*value)); value->left = value->right = CANARY;
}
static void arm_gain(gain_t *value) {
    memset(value, 0xa5, sizeof(*value)); value->left = value->right = CANARY;
}
static void assert_scaled_equal(native_vorbis_scaled_t a, native_vorbis_scaled_t b) {
    assert(bits(a.mantissa) == bits(b.mantissa) && a.exponent == b.exponent);
}
static void assert_gain_equal(native_vorbis_floor0_gain_t a, native_vorbis_floor0_gain_t b) {
    assert(a.kind == b.kind); assert_scaled_equal(a.log2_gain, b.log2_gain);
}

static unsigned metadata_controls(void) {
    unsigned count = 0;
    doubles_t input, output; arm_doubles(&input); arm_doubles(&output);
    input.values[0] = 0.25; input.values[1] = 0.75;
    scaled_t d; arm_scaled(&d);
    gain_t gain; arm_gain(&gain);
    maps_t map; memset(&map, 0xa5, sizeof(map)); map.left = map.right = CANARY;
    native_vorbis_floor0_amplitude_t amplitude = {1, 1, 255};
#define INVALID(call, object) do { \
    unsigned char saved[sizeof(object)]; memcpy(saved, &(object), sizeof(object)); \
    assert((call) == NATIVE_VORBIS_NUMERIC_INVALID); \
    assert(!memcmp(saved, &(object), sizeof(object))); ++count; \
} while (0)
    INVALID(native_vorbis_floor0_prepare_cosines(NULL, 1, output.values, 1), output);
    INVALID(native_vorbis_floor0_prepare_cosines(input.values, 0, output.values, 1), output);
    INVALID(native_vorbis_floor0_prepare_cosines(input.values, 256, output.values, 256), output);
    INVALID(native_vorbis_floor0_prepare_cosines(input.values, 2, output.values, 1), output);
    INVALID(native_vorbis_floor0_prepare_cosines(input.values, 1, NULL, 1), output);
    input.values[1] = NAN;
    INVALID(native_vorbis_floor0_prepare_cosines(input.values, 2, output.values, 2), output);
    INVALID(native_vorbis_floor0_prepare_cosines(input.values, 2, input.values, 2), input);
    input.values[1] = 0.75;
    INVALID(native_vorbis_floor0_denominator(NULL, 1, 0, &d.value), d);
    INVALID(native_vorbis_floor0_denominator(input.values, 0, 0, &d.value), d);
    INVALID(native_vorbis_floor0_denominator(input.values, 256, 0, &d.value), d);
    INVALID(native_vorbis_floor0_denominator(input.values, 2, NAN, &d.value), d);
    INVALID(native_vorbis_floor0_denominator(input.values, 2, INFINITY, &d.value), d);
    INVALID(native_vorbis_floor0_denominator(input.values, 2, 2.01, &d.value), d);
    INVALID(native_vorbis_floor0_denominator(input.values, 2, -2.01, &d.value), d);
    INVALID(native_vorbis_floor0_denominator(input.values, 2, 0, NULL), d);
    input.values[1] = NAN;
    INVALID(native_vorbis_floor0_denominator(input.values, 2, 0, &d.value), d);
    input.values[1] = 2.01;
    INVALID(native_vorbis_floor0_denominator(input.values, 2, 0, &d.value), d);
    input.values[1] = 0.75;
    native_vorbis_scaled_t normal = {0.5, 1};
    INVALID(native_vorbis_floor0_gain_from_denominator(NULL, &normal, &gain.value), gain);
    INVALID(native_vorbis_floor0_gain_from_denominator(&amplitude, NULL, &gain.value), gain);
    INVALID(native_vorbis_floor0_gain_from_denominator(&amplitude, &normal, NULL), gain);
    for (unsigned i = 0; i < 6; ++i) {
        native_vorbis_scaled_t bad[] = {{-0.5,1},{0.25,1},{1,0},{0,1},{NAN,0},{INFINITY,0}};
        INVALID(native_vorbis_floor0_gain_from_denominator(&amplitude, &bad[i], &gain.value), gain);
    }
    native_vorbis_floor0_amplitude_t bad_amplitudes[] = {{1,0,1},{2,1,1},{1,64,1},{1,1,256}};
    for (unsigned i = 0; i < 4; ++i)
        INVALID(native_vorbis_floor0_gain_from_denominator(&bad_amplitudes[i], &normal, &gain.value), gain);
    INVALID(native_vorbis_floor0_gain_at_cosine(&amplitude, NULL, 1, 0, &gain.value), gain);
    INVALID(native_vorbis_floor0_gain_at_cosine(&amplitude, input.values, 0, 0, &gain.value), gain);
    INVALID(native_vorbis_floor0_gain_at_cosine(&amplitude, input.values, 256, 0, &gain.value), gain);
    INVALID(native_vorbis_floor0_gain_at_cosine(&amplitude, input.values, 2, NAN, &gain.value), gain);
    INVALID(native_vorbis_floor0_bark_map(0, 16, 64, map.values, 16), map);
    INVALID(native_vorbis_floor0_bark_map(65536, 16, 64, map.values, 16), map);
    INVALID(native_vorbis_floor0_bark_map(48000, 0, 64, map.values, 16), map);
    INVALID(native_vorbis_floor0_bark_map(48000, 4097, 64, map.values, 4097), map);
    INVALID(native_vorbis_floor0_bark_map(48000, 16, 0, map.values, 16), map);
    INVALID(native_vorbis_floor0_bark_map(48000, 16, 65536, map.values, 16), map);
    INVALID(native_vorbis_floor0_bark_map(48000, 16, 64, map.values, 15), map);
    INVALID(native_vorbis_floor0_bark_map(48000, 16, 64, NULL, 16), map);
    INVALID(native_vorbis_floor0_bin_cosine(0, 0, &output.values[0]), output);
    INVALID(native_vorbis_floor0_bin_cosine(0, 65536, &output.values[0]), output);
    INVALID(native_vorbis_floor0_bin_cosine(64, 64, &output.values[0]), output);
    INVALID(native_vorbis_floor0_bin_cosine(0, 1, NULL), output);
    INVALID(native_vorbis_floor0_gain_at_bin(&amplitude, input.values, 2, 64, 64, &gain.value), gain);
    INVALID(native_vorbis_floor0_gain_at_bin(NULL, input.values, 2, 0, 64, &gain.value), gain);
#undef INVALID
    native_vorbis_floor0_amplitude_t absent = {0,0,255}, absent_copy = absent;
    assert(native_vorbis_floor0_gain_from_denominator(&absent, NULL, &gain.value) == 0);
    assert(gain.value.kind == NATIVE_VORBIS_FLOOR0_ABSENT); ++count;
    assert(!memcmp(&absent, &absent_copy, sizeof(absent)));
    assert(gain.left == CANARY && gain.right == CANARY);
    assert(d.left == CANARY && d.right == CANARY);
    assert(map.left == CANARY && map.right == CANARY);
    assert(input.left == CANARY && input.right == CANARY);
    assert(output.left == CANARY && output.right == CANARY);
    return count;
}

int main(int argc, char **argv) {
    assert(argc == 3);
    FILE *input = fopen(argv[1], "rb"), *output = fopen(argv[2], "wb");
    assert(input && output);
    unsigned char magic[8]; assert(fread(magic, 1, 8, input) == 8);
    assert(!memcmp(magic, "F0NUM001", 8));
    uint32_t count = (uint32_t)get(input, 4); assert(count > 0 && count < 200000);
    assert(fwrite("F0OUT001", 1, 8, output) == 8);
    put(output, count, 4); put(output, metadata_controls(), 4);
    for (uint32_t index = 0; index < count; ++index) {
        uint32_t operation = (uint32_t)get(input, 4);
        put(output, operation, 4); put(output, index, 4);
        if (operation == 1 || operation == 2 || operation == 6) {
            uint64_t raw_amplitude = get(input, 8);
            uint32_t amplitude_bits = (uint32_t)get(input, 4);
            uint32_t amplitude_offset = (uint32_t)get(input, 4);
            native_vorbis_floor0_amplitude_t amplitude = {
                raw_amplitude, amplitude_bits, amplitude_offset};
            native_vorbis_floor0_amplitude_t amplitude_copy = amplitude;
            scaled_t denominator; arm_scaled(&denominator);
            gain_t gain, repeated; arm_gain(&gain); arm_gain(&repeated);
            doubles_t coefficients, saved; arm_doubles(&coefficients);
            uint32_t order = 0, bin = 0, map_size = 0; double w = 0;
            int ds = -99, gs;
            if (operation == 2) {
                denominator.value = get_scaled(input);
                native_vorbis_scaled_t dcopy = denominator.value;
                gs = native_vorbis_floor0_gain_from_denominator(&amplitude, &denominator.value, &gain.value);
                assert_scaled_equal(dcopy, denominator.value);
                assert(native_vorbis_floor0_gain_from_denominator(&amplitude, &denominator.value,
                                                                 &repeated.value) == gs);
            } else {
                order = (uint32_t)get(input, 4); assert(order > 0 && order <= MAX_ORDER);
                if (operation == 1) w = number(get(input, 8));
                else { bin = (uint32_t)get(input, 4); map_size = (uint32_t)get(input, 4); }
                for (uint32_t j = 0; j < order; ++j) coefficients.values[j] = number(get(input, 8));
                memcpy(&saved, &coefficients, sizeof(saved));
                if (operation == 6) assert(native_vorbis_floor0_bin_cosine(bin, map_size, &w) == 0);
                ds = native_vorbis_floor0_denominator(coefficients.values, order, w, &denominator.value);
                assert(ds == 0);
                gs = operation == 1 ?
                    native_vorbis_floor0_gain_at_cosine(&amplitude, coefficients.values, order, w, &gain.value) :
                    native_vorbis_floor0_gain_at_bin(&amplitude, coefficients.values, order, bin, map_size, &gain.value);
                assert(native_vorbis_floor0_gain_from_denominator(&amplitude, &denominator.value,
                                                                 &repeated.value) == gs);
                assert(!memcmp(&saved, &coefficients, sizeof(saved)));
            }
            assert(gs == 0); assert_gain_equal(gain.value, repeated.value);
            assert(!memcmp(&amplitude, &amplitude_copy, sizeof(amplitude)));
            assert(denominator.left == CANARY && denominator.right == CANARY);
            assert(gain.left == CANARY && gain.right == CANARY);
            assert(repeated.left == CANARY && repeated.right == CANARY);
            put(output, (uint32_t)ds, 4); put_scaled(output, denominator.value);
            put(output, (uint32_t)gs, 4); put(output, (uint32_t)gain.value.kind, 4);
            put_scaled(output, gain.value.log2_gain); put(output, bits(w), 8);
            put(output, CHECKS, 4);
        } else if (operation == 3) {
            uint32_t order = (uint32_t)get(input, 4);
            uint32_t inplace = (uint32_t)get(input, 4);
            assert(order > 0 && order <= MAX_ORDER && inplace <= 1);
            doubles_t angles, result, saved; arm_doubles(&angles); arm_doubles(&result);
            for (uint32_t j = 0; j < order; ++j) angles.values[j] = number(get(input, 8));
            memcpy(&saved, &angles, sizeof(saved));
            double *destination = inplace ? angles.values : result.values;
            int status = native_vorbis_floor0_prepare_cosines(angles.values, order, destination, order);
            assert(status == 0);
            if (!inplace) assert(!memcmp(&saved, &angles, sizeof(saved)));
            for (uint32_t j = order; j < MAX_ORDER; ++j) {
                assert(bits(angles.values[j]) == bits(saved.values[j]));
                assert(bits(result.values[j]) == bits(saved.values[j]));
            }
            assert(angles.left == CANARY && angles.right == CANARY);
            assert(result.left == CANARY && result.right == CANARY);
            put(output, (uint32_t)status, 4); put(output, order, 4);
            for (uint32_t j = 0; j < order; ++j) put(output, bits(destination[j]), 8);
            put(output, CHECKS, 4);
        } else if (operation == 4) {
            uint32_t rate = (uint32_t)get(input, 4);
            uint32_t bins = (uint32_t)get(input, 4);
            uint32_t bark_size = (uint32_t)get(input, 4); assert(bins > 0 && bins <= MAX_BINS);
            maps_t map; memset(&map, 0xa5, sizeof(map)); map.left = map.right = CANARY;
            int status = native_vorbis_floor0_bark_map(rate, bins, bark_size, map.values, bins);
            assert(status == 0 && map.left == CANARY && map.right == CANARY);
            for (uint32_t j = bins; j < MAX_BINS; ++j) assert(map.values[j] == UINT16_C(0xa5a5));
            put(output, (uint32_t)status, 4); put(output, bins, 4);
            for (uint32_t j = 0; j < bins; ++j) put(output, map.values[j], 2);
            put(output, CHECKS, 4);
        } else if (operation == 5) {
            uint32_t bin = (uint32_t)get(input, 4);
            uint32_t bark_size = (uint32_t)get(input, 4);
            doubles_t result; arm_doubles(&result);
            int status = native_vorbis_floor0_bin_cosine(bin, bark_size, &result.values[0]);
            assert(status == 0 && result.left == CANARY && result.right == CANARY);
            for (uint32_t j = 1; j < MAX_ORDER; ++j) assert(bits(result.values[j]) == UINT64_C(0xa5a5a5a5a5a5a5a5));
            put(output, (uint32_t)status, 4); put(output, bits(result.values[0]), 8);
            put(output, CHECKS, 4);
        } else {
            assert(!"Unknown binary floor0 test operation");
        }
    }
    assert(fgetc(input) == EOF); assert(!fclose(input)); assert(!fclose(output));
    return 0;
}
