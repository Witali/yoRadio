// S16 output from complete exact window products, before any narrowing.
#pragma once
#include "native_vorbis_window_exact.h"

#ifdef __cplusplus
extern "C" {
#endif

// Round nearest-even ((previous + current)*32768), then clamp to S16.
// Each source is a canonical native_vorbis_window_product_t: zero has every
// field zero; nonzero magnitude is odd, at most106 bits (high<2^42), with
// shift in[-2148,1023]. Both full signed64 base exponents are accepted and
// exponent+shift remains symbolic. Every canonical106-bit magnitude is valid;
// callers need not prove that it factors into two53-bit significands.
// Sources are well-formed C objects, including ordinary bool representations.
//
// Null pointers/noncanonical products return INVALID before any result write.
// Every refusal preserves actual result/source bytes. Valid sources may share
// immutable storage; result is disjoint. Integer comparison adds both complete
// terms before clipping or rounding, preserving cancellation and tiny half-tie
// perturbations even across enormous exponent gaps. No heap/VLA/__int128,
// floating arithmetic or rounding-environment dependency. Exactness covers
// these supplied dyadics, not errors already introduced by floor/IMDCT/curve.
native_vorbis_numeric_status_t native_vorbis_pcm_s16_product_pair(
    const native_vorbis_window_product_t *previous,
    const native_vorbis_window_product_t *current, int16_t *result);

// Convert two logical slices from successful immutable exact-window views.
// At output i, read previous[previous_begin+i] and current[current_begin+i].
// Logical indices outside either full block are exact zero, including negative
// indices; arithmetic on int32 origins plus uint32 i is performed in int64.
// For adjacent legal sizes A/B use origins A/2 and ((int32_t)B-(int32_t)A)/4,
// count=(A+B)/4, with each prepared view using the actual neighbor's slope.
// Cast BEFORE subtraction: uint32 B-A would wrap on long-to-short transitions.
// This routine does not
// maintain history, decide priming/reset, trim granules or invent a flush block.
//
// Both views remain required, even for count0. A zero count permits null output.
// Capacity counts S16 elements; excessive byte extent returns RANGE, insufficient
// capacity CAPACITY, null views/nonzero output INVALID. View descriptor and all
// selected-read checks precede writes. Every refusal preserves output and all
// inputs, including a selected late nonfinite operand. Successful views/arrays
// stay immutable and alive through BOTH preflight and publication passes.
// They may share read-only storage; output is disjoint from all borrows/views.
// No full106-bit product arrays, heap, VLA, task or production selection.
native_vorbis_numeric_status_t native_vorbis_pcm_s16_windows(
    const native_vorbis_window_exact_view_t *previous, int32_t previous_begin,
    const native_vorbis_window_exact_view_t *current, int32_t current_begin,
    uint32_t count, int16_t *output, size_t output_capacity);

#ifdef __cplusplus
}
#endif
