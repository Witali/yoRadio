#pragma once

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"
#include "sdkconfig.h"

typedef struct {
    bool available;
    uint32_t completion_queue_drops;
    uint32_t write_errors;
} native_audio_output_health_t;

// Lifetime uint32 counters (modulo 2^32), read as aligned words on C3.
// Completion-queue drops indicate delayed service, not an acoustic gap count.
// Startup, idle and Stop may contribute: compare only sustained-play windows.
// The experimental direct-DMA backend currently reports unavailable.
native_audio_output_health_t native_audio_output_health(void);

#if defined(CONFIG_YORADIO_PIPELINE_PROFILE) || defined(CONFIG_YORADIO_STAGED_DMA_PROFILE)
// Lifetime modulo-2^32 counter; one ISR writer, aligned word read on C3.
// Queue overrun means a completion notification was discarded before reuse.
uint32_t native_audio_output_dma_overruns(void);
#endif

#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
// Embedded in the PCM queue item. The output task owns the item until release;
// neither the decoder nor the DMA ISR may modify it during this interval.
typedef struct native_audio_pcm_lease native_audio_pcm_lease_t;
struct native_audio_pcm_lease {
    native_audio_pcm_lease_t *next;
    void (*release)(native_audio_pcm_lease_t *);
    const uint8_t *data;
    size_t frame_bytes, output_frames;
    uint32_t left_gain, right_gain;
    uint16_t peak;
    uint8_t channels;
    bool current_valid;
    int16_t left, right;
};
esp_err_t native_audio_output_submit_pcm(native_audio_pcm_lease_t *lease,
    uint8_t *data, size_t size, uint8_t bits_per_sample, uint8_t channels,
    void (*release)(native_audio_pcm_lease_t *));
#endif

// Owned by the output task. Flush submits a zero-padded final DMA block; it
// does not wait for the hardware to play it. Discard drops software PCM
// and resampler history on Stop/new stream without draining old samples.
esp_err_t native_audio_output_flush_pcm(void);
void native_audio_output_discard_pcm(void);

esp_err_t native_audio_output_init(void);
esp_err_t native_audio_output_configure(uint32_t input_sample_rate);
esp_err_t native_audio_output_write_pcm(uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels);
void native_audio_output_set_volume(uint8_t volume);
uint8_t native_audio_output_get_volume(void);
void native_audio_output_set_balance(int8_t balance);
int8_t native_audio_output_get_balance(void);
void native_audio_output_request_normalizer_reset(void);
void native_audio_output_idle(void);
esp_err_t native_audio_output_suspend(void);
const char *native_audio_output_name(void);
