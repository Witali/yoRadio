// Frame-channel floor0 application; exact residue survives until joint rounding.
#pragma once
#include "native_vorbis_transform.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE = 0,
    NATIVE_VORBIS_FLOOR0_NEEDS_WIDER = 1,
    NATIVE_VORBIS_FLOOR0_NEEDS_PRECISION = 2,
    NATIVE_VORBIS_FLOOR0_UNDEFINED_MAPPING = 3,
    NATIVE_VORBIS_FLOOR0_UNDEFINED_POLE = 4,
    NATIVE_VORBIS_FLOOR0_UNDEFINED_INDETERMINATE = 5
} native_vorbis_floor0_route_t;

// Positive binary64 significand times2^exponent, with the residue's common
// exponent already incorporated. A zero mantissa is used only for zero residue
// bins. Nonzero mantissas have exactly53 bits, including binary64 unity/powers.
typedef struct {
    uint64_t mantissa;
    int64_t exponent;
} native_vorbis_floor0_factor_t;

typedef struct {
    const native_vorbis_packet_frame_t *frame;
    uint32_t channel, bins;
    native_vorbis_floor0_route_t route;
    const native_vorbis_floor0_factor_t *factors;
    const uint16_t *bark_map;
    int64_t exponent;
    uint32_t gain_evaluations, minimum_log_fraction_bits;
    uint32_t route_sample; // UINT32_MAX when no single bin identifies the route
    bool zero, approximate;
} native_vorbis_floor0_spectrum_plan_t;

// Frame/setup/pools are successful immutable owned front-end borrows. Select a
// type0 channel; another type is caller misuse, not an unsupported Vorbis stream.
// Preserve original floor presence: absent means silence even for coupled
// nonzero residue and bypasses Bark/LSP math. For active floors, zero rate/map
// is an unresolved mapping domain, not a newly invented header error. Exact
// affine LSPs are dyadic rationals; the only denominator pole for mapped
// theta in[0,pi) can occur at Bark0 when an even-index LSP is exactlyzero.
// Classify it before any zero-residue shortcut. Offset0 with positive D is unity.
//
// Nonzero finite bins use the existing owned approximate scaled-log gain,
// split into integer/fraction parts, then binary64 exp2(fraction). Their53-bit
// dyadic factors multiply exact residue integers before ONE spectrum rounding.
// The common output grid uses maximum unrounded top638 and requires minimum
// top>=-1022; rounding may reach2^639, within the existing IMDCT input bound.
// Larger spans route the entire channel to NEEDS_WIDER. A log with no retained
// binary64 fractional precision (scaled exponent>=53) routes NEEDS_PRECISION.
// Int64 fit or remaining fractional bits is NOT evidence of gain accuracy.
// Every non-identity gain candidate is explicitly approximate and has no
// universal error certificate; minimum_log_fraction_bits describes only the
// stored logarithm's resolution, not errors in preceding transcendental math.
//
// NEEDS_* retains frame/channel/raw amplitude/LSP/residue provenance through
// this borrowed plan. It is not an implemented wider fallback or permission to
// reject a valid stream. Undefined outcomes retain policy decisions separately.
// No output spectrum/PCM is published by prepare and no production route chosen.
//
// Nonzero candidates need bins map entries and bins factor entries. Absent or
// proven finite zero channels need neither. Capacity/byte checks precede scratch
// writes; scratch may change on later numeric failure or noncandidate routing.
// Every returned failure preserves plan. Successful routing publishes plan last;
// only CANDIDATE plans may be materialized. Keep frame/map/factors alive and
// immutable until consumption, disjoint from descriptors and later outputs.
native_vorbis_numeric_status_t native_vorbis_frame_floor0_prepare(
    const native_vorbis_packet_frame_t *frame, uint32_t channel,
    uint16_t *bark_map, size_t map_capacity,
    native_vorbis_floor0_factor_t *factors, size_t factor_capacity,
    native_vorbis_floor0_spectrum_plan_t *plan);

// Materialize a successful immutable CANDIDATE plan in bins caller doubles.
// Preflight all shapes/domains/capacities and selected factors before any output
// write. Every failure preserves output/result. Successful output is suitable
// for native_vorbis_imdct_transform_binary64; source residue is never narrowed
// first or multiplied by an overflowing standalone linear gain. Zero channels
// write canonical+0 and exponent0. No heap/VLA, transform, window, overlap or
// PCM conversion is executed here. Caller owns storage and serializes reuse.
native_vorbis_numeric_status_t native_vorbis_frame_floor0_materialize(
    const native_vorbis_floor0_spectrum_plan_t *plan,
    double *output, size_t output_capacity,
    native_vorbis_transform_block_t *result);

#ifdef __cplusplus
}
#endif
