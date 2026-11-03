#ifndef YORADIO_PCM_WORD_PLANE_H
#define YORADIO_PCM_WORD_PLANE_H

#include <stddef.h>
#include <stdint.h>

/* Packed raw S16 bit patterns for memory allowing aligned32-bit accesses only.
 * The caller owns alignment, allocation size, sample bounds and lifetime.
 * Clear every allocated word before partial/odd-half read-modify-write stores.
 * Two samples occupy each word: even index in low16, odd index in high16.
 * DRAM byte order/packing and output gathering belong to the caller; never pass
 * this storage to byte/halfword/FP readers, memcpy or memset.
 */
static inline void pcm_word_plane_clear(volatile uint32_t *words,
                                         size_t word_count)
{
    for (size_t index = 0; index < word_count; ++index) words[index] = UINT32_C(0);
}

static inline void pcm_word_plane_store(volatile uint32_t *words,
                                         size_t sample_index, uint16_t bits)
{
    const size_t index = sample_index >> 1;
    const unsigned shift = (unsigned)(sample_index & 1U) * 16U;
    const uint32_t previous = words[index];
    // Zero-extended halves toggle only the selected lane, retaining its neighbor.
    const uint32_t previous_half = (previous >> shift) & UINT32_C(0xffff);
    words[index] = previous ^ ((previous_half ^ (uint32_t)bits) << shift);
}

static inline uint16_t pcm_word_plane_load(const volatile uint32_t *words,
                                            size_t sample_index)
{
    const unsigned shift = (unsigned)(sample_index & 1U) * 16U;
    return (uint16_t)(words[sample_index >> 1] >> shift);
}

#endif
