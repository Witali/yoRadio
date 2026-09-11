#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"

/* Exactly two existing decoder frame slots, never an additional PCM copy. */
#define AUDIO_PCM_QUEUE_SLOTS 2U
#define AUDIO_PCM_QUEUE_FRAMES 960U
#ifndef AUDIO_PCM_QUEUE_STACK_BYTES
#define AUDIO_PCM_QUEUE_STACK_BYTES 2048U
#endif
#if AUDIO_PCM_QUEUE_STACK_BYTES != 1536 && AUDIO_PCM_QUEUE_STACK_BYTES != 2048
#error "PCM consumer stack supports only audited diagnostic sizes"
#endif
typedef bool (*audio_pcm_generation_fn)(uint32_t generation);
typedef void (*audio_pcm_progress_fn)(uint32_t generation, size_t frames);
typedef struct {
    uint32_t ready_frames, stack_free, submitted_frames, output_frames;
    uint32_t output_calls, output_us, error;
} audio_pcm_queue_health_t;
esp_err_t audio_pcm_queue_init(audio_pcm_generation_fn valid, audio_pcm_progress_fn progress);
/* Startup unwind only; normal playback retains the task/stack. */
void audio_pcm_queue_deinit(void);
esp_err_t audio_pcm_queue_begin(int16_t *pool, size_t samples, uint32_t generation);
int audio_pcm_queue_acquire(void *unused, int16_t **pcm, int samples);
void audio_pcm_queue_release(void *unused, int16_t *pcm);
bool audio_pcm_queue_submit(int16_t *pcm, size_t samples);
/* Audio owner only, outside decoder calls. Stops accepting frames, discards
 * queued data, waits for the current write to end, THEN detaches the pool.
 * The caller may only reset output or free codec memory after this returns. */
void audio_pcm_queue_stop(void);
void audio_pcm_queue_drain(void);
void audio_pcm_queue_health(audio_pcm_queue_health_t *health);
