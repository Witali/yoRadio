#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
#include "aac_compact_owner.h"
#include "aac_sbr_abi.h"
#include "aac_sbr_reset.h"
#include "aac_pointer_audit.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <string.h>
#ifdef CONFIG_YORADIO_AAC_LATE_SBR
#include "aac_analysis_core.h"
extern const aac_analysis_sample_rates_t samp_rate_info;
void __wrap_compact5_sbr_open(int rate,void *control,void *owner,int downsample);
#endif

#define AAC_TLS_SLOT 1
_Static_assert(CONFIG_FREERTOS_THREAD_LOCAL_STORAGE_POINTERS>AAC_TLS_SLOT,
               "AAC compact owner needs TLS slot 1; slot 0 belongs to pthreads");
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
#include "aac_high_reset.h"
typedef aac_high_owner_t owner_t;
typedef aac_high_channel_view_t owner_channel_t;
#define OWNER_CHANNEL(owner,ch) aac_high_owner_channel(owner,ch)
#define OWNER_PS_MEMBER(member) AAC_HIGH_RIGHT_MEMBER(ps_overlay.member)
#define OWNER_RELOCATED_PS(owner) (&aac_high_owner_right(owner)->ps_overlay.relocated_ps)
#define aac_sbr_reset_core aac_high_reset_core
#else
typedef aac_sbr_compact_relocated_owner_abi_t owner_t;
typedef aac_sbr_compact_channel_abi_t owner_channel_t;
#define OWNER_CHANNEL(owner,ch) (&(owner)->channel[ch])
#define OWNER_PS_MEMBER(member) channel[1].ps_overlay.member
#define OWNER_RELOCATED_PS(owner) (&(owner)->channel[1].ps_overlay.relocated_ps)
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
#ifdef CONFIG_YORADIO_AAC_LATE_SBR
enum { AAC_CORE_FRAME_SAMPLES=1024, AAC_QMF_PREFIX_SAMPLES=288,
       AAC_SBR_BANK_SAMPLES=AAC_CORE_FRAME_SAMPLES+AAC_QMF_PREFIX_SAMPLES };
int aac_late_sbr_retain(void) {
    aac_compact_owner_t *state=context();
    if(!state || !state->late_core)return 0;
    aac_analysis_core_t *core=state->late_core;
    assert(!core->sbr_stream->elements);
    // Missing extension data does not undo an already established SBR/PS
    // configuration. Reuse the native no-new-data synthesis path and history.
    return core->mc.sbr_present && state->owner && core->sbr_control &&
           core->sbr_control->output_rate;
}
void aac_late_sbr_after_fill(void *opaque_stream) {
    aac_compact_owner_t *state=context();
    if(!state || !state->late_core)return;
    aac_analysis_sbr_stream_t *stream=opaque_stream;
    if(!stream->elements)return;
    aac_analysis_core_t *core=state->late_core;
    assert(core->frame_length==AAC_CORE_FRAME_SAMPLES);
    // The native SBR history copy assumes bank 0 or 1312. AAC-LC instead
    // toggles 0/1024; its second bank would copy 288 samples BEFORE the array.
    // Select the initial SBR bank after detecting actual extension payload,
    // before the transform writes that frame. Keep both IMDCT overlaps intact.
    assert(core->ltp_buffer_state==0 || core->ltp_buffer_state==AAC_CORE_FRAME_SAMPLES ||
           core->ltp_buffer_state==AAC_SBR_BANK_SAMPLES);
    if(core->ltp_buffer_state==AAC_CORE_FRAME_SAMPLES)core->ltp_buffer_state=0;
}
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
aac_compact_owner_t *aac_compact_owner_audit_context(void) { assert(context());return context(); }
#endif
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
aac_high_runtime_t *aac_compact_owner_high_context(void) {
    aac_compact_owner_t *state=context();assert(state);
    return &state->high_history;
}
#ifdef AAC_HIGH_HISTORY_PC19_SIDECAR
unsigned aac_compact_owner_high_channel(const aac_high_frame_t *frame) {
    aac_compact_owner_t *state=context();assert(state && state->owner);
    for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch)
        if(frame==&OWNER_CHANNEL((owner_t *)state->owner,ch)->frame)return ch;
    assert(!"High-QMF frame must belong to the active decoder");return 0;
}
#endif
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
    owner->ps=state->ps_initialized ? OWNER_RELOCATED_PS(owner) :
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
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_allocate(p,n*(owner_request?sizeof(owner_t):size),state);
#endif
    if(owner_request && p) {
        assert(!state->owner);state->owner=p;state->ps_initialized=false;
#ifdef AAC_HIGH_HISTORY_PC19_SIDECAR
        memset(state->high_history.pc19_extra,0,sizeof(state->high_history.pc19_extra));
#endif
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
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_free(p,state);
#endif
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
#ifdef CONFIG_YORADIO_AAC_LATE_SBR
    aac_analysis_core_t *late_core=core;
    aac_analysis_external_t *late_external=external;
    assert(!state->late_core);
    if(!state->late_disabled)state->late_core=core;
    if(!state->late_disabled && late_core->requested_plus && late_core->sbr_stream) {
        late_core->plus_enabled=1;
        late_external->plus_enabled=1;
    }
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_core(core,external,false);
#endif
    int result=compact5_PVMP4AudioDecodeFrame(external,core);
#ifdef CONFIG_YORADIO_AAC_LATE_SBR
    state->late_core=NULL;
    if(!state->late_disabled && !result && late_core->plus_enabled && late_core->mc.sbr_present) {
        assert(late_core->mc.sample_rate_index>=0 && late_core->mc.sample_rate_index<12);
        assert(late_core->mc.upsampling==1 || late_core->mc.upsampling==2);
        late_external->sample_rate=samp_rate_info.entry[late_core->mc.sample_rate_index].rate * late_core->mc.upsampling;
        late_external->frame_length=late_core->frame_length * late_core->mc.upsampling;
        if(late_core->mc.upsampling==2)late_external->reposition=2;
    }
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_core(core,external,true);
#endif
    aac_profile_observe(core,result);
    return result;
}
int __real_compact5_sbr_applied(void *,void *,void *,void *,void *,void *,int,void *,void *,int);
int __wrap_compact5_sbr_applied(void *owner,void *stream,void *left,void *right,
                              void *out_l,void *out_r,int channels,void *control,void *core,int out_channels) {
    aac_compact_owner_t *state=context();
    assert(state && state->owner==owner && !state->inside_sbr);
#ifdef CONFIG_YORADIO_AAC_LATE_SBR
    aac_analysis_core_t *late_core=core;
    aac_sbr_control_abi_t *late_control=control;
    if(!state->late_disabled && !late_control->output_rate) {
        assert(late_core->mc.sample_rate_index>=0 && late_core->mc.sample_rate_index<12);
        __wrap_compact5_sbr_open(samp_rate_info.entry[late_core->mc.sample_rate_index].rate,
                                control,owner,late_core->mc.downsampled_sbr);
        late_core->mc.upsampling=OWNER_CHANNEL((owner_t *)owner,0)->frame.header.sample_rate_mode;
    }
#endif
    state->inside_sbr=true;ps_pointer(state);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_applied(owner,stream,left,right,out_l,out_r,control,core,false);
#endif
    int result=__real_compact5_sbr_applied(owner,stream,left,right,out_l,out_r,channels,control,core,out_channels);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_applied(owner,stream,left,right,out_l,out_r,control,core,true);
#endif
    state->inside_sbr=false;return result;
}
int __real_ps_read_data(void *,void *,unsigned);
int __wrap_ps_read_data(void *ps,void *bits,unsigned count) {
    aac_compact_owner_t *state=context();
    if(!state || !state->inside_sbr)return __real_ps_read_data(ps,bits,count);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_ps_bits(ps,bits,false);
#endif
    owner_t *owner=state->owner;
    aac_ps_abi_t *relocated=OWNER_RELOCATED_PS(owner);
    if(!state->ps_initialized) {
        memset(relocated,0,sizeof(*relocated));relocated->detected=owner->inactive_ps;
        state->ps_initialized=true;ps_pointer(state);
    }
    int result=__real_ps_read_data(relocated,bits,count);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_ps_bits(relocated,bits,true);
#endif
    return result;
}

void __real_PVMP4AudioDecoderResetBuffer(void *);
void __wrap_PVMP4AudioDecoderResetBuffer(void *opaque) {
    aac_compact_owner_t *state=context();
    if(!state){__real_PVMP4AudioDecoderResetBuffer(opaque);return;}
    aac_core_abi_t *core=opaque;owner_t *owner=core->sbr;
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_reset(core);
#endif
    if(!owner){aac_sbr_reset_core(core,NULL);return;}
    assert(owner==state->owner && !state->inside_sbr);ps_pointer(state);
    aac_sbr_reset_view_t view={
        .frame={(void *)&OWNER_CHANNEL(owner,0)->frame,(void *)&OWNER_CHANNEL(owner,1)->frame},
        .sync={&OWNER_CHANNEL(owner,0)->sync_state,&OWNER_CHANNEL(owner,1)->sync_state},
        .initialize_ps=&owner->initialize_ps,.ps=owner->ps,
        .ps_initialized=state->ps_initialized};
    aac_sbr_reset_core(core,&view);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_reset(core);
#endif
}
void __real_compact5_sbr_open(int,void *,void *,int);
int compact5_init_sbr_dec(int,int,void *,void *);
extern const uint32_t compact5_defaultHeader[16];
void __wrap_compact5_sbr_open(int rate,void *control,void *opaque,int downsample) {
    aac_compact_owner_t *state=context();owner_t *owner=opaque;
    assert(state && state->owner==owner);
#ifdef AAC_HIGH_HISTORY_PC19_SIDECAR
    // The native/typed open below clears QMF history. Its extra bits have the
    // same lifetime even when the inactive right-channel PS overlay survives.
    memset(state->high_history.pc19_extra,0,sizeof(state->high_history.pc19_extra));
#endif
#ifndef AAC_ASYMMETRIC_OWNER
    if(!state->ps_initialized) {
        __real_compact5_sbr_open(rate,control,owner,downsample);return;
    }
#endif
    const size_t start=offsetof(owner_t,OWNER_PS_MEMBER(relocated_ps));
    const size_t end=start+sizeof(aac_ps_abi_t);
    if(state->ps_initialized) {
        memset(owner,0,start);
        memset((uint8_t *)owner+end,0,offsetof(owner_t,initialize_ps)-end);
    } else {
        memset(owner,0,offsetof(owner_t,initialize_ps));
    }
    for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch) {
        owner_channel_t *channel=OWNER_CHANNEL(owner,ch);
        memcpy(&channel->frame.header,compact5_defaultHeader,sizeof(channel->frame.header));
        if(downsample || rate>24000)channel->frame.header.sample_rate_mode=1;
        channel->frame_size=compact5_init_sbr_dec(rate,OWNER_CHANNEL(owner,0)->frame.header.sample_rate_mode,control,&channel->frame);
        channel->sync_state=1;channel->frame.startup=1;
    }
}
#endif
