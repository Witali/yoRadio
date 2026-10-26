// Exact floor1/residue product, Vorbis I 4.3.6 and 7.2.4.
#pragma once
#include "native_vorbis_packet_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t bins, limbs, magnitude_bits;
    int32_t exponent;
    uint64_t limb_count;
} native_vorbis_floor1_product_layout_t;

typedef struct {
    native_vorbis_floor1_product_layout_t layout;
    const uint32_t *samples;
} native_vorbis_floor1_product_t;

// Scale one channel of a coherent planar residue grid by floor1 table indices.
// Each result is a little-significance-first two's-complement integer times
// 2^exponent, with absolute integer strictly below 2^magnitude_bits. The exact
// positive binary32 coefficients are the unchanged Xiph/spec inverse-dB table;
// no residue conversion to float, product rounding or clipping occurs.
//
// The input shape uses the residue representation (up to34 limbs); its numeric
// shape is checked independently of setup. Every selected sample must satisfy
// its signed domain. The planner uses actual curve factors, not a constant
// worst-case width. The universal output bound is36 limbs. Zero input grids
// retain bins but have all other numeric fields0 and need no indices or arrays.
// Index0 is a positive quiet floor; only an absent floor means silence.
//
// Measurement requires count==source.bins, including zero grids. Nonzero grids
// require count valid index bytes. Failure preserves layout. Scale remeasures,
// checks full source object extent and selected samples before output writes;
// every failure preserves output/result. Capacities count uint32 elements.
// All descriptors, arrays and outputs are disjoint and immutable inputs stay
// alive throughout. No heap, VLA, in-place operation or shared mutable state.
native_vorbis_numeric_status_t native_vorbis_floor1_scale_measure(
    const native_vorbis_residue_layout_t *source,
    const uint8_t *indices, size_t count,
    native_vorbis_floor1_product_layout_t *layout);

native_vorbis_numeric_status_t native_vorbis_floor1_scale(
    const native_vorbis_residue_layout_t *source,
    const uint32_t *spectrum, size_t spectrum_capacity, uint32_t channel,
    const uint8_t *indices, size_t count,
    uint32_t *output, size_t output_capacity,
    native_vorbis_floor1_product_t *result);

// Compose reconstruction/curve/product for one floor1 channel of a successful
// immutable frame. Setup and all frame borrows must remain alive. Reuse the
// caller's bins-byte curve scratch between channels; it may change on failure.
// A floor0 channel is an invalid use of this floor1-specific API, not a stream
// rejection. Absent floors and implicit-zero residue need no scratch or output.
// Present zero residue can be skipped because every floor1 factor is finite;
// this does not establish a floor0 pole policy. No transform/overlap/PCM yet.
// Measure preserves layout on failure; product preserves output and result.
native_vorbis_numeric_status_t native_vorbis_frame_floor1_measure(
    const native_vorbis_packet_frame_t *frame, uint32_t channel,
    uint8_t *curve, size_t curve_capacity,
    native_vorbis_floor1_product_layout_t *layout);

native_vorbis_numeric_status_t native_vorbis_frame_floor1_product(
    const native_vorbis_packet_frame_t *frame, uint32_t channel,
    uint8_t *curve, size_t curve_capacity,
    uint32_t *output, size_t output_capacity,
    native_vorbis_floor1_product_t *result);

#ifdef __cplusplus
}
#endif
