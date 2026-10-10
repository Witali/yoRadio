#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <limits.h>

#include "native_pcm_fir_coefficients.h"

enum {
    PCM_FIR_TAPS = 32,
    PCM_FIR_LOOKAHEAD = PCM_FIR_TAPS / 2,
    PCM_FIR_COEFFICIENT_BITS = 19,
    PCM_FIR_PHASE_PERIOD = 625000,
    PCM_FIR_RATE_DENOMINATOR = 13,
    PCM_FIR_TABLE_PHASES = 256,
    PCM_FIR_48K_STEP = 48000 * PCM_FIR_RATE_DENOMINATOR,
    PCM_FIR_48K_PHASE_UNIT = 1000,
    PCM_FIR_BLEND_BITS = 16,
};

typedef struct {
    int16_t history[PCM_FIR_TAPS][2];
    uint32_t phase;
    uint8_t next, priming;
    bool valid;
} pcm_fir_state_t;

typedef int (*pcm_fir_emit_t)(int16_t left, int16_t right);

static inline void pcm_fir_reset(pcm_fir_state_t *state) {
    // Old history is inaccessible until first-sample edge extension fills it.
    state->phase = 0;
    state->next = 0;
    state->priming = PCM_FIR_LOOKAHEAD;
    state->valid = false;
}

static inline int16_t pcm_fir_round_saturate(int64_t value) {
    const int64_t half = INT64_C(1) << (PCM_FIR_COEFFICIENT_BITS - 1);
    int64_t sample = value >= 0 ? (value + half) >> PCM_FIR_COEFFICIENT_BITS
                               : -((-value + half) >> PCM_FIR_COEFFICIENT_BITS);
    if (sample > INT16_MAX) return INT16_MAX;
    if (sample < INT16_MIN) return INT16_MIN;
    return (int16_t)sample;
}

static inline int pcm_fir_emit_frame(pcm_fir_state_t *state, uint32_t step,
                                      pcm_fir_emit_t emit) {
    const int32_t *a;
    const int32_t *b = NULL;
    uint32_t blend = 0;
    if (step == PCM_FIR_48K_STEP) {
        // 48 kHz visits exactly 625 phases, each divisible by 1000. A direct
        // table halves the tap work on the heavy-FLAC path, without rounding
        // its phase. It costs Flash, not a second RAM history.
        a = pcm_fir_48k_coefficients[state->phase / PCM_FIR_48K_PHASE_UNIT];
    } else {
        uint32_t scaled_phase = state->phase * PCM_FIR_TABLE_PHASES;
        uint32_t index = scaled_phase / PCM_FIR_PHASE_PERIOD;
        uint32_t remainder = scaled_phase - index * PCM_FIR_PHASE_PERIOD;
        a = pcm_fir_coefficients[index];
        if (remainder) {
            b = pcm_fir_coefficients[index + 1];
            // round(remainder * 65536 / 625000), using a Q32 reciprocal.
            blend = (uint32_t)(((uint64_t)remainder * UINT32_C(450359963) +
                               (UINT64_C(1) << 31)) >> 32);
        }
    }
    int64_t left = 0, right = 0, next_left = 0, next_right = 0;
    for (unsigned tap = 0; tap < PCM_FIR_TAPS; ++tap) {
        unsigned index = (state->next + tap) & (PCM_FIR_TAPS - 1);
        int32_t l = state->history[index][0];
        int32_t r = state->history[index][1];
        left += (int64_t)l * a[tap];
        right += (int64_t)r * a[tap];
        if (b) {
            next_left += (int64_t)l * b[tap];
            next_right += (int64_t)r * b[tap];
        }
    }
    if (b) {
        // Coefficient sums are exact at both endpoints. Blend before final
        // PCM rounding to preserve DC and avoid two rounds of quantization.
        left += (next_left - left) * blend / (INT64_C(1) << PCM_FIR_BLEND_BITS);
        right += (next_right - right) * blend / (INT64_C(1) << PCM_FIR_BLEND_BITS);
    }
    return emit(pcm_fir_round_saturate(left), pcm_fir_round_saturate(right));
}

static inline int pcm_fir_push(pcm_fir_state_t *state, int16_t left,
                                int16_t right, uint32_t step, bool last,
                                pcm_fir_emit_t emit) {
    if (!state->valid) {
        for (unsigned i = 0; i < PCM_FIR_TAPS; ++i) {
            state->history[i][0] = left;
            state->history[i][1] = right;
        }
        state->valid = true;
    }
    state->history[state->next][0] = left;
    state->history[state->next][1] = right;
    state->next = (state->next + 1) & (PCM_FIR_TAPS - 1);
    if (state->priming) {
        --state->priming;
        return 0;
    }
    while (state->phase < PCM_FIR_PHASE_PERIOD && (!last || !state->phase)) {
        int error = pcm_fir_emit_frame(state, step, emit);
        if (error) {
            pcm_fir_reset(state);
            return error;
        }
        state->phase += step;
    }
    // The last interval emits only an exactly coincident endpoint; drain
    // resets the phase immediately afterwards. Never underflow it there.
    if (!last) state->phase -= PCM_FIR_PHASE_PERIOD;
    return 0;
}

static inline int pcm_fir_drain(pcm_fir_state_t *state, uint32_t step,
                                 pcm_fir_emit_t emit) {
    if (!state->valid) return 0;
    unsigned last = (state->next + PCM_FIR_TAPS - 1) & (PCM_FIR_TAPS - 1);
    int16_t left = state->history[last][0], right = state->history[last][1];
    int error = 0;
    for (unsigned i = 0; i < PCM_FIR_LOOKAHEAD && !error; ++i) {
        error = pcm_fir_push(state, left, right, step,
                             i + 1 == PCM_FIR_LOOKAHEAD, emit);
    }
    pcm_fir_reset(state);
    return error;
}
