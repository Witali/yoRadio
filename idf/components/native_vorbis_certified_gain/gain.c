// Vorbis I 6.2.3 with stable half-angle products and directed enclosures.
#include "native_vorbis_certified_gain.h"
#include <string.h>

#define WORKSPACE_COOKIE UINT64_C(0x766761696e323032)
#define RESULT_COOKIE UINT64_C(0x766761696e726573)
typedef native_vorbis_interval_status_t status_t;
typedef native_vorbis_interval_t interval_t;
typedef native_vorbis_interval_scope_t scope_t;

static bool active(const native_vorbis_gain_workspace_t *w) {
    return w && w->cookie == WORKSPACE_COOKIE;
}
static bool owned(const native_vorbis_gain_workspace_t *w, const native_vorbis_gain_result_t *r) {
    return active(w) && r && r->cookie == RESULT_COOKIE && r->owner == w && w->result_owners;
}
static status_t scope_at(native_vorbis_gain_workspace_t *w, uint32_t p, scope_t *s) {
    if (!active(w)) return NATIVE_VORBIS_INTERVAL_INVALID;
    return native_vorbis_interval_scope_init(&w->arithmetic, p, s);
}
static status_t pair_init(const scope_t *s, interval_t *x) {
    return native_vorbis_interval_init(s, x);
}
static void pair_clear(const scope_t *s, interval_t *x) {
    // These private descriptors are initialized and only hold checked finite values.
    (void)native_vorbis_interval_clear(s, x);
}
static status_t result_check(const scope_t *s, const native_vorbis_gain_result_t *r) {
    status_t st = native_vorbis_interval_check(s, &r->denominator);
    return st == NATIVE_VORBIS_INTERVAL_OK ? native_vorbis_interval_check(s, &r->log2_gain) : st;
}
static void prepared_result(const scope_t *s, native_vorbis_gain_result_t *r, uint32_t p) {
    memset(r, 0, sizeof(*r));
    (void)pair_init(s, &r->denominator);
    (void)pair_init(s, &r->log2_gain);
    r->precision = p;
}
static void commit_result(const scope_t *s, native_vorbis_gain_result_t *r,
                          native_vorbis_gain_result_t *prepared) {
    // Both pairs were validated before preparation. No fallible work follows.
    (void)native_vorbis_interval_swap(s, &r->denominator, &prepared->denominator);
    (void)native_vorbis_interval_swap(s, &r->log2_gain, &prepared->log2_gain);
    r->kind = prepared->kind;
    r->has_denominator = prepared->has_denominator;
    r->has_log = prepared->has_log;
    r->precision = prepared->precision;
}

native_vorbis_bigfloat_status_t native_vorbis_gain_workspace_init(
    native_vorbis_gain_workspace_t *w, const native_vorbis_bigfloat_allocator_t *allocator) {
    if (!w || !allocator || !allocator->allocate || !allocator->release) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_bigfloat_allocator_t copy = *allocator;
    memset(w, 0, sizeof(*w));
    native_vorbis_bigfloat_status_t st = native_vorbis_bigfloat_context_init(&w->arithmetic, &copy);
    if (st != NATIVE_VORBIS_BIGFLOAT_OK) return st;
    scope_t s;
    (void)native_vorbis_interval_scope_init(&w->arithmetic, 2, &s);
    (void)pair_init(&s, &w->pi);
    (void)pair_init(&s, &w->ln2);
    w->cookie = WORKSPACE_COOKIE;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}
native_vorbis_bigfloat_status_t native_vorbis_gain_clear_failure(native_vorbis_gain_workspace_t *w) {
    if (!active(w)) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    return native_vorbis_bigfloat_clear_failure(&w->arithmetic);
}
native_vorbis_bigfloat_status_t native_vorbis_gain_workspace_end(native_vorbis_gain_workspace_t *w) {
    if (!active(w) || w->result_owners) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    scope_t s;
    status_t st = scope_at(w, 2, &s);
    if (st) return (native_vorbis_bigfloat_status_t)st;
    pair_clear(&s, &w->pi);
    pair_clear(&s, &w->ln2);
    w->cached_precision = 0;
    native_vorbis_bigfloat_status_t end = native_vorbis_bigfloat_context_end(&w->arithmetic);
    if (end == NATIVE_VORBIS_BIGFLOAT_OK) w->cookie = 0;
    return end;
}
native_vorbis_bigfloat_status_t native_vorbis_gain_result_init(
    native_vorbis_gain_workspace_t *w, native_vorbis_gain_result_t *r) {
    if (!active(w) || !r) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    if (w->result_owners == SIZE_MAX) return NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
    scope_t s;
    status_t st = scope_at(w, 2, &s);
    if (st) return (native_vorbis_bigfloat_status_t)st;
    prepared_result(&s, r, 0);
    r->owner = w;
    r->cookie = RESULT_COOKIE;
    r->kind = NATIVE_VORBIS_GAIN_ABSENT;
    ++w->result_owners;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}
native_vorbis_bigfloat_status_t native_vorbis_gain_result_clear(
    native_vorbis_gain_workspace_t *w, native_vorbis_gain_result_t *r) {
    if (!owned(w, r)) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    scope_t s;
    status_t st = scope_at(w, 2, &s);
    if (!st) st = result_check(&s, r);
    if (st) return (native_vorbis_bigfloat_status_t)st;
    pair_clear(&s, &r->denominator);
    pair_clear(&s, &r->log2_gain);
    memset(r, 0, sizeof(*r));
    --w->result_owners;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

static bool amplitude_valid(const native_vorbis_floor0_amplitude_t *a) {
    return a->amplitude_bits <= 63 && a->amplitude_offset <= 255 &&
        (a->amplitude_bits ? a->raw_amplitude <= (UINT64_C(1) << a->amplitude_bits) - 1 : !a->raw_amplitude);
}
typedef struct { uint64_t magnitude; int32_t exponent; bool negative; } term_t;
static term_t term(uint32_t packed, uint32_t multiplier) {
    term_t t = {(uint64_t)(packed & UINT32_C(0x1fffff)) * multiplier,
                (int32_t)((packed >> 21) & 1023U) - 788, (packed >> 31) != 0};
    if (t.magnitude) while (!(t.magnitude & 1)) { t.magnitude >>= 1; ++t.exponent; }
    return t;
}
static bool affine_zero(const native_vorbis_affine_t *a) {
    term_t x = term(a->minimum_bits, a->minimum_multiplier), y = term(a->delta_bits, a->delta_multiplier);
    if (!x.magnitude || !y.magnitude) return !x.magnitude && !y.magnitude;
    return x.negative != y.negative && x.exponent == y.exponent && x.magnitude == y.magnitude;
}
static status_t exact_affine(const scope_t *s, interval_t *r, const native_vorbis_affine_t *a) {
    term_t terms[2] = {term(a->minimum_bits, a->minimum_multiplier), term(a->delta_bits, a->delta_multiplier)};
    bf_t values[3];
    for (size_t i = 0; i < 3; ++i) (void)native_vorbis_bigfloat_init(s->context, &values[i]);
    native_vorbis_bigfloat_status_t st = NATIVE_VORBIS_BIGFLOAT_OK;
    for (size_t i = 0; i < 2 && !st; ++i) {
        uint64_t m = terms[i].magnitude;
        uint32_t words[2] = {(uint32_t)m, (uint32_t)(m >> 32)};
        size_t count = words[1] ? 2 : words[0] ? 1 : 0;
        st = native_vorbis_bigfloat_import(s->context, &values[i], words, count,
            count ? terms[i].exponent : 0, count && terms[i].negative);
    }
    // Each product has <=53 bits; packed exponents span1023. The exact
    // two-term sum has <=1077 significant bits, including a possible carry.
    if (!st) st = native_vorbis_bigfloat_add(s->context, &values[2], &values[0], &values[1],
                                           1100, NATIVE_VORBIS_BIGFLOAT_DOWN);
    status_t out = (status_t)st;
    if (!out) out = native_vorbis_interval_bounds(s, r, &values[2], &values[2]);
    for (size_t i = 0; i < 3; ++i) (void)native_vorbis_bigfloat_clear(s->context, &values[i]);
    return out;
}

static status_t constants(native_vorbis_gain_workspace_t *w, const scope_t *s) {
    if (w->cached_precision == s->precision) return NATIVE_VORBIS_INTERVAL_OK;
    interval_t pi, ln2;
    (void)pair_init(s, &pi); (void)pair_init(s, &ln2);
    status_t st = native_vorbis_interval_pi(s, &pi);
    if (!st) st = native_vorbis_interval_ln2(s, &ln2);
    if (!st) {
        (void)native_vorbis_interval_swap(s, &w->pi, &pi);
        (void)native_vorbis_interval_swap(s, &w->ln2, &ln2);
        w->cached_precision = s->precision;
    }
    pair_clear(s, &pi); pair_clear(s, &ln2);
    return st;
}

// D=(O*minus*plus+E)/4 for odd order, (O*minus+E*plus)/4 for
// positive even order; minus=4sin²(theta/2), plus=4cos²(theta/2).
static status_t denominator(const scope_t *s, const interval_t *pi,
    const native_vorbis_gain_input_t *input, interval_t *d) {
    enum { THETA, MAP, BIN, HALF, MINUS, PLUS, EVEN, ODD, PHI, U, V, SU, SV, FACTOR, SQUARE, P, Q, COUNT };
    interval_t x[COUNT];
    for (size_t i = 0; i < COUNT; ++i) (void)pair_init(s, &x[i]);
    status_t st = NATIVE_VORBIS_INTERVAL_OK;
#define DO(call) do { st = (call); if (st) goto done; } while (0)
    if (!input->order) { DO(native_vorbis_interval_set_u64(s, d, 1)); goto done; }
    DO(native_vorbis_interval_set_u64(s, &x[BIN], input->bark_index));
    DO(native_vorbis_interval_set_u64(s, &x[MAP], input->bark_map_size));
    DO(native_vorbis_interval_mul(s, &x[THETA], pi, &x[BIN]));
    DO(native_vorbis_interval_div(s, &x[THETA], &x[THETA], &x[MAP]));
    DO(native_vorbis_interval_scale2(s, &x[HALF], &x[THETA], -1));
    DO(native_vorbis_interval_sin(s, &x[MINUS], &x[HALF], pi));
    DO(native_vorbis_interval_square(s, &x[MINUS], &x[MINUS]));
    DO(native_vorbis_interval_scale2(s, &x[MINUS], &x[MINUS], 2));
    DO(native_vorbis_interval_cos(s, &x[PLUS], &x[HALF], pi));
    DO(native_vorbis_interval_square(s, &x[PLUS], &x[PLUS]));
    DO(native_vorbis_interval_scale2(s, &x[PLUS], &x[PLUS], 2));
    DO(native_vorbis_interval_set_u64(s, &x[EVEN], 1));
    DO(native_vorbis_interval_set_u64(s, &x[ODD], 1));
    for (size_t i = 0; i < input->order; ++i) {
        DO(exact_affine(s, &x[PHI], &input->angles[i]));
        DO(native_vorbis_interval_add(s, &x[U], &x[THETA], &x[PHI]));
        DO(native_vorbis_interval_sub(s, &x[V], &x[THETA], &x[PHI]));
        DO(native_vorbis_interval_scale2(s, &x[U], &x[U], -1));
        DO(native_vorbis_interval_scale2(s, &x[V], &x[V], -1));
        DO(native_vorbis_interval_sin(s, &x[SU], &x[U], pi));
        DO(native_vorbis_interval_sin(s, &x[SV], &x[V], pi));
        DO(native_vorbis_interval_mul(s, &x[FACTOR], &x[SU], &x[SV]));
        DO(native_vorbis_interval_scale2(s, &x[FACTOR], &x[FACTOR], 2));
        DO(native_vorbis_interval_square(s, &x[SQUARE], &x[FACTOR]));
        size_t product = i & 1U ? ODD : EVEN;
        DO(native_vorbis_interval_mul(s, &x[product], &x[product], &x[SQUARE]));
    }
    DO(native_vorbis_interval_mul(s, &x[P], &x[ODD], &x[MINUS]));
    if (input->order & 1U) {
        DO(native_vorbis_interval_mul(s, &x[P], &x[P], &x[PLUS]));
        DO(native_vorbis_interval_copy(s, &x[Q], &x[EVEN]));
    } else DO(native_vorbis_interval_mul(s, &x[Q], &x[EVEN], &x[PLUS]));
    DO(native_vorbis_interval_add(s, &x[P], &x[P], &x[Q]));
    DO(native_vorbis_interval_scale2(s, d, &x[P], -2));
done:
    for (size_t i = 0; i < COUNT; ++i) pair_clear(s, &x[i]);
#undef DO
    return st;
}

static status_t logarithm(const scope_t *s, const interval_t *ln2,
    const native_vorbis_floor0_amplitude_t *a, const interval_t *d, interval_t *log) {
    enum { RAW, OFFSET, MAXIMUM, AMPLITUDE, ROOT, RATIO, NUMERATOR, DENOMINATOR, DECIMAL, K, COUNT };
    interval_t x[COUNT];
    for (size_t i = 0; i < COUNT; ++i) (void)pair_init(s, &x[i]);
    status_t st;
#define DO(call) do { st = (call); if (st) goto done; } while (0)
    DO(native_vorbis_interval_set_u64(s, &x[RAW], a->raw_amplitude));
    DO(native_vorbis_interval_set_u64(s, &x[OFFSET], a->amplitude_offset));
    DO(native_vorbis_interval_set_u64(s, &x[MAXIMUM], (UINT64_C(1) << a->amplitude_bits) - 1));
    // Exact integer operands enter before directed operations; no binary64
    // conversion or fixed-width raw*offset product is used.
    DO(native_vorbis_interval_mul(s, &x[AMPLITUDE], &x[RAW], &x[OFFSET]));
    DO(native_vorbis_interval_div(s, &x[AMPLITUDE], &x[AMPLITUDE], &x[MAXIMUM]));
    DO(native_vorbis_interval_sqrt(s, &x[ROOT], d));
    DO(native_vorbis_interval_div(s, &x[RATIO], &x[AMPLITUDE], &x[ROOT]));
    DO(native_vorbis_interval_sub(s, &x[RATIO], &x[RATIO], &x[OFFSET]));
    DO(native_vorbis_interval_set_u64(s, &x[NUMERATOR], 11512925));
    DO(native_vorbis_interval_set_u64(s, &x[DENOMINATOR], 100000000));
    DO(native_vorbis_interval_div(s, &x[DECIMAL], &x[NUMERATOR], &x[DENOMINATOR]));
    DO(native_vorbis_interval_div(s, &x[K], &x[DECIMAL], ln2));
    DO(native_vorbis_interval_mul(s, log, &x[RATIO], &x[K]));
done:
    for (size_t i = 0; i < COUNT; ++i) pair_clear(s, &x[i]);
#undef DO
    return st;
}

native_vorbis_bigfloat_status_t native_vorbis_gain_enclose(
    native_vorbis_gain_workspace_t *w, const native_vorbis_gain_input_t *input,
    uint32_t precision, native_vorbis_gain_result_t *result) {
    if (!owned(w, result) || !input || !amplitude_valid(&input->amplitude) || input->order > 255)
        return NATIVE_VORBIS_BIGFLOAT_INVALID;
    scope_t s;
    status_t st = scope_at(w, precision, &s);
    if (!st) st = result_check(&s, result);
    if (st) return (native_vorbis_bigfloat_status_t)st;
    if (input->amplitude.raw_amplitude &&
        (input->bark_map_size > 65535 || (input->bark_map_size &&
         (input->bark_index >= input->bark_map_size || (input->order && !input->angles)))))
        return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_gain_result_t prepared;
    prepared_result(&s, &prepared, precision);
    if (!input->amplitude.raw_amplitude) prepared.kind = NATIVE_VORBIS_GAIN_ABSENT;
    else if (!input->bark_map_size) prepared.kind = NATIVE_VORBIS_GAIN_UNDEFINED_MAPPING;
    else {
        bool pole = false;
        if (!input->bark_index) for (size_t i = 0; i < input->order; i += 2)
            if (affine_zero(&input->angles[i])) pole = true;
        if (pole) {
            prepared.kind = input->amplitude.amplitude_offset ? NATIVE_VORBIS_GAIN_POLE : NATIVE_VORBIS_GAIN_INDETERMINATE;
            prepared.has_denominator = true; // Exact initialized[0,0].
        } else if (!input->amplitude.amplitude_offset) {
            // Exact dyadic LSPs cannot equal a nonzero rational multiple of pi.
            // Pole exclusion proves D>0; unity needs neither division nor trig.
            prepared.kind = NATIVE_VORBIS_GAIN_UNITY;
            prepared.has_log = true;
        } else {
            if (!input->order) {
                st = native_vorbis_interval_set_u64(&s, &prepared.denominator, 1);
                if (!st) prepared.has_denominator = true;
            } else {
                st = constants(w, &s);
                if (!st) st = denominator(&s, &w->pi, input, &prepared.denominator);
                if (!st) prepared.has_denominator = true;
            }
            if (!st && !input->order && input->amplitude.raw_amplitude ==
                (UINT64_C(1) << input->amplitude.amplitude_bits) - 1) {
                prepared.kind = NATIVE_VORBIS_GAIN_UNITY;
                prepared.has_log = true;
            } else if (!st && bf_is_zero(&prepared.denominator.lo)) {
                prepared.kind = NATIVE_VORBIS_GAIN_NEEDS_PRECISION;
            } else if (!st) {
                st = constants(w, &s);
                if (!st) st = logarithm(&s, &w->ln2, &input->amplitude, &prepared.denominator, &prepared.log2_gain);
                if (!st) { prepared.kind = NATIVE_VORBIS_GAIN_FINITE; prepared.has_log = true; }
            }
        }
    }
    if (st == NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION) {
        prepared.kind = NATIVE_VORBIS_GAIN_NEEDS_PRECISION;
        prepared.has_log = false;
        st = NATIVE_VORBIS_INTERVAL_OK;
    }
    if (!st) commit_result(&s, result, &prepared);
    pair_clear(&s, &prepared.denominator); pair_clear(&s, &prepared.log2_gain);
    return (native_vorbis_bigfloat_status_t)st;
}

native_vorbis_bigfloat_status_t native_vorbis_gain_floor_measure(
    const native_vorbis_gain_workspace_t *w, const native_vorbis_gain_result_t *r,
    native_vorbis_gain_floor_requirements_t *requirements) {
    if (!owned(w, r) || !r->has_log || !requirements) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_gain_floor_requirements_t n;
    native_vorbis_bigfloat_status_t st = native_vorbis_bigfloat_measure_floor(&w->arithmetic, &r->log2_gain.lo, &n.lower_words);
    if (!st) st = native_vorbis_bigfloat_measure_floor(&w->arithmetic, &r->log2_gain.hi, &n.upper_words);
    if (!st) *requirements = n;
    return st;
}
native_vorbis_bigfloat_status_t native_vorbis_gain_floor_export(
    const native_vorbis_gain_workspace_t *w, const native_vorbis_gain_result_t *r,
    uint32_t *lower, size_t lower_capacity, uint32_t *upper, size_t upper_capacity,
    native_vorbis_gain_floor_result_t *output) {
    if (!output) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_gain_floor_requirements_t n;
    native_vorbis_bigfloat_status_t st = native_vorbis_gain_floor_measure(w, r, &n);
    if (st) return st;
    if (lower_capacity > SIZE_MAX / sizeof(*lower) || upper_capacity > SIZE_MAX / sizeof(*upper))
        return NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
    if (lower_capacity < n.lower_words || upper_capacity < n.upper_words) return NATIVE_VORBIS_BIGFLOAT_CAPACITY;
    if ((n.lower_words && !lower) || (n.upper_words && !upper)) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_gain_floor_result_t out;
    // Identical immutable validated sources and capacities: both exports are
    // deterministic, allocation-free and cannot fail after the shared preflight.
    st = native_vorbis_bigfloat_export_floor(&w->arithmetic, &r->log2_gain.lo, lower, lower_capacity,
                                            &out.lower_words, &out.lower_negative);
    if (!st) st = native_vorbis_bigfloat_export_floor(&w->arithmetic, &r->log2_gain.hi, upper, upper_capacity,
                                                    &out.upper_words, &out.upper_negative);
    if (!st) {
        out.equal = out.lower_words == out.upper_words && out.lower_negative == out.upper_negative &&
            (!out.lower_words || !memcmp(lower, upper, out.lower_words * sizeof(*lower)));
        *output = out;
    }
    return st;
}
