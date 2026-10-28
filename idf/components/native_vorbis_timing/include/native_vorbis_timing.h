// Vorbis I appendix A.2, full-rate PCM sample counts per channel, not bytes.
#pragma once
#include "native_vorbis_floor0.h"

#ifdef __cplusplus
extern "C" {
#endif

// Every legal ready span is <=4096. Above this counter threshold all excess
// comparisons against signed64 wire anchors produce the same bounded trim.
// Saturation is internal bookkeeping, never an exact timestamp or format cap.
#define NATIVE_VORBIS_TIMING_COUNTER_LIMIT (UINT64_C(0x7fffffffffffffff) + UINT64_C(4096))

typedef struct {
    uint32_t short_size, long_size, previous_size;
    uint32_t position_known, end_seen;
    // Each is min(mathematical value,COUNTER_LIMIT). At the limit only a lower
    // bound is retained; neither is an exported exact total or inferred offset.
    uint64_t bounded_sample_count, bounded_prediction;
} native_vorbis_timing_t;

typedef struct {
    uint32_t blocksize;
    int64_t granule_position; // -1 unknown; 0..INT64_MAX known; lower invalid
    uint32_t end_of_stream, discontinuity; // each 0/1
} native_vorbis_timing_event_t;

typedef enum {
    NATIVE_VORBIS_POSITION_UNKNOWN = 0,
    NATIVE_VORBIS_POSITION_KNOWN = 1,
    NATIVE_VORBIS_POSITION_EXCEEDS_WIRE_DOMAIN = 2
} native_vorbis_position_kind_t;

typedef struct {
    uint32_t available, discard_start, discard_end, count;
    native_vorbis_position_kind_t position_kind;
    int64_t end_position; // exact estimated end only when position_kind==KNOWN
} native_vorbis_timing_result_t;

// Legal identification sizes are powers64..8192 with short<=long. Initialize
// or restart metadata only; no packet, PCM, overlap state, storage or task is
// touched. Failure preserves state. State/event/result objects are disjoint.
native_vorbis_numeric_status_t native_vorbis_timing_init(
    uint32_t short_size, uint32_t long_size, native_vorbis_timing_t *state);

// Hard restart primes again, retaining configured sizes. The stream owner must
// separately reset numeric overlap/history when it selects that recovery policy.
// A failed reset preserves state; no repair of a forged/corrupt state is implied.
native_vorbis_numeric_status_t native_vorbis_timing_reset(native_vorbis_timing_t *state);

// Process one decoded audio block after any pending output is consumed. First
// block has available0; otherwise available=(previous_size+blocksize)/4. Return
// a contiguous subspan [discard_start,discard_start+count) of that ready data.
// First known anchor trims the beginning unless EOS (then trim the end); later
// backdated EOS trims only current data. No call can rewind already returned data.
// Non-EOS anchor mismatches resynchronize position without inventing padding or
// dropping samples, matching Xiph. An unset EOS anchor adds no fabricated trim.
//
// Discontinuity resets position/local count but retains previous_size/ready
// overlap, matching Xiph's sequence-gap bookkeeping. It is NOT a hard restart.
// The caller detects transport sequence changes and chooses its numeric policy.
// end_seen is sticky; chain ownership decides when to stop or reset for a link.
//
// All validation precedes writes. Failure preserves state/event/result bytes;
// success publishes both state and result. No heap, VLA, counter overflow,
// floating arithmetic, transport parsing or deferred synthesis execution.
// Unknown runs are unbounded: counters saturate only where all trim decisions
// are provably unchanged. A prediction beyond signed64 is reported explicitly,
// never narrowed or returned as an exact end_position. Normal sample-rate
// conversion, channel interleave and output byte counts belong to later layers.
native_vorbis_numeric_status_t native_vorbis_timing_push(
    native_vorbis_timing_t *state, const native_vorbis_timing_event_t *event,
    native_vorbis_timing_result_t *result);

#ifdef __cplusplus
}
#endif
