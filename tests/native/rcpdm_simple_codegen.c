#include "rcpdm_simple.h"

#if RCPDM_SIMPLE_LX106_ASM != EXPECT_ASM
#error "Wrong RCPDM-Simple backend selected"
#endif

static rc_pdm_t state;
uint32_t codegen_sample(int16_t sample) {
    return rcpdm_simple_sample(&state, sample);
}
uint32_t codegen_variable(int16_t sample, unsigned count, unsigned shift) {
    return rcpdm_simple_bits(&state, sample, count, shift);
}
void codegen_batch(uint32_t *words, const int16_t *pcm, size_t frames, unsigned channels) {
    rcpdm_simple_fill(&state, words, pcm, frames, channels);
}
