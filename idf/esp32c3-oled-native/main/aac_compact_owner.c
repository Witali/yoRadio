#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
#include "aac_compact_owner.h"
#include "aac_sbr_abi.h"
#include "aac_sbr_reset.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <string.h>

#define AAC_TLS_SLOT 1
_Static_assert(CONFIG_FREERTOS_THREAD_LOCAL_STORAGE_POINTERS>AAC_TLS_SLOT,
               "AAC compact owner needs TLS slot 1; slot 0 belongs to pthreads");
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
#include "aac_high_reset.h"
typedef aac_high_owner_t owner_t;
typedef aac_high_channel_t owner_channel_t;
#define aac_sbr_reset_core aac_high_reset_core
#else
typedef aac_sbr_compact_relocated_owner_abi_t owner_t;
typedef aac_sbr_compact_channel_abi_t owner_channel_t;
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
static size_t fail_request;
static unsigned live_owners;
void aac_compact_owner_test_fail_next(size_t size) { assert(!fail_request);fail_request=size; }
void aac_compact_owner_test_assert_idle(void) { assert(!fail_request && !live_owners); }
#endif

static aac_compact_owner_t *context(void) {
    return pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT);
}
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
aac_high_runtime_t *aac_compact_owner_high_context(void) {
    aac_compact_owner_t *state=context();assert(state);
    return &state->high_history;
}
#endif
void aac_compact_owner_enter(aac_compact_owner_t *state) {
    assert(state && !context());state->allocation_failed=false;
    vTaskSetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT,state);
}
void aac_compact_owner_leave(void) {
    assert(context() && !context()->inside_sbr);
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
    assert(!context()->high_history.frame);
#endif
    vTaskSetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT,NULL);
}
static void ps_pointer(aac_compact_owner_t *state) {
    owner_t *owner=state->owner;
    owner->ps=state->ps_initialized ? &owner->channel[1].ps_overlay.relocated_ps :
                                     (void *)&owner->inactive_ps;
}

void *__real_media_lib_module_calloc(const char *,size_t,size_t);
void *__wrap_media_lib_module_calloc(const char *module,size_t n,size_t size) {
    aac_compact_owner_t *state=context();
    bool owner_request=state && n==1 && size==sizeof(aac_sbr_owner_abi_t);
    void *p;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(state && n==1 && size==fail_request) { fail_request=0;p=NULL; }
    else
#endif
    p=__real_media_lib_module_calloc(module,n,owner_request?sizeof(owner_t):size);
    if(owner_request && p) {
        assert(!state->owner);state->owner=p;state->ps_initialized=false;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
        ++live_owners;
#endif
    }
    if(state && !p && n==1 &&
       (size==sizeof(aac_sbr_owner_abi_t) || size==sizeof(aac_sbr_control_abi_t)))
        state->allocation_failed=true;
    return p;
}
void __real_media_lib_free(void *);
void __wrap_media_lib_free(void *p) {
    aac_compact_owner_t *state=context();
    if(state && p && state->owner==p) {
        assert(!state->inside_sbr);state->owner=NULL;state->ps_initialized=false;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
        assert(live_owners);--live_owners;
#endif
    }
    __real_media_lib_free(p);
}
int __real_PVMP4AudioDecodeFrame(void *,void *);
int compact5_PVMP4AudioDecodeFrame(void *,void *);
int __wrap_PVMP4AudioDecodeFrame(void *external,void *core) {
    aac_compact_owner_t *state=context();
    if(!state)return __real_PVMP4AudioDecodeFrame(external,core);
    assert(!((aac_core_abi_t *)core)->sbr || ((aac_core_abi_t *)core)->sbr==state->owner);
    return compact5_PVMP4AudioDecodeFrame(external,core);
}
int __real_compact5_sbr_applied(void *,void *,void *,void *,void *,void *,int,void *,void *,int);
int __wrap_compact5_sbr_applied(void *owner,void *stream,void *left,void *right,
                              void *out_l,void *out_r,int channels,void *control,void *core,int out_channels) {
    aac_compact_owner_t *state=context();
    assert(state && state->owner==owner && !state->inside_sbr);
    state->inside_sbr=true;ps_pointer(state);
    int result=__real_compact5_sbr_applied(owner,stream,left,right,out_l,out_r,channels,control,core,out_channels);
    state->inside_sbr=false;return result;
}
int __real_ps_read_data(void *,void *,unsigned);
int __wrap_ps_read_data(void *ps,void *bits,unsigned count) {
    aac_compact_owner_t *state=context();
    if(!state || !state->inside_sbr)return __real_ps_read_data(ps,bits,count);
    owner_t *owner=state->owner;
    aac_ps_abi_t *relocated=&owner->channel[1].ps_overlay.relocated_ps;
    if(!state->ps_initialized) {
        memset(relocated,0,sizeof(*relocated));relocated->detected=owner->inactive_ps;
        state->ps_initialized=true;ps_pointer(state);
    }
    return __real_ps_read_data(relocated,bits,count);
}

void __real_PVMP4AudioDecoderResetBuffer(void *);
void __wrap_PVMP4AudioDecoderResetBuffer(void *opaque) {
    aac_compact_owner_t *state=context();
    if(!state){__real_PVMP4AudioDecoderResetBuffer(opaque);return;}
    aac_core_abi_t *core=opaque;owner_t *owner=core->sbr;
    if(!owner){aac_sbr_reset_core(core,NULL);return;}
    assert(owner==state->owner && !state->inside_sbr);ps_pointer(state);
    aac_sbr_reset_view_t view={
        .frame={(void *)&owner->channel[0].frame,(void *)&owner->channel[1].frame},
        .sync={&owner->channel[0].sync_state,&owner->channel[1].sync_state},
        .initialize_ps=&owner->initialize_ps,.ps=owner->ps,
        .ps_initialized=state->ps_initialized};
    aac_sbr_reset_core(core,&view);
}
void __real_compact5_sbr_open(int,void *,void *,int);
int compact5_init_sbr_dec(int,int,void *,void *);
extern const uint32_t compact5_defaultHeader[16];
void __wrap_compact5_sbr_open(int rate,void *control,void *opaque,int downsample) {
    aac_compact_owner_t *state=context();owner_t *owner=opaque;
    assert(state && state->owner==owner);
    if(!state->ps_initialized) {
        __real_compact5_sbr_open(rate,control,owner,downsample);return;
    }
    const size_t start=offsetof(owner_t,channel[1].ps_overlay.relocated_ps);
    const size_t end=start+sizeof(aac_ps_abi_t);
    memset(owner,0,start);
    memset((uint8_t *)owner+end,0,offsetof(owner_t,initialize_ps)-end);
    for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch) {
        owner_channel_t *channel=&owner->channel[ch];
        memcpy(&channel->frame.header,compact5_defaultHeader,sizeof(channel->frame.header));
        if(downsample || rate>24000)channel->frame.header.sample_rate_mode=1;
        channel->frame_size=compact5_init_sbr_dec(rate,owner->channel[0].frame.header.sample_rate_mode,control,&channel->frame);
        channel->sync_state=1;channel->frame.startup=1;
    }
}
#endif
