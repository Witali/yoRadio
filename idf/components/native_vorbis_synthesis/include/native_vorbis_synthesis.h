// Stateful multi-channel exact-window synthesis with shared granule bookkeeping.
#pragma once
#include "native_vorbis_pcm_exact.h"
#include "native_vorbis_timing.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint64_t history_samples;
    uint32_t exponent_count, max_frames;
    uint64_t max_pcm_samples;
} native_vorbis_synthesis_requirements_t;

typedef struct {
    const native_vorbis_window_plan_t *short_plan, *long_plan;
    double *history;
    size_t history_capacity;
    int64_t *exponents;
    size_t exponent_capacity;
    uint32_t channels;
    native_vorbis_timing_t timing;
} native_vorbis_synthesis_t;

typedef struct {
    native_vorbis_timing_result_t timing;
    uint32_t channels;
    uint64_t pcm_samples;
} native_vorbis_synthesis_result_t;

// Legal identification sizes64..8192 and channels1..255, short<=long. History
// uses channels*(long_size/2) doubles with a fixed long_size/2 stride; one base
// exponent per channel. Output capacity counts interleaved S16 SAMPLES, while
// timing counts FRAMES per channel. Requirements are storage costs, not measured
// heap availability. Failure preserves requirements; no allocation is performed.
native_vorbis_numeric_status_t native_vorbis_synthesis_measure(
    uint32_t short_size, uint32_t long_size, uint32_t channels,
    native_vorbis_synthesis_requirements_t *requirements);

// Borrow successful immutable prepared windows and caller-owned history/base
// storage. Plans/lookups, state, storage and external destinations are disjoint;
// read-only window lookups may share storage. Capacity counts elements and has
// a checked byte extent. Initialization validates coefficients and publishes
// state last; it never reads or writes history/exponent storage. Failure leaves
// every supplied object unchanged. Keep all borrows alive and serialize use.
native_vorbis_numeric_status_t native_vorbis_synthesis_init(
    const native_vorbis_window_plan_t *short_plan,
    const native_vorbis_window_plan_t *long_plan, uint32_t channels,
    double *history, size_t history_capacity,
    int64_t *exponents, size_t exponent_capacity,
    native_vorbis_synthesis_t *state);

// Hard restart primes all channels again and resets timing. History/exponent
// bytes stay untouched and unread until a new priming block replaces them.
// Validation/failure preserves state; no repair of forged descriptors is implied.
native_vorbis_numeric_status_t native_vorbis_synthesis_reset(
    native_vorbis_synthesis_t *state);

// Push all channels of one complete UNWINDOWED IMDCT block, in original channel
// order. Every count matches event.blocksize; both descriptor/capacity arrays
// contain at least state.channels entries within block_capacity. All source
// values and active half-history are finite; window factors are finite[0,1].
// Source bases accept the whole signed64 domain without alignment/subtraction.
//
// Actual adjacent sizes determine slopes and ready frames. Exact window
// products retain up to106 bits; both contributions are added before one final
// nearest-even S16 rounding/clamp. Shared timing chooses a contiguous ready
// subspan; output is interleaved at frame*channels+channel. First block primes
// with no output. A zero-count span permits null output, but all current blocks
// are still required and their right halves are cached. No invented final block.
//
// Every descriptor, metadata, extent, capacity, coefficient and ALL channel
// source/active-history checks finish before ANY output/history/base/state/result
// write. Every returned failure preserves all supplied bytes, allowing retry.
// Under immutable borrows publication is infallible; all channel outputs are
// complete before current right halves/bases replace history and timing/result
// are published last. Unused history/output tails remain untouched.
//
// Gap/discontinuity follows the existing timing policy: position is reanchored
// while numeric overlap is retained. Reset is the separate hard-restart policy.
// EOS is sticky bookkeeping; the stream owner decides logical-link termination.
// State/history/bases/output/result/metadata/descriptors are disjoint from each
// other and the lookups/source arrays. Source channels may share immutable data.
// Consume output before reuse; no locks, heap, VLA, task, transport parsing,
// sample-rate conversion, production selection or changed core/audio backend.
native_vorbis_numeric_status_t native_vorbis_synthesis_push(
    native_vorbis_synthesis_t *state, const native_vorbis_timing_event_t *event,
    const native_vorbis_transform_block_t *blocks,
    const size_t *source_capacities, size_t block_capacity,
    int16_t *output, size_t output_capacity,
    native_vorbis_synthesis_result_t *result);

#ifdef __cplusplus
}
#endif
