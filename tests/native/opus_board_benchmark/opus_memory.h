#pragma once
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
void yoradio_opus_memory_bind(void *bytes, size_t byte_capacity, void *words, size_t word_capacity);
int yoradio_opus_decode_bounded(void *decoder, const unsigned char *packet,
                               int length, int16_t *pcm, int capacity);
size_t yoradio_opus_scratch_peak_bytes(void);
size_t yoradio_opus_scratch_peak_words(void);
#ifdef __cplusplus
}
#endif
