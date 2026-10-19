// Scoped temporary FIR row shared by the numerical probe and radio adapter.
#include "sdkconfig.h"
#include "aac_high_history_abi.h"
#include "aac_smoothing_history.h"
#include "aac_pointer_audit.h"

#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdbool.h>
static bool test_interleave;
static volatile unsigned test_live_calls,test_peak_calls;
static portMUX_TYPE test_calls_lock=portMUX_INITIALIZER_UNLOCKED;
void aac_smoothing_history_test_interleave(bool enable) {
    assert(!test_live_calls);
    if(enable)test_peak_calls=0;
    else assert(test_peak_calls==2);
    test_interleave=enable;
}
#endif

int __real_compact5_init_sbr_dec(int,int,void *,void *);
int __wrap_compact5_init_sbr_dec(int rate,int mode,void *control,void *frame) {
    int result=__real_compact5_init_sbr_dec(rate,mode,control,frame);
    aac_high_channel_view_t *channel=(void *)((uint8_t *)frame-
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
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_smoothing(frame,tables,&scratch,1);
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(test_interleave) {
        taskENTER_CRITICAL(&test_calls_lock);
        ++test_live_calls;
        if(test_live_calls>test_peak_calls)test_peak_calls=test_live_calls;
        taskEXIT_CRITICAL(&test_calls_lock);
        // Keep the first stack row live until the second decoder enters.
        // A single delay can miss the overlap when DSP instruction demand changes.
        TickType_t started=xTaskGetTickCount();
        while(test_peak_calls<2) {
            assert(xTaskGetTickCount()-started<pdMS_TO_TICKS(5000));
            vTaskDelay(1);
        }
        vTaskDelay(1);
    }
#endif
    calc_sbr_envelope(ENVELOPE_PASS);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_smoothing(frame,tables,&scratch,2);
#endif
    aac_smoothing_end(tables,&scratch);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_smoothing(frame,tables,NULL,0);
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(test_interleave) {
        taskENTER_CRITICAL(&test_calls_lock);
        --test_live_calls;
        taskEXIT_CRITICAL(&test_calls_lock);
    }
#endif
}
void aac_smoothing_history_envelope(ENVELOPE_ARGS) {
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_envelope(ENVELOPE_PASS);
#endif
    // LC-SBR passes null smoothing tables and never reads them. Keep that path
    // native and avoid allocating the temporary complex-FIR stack frame.
    if(real_only)calc_sbr_envelope(ENVELOPE_PASS);
    else complex_envelope(ENVELOPE_PASS);
}
