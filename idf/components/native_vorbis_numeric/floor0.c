// New scaled-product implementation of Vorbis I 6.2.3.
// https://xiph.org/vorbis/doc/Vorbis_I_spec.html
// Reference equations: https://github.com/xiph/vorbis/blob/v1.3.7/lib/lsp.c
#include "native_vorbis_floor0.h"
#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdbool.h>

_Static_assert(FLT_RADIX == 2 && sizeof(double) == 8 && DBL_MANT_DIG == 53 &&
               DBL_MIN_EXP == -1021 && DBL_MAX_EXP == 1024,
               "Floor0 arithmetic requires IEEE binary64 double");

static const double floor0_pi = 3.141592653589793238462643383279502884;
static const double floor0_db_to_log2 =
    0.11512925 / 0.693147180559945309417232121458176568;

static bool scaled_normalize(double value, int64_t exponent,
                             native_vorbis_scaled_t *result) {
    if (!isfinite(value)) return false;
    if (value == 0.0) {
        *result = (native_vorbis_scaled_t){0.0, 0};
        return true;
    }
    int adjustment;
    double mantissa = frexp(value, &adjustment);
    exponent += adjustment;
    if (exponent < INT32_MIN || exponent > INT32_MAX) return false;
    *result = (native_vorbis_scaled_t){mantissa, (int32_t)exponent};
    return true;
}

static bool scaled_product(native_vorbis_scaled_t a, native_vorbis_scaled_t b,
                           native_vorbis_scaled_t *result) {
    return scaled_normalize(a.mantissa * b.mantissa,
                            (int64_t)a.exponent + b.exponent, result);
}

static bool scaled_sum(native_vorbis_scaled_t a, native_vorbis_scaled_t b,
                       native_vorbis_scaled_t *result) {
    if (a.mantissa == 0.0) { *result = b; return true; }
    if (b.mantissa == 0.0) { *result = a; return true; }
    if (a.exponent < b.exponent) {
        native_vorbis_scaled_t temporary = a; a = b; b = temporary;
    }
    int64_t shift = (int64_t)b.exponent - a.exponent;
    // A normalized mantissa shifted beyond this cannot round a binary64 sum.
    // Avoid narrowing an arbitrary int64 difference to scalbn's int argument.
    double smaller = shift < -1075 ? 0.0 : scalbn(b.mantissa, (int)shift);
    return scaled_normalize(a.mantissa + smaller, a.exponent, result);
}

static bool scaled_valid_nonnegative(const native_vorbis_scaled_t *value) {
    return value && isfinite(value->mantissa) &&
        ((value->mantissa == 0.0 && value->exponent == 0) ||
         (value->mantissa >= 0.5 && value->mantissa < 1.0));
}

static bool amplitude_valid(const native_vorbis_floor0_amplitude_t *value) {
    if (!value || value->amplitude_bits > 63 || value->amplitude_offset > 255)
        return false;
    if (!value->amplitude_bits) return value->raw_amplitude == 0;
    return value->raw_amplitude <= ((UINT64_C(1) << value->amplitude_bits) - 1);
}

static void gain_kind(native_vorbis_floor0_gain_t *gain,
                      native_vorbis_floor0_kind_t kind) {
    *gain = (native_vorbis_floor0_gain_t){kind, {0.0, 0}};
}

native_vorbis_numeric_status_t native_vorbis_floor0_prepare_cosines(
    const double *angles, size_t order, double *coefficients, size_t capacity) {
    if (!angles || !coefficients || !order || order > 255 || capacity < order)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    for (size_t i = 0; i < order; ++i)
        if (!isfinite(angles[i])) return NATIVE_VORBIS_NUMERIC_INVALID;
    for (size_t i = 0; i < order; ++i) coefficients[i] = 2.0 * cos(angles[i]);
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor0_denominator(
    const double *coefficients, size_t order, double w,
    native_vorbis_scaled_t *denominator) {
    if (!coefficients || !denominator || !order || order > 255 ||
        !isfinite(w) || w < -2.0 || w > 2.0)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    for (size_t i = 0; i < order; ++i)
        if (!isfinite(coefficients[i]) || coefficients[i] < -2.0 ||
            coefficients[i] > 2.0) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_scaled_t products[2] = {{0.5, 1}, {0.5, 1}};
    for (size_t i = 0; i < order; ++i) {
        native_vorbis_scaled_t factor;
        if (!scaled_normalize(fabs(w - coefficients[i]), 0, &factor) ||
            !scaled_product(products[i & 1U], factor, &products[i & 1U]))
            return NATIVE_VORBIS_NUMERIC_RANGE;
    }
    native_vorbis_scaled_t p, q, minus, plus;
    if (!scaled_product(products[1], products[1], &p) ||
        !scaled_product(products[0], products[0], &q) ||
        !scaled_normalize(2.0 - w, 0, &minus) ||
        !scaled_normalize(2.0 + w, 0, &plus))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    if (order & 1U) {
        // (4-w*w) is factored, avoiding cancellation in the square.
        if (!scaled_product(p, minus, &p) || !scaled_product(p, plus, &p))
            return NATIVE_VORBIS_NUMERIC_RANGE;
    } else {
        if (!scaled_product(p, minus, &p) || !scaled_product(q, plus, &q))
            return NATIVE_VORBIS_NUMERIC_RANGE;
    }
    if (!scaled_normalize(p.mantissa, (int64_t)p.exponent - 2, &p) ||
        !scaled_normalize(q.mantissa, (int64_t)q.exponent - 2, &q))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    native_vorbis_scaled_t result;
    if (!scaled_sum(p, q, &result)) return NATIVE_VORBIS_NUMERIC_RANGE;
    *denominator = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor0_gain_from_denominator(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const native_vorbis_scaled_t *denominator, native_vorbis_floor0_gain_t *gain) {
    if (!gain || !amplitude_valid(amplitude)) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (!amplitude->raw_amplitude) {
        gain_kind(gain, NATIVE_VORBIS_FLOOR0_ABSENT);
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    if (!scaled_valid_nonnegative(denominator)) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (denominator->mantissa == 0.0) {
        gain_kind(gain, amplitude->amplitude_offset ? NATIVE_VORBIS_FLOOR0_POLE :
                  NATIVE_VORBIS_FLOOR0_INDETERMINATE);
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    if (!amplitude->amplitude_offset) {
        gain_kind(gain, NATIVE_VORBIS_FLOOR0_PRESENT);
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    uint64_t maximum = (UINT64_C(1) << amplitude->amplitude_bits) - 1;
    if (denominator->exponent == 0 || denominator->exponent == 1) {
        // Near D=1, raw/max can round to 1 before a tiny deficit is used.
        // Write raw/max-sqrt(D) as -(max-raw)/max-(sqrt(D)-1), and use
        // sqrt(D)-1=(D-1)/(sqrt(D)+1). This preserves wide-raw near-unity
        // differences without subtracting two prematurely rounded unities.
        double d = scalbn(denominator->mantissa, denominator->exponent);
        double root = sqrt(d);
        double deficit = (double)(maximum - amplitude->raw_amplitude) / (double)maximum;
        double difference = -deficit - (d - 1.0) / (root + 1.0);
        native_vorbis_scaled_t logarithm;
        if (!scaled_normalize((difference / root) * (double)amplitude->amplitude_offset *
                              floor0_db_to_log2, 0, &logarithm))
            return NATIVE_VORBIS_NUMERIC_RANGE;
        *gain = (native_vorbis_floor0_gain_t){NATIVE_VORBIS_FLOOR0_PRESENT, logarithm};
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    double scaled_amplitude = ((double)amplitude->raw_amplitude / (double)maximum) *
                              (double)amplitude->amplitude_offset;
    double mantissa = denominator->mantissa;
    int64_t exponent = denominator->exponent;
    if (exponent % 2) { mantissa *= 2.0; --exponent; }
    native_vorbis_scaled_t term, offset, logarithm;
    if (!scaled_normalize(scaled_amplitude / sqrt(mantissa), -exponent / 2, &term) ||
        !scaled_normalize(-(double)amplitude->amplitude_offset, 0, &offset) ||
        !scaled_sum(term, offset, &logarithm) ||
        !scaled_normalize(logarithm.mantissa * floor0_db_to_log2,
                          logarithm.exponent, &logarithm))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    *gain = (native_vorbis_floor0_gain_t){NATIVE_VORBIS_FLOOR0_PRESENT, logarithm};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor0_gain_at_cosine(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const double *coefficients, size_t order, double w,
    native_vorbis_floor0_gain_t *gain) {
    if (!gain || !amplitude_valid(amplitude) || !order || order > 255)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (!amplitude->raw_amplitude)
        return native_vorbis_floor0_gain_from_denominator(amplitude, NULL, gain);
    native_vorbis_scaled_t denominator;
    native_vorbis_numeric_status_t status = native_vorbis_floor0_denominator(
        coefficients, order, w, &denominator);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    return native_vorbis_floor0_gain_from_denominator(amplitude, &denominator, gain);
}

static double bark(double frequency) {
    return 13.1 * atan(0.00074 * frequency) +
           2.24 * atan(0.0000000185 * frequency * frequency) + 0.0001 * frequency;
}

native_vorbis_numeric_status_t native_vorbis_floor0_bark_map(
    uint32_t rate, size_t bins, uint32_t bark_map_size,
    uint16_t *map, size_t capacity) {
    if (!map || !rate || rate > 65535 || !bins || bins > 4096 ||
        !bark_map_size || bark_map_size > 65535 || capacity < bins)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    double nyquist_bark = bark(0.5 * (double)rate);
    for (size_t i = 0; i < bins; ++i) {
        double frequency = (double)rate * (double)i / (2.0 * (double)bins);
        double position = bark(frequency) * (double)bark_map_size / nyquist_bark;
        // The spec clamps to map_size-1. Check the floating value before cast.
        map[i] = position >= (double)(bark_map_size - 1) ?
                 (uint16_t)(bark_map_size - 1) : (uint16_t)position;
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor0_bin_cosine(
    uint32_t bin, uint32_t bark_map_size, double *w) {
    if (!w || !bark_map_size || bark_map_size > 65535 || bin >= bark_map_size)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (!bin) *w = 2.0;
    else if (2 * bin == bark_map_size) *w = 0.0;
    else if (3 * bin == bark_map_size) *w = 1.0;
    else if (3 * bin == 2 * bark_map_size) *w = -1.0;
    else *w = 2.0 * cos(floor0_pi * (double)bin / (double)bark_map_size);
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor0_gain_at_bin(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const double *coefficients, size_t order, uint32_t bin,
    uint32_t bark_map_size, native_vorbis_floor0_gain_t *gain) {
    double w;
    native_vorbis_numeric_status_t status = native_vorbis_floor0_bin_cosine(
        bin, bark_map_size, &w);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    return native_vorbis_floor0_gain_at_cosine(amplitude, coefficients, order, w, gain);
}
