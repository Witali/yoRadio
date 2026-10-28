// Exact S16 boundary for a sum of two independently scaled binary64 terms.
#pragma once
#include "native_vorbis_transform.h"

#ifdef __cplusplus
extern "C" {
#endif

// Each output is roundTiesToEven((previous[i]*2^previous.exponent +
// current[i]*2^current.exponent)*32768), then saturated to [-32768,32767].
// Both counts match; all input doubles must be finite. Both entire signed64
// exponents are accepted. Exact cancellation and arbitrarily tiny tie-breaking
// terms are retained; no standalone scale, addition or float-to-int conversion
// can overflow. This is exact for the supplied dyadic terms, not an accuracy
// guarantee for prior approximate transforms/windows or floor0 representations.
//
// Capacities count elements and must have addressable byte extents. A zero count
// permits NULL arrays/output. Descriptors remain required. Every failure leaves
// output and inputs unchanged, including rejection of a late NaN/Inf. Successful
// calls preserve all immutable inputs/descriptors. They may share immutable
// storage with each other, but output must be disjoint. No heap, VLA, task or
// rounding-environment dependency. No native/production selection is implied.
native_vorbis_numeric_status_t native_vorbis_pcm_s16_pair(
    const native_vorbis_transform_block_t *previous, size_t previous_capacity,
    const native_vorbis_transform_block_t *current, size_t current_capacity,
    int16_t *output, size_t output_capacity);

#ifdef __cplusplus
}
#endif
