// Deliberately overwrite data proposed for removal, while native readers,
// writers and the pointer audit remain intact. QEMU only; no RAM saving yet.
#include "aac_high_history.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>

#ifdef CONFIG_YORADIO_QEMU_AAC_LOW_POISON_HISTORY
enum { FIRST_POISON_ROW=AAC_LOW_HISTORY_ROWS-1 };
#else
enum { FIRST_POISON_ROW=AAC_LOW_HISTORY_ROWS };
#endif
static unsigned calls,real_calls,complex_calls,ps_calls;
static portMUX_TYPE counters_lock=portMUX_INITIALIZER_UNLOCKED;

void aac_low_lifetime_poison(aac_high_frame_t *frame,
                           const aac_sbr_control_abi_t *control,bool ps) {
    assert(control->columns==AAC_LOW_NEW_ROWS);
    assert(control->write_offset==AAC_LOW_HISTORY_ROWS);
    assert(control->qmf_buffer_length==AAC_LOW_ROWS);
    assert(control->read_offset==2);
    // Do not touch the inactive right channel: its QMF view contains live PS
    // state. This hook is called only for the actual sbr_dec frame argument.
    for(unsigned row=FIRST_POISON_ROW;row<AAC_LOW_ROWS;++row) {
        for(unsigned band=0;band<AAC_LOW_BANDS;++band) {
            // Large, signed, band-dependent values expose stale reads. Keep
            // the pattern independent of task scheduling for concurrent PCM.
            int32_t value=(int32_t)(UINT32_C(0x35a5a500)^(row<<16)^(band<<8));
            frame->low_real[row][band]=(band&1)?-value:value;
            frame->low_imag[row][band]=(band&1)?value:-value;
        }
    }
    taskENTER_CRITICAL(&counters_lock);
    ++calls;
    if(control->low_complexity)++real_calls;else ++complex_calls;
    if(ps)++ps_calls;
    taskEXIT_CRITICAL(&counters_lock);
}

void aac_low_lifetime_report(void) {
    assert(calls && real_calls && complex_calls && ps_calls);
    assert(calls==real_calls+complex_calls && ps_calls<=complex_calls);
    ESP_LOGI("low_lifetime","AAC_LOW_LIFETIME first_row=%u rows=%u bands=%u calls=%u real=%u complex=%u ps=%u poisoned_words=%u",
        FIRST_POISON_ROW,AAC_LOW_ROWS-FIRST_POISON_ROW,AAC_LOW_BANDS,calls,
        real_calls,complex_calls,ps_calls,
        calls*2*(AAC_LOW_ROWS-FIRST_POISON_ROW)*AAC_LOW_BANDS);
}
