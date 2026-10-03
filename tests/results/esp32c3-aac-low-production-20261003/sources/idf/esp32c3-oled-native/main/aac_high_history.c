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
static volatile unsigned test_live_calls, test_peak_calls;
static portMUX_TYPE test_calls_lock=portMUX_INITIALIZER_UNLOCKED;
#ifdef AAC_LOW_WORKSPACE
static unsigned low_workspace_calls;
void aac_low_workspace_report(void) {
    ESP_LOGI("low_workspace","AAC_LOW_WORKSPACE_PASS owner_bytes=%u work_bytes=%u stored_bytes=%u calls=%u",
        (unsigned)sizeof(aac_high_owner_t),(unsigned)sizeof(aac_low_workspace_t),
        (unsigned)(2*2*sizeof(((aac_high_frame_t *)0)->low_real)),low_workspace_calls);
}
#endif
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
#ifdef AAC_LOW_WORKSPACE
    enum { LOW_WORK_GUARD=0x51ab73cd };
    struct { uint32_t before; aac_low_workspace_t matrix; uint32_t after; } work;
    work.before=work.after=LOW_WORK_GUARD;
#ifdef CONFIG_YORADIO_QEMU_AAC_LOW_WORKSPACE
    // The qualification profile poisons transient rows; production relies on
    // the audited native analysis writes before their first use.
    memset(&work.matrix,0xa5,sizeof(work.matrix));
#endif
    aac_high_frame_t *f=frame;
    aac_high_channel_t *channel=aac_high_frame_channel(f);
    assert(!channel->low_real_relative && !channel->low_imag_relative);
    memcpy(work.matrix.real,f->low_real,sizeof(f->low_real));
    memcpy(work.matrix.imag,f->low_imag,sizeof(f->low_imag));
    channel->low_real_relative=(uintptr_t)work.matrix.real-(uintptr_t)f;
    channel->low_imag_relative=(uintptr_t)work.matrix.imag-(uintptr_t)f;
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_low_begin(f,&work.matrix);
#endif
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_frame(core,frame,control,ps,false);
    aac_pointer_audit_decode_io(input,output,frame,right_output,ps,core);
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_LOW_LIFETIME
    void aac_low_lifetime_poison(aac_high_frame_t *,const aac_sbr_control_abi_t *,bool);
    aac_low_lifetime_poison(frame,control,ps!=NULL);
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(test_interleave) {
        taskENTER_CRITICAL(&test_calls_lock);
        ++test_live_calls;
        if(test_live_calls>test_peak_calls)test_peak_calls=test_live_calls;
        taskEXIT_CRITICAL(&test_calls_lock);
        // Wait for observed overlap; one tick alone depends on DSP timing.
        TickType_t started=xTaskGetTickCount();
        while(test_peak_calls<2) {
            assert(xTaskGetTickCount()-started<pdMS_TO_TICKS(5000));
            vTaskDelay(1);
        }
        vTaskDelay(1);
    }
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
    if(state->real_only)++state->real_frames;else ++state->complex_frames;
#endif
    __real_compact5_sbr_dec(input,output,frame,apply,control,right_output,ps,core);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_frame(core,frame,control,ps,true);
    aac_pointer_audit_decode_io(input,output,frame,right_output,ps,core);
#endif
    assert(state->call_loads==(state->real_only?1:2));
    assert(state->call_stores==(state->real_only?1:2));
#ifdef AAC_LOW_WORKSPACE
    assert(work.before==LOW_WORK_GUARD && work.after==LOW_WORK_GUARD);
    memcpy(f->low_real,work.matrix.real,sizeof(f->low_real));
    // Real-only SBR leaves the imaginary history unchanged.
    if(!state->real_only)memcpy(f->low_imag,work.matrix.imag,sizeof(f->low_imag));
    channel->low_real_relative=channel->low_imag_relative=0;
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_low_end(f);
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    taskENTER_CRITICAL(&test_calls_lock);
    ++low_workspace_calls;
    taskEXIT_CRITICAL(&test_calls_lock);
#endif
#endif
    state->frame=NULL;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(test_interleave) {
        taskENTER_CRITICAL(&test_calls_lock);
        --test_live_calls;
        taskEXIT_CRITICAL(&test_calls_lock);
    }
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
