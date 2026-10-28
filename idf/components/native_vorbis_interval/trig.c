#include "interval_private.h"

// Compare positive exact endpoints e <= b*2^-p without constructing a tiny
// target. Distinct physical tops decide immediately. On equal tops, the view
// retains the validated significand and its top is that of the checked e.
static bool tail_small(const bf_t *error, const bf_t *base, uint32_t precision) {
    if (nvi_zero(error)) return true;
    if (nvi_zero(base)) return false;
    int64_t top = (int64_t)base->expn - precision;
    if ((int64_t)error->expn != top) return (int64_t)error->expn < top;
    bf_t view = *base;
    view.expn = error->expn;
    return bf_cmp(error, &view) <= 0;
}

static native_vorbis_interval_status_t reduce(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *residual, const native_vorbis_interval_t *angle,
    const native_vorbis_interval_t *pi, unsigned *quadrant) {
    enum { HALF_PI, QUOTIENT, HALF, SHIFTED, INTEGER, PRODUCT, RESULT, TWO, COUNT };
    native_vorbis_interval_t t[COUNT];
    for (unsigned i = 0; i < COUNT; ++i) nvi_init(scope, &t[i]);
    native_vorbis_interval_status_t status;
    uint32_t *words = NULL;
    bf_t zero; bf_init(&scope->context->engine, &zero);
    if (bf_cmp(&pi->lo, &zero) <= 0) {
        status = NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION;
        goto done;
    }
    NVI_TRY(native_vorbis_interval_scale2(scope, &t[HALF_PI], pi, -1));
    NVI_TRY(native_vorbis_interval_div(scope, &t[QUOTIENT], angle, &t[HALF_PI]));
    const uint32_t one = 1;
    NVI_TRY(native_vorbis_interval_import(scope, &t[HALF], &one, 1, -1, false));
    NVI_TRY(native_vorbis_interval_add(scope, &t[SHIFTED], &t[QUOTIENT], &t[HALF]));
    size_t count;
    NVI_BF(native_vorbis_bigfloat_measure_floor(scope->context, &t[SHIFTED].lo, &count));
    if (count > NATIVE_VORBIS_BIGFLOAT_MAX_WORDS || count > SIZE_MAX / sizeof(*words)) {
        status = NATIVE_VORBIS_INTERVAL_ENGINE_LIMIT;
        goto done;
    }
    if (count) {
        words = bf_malloc(&scope->context->engine, count * sizeof(*words));
        if (!words) { status = NATIVE_VORBIS_INTERVAL_NO_MEMORY; goto done; }
    }
    size_t written = 0;
    bool negative = false;
    NVI_BF(native_vorbis_bigfloat_export_floor(scope->context, &t[SHIFTED].lo,
        words, count, &written, &negative));
    unsigned mod = written ? words[0] & 3U : 0;
    if (negative) mod = (4U - mod) & 3U;
    NVI_TRY(native_vorbis_interval_import(scope, &t[INTEGER], words, written, 0, negative));
    NVI_TRY(native_vorbis_interval_mul(scope, &t[PRODUCT], &t[INTEGER], &t[HALF_PI]));
    NVI_TRY(native_vorbis_interval_sub(scope, &t[RESULT], angle, &t[PRODUCT]));
    NVI_TRY(native_vorbis_interval_set_u64(scope, &t[TWO], 2));
    if (bf_cmp(&t[RESULT].hi, &t[TWO].hi) > 0) {
        status = NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION;
        goto done;
    }
    bf_neg(&t[TWO].lo);
    if (bf_cmp(&t[RESULT].lo, &t[TWO].lo) < 0) {
        status = NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION;
        goto done;
    }
    status = nvi_publish(scope, residual, &t[RESULT]);
    if (status == NATIVE_VORBIS_INTERVAL_OK) *quadrant = mod;
done:
    bf_free(&scope->context->engine, words);
    for (unsigned i = 0; i < COUNT; ++i) nvi_drop(scope, &t[i]);
    return status;
}

static native_vorbis_interval_status_t polynomial(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *residual, bool sine) {
    enum { R2, TERM, SUM, DENOMINATOR, ERROR, M, M2, ONE, RESULT, COUNT };
    native_vorbis_interval_t t[COUNT];
    for (unsigned i = 0; i < COUNT; ++i) nvi_init(scope, &t[i]);
    native_vorbis_interval_status_t status;
    NVI_TRY(native_vorbis_interval_set_u64(scope, &t[ONE], 1));
    if (nvi_zero(&residual->lo) && nvi_zero(&residual->hi)) {
        if (sine) NVI_TRY(native_vorbis_interval_set_u64(scope, &t[RESULT], 0));
        else NVI_TRY(native_vorbis_interval_copy(scope, &t[RESULT], &t[ONE]));
        status = nvi_publish(scope, destination, &t[RESULT]);
        goto done;
    }
    // Two private copies are nonnegative point candidates, not an interval
    // until their maximum is chosen. Cleanup handles each endpoint separately.
    NVI_BF(native_vorbis_bigfloat_copy(scope->context, &t[M].lo, &residual->lo));
    NVI_BF(native_vorbis_bigfloat_copy(scope->context, &t[M].hi, &residual->hi));
    if (t[M].lo.sign) bf_neg(&t[M].lo);
    if (t[M].hi.sign) bf_neg(&t[M].hi);
    const bf_t *maximum = bf_cmp(&t[M].lo, &t[M].hi) > 0 ? &t[M].lo : &t[M].hi;
    NVI_TRY(nvi_point_interval(scope, &t[M2], maximum));
    nvi_drop(scope, &t[M]); // Absolute endpoint candidates may be reversed.
    NVI_TRY(native_vorbis_interval_copy(scope, &t[M], &t[M2]));
    NVI_BF(native_vorbis_bigfloat_mul(scope->context, &t[M2].hi, &t[M].hi, &t[M].hi,
        scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
    // M2.lo is unused after this point; keep a valid ordered private pair.
    NVI_BF(native_vorbis_bigfloat_set_u64(scope->context, &t[M2].lo, 0));
    NVI_TRY(native_vorbis_interval_square(scope, &t[R2], residual));
    if (sine) {
        NVI_TRY(native_vorbis_interval_copy(scope, &t[TERM], residual));
        NVI_TRY(native_vorbis_interval_copy(scope, &t[ERROR], &t[M]));
    } else {
        NVI_TRY(native_vorbis_interval_copy(scope, &t[TERM], &t[ONE]));
        NVI_TRY(native_vorbis_interval_copy(scope, &t[ERROR], &t[ONE]));
    }
    NVI_TRY(native_vorbis_interval_copy(scope, &t[SUM], &t[TERM]));
    for (uint32_t k = 0; k < scope->precision + 32; ++k) {
        uint64_t first = (uint64_t)2 * k + (sine ? 2U : 1U);
        uint64_t denominator = first * (first + 1);
        NVI_TRY(native_vorbis_interval_set_u64(scope, &t[DENOMINATOR], denominator));
        NVI_BF(native_vorbis_bigfloat_mul(scope->context, &t[ERROR].hi, &t[ERROR].hi,
            &t[M2].hi, scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
        NVI_BF(native_vorbis_bigfloat_div(scope->context, &t[ERROR].hi, &t[ERROR].hi,
            &t[DENOMINATOR].lo, scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
        // The lower error field is unused; reset it so the helper pair stays
        // ordered while the upper next-term bound decreases.
        NVI_BF(native_vorbis_bigfloat_set_u64(scope->context, &t[ERROR].lo, 0));
        const bf_t *base = sine ? &t[M].hi : &t[ONE].hi;
        if (tail_small(&t[ERROR].hi, base, scope->precision)) {
            NVI_TRY(nvi_expand(scope, &t[RESULT], &t[SUM], &t[ERROR].hi));
            // Both functions are mathematically in[-1,1]. Intersection uses
            // that proven range; it does not replace an unresolved remainder.
            if (bf_cmp(&t[RESULT].hi, &t[ONE].hi) > 0)
                NVI_BF(native_vorbis_bigfloat_copy(scope->context, &t[RESULT].hi, &t[ONE].hi));
            bf_neg(&t[ONE].lo);
            if (bf_cmp(&t[RESULT].lo, &t[ONE].lo) < 0)
                NVI_BF(native_vorbis_bigfloat_copy(scope->context, &t[RESULT].lo, &t[ONE].lo));
            status = nvi_publish(scope, destination, &t[RESULT]);
            goto done;
        }
        NVI_TRY(native_vorbis_interval_mul(scope, &t[TERM], &t[TERM], &t[R2]));
        NVI_TRY(native_vorbis_interval_div(scope, &t[TERM], &t[TERM], &t[DENOMINATOR]));
        if (k & 1) NVI_TRY(native_vorbis_interval_add(scope, &t[SUM], &t[SUM], &t[TERM]));
        else NVI_TRY(native_vorbis_interval_sub(scope, &t[SUM], &t[SUM], &t[TERM]));
    }
    status = NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION;
done:
    for (unsigned i = 0; i < COUNT; ++i) nvi_drop(scope, &t[i]);
    return status;
}

static native_vorbis_interval_status_t trig(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *angle,
    const native_vorbis_interval_t *pi, bool cosine) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = native_vorbis_interval_check(scope, angle);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = native_vorbis_interval_check(scope, pi);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    native_vorbis_interval_t residual, result;
    nvi_init(scope, &residual); nvi_init(scope, &result);
    unsigned quadrant = 0;
    NVI_TRY(reduce(scope, &residual, angle, pi, &quadrant));
    bool sine = cosine ? (quadrant & 1U) != 0 : (quadrant & 1U) == 0;
    NVI_TRY(polynomial(scope, &result, &residual, sine));
    bool negative = cosine ? (quadrant == 1 || quadrant == 2) : quadrant >= 2;
    if (negative) NVI_TRY(native_vorbis_interval_negate(scope, &result, &result));
    status = nvi_publish(scope, destination, &result);
done:
    nvi_drop(scope, &result); nvi_drop(scope, &residual);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_sin(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *angle, const native_vorbis_interval_t *pi) {
    return trig(scope, destination, angle, pi, false);
}

native_vorbis_interval_status_t native_vorbis_interval_cos(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *angle, const native_vorbis_interval_t *pi) {
    return trig(scope, destination, angle, pi, true);
}
