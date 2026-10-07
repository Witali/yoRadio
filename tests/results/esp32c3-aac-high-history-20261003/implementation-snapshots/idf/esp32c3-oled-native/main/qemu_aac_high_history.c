// Scoped to the copied sbr_dec object; no process-wide memcpy/memmove hook.
#include "aac_high_history.h"
#include "packed_complex_storage.h"
#include "esp_log.h"
#include <assert.h>
#include <string.h>

#ifdef AAC_HIGH_HISTORY_PC16
#define HISTORY_FORMAT PC_STORAGE_SHARED16
#else
#define HISTORY_FORMAT PC_STORAGE_SHARED18_FOUR
#endif
static struct {
    aac_high_frame_t *frame;
    bool real_only;
    unsigned loads, stores, complex_frames, real_frames;
    unsigned changed, saturations, max_shift;
    unsigned call_loads, call_stores;
} history;

static void unpack(const aac_high_history_t *h,unsigned i,int32_t *r,int32_t *im) {
    pc_storage_unpack(HISTORY_FORMAT,h->mantissas[i],
        pc_storage_load_metadata(HISTORY_FORMAT,h->metadata,i),r,im);
}
static void pack(aac_high_history_t *h,unsigned i,int32_t r,int32_t im) {
    unsigned metadata,saturated;
    h->mantissas[i]=pc_storage_pack(HISTORY_FORMAT,r,im,&metadata,&saturated);
    pc_storage_store_metadata(HISTORY_FORMAT,h->metadata,i,metadata);
    history.saturations+=saturated;
    unsigned shift=pc_storage_max_shift(HISTORY_FORMAT,metadata);
    if(shift>history.max_shift)history.max_shift=shift;
    int32_t restored_r,restored_im;
    unpack(h,i,&restored_r,&restored_im);
    history.changed+=(restored_r!=r)+(restored_im!=im);
}

void *aac_high_history_memmove(void *dest,const void *source,size_t bytes) {
    aac_high_frame_t *f=history.frame;
    assert(f);
    void *real_token=&f->high_history.mantissas[0];
    void *imag_token=&f->high_history.mantissas[1];
    const size_t native_bytes=AAC_HIGH_PAIRS*sizeof(int32_t);
    const unsigned tail=AAC_HIGH_NEW_ROWS*AAC_HIGH_BANDS;
    if(source==real_token) {
        assert(bytes==native_bytes && dest==f->high_real && !history.call_loads);
        for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
            int32_t r,im;unpack(&f->high_history,i,&r,&im);
            f->high_real[i]=r;
            if(!history.real_only)f->high_imag[i]=im;
        }
        ++history.loads;++history.call_loads;
    } else if(source==imag_token) {
        assert(!history.real_only && bytes==native_bytes && dest==f->high_imag && history.call_loads==1);
        ++history.call_loads;
    } else if(dest==real_token) {
        assert(bytes==native_bytes && source==f->high_real+tail && !history.call_stores);
        for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
            int32_t r,im;
            // LC-SBR leaves the imaginary history untouched. Retain its last
            // represented value instead of reading an unused scratch row.
            if(history.real_only)unpack(&f->high_history,i,&r,&im);
            else im=f->high_imag[tail+i];
            pack(&f->high_history,i,f->high_real[tail+i],im);
        }
        ++history.stores;++history.call_stores;
    } else if(dest==imag_token) {
        assert(!history.real_only && bytes==native_bytes && source==f->high_imag+tail && history.call_stores==1);
        ++history.call_stores;
    } else return memmove(dest,source,bytes);
    return dest;
}

void __real_compact5_sbr_dec(void *,void *,void *,int,void *,void *,void *,void *);
void __wrap_compact5_sbr_dec(void *input,void *output,void *frame,int apply,
                           void *control,void *right_output,void *ps,void *core) {
    assert(!history.frame);
    history.frame=frame;history.real_only=((aac_sbr_control_abi_t *)control)->low_complexity!=0;
    history.call_loads=history.call_stores=0;
    if(history.real_only)++history.real_frames;else ++history.complex_frames;
    __real_compact5_sbr_dec(input,output,frame,apply,control,right_output,ps,core);
    assert(history.call_loads==(history.real_only?1:2));
    assert(history.call_stores==(history.real_only?1:2));
    history.frame=NULL;
}
void aac_high_history_clear(aac_high_frame_t *f,bool both) {
    if(both)memset(&f->high_history,0,sizeof(f->high_history));
    else for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
        int32_t r,im;unpack(&f->high_history,i,&r,&im);pack(&f->high_history,i,0,im);
    }
}
void aac_high_history_reset_counters(void) { assert(!history.frame);memset(&history,0,sizeof(history)); }
void aac_high_history_report(const char *name,unsigned variant,unsigned run) {
    assert(!history.frame && history.loads==history.stores);
    ESP_LOGI("high_history","HIGHHISTORY_MEMORY case=%s variant=%u run=%u bytes=%u state_bytes=%u"
        " loads=%u stores=%u real_frames=%u complex_frames=%u changed=%u saturations=%u max_shift=%u",
        name,variant,run,(unsigned)sizeof(aac_high_history_t),(unsigned)sizeof(history),
        history.loads,history.stores,history.real_frames,history.complex_frames,
        history.changed,history.saturations,history.max_shift);
}
