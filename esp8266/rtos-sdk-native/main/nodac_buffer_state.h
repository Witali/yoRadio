#pragma once

#include <stdbool.h>
#include <stdint.h>

#if defined(__GNUC__)
#define NODAC_INLINE static inline __attribute__((always_inline))
#else
#define NODAC_INLINE static inline
#endif

/* Single producer; calls are serialized with the EOF ISR. DMA descriptors
 * MUST terminate (next == NULL), otherwise software ownership is meaningless.
 * The ISR submits the selected committed buffer after the previous DMA read.
 * No payload is copied here. This same state machine is exercised on the host. */
enum { NODAC_FREE, NODAC_FILLING, NODAC_READY, NODAC_DMA };
typedef struct {
    uint8_t state[2];
    uint8_t active;
    bool silent;
    bool mute;
} nodac_buffer_state_t;

NODAC_INLINE void nodac_state_init(nodac_buffer_state_t *s) {
    s->state[0] = NODAC_DMA;
    s->state[1] = NODAC_FREE;
    s->active = 0;
    s->silent = true;
    s->mute = false;
}

NODAC_INLINE int nodac_state_acquire(nodac_buffer_state_t *s) {
    unsigned other = s->active ^ 1U;
    if (s->state[other] != NODAC_FREE) return -1;
    s->state[other] = NODAC_FILLING;
    return (int)other;
}

NODAC_INLINE bool nodac_state_publish(nodac_buffer_state_t *s,
                                      unsigned index) {
    if (index > 1U || s->state[index] != NODAC_FILLING) return false;
    s->state[index] = NODAC_READY;
    return true;
}

/* Return true only when the just-completed DMA buffer must be filled with
 * neutral PDM before re-submitting it. Never touch a FILLING/READY payload. */
NODAC_INLINE bool nodac_state_eof(nodac_buffer_state_t *s) {
    unsigned old = s->active;
    unsigned next = old ^ 1U;
    if (s->state[next] == NODAC_READY && !s->mute) {
        s->state[old] = NODAC_FREE;
        s->state[next] = NODAC_DMA;
        s->active = (uint8_t)next;
        s->silent = false;
        return false;
    }
    bool clear = !s->silent || s->mute;
    s->silent = true;
    s->mute = false;
    return clear;
}

/* Called by the SAME producer between writes; discard partial/queued audio.
 * Active DMA memory is untouched until EOF. New writes may prepare the next
 * block immediately, but the pending mute boundary is processed first. */
NODAC_INLINE void nodac_state_silence(nodac_buffer_state_t *s) {
    s->state[s->active ^ 1U] = NODAC_FREE;
    s->mute = true;
}

#undef NODAC_INLINE
