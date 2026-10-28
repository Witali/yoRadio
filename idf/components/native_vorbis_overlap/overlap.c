// Xiph-compatible overlap geometry; retain scales until the final addition.
#include "native_vorbis_overlap.h"
#include <math.h>
#include <string.h>

static int legal_size(uint32_t n) {
    return n >= 64 && n <= 8192 && !(n & (n - 1));
}

static int coherent_plans(const native_vorbis_window_plan_t *small,
    const native_vorbis_window_plan_t *large) {
    return small && large && legal_size(small->blocksize) && legal_size(large->blocksize) &&
        small->blocksize <= large->blocksize && small->rise && large->rise;
}

static native_vorbis_numeric_status_t coherent_state(const native_vorbis_overlap_t *state) {
    if (!state || !coherent_plans(state->short_plan, state->long_plan) ||
        (state->previous_size && state->previous_size != state->short_plan->blocksize &&
         state->previous_size != state->long_plan->blocksize)) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (state->history_capacity > SIZE_MAX / sizeof(*state->history)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (state->history_capacity < state->long_plan->blocksize / 2) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!state->history) return NATIVE_VORBIS_NUMERIC_INVALID;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_overlap_init(
    const native_vorbis_window_plan_t *short_plan,
    const native_vorbis_window_plan_t *long_plan,
    double *history, size_t history_capacity, native_vorbis_overlap_t *state) {
    if (!state || !coherent_plans(short_plan, long_plan)) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_overlap_t candidate = {.short_plan = short_plan, .long_plan = long_plan,
        .history = history, .history_capacity = history_capacity};
    native_vorbis_numeric_status_t status = coherent_state(&candidate);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    *state = candidate;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_overlap_reset(native_vorbis_overlap_t *state) {
    native_vorbis_numeric_status_t status = coherent_state(state);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    state->previous_size = 0;
    state->previous_exponent = 0;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_overlap_measure(
    const native_vorbis_overlap_t *state, uint32_t blocksize,
    native_vorbis_overlap_requirements_t *requirements) {
    if (!requirements) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_numeric_status_t status = coherent_state(state);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (blocksize != state->short_plan->blocksize && blocksize != state->long_plan->blocksize)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    *requirements = (native_vorbis_overlap_requirements_t){
        .count = state->previous_size ? (state->previous_size + blocksize) / 4 : 0,
        .history_count = blocksize / 2};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_overlap_push(
    native_vorbis_overlap_t *state,
    const native_vorbis_transform_block_t *source, size_t source_capacity,
    double *previous_output, size_t previous_capacity,
    double *current_output, size_t current_capacity,
    native_vorbis_overlap_terms_t *result) {
    if (!source || !result) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_overlap_requirements_t needed;
    native_vorbis_numeric_status_t status = native_vorbis_overlap_measure(state, source->count, &needed);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (source_capacity > SIZE_MAX / sizeof(*source->samples) ||
        previous_capacity > SIZE_MAX / sizeof(*previous_output) ||
        current_capacity > SIZE_MAX / sizeof(*current_output)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (source_capacity < source->count || previous_capacity < needed.count || current_capacity < needed.count)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!source->samples || (needed.count && (!previous_output || !current_output)))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    for (uint32_t i = 0; i < source->count; ++i)
        if (!isfinite(source->samples[i])) return NATIVE_VORBIS_NUMERIC_RANGE;
    for (uint32_t i = 0; i < state->previous_size / 2; ++i)
        if (!isfinite(state->history[i])) return NATIVE_VORBIS_NUMERIC_RANGE;
    int64_t previous_exponent = state->previous_exponent;
    if (state->previous_size) {
        uint32_t a = state->previous_size, b = source->count;
        uint32_t small = a < b ? a : b;
        uint32_t plateau_previous = (a - small) / 4, plateau_current = (b - small) / 4;
        const double *rise = small == state->short_plan->blocksize ?
            state->short_plan->rise : state->long_plan->rise;
        for (uint32_t i = 0; i < plateau_previous; ++i) {
            previous_output[i] = state->history[i];
            current_output[i] = 0.0;
        }
        for (uint32_t i = 0; i < small / 2; ++i) {
            uint32_t t = plateau_previous + i;
            previous_output[t] = state->history[t] * rise[small / 2 - i - 1];
            current_output[t] = source->samples[plateau_current + i] * rise[i];
        }
        for (uint32_t t = plateau_previous + small / 2; t < needed.count; ++t) {
            previous_output[t] = 0.0;
            current_output[t] = source->samples[plateau_current + t - plateau_previous];
        }
    }
    memcpy(state->history, source->samples + needed.history_count, needed.history_count * sizeof(*state->history));
    state->previous_size = source->count;
    state->previous_exponent = source->exponent;
    *result = (native_vorbis_overlap_terms_t){
        .previous = {.count = needed.count, .exponent = previous_exponent, .samples = previous_output},
        .current = {.count = needed.count, .exponent = source->exponent, .samples = current_output}};
    return NATIVE_VORBIS_NUMERIC_OK;
}
