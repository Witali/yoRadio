// QEMU qualification only. The original envelope arithmetic is unchanged.
#include "aac_high_history_abi.h"
#include "aac_smoothing_history.h"

int __real_compact5_init_sbr_dec(int,int,void *,void *);
int __wrap_compact5_init_sbr_dec(int rate,int mode,void *control,void *frame) {
    int result=__real_compact5_init_sbr_dec(rate,mode,control,frame);
    aac_high_channel_t *channel=(void *)((uint8_t *)frame-
        offsetof(aac_high_channel_t,frame));
    // The native initializer constructs five addresses. Only four rows exist
    // per matrix here; the fifth address is never dereferenced before this clear.
    for(unsigned t=0;t<AAC_SMOOTHING_TABLES;++t)
        channel->smoothing[t][AAC_SMOOTHING_PAST_ROWS]=NULL;
    return result;
}

// The 23-argument RV32 ABI was checked against calc_sbr_envelope's call site.
// Opaque scratch/patch arguments pass through without inferring private fields.
#define ENVELOPE_ARGS \
    void *frame,int32_t *real,int32_t *imag,int32_t *frequency,int32_t *frequency_count, \
    int32_t *noise_frequency,int noise_bands,int reset,void *alias,int32_t *harmonic_index, \
    int32_t *noise_index,int32_t *previous_harmonics,int32_t *startup,int32_t *limiter_bands, \
    int32_t *gate_mode,int32_t **gain,int32_t **gain_exp,int32_t **noise, \
    int32_t **noise_exp,void *workspace,void *patch,void *sqrt_cache,int real_only
#define ENVELOPE_PASS \
    frame,real,imag,frequency,frequency_count,noise_frequency,noise_bands,reset,alias,harmonic_index, \
    noise_index,previous_harmonics,startup,limiter_bands,gate_mode,gain,gain_exp, \
    noise,noise_exp,workspace,patch,sqrt_cache,real_only
void calc_sbr_envelope(ENVELOPE_ARGS);
static __attribute__((noinline)) void complex_envelope(ENVELOPE_ARGS) {
    aac_smoothing_scratch_t scratch;
    int32_t **tables[AAC_SMOOTHING_TABLES]={gain,gain_exp,noise,noise_exp};
    aac_smoothing_begin(tables,&scratch);
    calc_sbr_envelope(ENVELOPE_PASS);
    aac_smoothing_end(tables,&scratch);
}
void aac_smoothing_history_envelope(ENVELOPE_ARGS) {
    // LC-SBR passes null smoothing tables and never reads them. Keep that path
    // native and avoid allocating the temporary complex-FIR stack frame.
    if(real_only)calc_sbr_envelope(ENVELOPE_PASS);
    else complex_envelope(ENVELOPE_PASS);
}
