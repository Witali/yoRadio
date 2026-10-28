// Vorbis I window, sections 4.3.1 and 4.3.8; caller-owned binary64 storage.
#pragma once
#include "native_vorbis_transform.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t blocksize;
    const double *rise; // blocksize/2 immutable coefficients
} native_vorbis_window_plan_t;

typedef struct {
    uint32_t blocksize, left_size, right_size;
    uint32_t left_begin, left_end, right_begin, right_end;
} native_vorbis_window_shape_t;

// Prepare the rising half of a legal 64..8192 power-of-two window. The caller
// provides blocksize/2 doubles. Checks precede writes; failure preserves plan
// and coefficients. Plan, storage and live old-plan borrows are disjoint.
// After success keep both plan and coefficients alive and immutable.
native_vorbis_numeric_status_t native_vorbis_window_prepare(
    uint32_t blocksize, double *coefficients, size_t capacity,
    native_vorbis_window_plan_t *plan);

// Short/long are the identification-header sizes, short<=long. Flags are 0/1.
// Short blocks ignore previous/next flags and use short slopes on both sides.
// Failure preserves shape. A stream may instead infer neighbor flags from
// actual adjacent block sizes, as explicitly permitted by Vorbis I 1.3.2.
native_vorbis_numeric_status_t native_vorbis_window_shape(
    uint32_t short_size, uint32_t long_size, unsigned current_long,
    unsigned previous_long, unsigned next_long,
    native_vorbis_window_shape_t *shape);

// Apply a coherent shape using successful plans of left_size/right_size and
// a full unwindowed transform block. Every input sample must be finite. Input
// and output storage, descriptors, shape and lookup borrows are disjoint.
// Failure preserves output/result; success retains the entire int64 exponent.
// Outside support use +0; the plateau preserves input bits; slopes use one
// binary64 product. Normal nearest arithmetic, no fast-math/contraction.
// No clipping, rescaling, allocation, overlap/history or granule trimming.
native_vorbis_numeric_status_t native_vorbis_window_apply(
    const native_vorbis_window_shape_t *shape,
    const native_vorbis_window_plan_t *left,
    const native_vorbis_window_plan_t *right,
    const native_vorbis_transform_block_t *source, size_t source_capacity,
    double *output, size_t output_capacity,
    native_vorbis_transform_block_t *result);

#ifdef __cplusplus
}
#endif
