// Rigorous interval enclosures over the selected checked bigfloat foundation.
#pragma once
#include "native_vorbis_bigfloat.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NATIVE_VORBIS_INTERVAL_OK = 0,
    NATIVE_VORBIS_INTERVAL_INVALID = -1,
    NATIVE_VORBIS_INTERVAL_ENGINE_LIMIT = -2,
    NATIVE_VORBIS_INTERVAL_NO_MEMORY = -3,
    NATIVE_VORBIS_INTERVAL_ARITHMETIC = -4,
    NATIVE_VORBIS_INTERVAL_CAPACITY = -5,
    NATIVE_VORBIS_INTERVAL_NEEDS_PRECISION = -6
} native_vorbis_interval_status_t;

typedef struct { bf_t lo, hi; } native_vorbis_interval_t;
typedef struct {
    native_vorbis_bigfloat_context_t *context;
    uint32_t precision; //2..NATIVE_VORBIS_BIGFLOAT_MAX_BITS, engine resource only.
} native_vorbis_interval_scope_t;

// All live descriptors belong to this serialized context. Caller storage is
// disjoint except explicitly permitted destination/operand aliasing. Initialize
// scope and intervals before use; allocator context outlives every interval.
// Arithmetic/constants/trig publish BOTH endpoints transactionally. A failure
// preserves destination fields/storage, releases temporary ownership, and may
// retain engine caches/OOM latch/statistics. Clear the foundation latch before
// retrying an allocation failure. It is not reset silently by this layer.
native_vorbis_interval_status_t native_vorbis_interval_scope_init(
    native_vorbis_bigfloat_context_t *context, uint32_t precision,
    native_vorbis_interval_scope_t *scope);
native_vorbis_interval_status_t native_vorbis_interval_init(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *value);
native_vorbis_interval_status_t native_vorbis_interval_clear(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *value);
native_vorbis_interval_status_t native_vorbis_interval_check(
    const native_vorbis_interval_scope_t *scope, const native_vorbis_interval_t *value);
// Safe ownership transfer: validates both pairs before allocation-free swap.
// A caller may use swap to commit a prepared pair, then clear the old temporary.
native_vorbis_interval_status_t native_vorbis_interval_swap(
    const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *left, native_vorbis_interval_t *right);

// Exact imports/copy do not round to scope.precision. Portable dyadic import
// follows the foundation's canonical input rules and engine envelope.
native_vorbis_interval_status_t native_vorbis_interval_set_u64(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    uint64_t value);
native_vorbis_interval_status_t native_vorbis_interval_import(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const uint32_t *words, size_t count, int64_t exponent, bool negative);
native_vorbis_interval_status_t native_vorbis_interval_bounds(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const bf_t *lower, const bf_t *upper);
native_vorbis_interval_status_t native_vorbis_interval_copy(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const native_vorbis_interval_t *source);

#define NATIVE_VORBIS_INTERVAL_BINARY_DECL(name) \
native_vorbis_interval_status_t native_vorbis_interval_##name( \
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination, \
    const native_vorbis_interval_t *left, const native_vorbis_interval_t *right)
NATIVE_VORBIS_INTERVAL_BINARY_DECL(add);
NATIVE_VORBIS_INTERVAL_BINARY_DECL(sub);
NATIVE_VORBIS_INTERVAL_BINARY_DECL(mul);
NATIVE_VORBIS_INTERVAL_BINARY_DECL(div);
#undef NATIVE_VORBIS_INTERVAL_BINARY_DECL
// Division that cannot establish a zero-free divisor returns NEEDS_PRECISION;
// exact zero division returns ARITHMETIC. Sqrt entirely below zero is ARITHMETIC;
// crossing below zero is NEEDS_PRECISION. Square always has a nonnegative lower
// bound, exactly0 when the input contains0. No per-endpoint clipping hides error.
native_vorbis_interval_status_t native_vorbis_interval_square(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const native_vorbis_interval_t *source);
native_vorbis_interval_status_t native_vorbis_interval_sqrt(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const native_vorbis_interval_t *source);
native_vorbis_interval_status_t native_vorbis_interval_negate(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const native_vorbis_interval_t *source);
native_vorbis_interval_status_t native_vorbis_interval_scale2(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const native_vorbis_interval_t *source, int64_t exponent);
// Validated finite POINT comparison (not an ambiguous ordering of intervals).
native_vorbis_interval_status_t native_vorbis_interval_point_cmp(
    const native_vorbis_interval_scope_t *scope,
    const bf_t *left, const bf_t *right, int *result);

// Proven rational-series enclosures; no stock constants/transcendentals.
// Pi uses Machin's alternating arctan identity; ln2 uses positive atanh series
// with an explicit geometric tail. Precision controls endpoint arithmetic and
// a tail budget, not a claim that the final interval has exactly2^-p width.
native_vorbis_interval_status_t native_vorbis_interval_pi(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination);
native_vorbis_interval_status_t native_vorbis_interval_ln2(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination);

// Supplied pi must be a PROVEN enclosure of mathematical pi, e.g. pi() above;
// finite numeric endpoints alone cannot prove that provenance. The caller may
// cache pi externally at each precision. A candidate integer quadrant is kept
// as arbitrary-limb magnitude; reduction must verify residual in[-2,2], or
// returns NEEDS_PRECISION. Exact-zero residual identities stay exact. Taylor
// remainders are explicit; sine's tail target is relative to max|residual| so
// tiny values are not replaced by a fixed absolute cutoff. Resource/precision
// refusal remains retryable and is never a malformed-stream classification.
native_vorbis_interval_status_t native_vorbis_interval_sin(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const native_vorbis_interval_t *angle, const native_vorbis_interval_t *pi);
native_vorbis_interval_status_t native_vorbis_interval_cos(
    const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *destination,
    const native_vorbis_interval_t *angle, const native_vorbis_interval_t *pi);

#ifdef __cplusplus
}
#endif
