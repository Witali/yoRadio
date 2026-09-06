#include "rc_pdm_feedback.h"
uint32_t rc_feedback_codegen_sample(rc_pdm_feedback_t *p, int16_t pcm) {
    return rc_pdm_feedback_sample(p, pcm);
}
void rc_feedback_codegen_fill(rc_pdm_feedback_t *p, uint32_t *out,
        const int16_t *pcm, size_t frames, unsigned channels) {
    rc_pdm_feedback_fill(p,out,pcm,frames,channels);
}
