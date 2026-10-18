#pragma once

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

esp_err_t native_audio_output_init(void);
esp_err_t native_audio_output_configure(uint32_t input_sample_rate);
// Signed packed little-endian PCM, with a sample width of 8, 16, 24 or 32 bits.
// Wider interleaved layouts retain CYD's first-two-channel mono mix. The input
// remains read-only, may be unaligned, and only complete frames are consumed.
bool native_audio_output_supports_pcm(uint8_t bits_per_sample,
                                      uint8_t channels);
esp_err_t native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels);
void native_audio_output_set_volume(uint8_t volume);
uint8_t native_audio_output_get_volume(void);
void native_audio_output_set_balance(int8_t balance);
int8_t native_audio_output_get_balance(void);
// Safe from control tasks: the output owner consumes this request before PCM.
void native_audio_output_request_normalizer_reset(void);
void native_audio_output_idle(void);
// Only the output task may discard history or submit the final partial block.
void native_audio_output_discard_pcm(void);
esp_err_t native_audio_output_flush_pcm(void);
// Output owner only, after it has returned its current PCM lease. Success
// means DMA is stopped and the backend released; configure starts it again.
// Failure retains ownership so the owner can retry without freeing live DMA.
esp_err_t native_audio_output_pause(void);
// Control task may request cancellation between driver blocks. It never
// disables a driver; only the output owner may call pause after its write.
void native_audio_output_request_pause(bool requested);
const char *native_audio_output_name(void);
