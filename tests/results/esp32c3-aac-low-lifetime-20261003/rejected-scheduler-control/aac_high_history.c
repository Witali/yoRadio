// Scoped to the copied sbr_dec object; no process-wide memcpy/memmove hook.
#include "aac_high_history.h"
#include "aac_pointer_audit.h"
#include "packed_complex_storage.h"
#include "esp_log.h"
#include <assert.h>
#include <string.h>

#ifdef AAC_HIGH_HISTORY_PC16
#define HISTORY_FORMAT PC_STORAGE_SHARED16
#else
#define HISTORY_FORMAT PC_STORAGE_SHARED18_FOUR
#endif
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
#include "aac_compact_owner.h"
#define active_history aac_compact_owner_high_context
#else
static aac_high_runtime_t history;
static aac_high_runtime_t *active_history(void) { return &history; }
#endif

#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
static bool test_interleave;
static unsigned test_live_calls, test_peak_calls;
void aac_high_history_test_interleave(bool enable) {
    assert(!test_live_calls);
    if(enable)test_peak_calls=0;
    else assert(test_peak_calls==2);
    test_interleave=enable;
}
#endif

static void unpack(const aac_high_history_t *h,unsigned i,int32_t *r,int32_t *im) {
    pc_storage_unpack(HISTORY_FORMAT,h->mantissas[i],
        pc_storage_load_metadata(HISTORY_FORMAT,h->metadata,i),r,im);
}
static void pack(aac_high_runtime_t *state,aac_high_history_t *h,unsigned i,int32_t r,int32_t im) {
    unsigned metadata,saturated;
    h->mantissas[i]=pc_storage_pack(HISTORY_FORMAT,r,im,&metadata,&saturated);
    pc_storage_store_metadata(HISTORY_FORMAT,h->metadata,i,metadata);
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
    state->saturations+=saturated;
    unsigned shift=pc_storage_max_shift(HISTORY_FORMAT,metadata);
    if(shift>state->max_shift)state->max_shift=shift;
    int32_t restored_r,restored_im;
    unpack(h,i,&restored_r,&restored_im);
    state->changed+=(restored_r!=r)+(restored_im!=im);
#else
    (void)state;
#endif
}

void *aac_high_history_memmove(void *dest,const void *source,size_t bytes) {
    aac_high_runtime_t *state=active_history();
    aac_high_frame_t *f=state->frame;
    assert(f);
    void *real_token=&f->high_history.mantissas[0];
    void *imag_token=&f->high_history.mantissas[1];
    const size_t native_bytes=AAC_HIGH_PAIRS*sizeof(int32_t);
    const unsigned tail=AAC_HIGH_NEW_ROWS*AAC_HIGH_BANDS;
    if(source==real_token) {
        assert(bytes==native_bytes && dest==f->high_real && !state->call_loads);
        for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
            int32_t r,im;unpack(&f->high_history,i,&r,&im);
            f->high_real[i]=r;
            if(!state->real_only)f->high_imag[i]=im;
        }
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
        ++state->loads;
#endif
        ++state->call_loads;
    } else if(source==imag_token) {
        assert(!state->real_only && bytes==native_bytes && dest==f->high_imag && state->call_loads==1);
        ++state->call_loads;
    } else if(dest==real_token) {
        assert(bytes==native_bytes && source==f->high_real+tail && !state->call_stores);
        for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
            int32_t r,im;
            // LC-SBR leaves the imaginary history untouched. Retain its last
            // represented value instead of reading an unused scratch row.
            if(state->real_only)unpack(&f->high_history,i,&r,&im);
            else im=f->high_imag[tail+i];
            pack(state,&f->high_history,i,f->high_real[tail+i],im);
        }
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
        ++state->stores;
#endif
        ++state->call_stores;
    } else if(dest==imag_token) {
        assert(!state->real_only && bytes==native_bytes && source==f->high_imag+tail && state->call_stores==1);
        ++state->call_stores;
    } else {
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
        aac_pointer_audit_copy(dest,source,bytes);
#endif
        return memmove(dest,source,bytes);
    }
    return dest;
}

void __real_compact5_sbr_dec(void *,void *,void *,int,void *,void *,void *,void *);
void __wrap_compact5_sbr_dec(void *input,void *output,void *frame,int apply,
                           void *control,void *right_output,void *ps,void *core) {
    aac_high_runtime_t *state=active_history();
    assert(!state->frame);
    state->frame=frame;state->real_only=((aac_sbr_control_abi_t *)control)->low_complexity!=0;
    state->call_loads=state->call_stores=0;
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_frame(core,frame,control,ps,false);
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_LOW_LIFETIME
    void aac_low_lifetime_poison(aac_high_frame_t *,const aac_sbr_control_abi_t *,bool);
    aac_low_lifetime_poison(frame,control,ps!=NULL);
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(test_interleave) {
        ++test_live_calls;
        if(test_live_calls>test_peak_calls)test_peak_calls=test_live_calls;
        // Force another decoder to enter with a live frame in this task's TLS.
        vTaskDelay(1);
    }
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
    if(state->real_only)++state->real_frames;else ++state->complex_frames;
#endif
    __real_compact5_sbr_dec(input,output,frame,apply,control,right_output,ps,core);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_frame(core,frame,control,ps,true);
#endif
    assert(state->call_loads==(state->real_only?1:2));
    assert(state->call_stores==(state->real_only?1:2));
    state->frame=NULL;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(test_interleave)--test_live_calls;
#endif
}
void aac_high_history_clear(aac_high_frame_t *f,bool both) {
    aac_high_runtime_t *state=active_history();
    if(both)memset(&f->high_history,0,sizeof(f->high_history));
    else for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
        int32_t r,im;unpack(&f->high_history,i,&r,&im);pack(state,&f->high_history,i,0,im);
    }
}
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
void aac_high_history_reset_counters(void) { assert(!history.frame);memset(&history,0,sizeof(history)); }
void aac_high_history_report(const char *name,unsigned variant,unsigned run) {
    assert(!history.frame && history.loads==history.stores);
    ESP_LOGI("high_history","HIGHHISTORY_MEMORY case=%s variant=%u run=%u bytes=%u state_bytes=%u"
        " loads=%u stores=%u real_frames=%u complex_frames=%u changed=%u saturations=%u max_shift=%u",
        name,variant,run,(unsigned)sizeof(aac_high_history_t),(unsigned)sizeof(history),
        history.loads,history.stores,history.real_frames,history.complex_frames,
        history.changed,history.saturations,history.max_shift);
}
#endif
