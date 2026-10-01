#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
#include "aac_scratch_reserve.h"
#include <assert.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Pinned 2.6.2 initialization allocates this workspace after the 35460-byte
// core and several small owners. Request it before the caller PCM/core instead,
// so a smaller heap region can satisfy it without splitting the SBR region.
// No change to workspace size, arithmetic, or normal SDK free ownership.
#define SCRATCH_BYTES 12288u
#define AAC_TLS_SLOT 1
_Static_assert(CONFIG_FREERTOS_THREAD_LOCAL_STORAGE_POINTERS > AAC_TLS_SLOT,
               "AAC placement needs TLS slot 1; slot 0 belongs to pthreads");

void aac_scratch_reserve_prepare(aac_scratch_reserve_t *state) {
    assert(!state->pending);
    state->pending=calloc(1,SCRATCH_BYTES);
    state->allocation_failed=false;
}
void aac_scratch_reserve_discard(aac_scratch_reserve_t *state) {
    free(state->pending);state->pending=NULL;
}
void aac_scratch_reserve_enter(aac_scratch_reserve_t *state) {
    assert(!pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT));
    state->allocation_failed=false;
    vTaskSetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT,state);
}
void aac_scratch_reserve_leave(void) {
    vTaskSetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT,NULL);
}

void *__real_media_lib_module_calloc(const char *,size_t,size_t);
void *__wrap_media_lib_module_calloc(const char *module,size_t n,size_t size) {
    aac_scratch_reserve_t *state=pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT);
    if(state && n==1 && size==SCRATCH_BYTES && state->pending) {
        void *p=state->pending;state->pending=NULL;return p;
    }
    size_t request=size;
#ifdef CONFIG_YORADIO_AAC_RELOCATE_PS
    if(state && n==1 && size==55128)request=51596;
#endif
    void *p=__real_media_lib_module_calloc(module,n,request);
#ifdef CONFIG_YORADIO_AAC_RELOCATE_PS
    if(state && n==1 && size==55128 && p) {
        assert(!state->owner);
        state->owner=p;state->ps_active=false;
#ifdef CONFIG_YORADIO_AAC_PS_PC16
        state->ps_packed=false;
#endif
    }
#endif
    // SBR OOM must be an error, not apparently successful core-only output.
    if(state && !p && n==1 && (size==55128 || size==1180))
        state->allocation_failed=true;
    return p;
}

#ifdef CONFIG_YORADIO_AAC_RELOCATE_PS
// Same lossless layout as the guarded 81-case QEMU trial. A mono core with
// PS does not use the right SBR work area [0x93b4,0xa780); both PS delay/hybrid
// data below it and right synthesis history above it remain untouched.
#define PS_POINTER 0xc984u
#define PS_SENTINEL 0xc988u
#define PS_RELOCATED 0x93b4u
#define PS_BYTES 3536u
_Static_assert(sizeof(void*)==4,"Pinned RV32 pointer layout");
_Static_assert(PS_RELOCATED+PS_BYTES<=0xa780,"PS must precede right synthesis");
static void ps_pointer(aac_scratch_reserve_t *state) {
    void *p=state->owner+(state->ps_active?PS_RELOCATED:PS_SENTINEL);
    memcpy(state->owner+PS_POINTER,&p,4);
}
void __real_media_lib_free(void *);
void __wrap_media_lib_free(void *p) {
    aac_scratch_reserve_t *state=pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT);
    if(state && state->owner==p) {
        assert(!state->inside_sbr);
        state->owner=NULL;state->ps_active=false;
    }
    __real_media_lib_free(p);
}
int __real_sbr_applied(void *,void *,void *,void *,void *,void *,int,void *,void *,int);
int __real_ps_read_data(void *,void *,unsigned);
int __wrap_sbr_applied(void *owner,void *stream,void *left,void *right,
                      void *out_l,void *out_r,int channels,void *control,void *core,int out_channels) {
    aac_scratch_reserve_t *state=pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT);
    if(!state || state->owner!=owner)
        return __real_sbr_applied(owner,stream,left,right,out_l,out_r,channels,control,core,out_channels);
    assert(!state->inside_sbr);state->inside_sbr=true;
    // Vendor frame controller refreshes the embedded pointer every frame.
    ps_pointer(state);
    int result=__real_sbr_applied(owner,stream,left,right,out_l,out_r,channels,control,core,out_channels);
    state->inside_sbr=false;
    return result;
}
int __wrap_ps_read_data(void *ps,void *bits,unsigned count) {
    aac_scratch_reserve_t *state=pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT);
    if(!state || !state->inside_sbr)return __real_ps_read_data(ps,bits,count);
    if(!state->ps_active) {
        memset(state->owner+PS_RELOCATED,0,PS_BYTES);
        memcpy(state->owner+PS_RELOCATED,state->owner+PS_SENTINEL,4);
        state->ps_active=true;ps_pointer(state);
    }
    return __real_ps_read_data(state->owner+PS_RELOCATED,bits,count);
}
#ifdef CONFIG_YORADIO_AAC_PS_PC16
void aac_ps_pc16_allocate(void *,uint32_t,bool);
void aac_ps_pc16_decode(void *,void *,int32_t *,int32_t *,int32_t *,int32_t *,int32_t *);
void __real_ps_allocate_decoder(void *,uint32_t);
void __real_ps_decorrelate(void *,int32_t *,int32_t *,int32_t *,int32_t *,int32_t *);
void __wrap_ps_allocate_decoder(void *owner,uint32_t samples) {
    aac_scratch_reserve_t *s=pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT);
    if(!s || s->owner!=owner){__real_ps_allocate_decoder(owner,samples);return;}
    assert(s->ps_active && s->inside_sbr);
    aac_ps_pc16_allocate(owner,samples,!s->ps_packed);s->ps_packed=true;
}
void __wrap_ps_decorrelate(void *ps,int32_t *lr,int32_t *li,int32_t *rr,int32_t *ri,int32_t *scratch) {
    aac_scratch_reserve_t *s=pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT);
    if(!s || !s->ps_packed){__real_ps_decorrelate(ps,lr,li,rr,ri,scratch);return;}
    assert(s->inside_sbr && ps==s->owner+PS_RELOCATED);
    aac_ps_pc16_decode(s->owner,ps,lr,li,rr,ri,scratch);
}
#endif
#endif
#endif
