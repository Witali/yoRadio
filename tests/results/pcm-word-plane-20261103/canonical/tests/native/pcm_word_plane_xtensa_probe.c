/* Each memory operand in these noinline probes addresses word storage.
 * No stack/local byte arrays, source pointer or SDK/codec ABI is involved. */
#include "pcm_word_plane.h"

__attribute__((noinline,used))
void pcm_word_probe_clear(volatile uint32_t *words,size_t word_count) {
    pcm_word_plane_clear(words,word_count);
}
__attribute__((noinline,used))
void pcm_word_probe_store(volatile uint32_t *words,size_t sample_index,uint16_t bits) {
    pcm_word_plane_store(words,sample_index,bits);
}
__attribute__((noinline,used))
uint16_t pcm_word_probe_load(const volatile uint32_t *words,size_t sample_index) {
    return pcm_word_plane_load(words,sample_index);
}
