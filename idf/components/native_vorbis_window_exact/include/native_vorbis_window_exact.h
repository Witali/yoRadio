// Exact products of the existing binary64 Vorbis samples and window factors.
#pragma once
#include "native_vorbis_window.h"

#ifdef __cplusplus
extern "C" {
#endif

// Value = (-1)^negative * (low + 2^64*high) * 2^(exponent + shift).
// The sum exponent+shift is SYMBOLIC, never signed64 arithmetic. Nonzero
// magnitude is odd and at most106 bits; shift lies in[-2148,1023]. The complete
// supplied signed64 base exponent is retained. Zero has every field zero.
// This is exact for the supplied binary64 operands, not the real-valued
// transcendental window curve or an approximate preceding inverse transform.
typedef struct {
    uint64_t low, high;
    int64_t exponent;
    int32_t shift;
    bool negative;
} native_vorbis_window_product_t;

// Any finite binary64 sample and finite window factor in[0,1] are accepted.
// Either sign of zero is permitted and canonicalized. Check both operands
// before a zero shortcut: NaN/Inf or a factor outside[0,1] returns RANGE.
// Null result returns INVALID. Every failure preserves actual result bytes.
// Bit decomposition/integer multiplication performs no floating product or
// rounding and cannot underflow, overflow or depend on the rounding mode.
// No heap, VLA, __int128 or arithmetic on the base exponent is required.
native_vorbis_numeric_status_t native_vorbis_window_multiply_exact(
    double sample, double factor, int64_t exponent,
    native_vorbis_window_product_t *result);

// Copy descriptors, borrowing successful immutable prepared-window lookups
// and a full unwindowed transform sample array. Descriptors supplied during
// preparation need not remain alive; the borrowed arrays must remain alive
// and immutable until all reads end. The view stores no materialized array.
typedef struct {
    native_vorbis_window_shape_t shape;
    native_vorbis_window_plan_t left, right;
    native_vorbis_transform_block_t source;
} native_vorbis_window_exact_view_t;

// Coherent geometry matches the existing window API, with legal64..8192 sizes.
// Capacity counts doubles and must have an addressable byte extent. All source
// samples and both whole lookup arrays are checked before publishing the view,
// even outside active support. Finite factors in[0,1] are required. Every
// refusal preserves view and all supplied source/descriptor/lookup bytes.
// Immutable sources/lookups may share storage; view is disjoint from borrows.
native_vorbis_numeric_status_t native_vorbis_window_exact_prepare(
    const native_vorbis_window_shape_t *shape,
    const native_vorbis_window_plan_t *left,
    const native_vorbis_window_plan_t *right,
    const native_vorbis_transform_block_t *source, size_t source_capacity,
    native_vorbis_window_exact_view_t *view);

// Read one index from a successful immutable view. Support zeros, ascending
// and descending slopes and unity plateau retain existing window geometry.
// The exact scalar product preserves subnormal operands and all106 product
// bits without materializing a floating product or a standalone huge scale.
// Failure preserves result; success preserves view/arrays. Result is disjoint.
// No overlap/history, PCM, granule trimming, task or production selection.
native_vorbis_numeric_status_t native_vorbis_window_exact_at(
    const native_vorbis_window_exact_view_t *view, uint32_t index,
    native_vorbis_window_product_t *result);

#ifdef __cplusplus
}
#endif
