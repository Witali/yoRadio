/* Host-only directed reference for Vorbis I 6.2.3, using MPFR >= 4.2.
 * This deliberately uses direct cosines, not the production half-angle path.
 * See vorbis_floor0_mpfr_oracle.md for protocol, scope and fatal host OOM.
 */
#include <inttypes.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <mpfr.h>

#if MPFR_VERSION < MPFR_VERSION_NUM(4, 2, 0)
#error "The independent exact rational-pi cosine requires MPFR >= 4.2"
#endif

typedef struct { uint32_t minimum, delta, minimum_multiplier, delta_multiplier; } affine_t;
typedef struct {
    uint64_t ordinal;
    mpfr_prec_t precision;
    uint32_t order, bin, map, bits, offset;
    uint64_t raw;
    affine_t angles[255];
} request_t;
typedef struct { mpfr_t lo, hi; } interval_t;
enum { C, COEFFICIENT, DIFFERENCE, SQUARE, ODD, EVEN, AUXILIARY,
       P, Q, DENOMINATOR, AMPLITUDE, ROOT, RATIO, LN2, DECIMAL, K, LOG_GAIN,
       INTERVAL_COUNT };
typedef struct {
    interval_t values[INTERVAL_COUNT];
    mpfr_t exact_angle, integer_bin, temporary;
    mpz_t integer, term, floor_lo, floor_hi;
    mpq_t rational;
} workspace_t;

/* Only canonical decimal tokens, separated by ASCII spaces or tabs. */
static bool unsigned_token(const char **cursor, uint64_t maximum, uint64_t *value) {
    const char *p = *cursor;
    while (*p == ' ' || *p == '\t') ++p;
    if (*p < '0' || *p > '9' || (*p == '0' && p[1] >= '0' && p[1] <= '9')) return false;
    uint64_t result = 0;
    do {
        unsigned digit = (unsigned)(*p - '0');
        if (result > maximum / 10 ||
            (result == maximum / 10 && digit > maximum % 10)) return false;
        result = result * 10 + digit;
        ++p;
    } while (*p >= '0' && *p <= '9');
    if (*p && *p != ' ' && *p != '\t') return false;
    *cursor = p;
    *value = result;
    return true;
}

static bool parse_request(const char *line, request_t *r) {
    if (strncmp(line, "F0MPFR1 ", 8)) return false;
    const char *p = line + 8;
    uint64_t fields[7];
    const uint64_t maxima[7] = {(uint64_t)MPFR_PREC_MAX, 255, 65534, 65535,
        63, UINT64_C(0x7fffffffffffffff), 255};
    for (unsigned i = 0; i < 7; ++i)
        if (!unsigned_token(&p, maxima[i], &fields[i])) return false;
    if (fields[0] < (uint64_t)MPFR_PREC_MIN || !fields[3] || fields[2] >= fields[3] ||
        (!fields[4] ? fields[5] != 0 : fields[5] > (UINT64_C(1) << fields[4]) - 1)) return false;
    r->precision = (mpfr_prec_t)fields[0];
    r->order = (uint32_t)fields[1]; r->bin = (uint32_t)fields[2];
    r->map = (uint32_t)fields[3]; r->bits = (uint32_t)fields[4];
    r->raw = fields[5]; r->offset = (uint32_t)fields[6];
    for (uint32_t i = 0; i < r->order; ++i) {
        uint64_t a[4];
        for (unsigned j = 0; j < 4; ++j)
            if (!unsigned_token(&p, UINT32_MAX, &a[j])) return false;
        r->angles[i] = (affine_t){(uint32_t)a[0], (uint32_t)a[1],
            (uint32_t)a[2], (uint32_t)a[3]};
    }
    while (*p == ' ' || *p == '\t') ++p;
    return !*p;
}

static void interval_init(interval_t *a, mpfr_prec_t precision) {
    mpfr_init2(a->lo, precision); mpfr_init2(a->hi, precision);
}
static void interval_set_ui(interval_t *a, unsigned long value) {
    mpfr_set_ui(a->lo, value, MPFR_RNDD); mpfr_set_ui(a->hi, value, MPFR_RNDU);
}
static void interval_set_q(interval_t *a, const mpq_t value) {
    mpfr_set_q(a->lo, value, MPFR_RNDD); mpfr_set_q(a->hi, value, MPFR_RNDU);
}
/* Inputs are nonnegative; aliasing the destination is supported. */
static void interval_multiply_nonnegative(interval_t *r, const interval_t *a,
                                          const interval_t *b) {
    mpfr_mul(r->lo, a->lo, b->lo, MPFR_RNDD);
    mpfr_mul(r->hi, a->hi, b->hi, MPFR_RNDU);
}
/* Destination must differ from input. Squaring is not endpoint multiplication
 * when the interval crosses zero: its exact lower bound is then zero. */
static void interval_square(interval_t *r, const interval_t *a, mpfr_t temporary) {
    if (mpfr_sgn(a->lo) >= 0) {
        mpfr_sqr(r->lo, a->lo, MPFR_RNDD); mpfr_sqr(r->hi, a->hi, MPFR_RNDU);
    } else if (mpfr_sgn(a->hi) <= 0) {
        mpfr_sqr(r->lo, a->hi, MPFR_RNDD); mpfr_sqr(r->hi, a->lo, MPFR_RNDU);
    } else {
        mpfr_set_zero(r->lo, 1);
        mpfr_sqr(r->hi, a->lo, MPFR_RNDU); mpfr_sqr(temporary, a->hi, MPFR_RNDU);
        if (mpfr_cmp(temporary, r->hi) > 0) mpfr_set(r->hi, temporary, MPFR_RNDU);
    }
}

static void set_u64(mpz_t result, uint64_t value) {
    uint32_t words[2] = {(uint32_t)value, (uint32_t)(value >> 32)};
    mpz_import(result, 2, -1, sizeof(words[0]), 0, 0, words);
}
/* Exact affine integer on the common 2^-788 grid. No floating sum occurs. */
static void affine_integer(mpz_t result, mpz_t term, const affine_t *a) {
    const uint32_t packed[2] = {a->minimum, a->delta};
    const uint32_t multiplier[2] = {a->minimum_multiplier, a->delta_multiplier};
    mpz_set_ui(result, 0);
    for (unsigned j = 0; j < 2; ++j) {
        set_u64(term, (uint64_t)(packed[j] & UINT32_C(0x1fffff)) * multiplier[j]);
        mpz_mul_2exp(term, term, (packed[j] >> 21) & 1023U);
        if (packed[j] & UINT32_C(0x80000000)) mpz_neg(term, term);
        mpz_add(result, result, term);
    }
}

static void workspace_init(workspace_t *w, mpfr_prec_t precision) {
    for (unsigned i = 0; i < INTERVAL_COUNT; ++i) interval_init(&w->values[i], precision);
    mpfr_init2(w->exact_angle, precision);
    mpfr_init2(w->integer_bin, precision < 16 ? 16 : precision);
    mpfr_init2(w->temporary, precision);
    mpz_inits(w->integer, w->term, w->floor_lo, w->floor_hi, (mpz_ptr)NULL);
    mpq_init(w->rational);
}
static void workspace_clear(workspace_t *w) {
    for (unsigned i = 0; i < INTERVAL_COUNT; ++i) {
        mpfr_clear(w->values[i].lo); mpfr_clear(w->values[i].hi);
    }
    mpfr_clear(w->exact_angle); mpfr_clear(w->integer_bin); mpfr_clear(w->temporary);
    mpz_clears(w->integer, w->term, w->floor_lo, w->floor_hi, (mpz_ptr)NULL);
    mpq_clear(w->rational);
}
static bool numeric_range_failure(void) {
    return mpfr_overflow_p() || mpfr_underflow_p() || mpfr_nanflag_p() || mpfr_erangeflag_p();
}
static bool valid_interval(const interval_t *a) {
    return mpfr_number_p(a->lo) && mpfr_number_p(a->hi) && mpfr_cmp(a->lo, a->hi) <= 0;
}

static bool denominator(const request_t *r, workspace_t *w) {
    interval_t *v = w->values;
    if (!r->order) { interval_set_ui(&v[DENOMINATOR], 1); return true; }
    if (mpfr_set_ui(w->integer_bin, r->bin, MPFR_RNDN)) return false;
    mpfr_cosu(v[C].lo, w->integer_bin, 2UL * r->map, MPFR_RNDD);
    mpfr_cosu(v[C].hi, w->integer_bin, 2UL * r->map, MPFR_RNDU);
    interval_set_ui(&v[ODD], 1); interval_set_ui(&v[EVEN], 1);
    for (uint32_t i = 0; i < r->order; ++i) {
        affine_integer(w->integer, w->term, &r->angles[i]);
        size_t exact_bits = mpz_sizeinbase(w->integer, 2);
        if (exact_bits > (uintmax_t)MPFR_PREC_MAX) return false;
        mpfr_prec_t input_precision = (mpfr_prec_t)exact_bits;
        if (input_precision < MPFR_PREC_MIN) input_precision = MPFR_PREC_MIN;
        mpfr_set_prec(w->exact_angle, input_precision);
        if (mpfr_set_z_2exp(w->exact_angle, w->integer, -788, MPFR_RNDN)) return false;
        mpfr_cos(v[COEFFICIENT].lo, w->exact_angle, MPFR_RNDD);
        mpfr_cos(v[COEFFICIENT].hi, w->exact_angle, MPFR_RNDU);
        mpfr_sub(v[DIFFERENCE].lo, v[COEFFICIENT].lo, v[C].hi, MPFR_RNDD);
        mpfr_sub(v[DIFFERENCE].hi, v[COEFFICIENT].hi, v[C].lo, MPFR_RNDU);
        mpfr_mul_2ui(v[DIFFERENCE].lo, v[DIFFERENCE].lo, 1, MPFR_RNDD);
        mpfr_mul_2ui(v[DIFFERENCE].hi, v[DIFFERENCE].hi, 1, MPFR_RNDU);
        interval_square(&v[SQUARE], &v[DIFFERENCE], w->temporary);
        unsigned product = (i & 1U) ? ODD : EVEN;
        interval_multiply_nonnegative(&v[product], &v[product], &v[SQUARE]);
    }
    if (r->order & 1U) {
        interval_square(&v[AUXILIARY], &v[C], w->temporary);
        mpfr_ui_sub(v[P].lo, 1, v[AUXILIARY].hi, MPFR_RNDD);
        mpfr_ui_sub(v[P].hi, 1, v[AUXILIARY].lo, MPFR_RNDU);
        interval_multiply_nonnegative(&v[P], &v[P], &v[ODD]);
        mpfr_div_2ui(v[Q].lo, v[EVEN].lo, 2, MPFR_RNDD);
        mpfr_div_2ui(v[Q].hi, v[EVEN].hi, 2, MPFR_RNDU);
    } else {
        mpfr_ui_sub(v[P].lo, 1, v[C].hi, MPFR_RNDD);
        mpfr_ui_sub(v[P].hi, 1, v[C].lo, MPFR_RNDU);
        mpfr_add_ui(v[Q].lo, v[C].lo, 1, MPFR_RNDD);
        mpfr_add_ui(v[Q].hi, v[C].hi, 1, MPFR_RNDU);
        interval_multiply_nonnegative(&v[P], &v[P], &v[ODD]);
        interval_multiply_nonnegative(&v[Q], &v[Q], &v[EVEN]);
        mpfr_div_2ui(v[P].lo, v[P].lo, 1, MPFR_RNDD);
        mpfr_div_2ui(v[P].hi, v[P].hi, 1, MPFR_RNDU);
        mpfr_div_2ui(v[Q].lo, v[Q].lo, 1, MPFR_RNDD);
        mpfr_div_2ui(v[Q].hi, v[Q].hi, 1, MPFR_RNDU);
    }
    mpfr_add(v[DENOMINATOR].lo, v[P].lo, v[Q].lo, MPFR_RNDD);
    mpfr_add(v[DENOMINATOR].hi, v[P].hi, v[Q].hi, MPFR_RNDU);
    return !numeric_range_failure() && valid_interval(&v[DENOMINATOR]) &&
        mpfr_sgn(v[DENOMINATOR].lo) >= 0;
}

static bool logarithm(const request_t *r, workspace_t *w) {
    interval_t *v = w->values;
    set_u64(mpq_numref(w->rational), r->raw);
    mpz_mul_ui(mpq_numref(w->rational), mpq_numref(w->rational), r->offset);
    set_u64(mpq_denref(w->rational), (UINT64_C(1) << r->bits) - 1);
    mpq_canonicalize(w->rational);
    interval_set_q(&v[AMPLITUDE], w->rational);
    mpfr_sqrt(v[ROOT].lo, v[DENOMINATOR].lo, MPFR_RNDD);
    mpfr_sqrt(v[ROOT].hi, v[DENOMINATOR].hi, MPFR_RNDU);
    mpfr_div(v[RATIO].lo, v[AMPLITUDE].lo, v[ROOT].hi, MPFR_RNDD);
    mpfr_div(v[RATIO].hi, v[AMPLITUDE].hi, v[ROOT].lo, MPFR_RNDU);
    mpfr_sub_ui(v[RATIO].lo, v[RATIO].lo, r->offset, MPFR_RNDD);
    mpfr_sub_ui(v[RATIO].hi, v[RATIO].hi, r->offset, MPFR_RNDU);
    mpq_set_ui(w->rational, 11512925, 100000000);
    mpq_canonicalize(w->rational);
    interval_set_q(&v[DECIMAL], w->rational);
    mpfr_const_log2(v[LN2].lo, MPFR_RNDD); mpfr_const_log2(v[LN2].hi, MPFR_RNDU);
    mpfr_div(v[K].lo, v[DECIMAL].lo, v[LN2].hi, MPFR_RNDD);
    mpfr_div(v[K].hi, v[DECIMAL].hi, v[LN2].lo, MPFR_RNDU);
    /* K is positive. A negative ratio reverses which endpoint of K is used. */
    mpfr_mul(v[LOG_GAIN].lo, v[RATIO].lo,
        mpfr_sgn(v[RATIO].lo) < 0 ? v[K].hi : v[K].lo, MPFR_RNDD);
    mpfr_mul(v[LOG_GAIN].hi, v[RATIO].hi,
        mpfr_sgn(v[RATIO].hi) < 0 ? v[K].lo : v[K].hi, MPFR_RNDU);
    return !numeric_range_failure() && valid_interval(&v[LOG_GAIN]);
}

static void print_dyadic(const mpfr_t value, mpz_t integer) {
    if (mpfr_zero_p(value)) { fputs("{\"hex\":\"0\",\"exp2\":0}", stdout); return; }
    _Static_assert(sizeof(mpfr_exp_t) <= sizeof(intmax_t), "Exact exponent export must fit intmax_t");
    intmax_t exponent = (intmax_t)mpfr_get_z_2exp(integer, value);
    /* Remove trailing zero bits for a compact canonical exact export. */
    mpz_t magnitude;
    mpz_init(magnitude); mpz_abs(magnitude, integer);
    mp_bitcnt_t shift = mpz_scan1(magnitude, 0);
    mpz_clear(magnitude);
    /* Shifting may exceed mpfr_exp_t only at its endpoints. Retain the exact
     * unnormalized export there rather than overflowing signed arithmetic. */
    if ((uintmax_t)shift <= (uintmax_t)INTMAX_MAX &&
        exponent <= INTMAX_MAX - (intmax_t)shift) {
        mpz_tdiv_q_2exp(integer, integer, shift);
        exponent += (intmax_t)shift;
    }
    fputs("{\"hex\":\"", stdout); mpz_out_str(stdout, 16, integer);
    printf("\",\"exp2\":%jd}", exponent);
}
static void print_interval(const interval_t *value, mpz_t integer) {
    fputs("{\"lo\":", stdout); print_dyadic(value->lo, integer);
    fputs(",\"hi\":", stdout); print_dyadic(value->hi, integer); fputc('}', stdout);
}
static void response(const request_t *r, workspace_t *w, const char *status,
                     const char *reason, bool have_denominator, bool have_log) {
    printf("{\"schema\":\"F0MPFR1\",\"ordinal\":%" PRIu64 ",\"status\":\"%s\",\"reason\":\"%s\","
           "\"precision\":%jd,\"denominator\":", r->ordinal, status, reason, (intmax_t)r->precision);
    if (have_denominator) print_interval(&w->values[DENOMINATOR], w->integer);
    else fputs("null", stdout);
    fputs(",\"log2_gain\":", stdout);
    if (have_log) print_interval(&w->values[LOG_GAIN], w->integer);
    else fputs("null", stdout);
    fputs(",\"floor_lo\":", stdout);
    if (have_log) { fputc('"', stdout); mpz_out_str(stdout, 16, w->floor_lo); fputc('"', stdout); }
    else fputs("null", stdout);
    fputs(",\"floor_hi\":", stdout);
    if (have_log) { fputc('"', stdout); mpz_out_str(stdout, 16, w->floor_hi); fputc('"', stdout); }
    else fputs("null", stdout);
    printf(",\"floor_equal\":%s}\n", have_log ?
        (mpz_cmp(w->floor_lo, w->floor_hi) ? "false" : "true") : "null");
}

static void evaluate(const request_t *r, mpfr_prec_t caller_budget) {
    if (r->precision > caller_budget) {
        response(r, NULL, "resource", "caller_precision_budget", false, false); return;
    }
    if (!r->raw) {
        response(r, NULL, "absent", "raw_zero", false, false); return;
    }
    workspace_t w;
    workspace_init(&w, r->precision); mpfr_clear_flags();
    /* Rational phi can equal a rational multiple of pi modulo 2*pi only at
     * phi=0 and Bark0. At Bark0 P=0; Q=0 exactly iff an even LSP is zero. */
    bool pole = false;
    if (!r->bin) for (uint32_t i = 0; i < r->order; i += 2) {
        affine_integer(w.integer, w.term, &r->angles[i]);
        if (!mpz_sgn(w.integer)) pole = true;
    }
    if (pole) {
        interval_set_ui(&w.values[DENOMINATOR], 0);
        response(r, &w, r->offset ? "pole" : "indeterminate", "exact_zero_denominator", true, false);
    } else if (!denominator(r, &w)) {
        response(r, &w, "range", "mpfr_range_or_nonfinite", false, false);
    } else if (!r->offset) {
        /* Exact pole exclusion already proves D>0 for these exact rational
         * angles. Offset0 is unity even if a coarse direct-cos bound contains
         * zero; no numerical division by that interval is performed. */
        interval_set_ui(&w.values[LOG_GAIN], 0);
        mpz_set_ui(w.floor_lo, 0); mpz_set_ui(w.floor_hi, 0);
        response(r, &w, "unity", "exact_identity", true, true);
    } else if (mpfr_sgn(w.values[DENOMINATOR].lo) <= 0) {
        response(r, &w, "unresolved", "denominator_lower_zero", true, false);
    } else {
        uint64_t maximum = (UINT64_C(1) << r->bits) - 1;
        bool unity = r->raw == maximum &&
            mpfr_cmp_ui(w.values[DENOMINATOR].lo, 1) == 0 &&
            mpfr_cmp_ui(w.values[DENOMINATOR].hi, 1) == 0;
        if (unity) interval_set_ui(&w.values[LOG_GAIN], 0);
        if (!unity && !logarithm(r, &w)) {
            response(r, &w, "range", "mpfr_range_or_nonfinite", true, false);
        } else {
            mpfr_get_z(w.floor_lo, w.values[LOG_GAIN].lo, MPFR_RNDD);
            mpfr_get_z(w.floor_hi, w.values[LOG_GAIN].hi, MPFR_RNDD);
            bool equal = mpz_cmp(w.floor_lo, w.floor_hi) == 0;
            response(r, &w, unity ? "unity" : (equal ? "certified" : "unresolved"),
                unity ? "exact_identity" : (equal ? "floor_agrees" : "integer_boundary"), true, true);
        }
    }
    workspace_clear(&w); mpfr_free_cache();
}

int main(int argc, char **argv) {
    if (argc == 2 && !strcmp(argv[1], "--version")) {
        printf("F0MPFR1 MPFR=%s GMP=%s\n", mpfr_get_version(), gmp_version); return 0;
    }
    uint64_t budget;
    const char *budget_token = argc >= 3 ? argv[2] : "";
    if ((argc != 3 && argc != 4) || strcmp(argv[1], "--max-precision") ||
        !unsigned_token(&budget_token, (uint64_t)MPFR_PREC_MAX, &budget) || *budget_token ||
        budget < (uint64_t)MPFR_PREC_MIN) {
        fputs("usage: vorbis_floor0_mpfr_oracle --max-precision BITS [input-file]\n"
              "       vorbis_floor0_mpfr_oracle --version\n", stderr); return 2;
    }
    FILE *input = stdin;
    if (argc == 4) {
        input = fopen(argv[3], "rb");
        if (!input) { fputs("cannot open oracle input file\n", stderr); return 2; }
    }
    if (mpfr_set_emin(mpfr_get_emin_min()) || mpfr_set_emax(mpfr_get_emax_max())) return 2;
    /* 1,027 bounded canonical tokens fit below this limit. Overlong or binary
     * input is rejected as one line, without unbounded input allocation. */
    char line[32768];
    uint64_t ordinal = 0;
    bool had_invalid = false;
    for (;;) {
        size_t length = 0; bool invalid = false; int c;
        while ((c = fgetc(input)) != EOF && c != '\n') {
            if (c == 0 || c > 127 || length == sizeof(line) - 1) invalid = true;
            else line[length++] = (char)c;
        }
        if (c == EOF && !length && !invalid) break;
        if (ordinal == UINT64_MAX) { had_invalid = true; break; }
        ++ordinal;
        if (c == EOF) invalid = true; /* A final partial record is an error. */
        if (length && line[length - 1] == '\r') --length;
        line[length] = 0;
        request_t request;
        if (invalid || !parse_request(line, &request)) {
            printf("{\"schema\":\"F0MPFR1\",\"ordinal\":%" PRIu64
                ",\"status\":\"invalid\",\"reason\":\"protocol\",\"precision\":null,"
                "\"denominator\":null,\"log2_gain\":null,\"floor_lo\":null,\"floor_hi\":null,"
                "\"floor_equal\":null}\n", ordinal);
            had_invalid = true;
        } else { request.ordinal = ordinal; evaluate(&request, (mpfr_prec_t)budget); }
        if (fflush(stdout) || ferror(stdout)) return 2;
        if (c == EOF) break;
    }
    mpfr_free_cache();
    bool input_error = ferror(input) != 0;
    if (input != stdin && fclose(input)) input_error = true;
    return had_invalid || input_error || ferror(stdout) ? 2 : 0;
}
