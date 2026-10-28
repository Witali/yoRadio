// Vorbis I 4.3.8: adjacent-block window terms with independent retained scales.
#pragma once
#include "native_vorbis_window.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    const native_vorbis_window_plan_t *short_plan, *long_plan;
    double *history;
    size_t history_capacity;
    uint32_t previous_size; // 0 means priming/reset; otherwise one configured size
    int64_t previous_exponent;
} native_vorbis_overlap_t;

typedef struct {
    uint32_t count, history_count;
} native_vorbis_overlap_requirements_t;

typedef struct {
    native_vorbis_transform_block_t previous, current;
} native_vorbis_overlap_terms_t;

// Keep successful prepared plans and their lookups alive/immutable. Reserve
// long_size/2 history doubles so every size transition can run without allocation.
// This constructor does not read or initialize history. All borrows/storage/state
// are disjoint; replacing an existing state also requires disjoint new storage.
// Failure preserves state/history. No heap, VLA, task or internal synchronization.
native_vorbis_numeric_status_t native_vorbis_overlap_init(
    const native_vorbis_window_plan_t *short_plan,
    const native_vorbis_window_plan_t *long_plan,
    double *history, size_t history_capacity, native_vorbis_overlap_t *state);

// Discard prior overlap, retaining configured plans/storage. History bytes are
// left alone and are not read by the next priming block. Failure preserves state.
native_vorbis_numeric_status_t native_vorbis_overlap_reset(native_vorbis_overlap_t *state);

// For the first block, count==0. Otherwise count=(previous_size+blocksize)/4.
// history_count==blocksize/2. No sample values are read; failure preserves result.
native_vorbis_numeric_status_t native_vorbis_overlap_measure(
    const native_vorbis_overlap_t *state, uint32_t blocksize,
    native_vorbis_overlap_requirements_t *requirements);

// Accept one full UNWINDOWED inverse-transform block. Infer slopes from actual
// neighboring sizes (Vorbis I 1.3.2), keep its unwindowed right half as history,
// and emit the two windowed contributions to each ready sample. Their exponents
// are retained independently and never subtracted/aligned here. Consumers must
// add/round them together; individually clipping or discarding one term can lose
// cancellation or change a PCM half tie. No invented terminal block/flush.
//
// All source and active history values must be finite. Size, byte extent,
// capacities and every value are checked BEFORE any state/history/output/result
// write. Every returned failure preserves all of them, allowing retry. On success
// output count agrees for both terms; exponent and pointer identify each borrow.
// Priming accepts null output pointers with zero capacities and emits count0.
// Unused tails are unchanged. Binary64 slope products may underflow normally.
// Source/state/history/plans/lookups/both outputs/result are disjoint. Serialize
// state use and consume outputs before reusing their arrays. Reset, discontinuity,
// granule/EOS trimming and channel scheduling belong to the stream owner.
native_vorbis_numeric_status_t native_vorbis_overlap_push(
    native_vorbis_overlap_t *state,
    const native_vorbis_transform_block_t *source, size_t source_capacity,
    double *previous_output, size_t previous_capacity,
    double *current_output, size_t current_capacity,
    native_vorbis_overlap_terms_t *result);

#ifdef __cplusplus
}
#endif
