#pragma once
#include <stdint.h>
#include <stdbool.h>
typedef struct { uint32_t ms, frames, misses; } audio_window_point_t;
typedef struct {
    audio_window_point_t start, end;
    uint32_t generation;
} audio_window_result_t;
typedef struct {
    audio_window_point_t current;
    audio_window_result_t result;
    uint32_t generation;
    bool primed, valid;
} audio_window_state_t;
/* Caller serializes access. No clock/heap/RTOS calls in the state machine.
 * Windows include all stalls; a long stall is NOT reset or excluded. */
static inline void audio_window_record(audio_window_state_t *s, uint32_t generation,
                                      uint32_t ms, uint32_t frames, uint32_t misses) {
    audio_window_point_t now = {ms, frames, misses};
    if (!s->primed || s->generation != generation) {
        s->current = now; s->generation = generation;
        s->primed = true; s->valid = false;
    } else if ((uint32_t)(ms - s->current.ms) >= 25000U) {
        s->result.start = s->current; s->result.end = now;
        s->result.generation = generation; s->valid = true;
        s->current = now;
    }
}
