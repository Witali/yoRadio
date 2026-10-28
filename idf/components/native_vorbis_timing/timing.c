// Xiph-compatible trim decisions without signed/ILP32 intermediate overflow.
#include "native_vorbis_timing.h"

static int legal_size(uint32_t n) {
    return n >= 64 && n <= 8192 && !(n & (n - 1));
}

static int coherent_state(const native_vorbis_timing_t *state) {
    if (!state || !legal_size(state->short_size) || !legal_size(state->long_size) ||
        state->short_size > state->long_size || state->position_known > 1 || state->end_seen > 1 ||
        (state->previous_size && state->previous_size != state->short_size &&
         state->previous_size != state->long_size) ||
        state->bounded_sample_count > NATIVE_VORBIS_TIMING_COUNTER_LIMIT ||
        state->bounded_prediction > NATIVE_VORBIS_TIMING_COUNTER_LIMIT ||
        (!state->position_known && state->bounded_prediction)) return 0;
    if (!state->previous_size && (state->position_known || state->end_seen ||
        state->bounded_sample_count || state->bounded_prediction)) return 0;
    return 1;
}

static uint64_t capped_add(uint64_t value, uint32_t increment) {
    return value > NATIVE_VORBIS_TIMING_COUNTER_LIMIT - increment ?
        NATIVE_VORBIS_TIMING_COUNTER_LIMIT : value + increment;
}

static uint32_t bounded_excess(uint64_t predicted, uint64_t anchor, uint32_t available) {
    if (predicted <= anchor) return 0;
    uint64_t extra = predicted - anchor;
    return extra > available ? available : (uint32_t)extra;
}

native_vorbis_numeric_status_t native_vorbis_timing_init(
    uint32_t short_size, uint32_t long_size, native_vorbis_timing_t *state) {
    if (!state || !legal_size(short_size) || !legal_size(long_size) || short_size > long_size)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    *state = (native_vorbis_timing_t){.short_size = short_size, .long_size = long_size};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_timing_reset(native_vorbis_timing_t *state) {
    if (!coherent_state(state)) return NATIVE_VORBIS_NUMERIC_INVALID;
    return native_vorbis_timing_init(state->short_size, state->long_size, state);
}

native_vorbis_numeric_status_t native_vorbis_timing_push(
    native_vorbis_timing_t *state, const native_vorbis_timing_event_t *event,
    native_vorbis_timing_result_t *result) {
    if (!coherent_state(state) || !event || !result || event->granule_position < -1 ||
        event->end_of_stream > 1 || event->discontinuity > 1 ||
        (event->blocksize != state->short_size && event->blocksize != state->long_size))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    uint32_t available = state->previous_size ? (state->previous_size + event->blocksize) / 4 : 0;
    native_vorbis_timing_t next = *state;
    native_vorbis_timing_result_t span = {.available = available, .count = available};
    if (!state->previous_size || event->discontinuity) {
        next.bounded_sample_count = 0;
        next.bounded_prediction = 0;
        next.position_known = 0;
    } else {
        next.bounded_sample_count = capped_add(next.bounded_sample_count, available);
    }
    if (!next.position_known) {
        if (event->granule_position >= 0) {
            uint64_t anchor = (uint64_t)event->granule_position;
            uint32_t extra = bounded_excess(next.bounded_sample_count, anchor, available);
            if (event->end_of_stream) span.discard_end = extra;
            else span.discard_start = extra;
            next.bounded_prediction = anchor;
            next.position_known = 1;
        }
    } else {
        next.bounded_prediction = capped_add(next.bounded_prediction, available);
        if (event->granule_position >= 0) {
            uint64_t anchor = (uint64_t)event->granule_position;
            if (event->end_of_stream)
                span.discard_end = bounded_excess(next.bounded_prediction, anchor, available);
            next.bounded_prediction = anchor;
        }
    }
    span.count -= span.discard_start + span.discard_end;
    if (!next.position_known) {
        span.position_kind = NATIVE_VORBIS_POSITION_UNKNOWN;
    } else if (next.bounded_prediction > INT64_MAX) {
        span.position_kind = NATIVE_VORBIS_POSITION_EXCEEDS_WIRE_DOMAIN;
    } else {
        span.position_kind = NATIVE_VORBIS_POSITION_KNOWN;
        span.end_position = (int64_t)next.bounded_prediction;
    }
    next.previous_size = event->blocksize;
    next.end_seen |= event->end_of_stream;
    *state = next;
    *result = span;
    return NATIVE_VORBIS_NUMERIC_OK;
}
