#include "interval_private.h"

native_vorbis_interval_status_t nvi_ratio(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, uint64_t numerator, uint64_t denominator) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    if (!denominator) return NATIVE_VORBIS_INTERVAL_ARITHMETIC;
    native_vorbis_interval_t temporary, operands;
    nvi_init(scope, &temporary); nvi_init(scope, &operands);
    NVI_BF(native_vorbis_bigfloat_set_u64(scope->context, &operands.lo, numerator));
    NVI_BF(native_vorbis_bigfloat_set_u64(scope->context, &operands.hi, denominator));
    NVI_BF(native_vorbis_bigfloat_div(scope->context, &temporary.lo, &operands.lo, &operands.hi,
        scope->precision, NATIVE_VORBIS_BIGFLOAT_DOWN));
    NVI_BF(native_vorbis_bigfloat_div(scope->context, &temporary.hi, &operands.lo, &operands.hi,
        scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &operands); nvi_drop(scope, &temporary);
    return status;
}

native_vorbis_interval_status_t nvi_expand(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *source, const bf_t *error) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = native_vorbis_interval_check(scope, source);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = nvi_point(scope, error);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    if (error->sign && error->len) return NATIVE_VORBIS_INTERVAL_INVALID;
    native_vorbis_interval_t temporary; nvi_init(scope, &temporary);
    NVI_BF(native_vorbis_bigfloat_sub(scope->context, &temporary.lo, &source->lo, error,
        scope->precision, NATIVE_VORBIS_BIGFLOAT_DOWN));
    NVI_BF(native_vorbis_bigfloat_add(scope->context, &temporary.hi, &source->hi, error,
        scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &temporary);
    return status;
}

static native_vorbis_interval_status_t atan_reciprocal(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, uint64_t reciprocal) {
    enum { X, X2, POWER, SUM, TERM, ODD, NEXT, TARGET, RESULT, COUNT };
    native_vorbis_interval_t t[COUNT];
    for (unsigned i = 0; i < COUNT; ++i) nvi_init(scope, &t[i]);
    native_vorbis_interval_status_t status;
    NVI_TRY(nvi_ratio(scope, &t[X], 1, reciprocal));
    NVI_TRY(native_vorbis_interval_square(scope, &t[X2], &t[X]));
    NVI_TRY(native_vorbis_interval_copy(scope, &t[POWER], &t[X]));
    const uint32_t one = 1;
    NVI_TRY(native_vorbis_interval_import(scope, &t[TARGET], &one, 1, -(int64_t)scope->precision, false));
    // x=1/5 or1/239. The exact alternating remainder is at most the next
    // x^(2k+3)/(2k+3), bounded upward by our positive interval recurrence.
    for (uint32_t k = 0; k < scope->precision + 32; ++k) {
        NVI_TRY(native_vorbis_interval_set_u64(scope, &t[ODD], (uint64_t)2 * k + 1));
        NVI_TRY(native_vorbis_interval_div(scope, &t[TERM], &t[POWER], &t[ODD]));
        if (k & 1) NVI_TRY(native_vorbis_interval_sub(scope, &t[SUM], &t[SUM], &t[TERM]));
        else NVI_TRY(native_vorbis_interval_add(scope, &t[SUM], &t[SUM], &t[TERM]));
        NVI_TRY(native_vorbis_interval_mul(scope, &t[POWER], &t[POWER], &t[X2]));
        NVI_TRY(native_vorbis_interval_set_u64(scope, &t[ODD], (uint64_t)2 * k + 3));
        NVI_TRY(native_vorbis_interval_div(scope, &t[NEXT], &t[POWER], &t[ODD]));
        if (bf_cmp(&t[NEXT].hi, &t[TARGET].lo) <= 0) {
            NVI_TRY(nvi_expand(scope, &t[RESULT], &t[SUM], &t[NEXT].hi));
            status = nvi_publish(scope, destination, &t[RESULT]);
            goto done;
        }
    }
    status = NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION;
done:
    for (unsigned i = 0; i < COUNT; ++i) nvi_drop(scope, &t[i]);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_pi(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    native_vorbis_interval_t a, b, result;
    nvi_init(scope, &a); nvi_init(scope, &b); nvi_init(scope, &result);
    NVI_TRY(atan_reciprocal(scope, &a, 5));
    NVI_TRY(atan_reciprocal(scope, &b, 239));
    NVI_TRY(native_vorbis_interval_scale2(scope, &a, &a, 4));
    NVI_TRY(native_vorbis_interval_scale2(scope, &b, &b, 2));
    NVI_TRY(native_vorbis_interval_sub(scope, &result, &a, &b));
    status = nvi_publish(scope, destination, &result);
done:
    nvi_drop(scope, &result); nvi_drop(scope, &b); nvi_drop(scope, &a);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_ln2(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    enum { X, X2, POWER, SUM, TERM, ODD, NEXT, TAIL, TARGET, FACTOR, RESULT, COUNT };
    native_vorbis_interval_t t[COUNT];
    for (unsigned i = 0; i < COUNT; ++i) nvi_init(scope, &t[i]);
    NVI_TRY(nvi_ratio(scope, &t[X], 1, 3));
    NVI_TRY(native_vorbis_interval_square(scope, &t[X2], &t[X]));
    NVI_TRY(native_vorbis_interval_copy(scope, &t[POWER], &t[X]));
    const uint32_t one = 1, nine = 9;
    NVI_TRY(native_vorbis_interval_import(scope, &t[TARGET], &one, 1, -(int64_t)scope->precision, false));
    NVI_TRY(native_vorbis_interval_import(scope, &t[FACTOR], &nine, 1, -2, false));
    // ln2=2 sum x^(2k+1)/(2k+1), x=1/3. After a partial sum its
    // positive tail <=2*next_term/(1-x^2)=(9/4)*next_term.
    for (uint32_t k = 0; k < scope->precision + 32; ++k) {
        NVI_TRY(native_vorbis_interval_set_u64(scope, &t[ODD], (uint64_t)2 * k + 1));
        NVI_TRY(native_vorbis_interval_div(scope, &t[TERM], &t[POWER], &t[ODD]));
        NVI_TRY(native_vorbis_interval_add(scope, &t[SUM], &t[SUM], &t[TERM]));
        NVI_TRY(native_vorbis_interval_mul(scope, &t[POWER], &t[POWER], &t[X2]));
        NVI_TRY(native_vorbis_interval_set_u64(scope, &t[ODD], (uint64_t)2 * k + 3));
        NVI_TRY(native_vorbis_interval_div(scope, &t[NEXT], &t[POWER], &t[ODD]));
        NVI_TRY(native_vorbis_interval_mul(scope, &t[TAIL], &t[NEXT], &t[FACTOR]));
        if (bf_cmp(&t[TAIL].hi, &t[TARGET].lo) <= 0) {
            NVI_TRY(native_vorbis_interval_scale2(scope, &t[RESULT], &t[SUM], 1));
            NVI_BF(native_vorbis_bigfloat_add(scope->context, &t[RESULT].hi, &t[RESULT].hi,
                &t[TAIL].hi, scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
            status = nvi_publish(scope, destination, &t[RESULT]);
            goto done;
        }
    }
    status = NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION;
done:
    for (unsigned i = 0; i < COUNT; ++i) nvi_drop(scope, &t[i]);
    return status;
}
