#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void native_audio_normalizer_configure(bool enabled, uint8_t max_gain_db,
                                       int8_t target_dbfs,
                                       uint16_t time_ms,
                                       uint32_t sample_rate);
void native_audio_normalizer_set_sample_rate(uint32_t sample_rate);
void native_audio_normalizer_reset(void);
void native_audio_normalizer_process(int16_t samples[2]);
void native_audio_normalizer_process_block(int16_t *samples, size_t frames,
                                           uint8_t channels);

#ifdef __cplusplus
}
#endif
