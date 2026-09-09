#pragma once
#include <stdint.h>
typedef struct { uint32_t next_packet; } OpusDecoder;
#ifdef __cplusplus
extern "C" {
#endif
int opus_decoder_get_size(int channels);
int opus_decoder_init(OpusDecoder *decoder, int sample_rate, int channels);
#ifdef __cplusplus
}
#endif
