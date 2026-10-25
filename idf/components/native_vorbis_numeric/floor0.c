// New scaled-product implementation of Vorbis I 6.2.3.
// https://xiph.org/vorbis/doc/Vorbis_I_spec.html
// Reference equations: https://github.com/xiph/vorbis/blob/v1.3.7/lib/lsp.c
#include "native_vorbis_floor0.h"
#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

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

static bool floor0_finish_products(const native_vorbis_scaled_t products[2],
                                   native_vorbis_scaled_t minus,
                                   native_vorbis_scaled_t plus, size_t order,
                                   native_vorbis_scaled_t *result) {
    native_vorbis_scaled_t p, q;
    if (!scaled_product(products[1], products[1], &p) ||
        !scaled_product(products[0], products[0], &q)) return false;
    if (order & 1U) {
        if (!scaled_product(p, minus, &p) || !scaled_product(p, plus, &p))
            return false;
    } else {
        if (!scaled_product(p, minus, &p) || !scaled_product(q, plus, &q))
            return false;
    }
    if (!scaled_normalize(p.mantissa, (int64_t)p.exponent - 2, &p) ||
        !scaled_normalize(q.mantissa, (int64_t)q.exponent - 2, &q)) return false;
    return scaled_sum(p, q, result);
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
    native_vorbis_scaled_t minus, plus;
    if (!scaled_normalize(2.0 - w, 0, &minus) ||
        !scaled_normalize(2.0 + w, 0, &plus))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    native_vorbis_scaled_t result;
    if (!floor0_finish_products(products, minus, plus, order, &result))
        return NATIVE_VORBIS_NUMERIC_RANGE;
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

// Phase = (2*angle/pi) modulo 8. Keep 1152 fractional bits so even DBL_TRUE_MIN
// retains more than 77 significant bits before conversion to a scaled sine.
// A 2304-bit 2/pi constant also leaves >127 guard bits at DBL_MAX. No rounded
// multiple of pi, half of a subnormal, or large floating remainder is formed.
enum { PHASE_FRACTION_WORDS = 36, PHASE_WORDS = 37, PHASE_TABLE_WORDS = 72 };
typedef struct { uint32_t word[PHASE_WORDS]; } floor0_phase_t;

// floor((2/pi)*2^2304), least-significant limb first. Generated with Machin's
// pi formula at 840 decimal digits; the independent tests rederive the value.
static const uint32_t floor0_two_over_pi[PHASE_TABLE_WORDS] = {
    UINT32_C(0x2c5d000c), UINT32_C(0xc4ad414d), UINT32_C(0x9d19c3c2), UINT32_C(0x15c614b5),
    UINT32_C(0x2d30433b), UINT32_C(0xfa6ed577), UINT32_C(0x7c7c246a), UINT32_C(0x87f12190),
    UINT32_C(0xcaf27f1d), UINT32_C(0x9f3a1f35), UINT32_C(0x6b1e5ef8), UINT32_C(0xc33d26ef),
    UINT32_C(0x98327dbb), UINT32_C(0x32c2de4f), UINT32_C(0x3f7e33e8), UINT32_C(0xa5ff0705),
    UINT32_C(0x5719053e), UINT32_C(0xddaf44d1), UINT32_C(0x8b961ca6), UINT32_C(0x8359c476),
    UINT32_C(0xdce8092a), UINT32_C(0x19c367cd), UINT32_C(0x8c6b47c4), UINT32_C(0x60e27bc0),
    UINT32_C(0xca73a8c9), UINT32_C(0x06061556), UINT32_C(0x4d732731), UINT32_C(0x8dffd880),
    UINT32_C(0x14a06840), UINT32_C(0x6599855f), UINT32_C(0x5ee61b08), UINT32_C(0xa9e39161),
    UINT32_C(0x9af4361d), UINT32_C(0xf0cfbc20), UINT32_C(0xfc7b6bab), UINT32_C(0x56033046),
    UINT32_C(0x1f8d5d08), UINT32_C(0x6bfb5fb1), UINT32_C(0x8a5292ea), UINT32_C(0x3d0739f7),
    UINT32_C(0xebe5f17b), UINT32_C(0x7527bac7), UINT32_C(0x9e5fea2d), UINT32_C(0x4f463f66),
    UINT32_C(0x27cb09b7), UINT32_C(0x6d367ecf), UINT32_C(0x5a0a6d1f), UINT32_C(0xef2f118b),
    UINT32_C(0xde05980f), UINT32_C(0x1ff897ff), UINT32_C(0xbdf9283b), UINT32_C(0x9c845f8b),
    UINT32_C(0x835339f4), UINT32_C(0x3991d639), UINT32_C(0xb45f7e41), UINT32_C(0xe99c7026),
    UINT32_C(0x2ebb4484), UINT32_C(0xe88235f5), UINT32_C(0xb129a73e), UINT32_C(0xfe1deb1c),
    UINT32_C(0x09d1921c), UINT32_C(0x06492eea), UINT32_C(0x424dd2e0), UINT32_C(0xb7246e3a),
    UINT32_C(0xdebbc561), UINT32_C(0xfe5163ab), UINT32_C(0x3c439041), UINT32_C(0xdb629599),
    UINT32_C(0xf534ddc0), UINT32_C(0xfc2757d1), UINT32_C(0x4e441529), UINT32_C(0xa2f9836e)
};

static void phase_negate(floor0_phase_t *phase) {
    uint64_t carry = 1;
    for (size_t i = 0; i < PHASE_WORDS; ++i) {
        uint64_t value = (uint64_t)(uint32_t)~phase->word[i] + carry;
        phase->word[i] = (uint32_t)value;
        carry = value >> 32;
    }
    phase->word[PHASE_FRACTION_WORDS] &= 7U;
}

static void phase_combine(const floor0_phase_t *a, const floor0_phase_t *b,
                           bool subtract, floor0_phase_t *result) {
    uint64_t carry = subtract ? 1 : 0;
    for (size_t i = 0; i < PHASE_WORDS; ++i) {
        uint32_t other = subtract ? ~b->word[i] : b->word[i];
        uint64_t value = (uint64_t)a->word[i] + other + carry;
        result->word[i] = (uint32_t)value;
        carry = value >> 32;
    }
    result->word[PHASE_FRACTION_WORDS] &= 7U;
}

static void phase_from_angle(double angle, floor0_phase_t *result) {
    uint64_t bits;
    memcpy(&bits, &angle, sizeof(bits));
    uint32_t exponent = (uint32_t)((bits >> 52) & 2047U);
    uint64_t significand = bits & UINT64_C(0x000fffffffffffff);
    int power = -1074;
    if (exponent) {
        significand |= UINT64_C(0x0010000000000000);
        power = (int)exponent - 1075;
    }
    uint32_t product[PHASE_TABLE_WORDS + 2] = {0};
    for (size_t j = 0; j < 2; ++j) {
        uint32_t multiplier = (uint32_t)(significand >> (32 * j));
        uint64_t carry = 0;
        for (size_t i = 0; i < PHASE_TABLE_WORDS; ++i) {
            // The complete unsigned sum is <= 2^64-1, including both carries.
            uint64_t value = (uint64_t)floor0_two_over_pi[i] * multiplier +
                             product[i + j] + carry;
            product[i + j] = (uint32_t)value;
            carry = value >> 32;
        }
        product[PHASE_TABLE_WORDS + j] = (uint32_t)carry;
    }
    // Right shift is 181..2226 across the complete finite binary64 domain.
    unsigned shift = (unsigned)(32 * (PHASE_TABLE_WORDS - PHASE_FRACTION_WORDS) - power);
    size_t first = shift / 32;
    unsigned offset = shift % 32;
    for (size_t i = 0; i < PHASE_WORDS; ++i) {
        size_t index = first + i;
        uint32_t value = index < PHASE_TABLE_WORDS + 2 ? product[index] >> offset : 0;
        if (offset && index + 1 < PHASE_TABLE_WORDS + 2)
            value |= product[index + 1] << (32 - offset);
        result->word[i] = value;
    }
    result->word[PHASE_FRACTION_WORDS] &= 7U;
    if (bits >> 63) phase_negate(result);
}

static void phase_from_bin(uint32_t bin, uint32_t size, floor0_phase_t *result) {
    uint32_t remainder = 2 * bin;
    result->word[PHASE_FRACTION_WORDS] = remainder / size;
    remainder %= size;
    for (size_t i = PHASE_FRACTION_WORDS; i > 0; --i) {
        uint64_t numerator = (uint64_t)remainder << 32;
        result->word[i - 1] = (uint32_t)(numerator / size);
        remainder = (uint32_t)(numerator % size);
    }
}

static bool phase_sine_magnitude(const floor0_phase_t *phase,
                                 native_vorbis_scaled_t *result) {
    floor0_phase_t distance = *phase;
    if (distance.word[PHASE_FRACTION_WORDS] >= 4) phase_negate(&distance);
    if (distance.word[PHASE_FRACTION_WORDS] >= 2) {
        floor0_phase_t four = {{0}};
        four.word[PHASE_FRACTION_WORDS] = 4;
        phase_combine(&four, &distance, true, &distance);
    }
    int high = PHASE_FRACTION_WORDS;
    while (high >= 0 && !distance.word[high]) --high;
    if (high < 0) { *result = (native_vorbis_scaled_t){0, 0}; return true; }
    // At least 65 significant bits feed the rounded normalized binary64 value.
    // Even an extremely small phase never passes through an ordinary double.
    double fraction = 0;
    for (int i = 0; i < 3 && high - i >= 0; ++i)
        fraction += scalbn((double)distance.word[high - i], -32 * (i + 1));
    native_vorbis_scaled_t value;
    if (!scaled_normalize(fraction, (high + 1 - PHASE_FRACTION_WORDS) * 32, &value))
        return false;
    const double quarter_pi = 0.785398163397448309615660845819875721;
    if (value.exponent < -26) {
        // |x| < (pi/4)*2^-27: |sin(x)/x-1| < 6e-18. Scaling before
        // returning preserves phases below the ordinary subnormal range.
        return scaled_normalize(value.mantissa * quarter_pi, value.exponent, result);
    }
    return scaled_normalize(sin(quarter_pi * scalbn(value.mantissa, value.exponent)),
                            0, result);
}

static bool phase_squared_factor(const floor0_phase_t *phase,
                                 native_vorbis_scaled_t *result) {
    native_vorbis_scaled_t sine;
    return phase_sine_magnitude(phase, &sine) && scaled_product(sine, sine, result) &&
           scaled_normalize(result->mantissa, (int64_t)result->exponent + 2, result);
}

native_vorbis_numeric_status_t native_vorbis_floor0_denominator_at_bin(
    const double *angles, size_t order, uint32_t bin, uint32_t bark_map_size,
    native_vorbis_scaled_t *denominator) {
    if (!angles || !denominator || !order || order > 255 || !bark_map_size ||
        bark_map_size > 65535 || bin >= bark_map_size) return NATIVE_VORBIS_NUMERIC_INVALID;
    for (size_t i = 0; i < order; ++i)
        if (!isfinite(angles[i])) return NATIVE_VORBIS_NUMERIC_INVALID;

    floor0_phase_t bin_phase;
    phase_from_bin(bin, bark_map_size, &bin_phase);
    native_vorbis_scaled_t products[2] = {{0.5, 1}, {0.5, 1}};
    for (size_t i = 0; i < order; ++i) {
        floor0_phase_t angle_phase, combined;
        native_vorbis_scaled_t sum_sine, difference_sine, factor;
        phase_from_angle(angles[i], &angle_phase);
        phase_combine(&angle_phase, &bin_phase, false, &combined);
        if (!phase_sine_magnitude(&combined, &sum_sine)) return NATIVE_VORBIS_NUMERIC_RANGE;
        phase_combine(&angle_phase, &bin_phase, true, &combined);
        if (!phase_sine_magnitude(&combined, &difference_sine) ||
            !scaled_product(sum_sine, difference_sine, &factor) ||
            !scaled_normalize(factor.mantissa, (int64_t)factor.exponent + 2, &factor) ||
            !scaled_product(products[i & 1U], factor, &products[i & 1U]))
            return NATIVE_VORBIS_NUMERIC_RANGE;
    }
    floor0_phase_t endpoint = {{0}};
    endpoint.word[PHASE_FRACTION_WORDS] = 2;
    phase_combine(&endpoint, &bin_phase, true, &endpoint);
    native_vorbis_scaled_t minus, plus, result;
    if (!phase_squared_factor(&bin_phase, &minus) ||
        !phase_squared_factor(&endpoint, &plus) ||
        !floor0_finish_products(products, minus, plus, order, &result))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    *denominator = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor0_gain_from_angles(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const double *angles, size_t order, uint32_t bin, uint32_t bark_map_size,
    native_vorbis_floor0_gain_t *gain) {
    if (!gain || !amplitude_valid(amplitude) || !order || order > 255 ||
        !bark_map_size || bark_map_size > 65535 || bin >= bark_map_size)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (!amplitude->raw_amplitude)
        return native_vorbis_floor0_gain_from_denominator(amplitude, NULL, gain);
    native_vorbis_scaled_t denominator;
    native_vorbis_numeric_status_t status = native_vorbis_floor0_denominator_at_bin(
        angles, order, bin, bark_map_size, &denominator);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    return native_vorbis_floor0_gain_from_denominator(amplitude, &denominator, gain);
}
