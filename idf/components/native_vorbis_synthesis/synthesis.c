// Shared frame timing and channel histories retain exact window terms to S16.
#include "native_vorbis_synthesis.h"
#include <float.h>
#include <string.h>

_Static_assert(sizeof(double) == sizeof(uint64_t) && FLT_RADIX == 2 &&
    DBL_MANT_DIG == 53 && DBL_MIN_EXP == -1021 && DBL_MAX_EXP == 1024,
    "binary64 storage required");

static uint64_t double_word(const double *value) {
    uint64_t word;
    memcpy(&word, value, sizeof(word));
    return word;
}

static bool finite_sample(const double *value) {
    return ((double_word(value) >> 52) & 2047) != 2047;
}

static bool valid_factor(const double *value) {
    uint64_t word = double_word(value);
    uint64_t absolute = word & UINT64_C(0x7fffffffffffffff);
    return absolute <= UINT64_C(0x3ff0000000000000) && (!(word >> 63) || !absolute);
}

native_vorbis_numeric_status_t native_vorbis_synthesis_measure(
    uint32_t short_size, uint32_t long_size, uint32_t channels,
    native_vorbis_synthesis_requirements_t *requirements) {
    if (!requirements || !channels || channels > 255) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_timing_t timing;
    native_vorbis_numeric_status_t status = native_vorbis_timing_init(short_size, long_size, &timing);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    uint32_t maximum = long_size / 2;
    *requirements = (native_vorbis_synthesis_requirements_t){
        .history_samples = (uint64_t)channels * maximum,
        .exponent_count = channels, .max_frames = maximum,
        .max_pcm_samples = (uint64_t)channels * maximum};
    return NATIVE_VORBIS_NUMERIC_OK;
}

// This validation never dereferences history or exponent elements. In
// particular, init/reset and a fresh priming frame may use unread storage.
static native_vorbis_numeric_status_t coherent_state(const native_vorbis_synthesis_t *state) {
    if (!state || !state->short_plan || !state->long_plan ||
        !state->short_plan->rise || !state->long_plan->rise) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_synthesis_requirements_t needed;
    native_vorbis_numeric_status_t status = native_vorbis_synthesis_measure(
        state->short_plan->blocksize, state->long_plan->blocksize, state->channels, &needed);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (state->timing.short_size != state->short_plan->blocksize ||
        state->timing.long_size != state->long_plan->blocksize) return NATIVE_VORBIS_NUMERIC_INVALID;
    // Reuse the public metadata validator without publishing the reset copy.
    native_vorbis_timing_t checked = state->timing;
    status = native_vorbis_timing_reset(&checked);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (state->history_capacity > SIZE_MAX / sizeof(*state->history) ||
        state->exponent_capacity > SIZE_MAX / sizeof(*state->exponents)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (state->history_capacity < needed.history_samples || state->exponent_capacity < needed.exponent_count)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!state->history || !state->exponents) return NATIVE_VORBIS_NUMERIC_INVALID;
    for (uint32_t i = 0; i < state->short_plan->blocksize / 2; ++i)
        if (!valid_factor(state->short_plan->rise + i)) return NATIVE_VORBIS_NUMERIC_RANGE;
    for (uint32_t i = 0; i < state->long_plan->blocksize / 2; ++i)
        if (!valid_factor(state->long_plan->rise + i)) return NATIVE_VORBIS_NUMERIC_RANGE;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_synthesis_init(
    const native_vorbis_window_plan_t *short_plan,
    const native_vorbis_window_plan_t *long_plan, uint32_t channels,
    double *history, size_t history_capacity,
    int64_t *exponents, size_t exponent_capacity,
    native_vorbis_synthesis_t *state) {
    if (!state || !short_plan || !long_plan) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_synthesis_t candidate = {.short_plan = short_plan, .long_plan = long_plan,
        .history = history, .history_capacity = history_capacity,
        .exponents = exponents, .exponent_capacity = exponent_capacity, .channels = channels};
    native_vorbis_numeric_status_t status = native_vorbis_timing_init(
        short_plan->blocksize, long_plan->blocksize, &candidate.timing);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = coherent_state(&candidate);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    *state = candidate;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_synthesis_reset(native_vorbis_synthesis_t *state) {
    native_vorbis_numeric_status_t status = coherent_state(state);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_timing_t next = state->timing;
    // Coherence is already established; immutable configuration makes this
    // repeated metadata reset infallible and leaves all history bytes unread.
    (void)native_vorbis_timing_reset(&next);
    state->timing = next;
    return NATIVE_VORBIS_NUMERIC_OK;
}

// All sources, factors, resources and metadata were checked before entry.
// The two public exact helpers therefore cannot refuse during publication.
static void publish_pcm(const native_vorbis_synthesis_t *state,
    const native_vorbis_transform_block_t *blocks,
    const native_vorbis_timing_result_t *span, int16_t *output) {
    if (!span->count) return;
    uint32_t a = state->timing.previous_size, b = blocks[0].count;
    uint32_t small = a < b ? a : b;
    uint32_t previous_plateau = (a - small) / 4, current_plateau = (b - small) / 4;
    uint32_t stride = state->long_plan->blocksize / 2;
    const double *rise = small == state->short_plan->blocksize ?
        state->short_plan->rise : state->long_plan->rise;
    for (uint32_t channel = 0; channel < state->channels; ++channel) {
        const double *history = state->history + (size_t)channel * stride;
        int64_t previous_exponent = state->exponents[channel];
        const native_vorbis_transform_block_t *block = blocks + channel;
        for (uint32_t i = 0; i < span->count; ++i) {
            uint32_t t = span->discard_start + i;
            native_vorbis_window_product_t previous = {0}, current = {0};
            if (t < previous_plateau) {
                (void)native_vorbis_window_multiply_exact(history[t], 1.0, previous_exponent, &previous);
            } else if (t < previous_plateau + small / 2) {
                uint32_t at = t - previous_plateau;
                (void)native_vorbis_window_multiply_exact(history[t], rise[small / 2 - at - 1],
                    previous_exponent, &previous);
                (void)native_vorbis_window_multiply_exact(block->samples[current_plateau + at], rise[at],
                    block->exponent, &current);
            } else {
                (void)native_vorbis_window_multiply_exact(
                    block->samples[current_plateau + t - previous_plateau], 1.0, block->exponent, &current);
            }
            (void)native_vorbis_pcm_s16_product_pair(&previous, &current,
                output + (size_t)i * state->channels + channel);
        }
    }
}

native_vorbis_numeric_status_t native_vorbis_synthesis_push(
    native_vorbis_synthesis_t *state, const native_vorbis_timing_event_t *event,
    const native_vorbis_transform_block_t *blocks,
    const size_t *source_capacities, size_t block_capacity,
    int16_t *output, size_t output_capacity,
    native_vorbis_synthesis_result_t *result) {
    if (!event || !result) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_numeric_status_t status = coherent_state(state);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (block_capacity > SIZE_MAX / sizeof(*blocks) ||
        block_capacity > SIZE_MAX / sizeof(*source_capacities) ||
        output_capacity > SIZE_MAX / sizeof(*output)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (block_capacity < state->channels) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!blocks || !source_capacities) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_timing_t next = state->timing;
    native_vorbis_timing_result_t span;
    status = native_vorbis_timing_push(&next, event, &span);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    uint64_t pcm_samples = (uint64_t)span.count * state->channels;
    if (output_capacity < pcm_samples) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (pcm_samples && !output) return NATIVE_VORBIS_NUMERIC_INVALID;
    for (uint32_t channel = 0; channel < state->channels; ++channel) {
        const native_vorbis_transform_block_t *block = blocks + channel;
        if (block->count != event->blocksize) return NATIVE_VORBIS_NUMERIC_INVALID;
        if (source_capacities[channel] > SIZE_MAX / sizeof(*block->samples)) return NATIVE_VORBIS_NUMERIC_RANGE;
        if (source_capacities[channel] < block->count) return NATIVE_VORBIS_NUMERIC_CAPACITY;
        if (!block->samples) return NATIVE_VORBIS_NUMERIC_INVALID;
        for (uint32_t i = 0; i < block->count; ++i)
            if (!finite_sample(block->samples + i)) return NATIVE_VORBIS_NUMERIC_RANGE;
    }
    uint32_t stride = state->long_plan->blocksize / 2;
    if (state->timing.previous_size) {
        for (uint32_t channel = 0; channel < state->channels; ++channel) {
            const double *history = state->history + (size_t)channel * stride;
            for (uint32_t i = 0; i < state->timing.previous_size / 2; ++i)
                if (!finite_sample(history + i)) return NATIVE_VORBIS_NUMERIC_RANGE;
        }
    }
    publish_pcm(state, blocks, &span, output);
    // No channel history is replaced until all channel outputs are complete.
    uint32_t half = event->blocksize / 2;
    for (uint32_t channel = 0; channel < state->channels; ++channel) {
        memcpy(state->history + (size_t)channel * stride, blocks[channel].samples + half,
            (size_t)half * sizeof(*state->history));
    }
    for (uint32_t channel = 0; channel < state->channels; ++channel) {
        state->exponents[channel] = blocks[channel].exponent;
    }
    state->timing = next;
    *result = (native_vorbis_synthesis_result_t){.timing = span,
        .channels = state->channels, .pcm_samples = pcm_samples};
    return NATIVE_VORBIS_NUMERIC_OK;
}
