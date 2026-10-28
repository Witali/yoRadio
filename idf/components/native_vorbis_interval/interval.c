#include "interval_private.h"

native_vorbis_interval_status_t nvi_bf(native_vorbis_bigfloat_status_t status) {
    switch (status) {
    case NATIVE_VORBIS_BIGFLOAT_OK: return NATIVE_VORBIS_INTERVAL_OK;
    case NATIVE_VORBIS_BIGFLOAT_INVALID: return NATIVE_VORBIS_INTERVAL_INVALID;
    case NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT: return NATIVE_VORBIS_INTERVAL_ENGINE_LIMIT;
    case NATIVE_VORBIS_BIGFLOAT_NO_MEMORY: return NATIVE_VORBIS_INTERVAL_NO_MEMORY;
    case NATIVE_VORBIS_BIGFLOAT_CAPACITY: return NATIVE_VORBIS_INTERVAL_CAPACITY;
    default: return NATIVE_VORBIS_INTERVAL_ARITHMETIC;
    }
}

native_vorbis_interval_status_t nvi_scope(const native_vorbis_interval_scope_t *scope) {
    if (!scope || scope->precision < 2) return NATIVE_VORBIS_INTERVAL_INVALID;
    if (scope->precision > NATIVE_VORBIS_BIGFLOAT_MAX_BITS) return NATIVE_VORBIS_INTERVAL_ENGINE_LIMIT;
    native_vorbis_bigfloat_stats_t stats;
    return nvi_bf(native_vorbis_bigfloat_stats(scope->context, &stats));
}

native_vorbis_interval_status_t nvi_point(const native_vorbis_interval_scope_t *scope, const bf_t *value) {
    native_vorbis_interval_status_t status = nvi_scope(scope);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    size_t count;
    return nvi_bf(native_vorbis_bigfloat_measure_dyadic(scope->context, value, &count));
}

bool nvi_zero(const bf_t *value) { return value->len == 0; }

void nvi_init(const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *value) {
    bf_init(&scope->context->engine, &value->lo);
    bf_init(&scope->context->engine, &value->hi);
}

void nvi_drop(const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *value) {
    // Each endpoint is independently a checked owned number, even if a failed
    // private pair preparation has not established endpoint ordering yet.
    (void)native_vorbis_bigfloat_clear(scope->context, &value->lo);
    (void)native_vorbis_bigfloat_clear(scope->context, &value->hi);
}

native_vorbis_interval_status_t native_vorbis_interval_scope_init(
    native_vorbis_bigfloat_context_t *context, uint32_t precision,
    native_vorbis_interval_scope_t *scope) {
    if (!scope) return NATIVE_VORBIS_INTERVAL_INVALID;
    native_vorbis_interval_scope_t temporary = {context, precision};
    native_vorbis_interval_status_t status = nvi_scope(&temporary);
    if (status == NATIVE_VORBIS_INTERVAL_OK) *scope = temporary;
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_init(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *value) {
    if (!value) return NATIVE_VORBIS_INTERVAL_INVALID;
    native_vorbis_interval_status_t status = nvi_scope(scope);
    if (status == NATIVE_VORBIS_INTERVAL_OK) nvi_init(scope, value);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_check(
    const native_vorbis_interval_scope_t *scope, const native_vorbis_interval_t *value) {
    if (!value) return NATIVE_VORBIS_INTERVAL_INVALID;
    native_vorbis_interval_status_t status = nvi_point(scope, &value->lo);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = nvi_point(scope, &value->hi);
    if (status == NATIVE_VORBIS_INTERVAL_OK && bf_cmp(&value->lo, &value->hi) > 0)
        status = NATIVE_VORBIS_INTERVAL_INVALID;
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_clear(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *value) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, value);
    if (status == NATIVE_VORBIS_INTERVAL_OK) nvi_drop(scope, value);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_swap(
    const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *left, native_vorbis_interval_t *right) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, left);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = native_vorbis_interval_check(scope, right);
    if (status == NATIVE_VORBIS_INTERVAL_OK && left != right) {
        native_vorbis_interval_t temporary = *left;
        *left = *right; *right = temporary;
    }
    return status;
}

native_vorbis_interval_status_t nvi_publish(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, native_vorbis_interval_t *temporary) {
    return native_vorbis_interval_swap(scope, destination, temporary);
}

native_vorbis_interval_status_t native_vorbis_interval_point_cmp(
    const native_vorbis_interval_scope_t *scope, const bf_t *left, const bf_t *right, int *result) {
    if (!result) return NATIVE_VORBIS_INTERVAL_INVALID;
    native_vorbis_interval_status_t status = nvi_point(scope, left);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = nvi_point(scope, right);
    if (status == NATIVE_VORBIS_INTERVAL_OK) *result = bf_cmp(left, right);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_bounds(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const bf_t *lower, const bf_t *upper) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = nvi_point(scope, lower);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = nvi_point(scope, upper);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    if (bf_cmp(lower, upper) > 0) return NATIVE_VORBIS_INTERVAL_INVALID;
    native_vorbis_interval_t temporary; nvi_init(scope, &temporary);
    NVI_BF(native_vorbis_bigfloat_copy(scope->context, &temporary.lo, lower));
    NVI_BF(native_vorbis_bigfloat_copy(scope->context, &temporary.hi, upper));
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &temporary);
    return status;
}

native_vorbis_interval_status_t nvi_point_interval(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const bf_t *value) {
    return native_vorbis_interval_bounds(scope, destination, value, value);
}

native_vorbis_interval_status_t native_vorbis_interval_copy(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const native_vorbis_interval_t *source) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, source);
    return status == NATIVE_VORBIS_INTERVAL_OK ? native_vorbis_interval_bounds(scope, destination, &source->lo, &source->hi) : status;
}

native_vorbis_interval_status_t native_vorbis_interval_set_u64(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination, uint64_t value) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    native_vorbis_interval_t temporary; nvi_init(scope, &temporary);
    NVI_BF(native_vorbis_bigfloat_set_u64(scope->context, &temporary.lo, value));
    NVI_BF(native_vorbis_bigfloat_copy(scope->context, &temporary.hi, &temporary.lo));
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &temporary);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_import(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const uint32_t *words, size_t count, int64_t exponent, bool negative) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    native_vorbis_interval_t temporary; nvi_init(scope, &temporary);
    NVI_BF(native_vorbis_bigfloat_import(scope->context, &temporary.lo, words, count, exponent, negative));
    NVI_BF(native_vorbis_bigfloat_copy(scope->context, &temporary.hi, &temporary.lo));
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &temporary);
    return status;
}

typedef native_vorbis_bigfloat_status_t (*point_binary_t)(native_vorbis_bigfloat_context_t *,
    bf_t *, const bf_t *, const bf_t *, uint32_t, native_vorbis_bigfloat_round_t);

static native_vorbis_interval_status_t binary_check(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *left,
    const native_vorbis_interval_t *right) {
    native_vorbis_interval_status_t status = native_vorbis_interval_check(scope, destination);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = native_vorbis_interval_check(scope, left);
    if (status == NATIVE_VORBIS_INTERVAL_OK) status = native_vorbis_interval_check(scope, right);
    return status;
}

static native_vorbis_interval_status_t ordered_binary(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *left,
    const native_vorbis_interval_t *right, bool subtract) {
    native_vorbis_interval_status_t status = binary_check(scope, destination, left, right);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    native_vorbis_interval_t temporary; nvi_init(scope, &temporary);
    point_binary_t operation = subtract ? native_vorbis_bigfloat_sub : native_vorbis_bigfloat_add;
    NVI_BF(operation(scope->context, &temporary.lo, &left->lo, subtract ? &right->hi : &right->lo,
        scope->precision, NATIVE_VORBIS_BIGFLOAT_DOWN));
    NVI_BF(operation(scope->context, &temporary.hi, &left->hi, subtract ? &right->lo : &right->hi,
        scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &temporary);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_add(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *left, const native_vorbis_interval_t *right) {
    return ordered_binary(scope, destination, left, right, false);
}

native_vorbis_interval_status_t native_vorbis_interval_sub(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *left, const native_vorbis_interval_t *right) {
    return ordered_binary(scope, destination, left, right, true);
}

static void point_swap(bf_t *left, bf_t *right) { bf_t temporary = *left; *left = *right; *right = temporary; }

static native_vorbis_interval_status_t corner_binary(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *left,
    const native_vorbis_interval_t *right, bool divide) {
    native_vorbis_interval_status_t status = binary_check(scope, destination, left, right);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    bf_t zero; bf_init(&scope->context->engine, &zero);
    if (divide && bf_cmp(&right->lo, &zero) <= 0 && bf_cmp(&right->hi, &zero) >= 0)
        return nvi_zero(&right->lo) && nvi_zero(&right->hi) ? NATIVE_VORBIS_INTERVAL_ARITHMETIC : NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION;
    native_vorbis_interval_t temporary, candidate;
    nvi_init(scope, &temporary); nvi_init(scope, &candidate);
    point_binary_t operation = divide ? native_vorbis_bigfloat_div : native_vorbis_bigfloat_mul;
    for (unsigned i = 0; i < 4; ++i) {
        const bf_t *a = (i & 1) ? &left->hi : &left->lo;
        const bf_t *b = (i & 2) ? &right->hi : &right->lo;
        NVI_BF(operation(scope->context, &candidate.lo, a, b, scope->precision, NATIVE_VORBIS_BIGFLOAT_DOWN));
        NVI_BF(operation(scope->context, &candidate.hi, a, b, scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
        if (!i || bf_cmp(&candidate.lo, &temporary.lo) < 0) point_swap(&candidate.lo, &temporary.lo);
        if (!i || bf_cmp(&candidate.hi, &temporary.hi) > 0) point_swap(&candidate.hi, &temporary.hi);
    }
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &candidate); nvi_drop(scope, &temporary);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_mul(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *left, const native_vorbis_interval_t *right) {
    return corner_binary(scope, destination, left, right, false);
}

native_vorbis_interval_status_t native_vorbis_interval_div(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *left, const native_vorbis_interval_t *right) {
    return corner_binary(scope, destination, left, right, true);
}

native_vorbis_interval_status_t native_vorbis_interval_square(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *source) {
    native_vorbis_interval_status_t status = binary_check(scope, destination, source, source);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    native_vorbis_interval_t first, second;
    nvi_init(scope, &first); nvi_init(scope, &second);
    NVI_BF(native_vorbis_bigfloat_mul(scope->context, &first.lo, &source->lo, &source->lo, scope->precision, NATIVE_VORBIS_BIGFLOAT_DOWN));
    NVI_BF(native_vorbis_bigfloat_mul(scope->context, &first.hi, &source->lo, &source->lo, scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
    NVI_BF(native_vorbis_bigfloat_mul(scope->context, &second.lo, &source->hi, &source->hi, scope->precision, NATIVE_VORBIS_BIGFLOAT_DOWN));
    NVI_BF(native_vorbis_bigfloat_mul(scope->context, &second.hi, &source->hi, &source->hi, scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
    if (bf_cmp(&second.lo, &first.lo) < 0) point_swap(&second.lo, &first.lo);
    if (bf_cmp(&second.hi, &first.hi) > 0) point_swap(&second.hi, &first.hi);
    bf_t zero; bf_init(&scope->context->engine, &zero);
    if (bf_cmp(&source->lo, &zero) <= 0 && bf_cmp(&source->hi, &zero) >= 0)
        NVI_BF(native_vorbis_bigfloat_set_u64(scope->context, &first.lo, 0));
    status = nvi_publish(scope, destination, &first);
done:
    nvi_drop(scope, &second); nvi_drop(scope, &first);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_sqrt(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *source) {
    native_vorbis_interval_status_t status = binary_check(scope, destination, source, source);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    bf_t zero; bf_init(&scope->context->engine, &zero);
    if (bf_cmp(&source->lo, &zero) < 0)
        return bf_cmp(&source->hi, &zero) < 0 ? NATIVE_VORBIS_INTERVAL_ARITHMETIC : NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION;
    native_vorbis_interval_t temporary; nvi_init(scope, &temporary);
    NVI_BF(native_vorbis_bigfloat_sqrt(scope->context, &temporary.lo, &source->lo, scope->precision, NATIVE_VORBIS_BIGFLOAT_DOWN));
    NVI_BF(native_vorbis_bigfloat_sqrt(scope->context, &temporary.hi, &source->hi, scope->precision, NATIVE_VORBIS_BIGFLOAT_UP));
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &temporary);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_negate(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *source) {
    native_vorbis_interval_status_t status = binary_check(scope, destination, source, source);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    native_vorbis_interval_t temporary; nvi_init(scope, &temporary);
    NVI_BF(native_vorbis_bigfloat_copy(scope->context, &temporary.lo, &source->hi));
    NVI_BF(native_vorbis_bigfloat_copy(scope->context, &temporary.hi, &source->lo));
    bf_neg(&temporary.lo); bf_neg(&temporary.hi);
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &temporary);
    return status;
}

native_vorbis_interval_status_t native_vorbis_interval_scale2(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *source, int64_t exponent) {
    native_vorbis_interval_status_t status = binary_check(scope, destination, source, source);
    if (status != NATIVE_VORBIS_INTERVAL_OK) return status;
    const bf_t *points[2] = {&source->lo, &source->hi};
    for (unsigned i = 0; i < 2; ++i) {
        if (!points[i]->len) continue;
        int64_t top = points[i]->expn;
        if (exponent < -(int64_t)NATIVE_VORBIS_BIGFLOAT_MAX_TOP - top ||
            exponent > (int64_t)NATIVE_VORBIS_BIGFLOAT_MAX_TOP - top)
            return NATIVE_VORBIS_INTERVAL_ENGINE_LIMIT;
    }
    native_vorbis_interval_t temporary; nvi_init(scope, &temporary);
    NVI_TRY(native_vorbis_interval_copy(scope, &temporary, source));
    if (temporary.lo.len) temporary.lo.expn = (slimb_t)((int64_t)temporary.lo.expn + exponent);
    if (temporary.hi.len) temporary.hi.expn = (slimb_t)((int64_t)temporary.hi.expn + exponent);
    status = nvi_publish(scope, destination, &temporary);
done:
    nvi_drop(scope, &temporary);
    return status;
}
