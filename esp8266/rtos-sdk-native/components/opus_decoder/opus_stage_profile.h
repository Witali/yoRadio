#pragma once
#include <stdint.h>

#ifndef YORADIO_OPUS_PROFILE_STAGE
#define YORADIO_OPUS_PROFILE_STAGE 0
#endif
#if YORADIO_OPUS_PROFILE_STAGE < 0 || YORADIO_OPUS_PROFILE_STAGE > 11
#error "Opus profile stage must be 0 (off) or 1..11"
#endif
#define OPUS_STAGE_SILK_INDICES 1
#define OPUS_STAGE_SILK_PULSES 2
#define OPUS_STAGE_SILK_PARAMETERS 3
#define OPUS_STAGE_SILK_CORE 4
#define OPUS_STAGE_SILK_RESAMPLE 5
#define OPUS_STAGE_CELT_ENERGY 6
#define OPUS_STAGE_CELT_ALLOCATION 7
#define OPUS_STAGE_CELT_BANDS 8
#define OPUS_STAGE_CELT_SYNTHESIS 9
#define OPUS_STAGE_CELT_POSTFILTER 10
#define OPUS_STAGE_CELT_DEEMPHASIS 11

/* One selected scope per build; no nested timers, allocation, ISR or task.
 * Only the audio owner resets/reads/updates this state, OUTSIDE a web reader.
 * Publish a COPY through the benchmark's existing critical-section snapshot.
 * Cycles include preemption and ISR, NOT exclusive decoder CPU ticks. */
typedef struct {
    uint64_t ticks;
    uint32_t calls, max_ticks;
} opus_stage_profile_t;

#if YORADIO_OPUS_PROFILE_STAGE
#ifdef __cplusplus
extern "C" {
#endif
void opus_stage_profile_reset(void);
opus_stage_profile_t opus_stage_profile_snapshot(void);
void opus_stage_profile_record(uint32_t elapsed);
/* Target: coherent SDK microseconds. Host: correctness-only monotonic ticks.
 * Raw CCOUNT is invalid here: this SDK resets it on every RTOS tick. */
uint32_t opus_stage_profile_clock(void);
#ifdef __cplusplus
}
#endif
#define OPUS_STAGE_BEGIN(id) { \
    const uint32_t opus_stage_started = (YORADIO_OPUS_PROFILE_STAGE == (id)) \
        ? opus_stage_profile_clock() : 0;
#define OPUS_STAGE_END(id) \
    if (YORADIO_OPUS_PROFILE_STAGE == (id)) \
        opus_stage_profile_record(opus_stage_profile_clock() - opus_stage_started); \
    }
#else
#define OPUS_STAGE_BEGIN(id) ((void)0);
#define OPUS_STAGE_END(id) ((void)0);
#endif
