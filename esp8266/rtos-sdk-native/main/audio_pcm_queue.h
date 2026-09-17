#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
#ifndef YORADIO_ESP8266_OPUS_PCM_APP_TASK
#define YORADIO_ESP8266_OPUS_PCM_APP_TASK 0
#endif

/* Decoder-owned frame slots, never an additional PCM copy. */
#ifndef YORADIO_ESP8266_OPUS_PCM_SLOTS
#define YORADIO_ESP8266_OPUS_PCM_SLOTS 2
#endif
#if YORADIO_ESP8266_OPUS_PCM_SLOTS != 2 && YORADIO_ESP8266_OPUS_PCM_SLOTS != 3
#error "PCM queue supports two or three decoder-owned slots"
#endif
#define AUDIO_PCM_QUEUE_SLOTS YORADIO_ESP8266_OPUS_PCM_SLOTS
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
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
    uint32_t service_calls, service_us, service_max_us, service_misses;
#endif
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
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
/* Called only by the app owner; consumes at most one frame. Existing DMA
 * backpressure sleeps this same task; no new task, stack or PCM copy. */
bool audio_pcm_queue_poll(void);
bool audio_pcm_queue_pending(void);
/* Diagnostic wall time (including preemption), not CPU time. No allocation. */
void audio_pcm_queue_record_service(uint32_t elapsed_us, uint32_t misses);
#endif
