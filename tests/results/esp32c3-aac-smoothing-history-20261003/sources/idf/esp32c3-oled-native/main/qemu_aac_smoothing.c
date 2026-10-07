// QEMU-only guarded A/B adapter for compact_sbr_tables.py.
// The candidate has actual five-entry tables and a smaller owner allocation.
#include "qemu_aac_packed_history.h"
#include "aac_sbr_abi.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
#include "aac_high_history.h"
#define aac_sbr_compact_channel_abi_t aac_high_channel_t
#define aac_sbr_compact_owner_abi_t aac_high_full_owner_t
#define aac_sbr_compact_relocated_owner_abi_t aac_high_owner_t
#endif
#define ORIGINAL_SIZE sizeof(aac_sbr_owner_abi_t)
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_OWNER_TEST
#define COMPACT_SIZE sizeof(aac_sbr_compact_relocated_owner_abi_t)
#define PS_RELOCATED 4u
#else
#define COMPACT_SIZE sizeof(aac_sbr_compact_owner_abi_t)
#endif
#define GUARD_BYTES 16u
typedef struct { uint8_t *owner, *allocation; size_t size, physical; unsigned variant, ps; } owner_t;
static owner_t owners[4];
static owner_t *active;
static unsigned selected, calls, allocations, frees, ps_reads;
static size_t fail_size[2], requested[2], physical[2];
static const char *TAG = "sbr_compact5";
void *__real_media_lib_module_calloc(const char *, size_t, size_t);
void __real_media_lib_free(void *);
int __real_PVMP4AudioDecodeFrame(void *, void *);
int compact5_PVMP4AudioDecodeFrame(void *, void *);
int __real_ps_read_data(void *, void *, unsigned);
void __real_PVMP4AudioDecoderResetBuffer(void *);
void sbr_open(int,void *,void *,int);
void compact5_sbr_open(int,void *,void *,int);
void ps_allocate_decoder(void *,unsigned);
void compact5_ps_allocate_decoder(void *,unsigned);

#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_OWNER_TEST
static void ps_pointer(owner_t *o) {
    aac_sbr_compact_relocated_owner_abi_t *sbr=(void *)o->owner;
    sbr->ps=o->ps&PS_RELOCATED ? &sbr->channel[1].ps_overlay.relocated_ps :
                               (void *)&sbr->inactive_ps;
}
#endif

static owner_t *find(void *p) {
    for(unsigned i=0;i<4;++i) if(p && owners[i].owner==p)return owners+i;
    return NULL;
}
static void check(owner_t *o) {
    for(unsigned i=0;i<GUARD_BYTES;++i) {
        assert(o->allocation[i]==0xa5);
        assert(o->owner[o->size+i]==0x5a);
    }
}
void *__wrap_media_lib_module_calloc(const char *module,size_t n,size_t size) {
#ifdef CONFIG_YORADIO_QEMU_AAC_RESET_TEST
    bool qemu_aac_reset_calloc(const char *,size_t,size_t,void **);
    void *result;
    if(qemu_aac_reset_calloc(module,n,size,&result))return result;
#endif
    unsigned leg=selected==1;
    if(n==1 && fail_size[leg] && size==fail_size[leg]) { fail_size[leg]=0;return NULL; }
    if(n!=1 || size!=ORIGINAL_SIZE)return __real_media_lib_module_calloc(module,n,size);
    owner_t *o=NULL;
    for(unsigned i=0;i<4;++i)if(!owners[i].owner){o=owners+i;break;}
    assert(o);
    size_t payload=leg?COMPACT_SIZE:ORIGINAL_SIZE;
    uint8_t *raw=__real_media_lib_module_calloc(module,1,payload+2*GUARD_BYTES);
    if(!raw)return NULL;
    memset(raw,0xa5,GUARD_BYTES);memset(raw+GUARD_BYTES+payload,0x5a,GUARD_BYTES);
    *o=(owner_t){.owner=raw+GUARD_BYTES,.allocation=raw,.size=payload,
        .physical=heap_caps_get_allocated_size(raw),.variant=selected};
    ++allocations;requested[leg]=payload;physical[leg]=o->physical;
    return o->owner;
}
void __wrap_media_lib_free(void *p) {
#ifdef CONFIG_YORADIO_QEMU_AAC_RESET_TEST
    bool qemu_aac_reset_free(void *);
    if(qemu_aac_reset_free(p))return;
#endif
    owner_t *o=find(p);
    if(!o){__real_media_lib_free(p);return;}
    check(o);void *raw=o->allocation;memset(o,0,sizeof(*o));++frees;
    __real_media_lib_free(raw);
}
int __wrap_PVMP4AudioDecodeFrame(void *external,void *core) {
    if(selected!=1)return __real_PVMP4AudioDecodeFrame(external,core);
    assert(!active);
    aac_core_abi_t *decoder=core;
    void *owner=decoder->sbr;
    active=find(owner);
    if(active) { assert(active->variant==1);check(active); }
    int result=compact5_PVMP4AudioDecodeFrame(external,core);
    owner=decoder->sbr;
    active=find(owner);
    if(active){
        check(active);++calls;
        aac_sbr_compact_owner_abi_t *sbr=(void *)active->owner;
        for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch) {
            aac_sbr_compact_channel_abi_t *channel=&sbr->channel[ch];
            if(channel->sync_state==2){
                unsigned mode=channel->frame.header.smoothing_mode;
                assert(mode<=1);active->ps|=1u<<mode;
            }
        }
    }
    active=NULL;
    return result;
}
int __wrap_ps_read_data(void *ps,void *bits,unsigned count) {
    if(selected==1)++ps_reads;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_OWNER_TEST
    if(active && active->variant==1) {
        aac_sbr_compact_relocated_owner_abi_t *sbr=(void *)active->owner;
        aac_ps_abi_t *relocated=&sbr->channel[1].ps_overlay.relocated_ps;
        if(!(active->ps&PS_RELOCATED)) {
            memset(relocated,0,sizeof(*relocated));
            relocated->detected=sbr->inactive_ps;
            active->ps|=PS_RELOCATED;ps_pointer(active);
        }
        return __real_ps_read_data(relocated,bits,count);
    }
#endif
    return __real_ps_read_data(ps,bits,count);
}
#ifndef CONFIG_YORADIO_QEMU_AAC_RESET_TEST
void __wrap_PVMP4AudioDecoderResetBuffer(void *core) {
    void *owner=((aac_core_abi_t *)core)->sbr;
    owner_t *o=find(owner);
    // This API has additional fixed offsets and a pre-existing out-of-core
    // write. It must never run against the experimental layout. The radio
    // adapter resets by destroying/reopening the decoder instead.
    assert(selected!=1 && (!o || o->variant!=1));
    __real_PVMP4AudioDecoderResetBuffer(core);
}
#endif

#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_OWNER_TEST
int __real_compact5_sbr_applied(void *,void *,void *,void *,void *,void *,int,void *,void *,int);
int __wrap_compact5_sbr_applied(void *owner,void *stream,void *left,void *right,
                              void *out_l,void *out_r,int channels,void *control,void *core,int out_channels) {
    owner_t *o=find(owner);assert(o && o->variant==1 && (!active || active==o));
    active=o;ps_pointer(o);check(o);
    int result=__real_compact5_sbr_applied(owner,stream,left,right,out_l,out_r,channels,control,core,out_channels);
    check(o);active=NULL;return result;
}
void *aac_sbr_layout_ps(void *owner) {
    owner_t *o=find(owner);assert(o && o->variant==1);ps_pointer(o);
    return ((aac_sbr_compact_relocated_owner_abi_t *)owner)->ps;
}
void __real_compact5_sbr_open(int,void *,void *,int);
int compact5_init_sbr_dec(int,int,void *,void *);
extern const uint32_t compact5_defaultHeader[16];
void __wrap_compact5_sbr_open(int rate,void *control,void *owner,int downsample) {
    owner_t *o=find(owner);
    if(!o || !(o->ps&PS_RELOCATED)) {
        __real_compact5_sbr_open(rate,control,owner,downsample);return;
    }
    // Preserve relocated PS control across reset, like the original tail.
    aac_sbr_compact_relocated_owner_abi_t *sbr=owner;
    const size_t start=offsetof(aac_sbr_compact_relocated_owner_abi_t,channel[1].ps_overlay.relocated_ps);
    const size_t end=start+sizeof(aac_ps_abi_t);
    memset(owner,0,start);
    memset(o->owner+end,0,offsetof(aac_sbr_compact_relocated_owner_abi_t,initialize_ps)-end);
    for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch) {
        aac_sbr_compact_channel_abi_t *channel=&sbr->channel[ch];
        memcpy(&channel->frame.header,compact5_defaultHeader,sizeof(channel->frame.header));
        if(downsample || rate>24000)channel->frame.header.sample_rate_mode=1;
        channel->frame_size=compact5_init_sbr_dec(rate,sbr->channel[0].frame.header.sample_rate_mode,control,&channel->frame);
        channel->sync_state=1;channel->frame.startup=1;
    }
    check(o);
}
#endif
void packed_history_reset(unsigned run) {
    (void)run;
    for(unsigned i=0;i<4;++i)assert(!owners[i].owner);
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
    aac_high_history_reset_counters();
#endif
    selected=calls=allocations=frees=ps_reads=0;
    memset(requested,0,sizeof(requested));memset(physical,0,sizeof(physical));
}
void packed_history_select(unsigned variant) {assert(variant==0||variant==1||variant==7);selected=variant;}
void packed_history_report(const char *name,unsigned variant,unsigned run,uint32_t *rows,uint32_t *changed,unsigned *shift) {
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
    aac_high_history_report(name,variant,run);
#endif
    unsigned modes=0;
    for(unsigned i=0;i<4;++i)if(owners[i].owner)check(owners+i);
    for(unsigned i=0;i<4;++i)if(owners[i].owner && owners[i].variant==1)modes|=owners[i].ps&3u;
    *rows=calls;*changed=*shift=0;
    ESP_LOGI(TAG,"SBRLAYOUT_MEMORY case=%s variant=%u run=%u calls=%u ps_reads=%u allocations=%u frees=%u"
        " reference=%u candidate=%u physical_reference=%u physical_candidate=%u static_test_state=%u guard_bytes=%u smoothing_modes=%u",
        name,variant,run,calls,ps_reads,allocations,frees,(unsigned)requested[0],(unsigned)requested[1],
        (unsigned)physical[0],(unsigned)physical[1],
        (unsigned)(sizeof(owners)+sizeof(active)+sizeof(selected)+sizeof(calls)+sizeof(allocations)+sizeof(frees)+sizeof(ps_reads)+sizeof(fail_size)+sizeof(requested)+sizeof(physical)),2*GUARD_BYTES,modes);
}
static size_t map_offset(size_t offset) {
    const size_t old_channel=sizeof(aac_sbr_channel_abi_t);
    const size_t new_channel=sizeof(aac_sbr_compact_channel_abi_t);
    if(offset>=offsetof(aac_sbr_owner_abi_t,initialize_ps))
        return offset-(ORIGINAL_SIZE-sizeof(aac_sbr_compact_owner_abi_t));
    size_t channel=offset/old_channel, local=offset%old_channel;
    const size_t tables=offsetof(aac_sbr_channel_abi_t,smoothing);
    const size_t old_table=sizeof(((aac_sbr_channel_abi_t *)0)->smoothing[0]);
    const size_t new_table=sizeof(((aac_sbr_compact_channel_abi_t *)0)->smoothing[0]);
    if(local>=tables) {
        size_t table=(local-tables)/old_table, slot=(local-tables)%old_table;
        if(slot>=new_table)return SIZE_MAX;
#ifdef CONFIG_YORADIO_QEMU_AAC_SMOOTHING_HISTORY_TEST
        if(slot==AAC_SMOOTHING_PERSISTENT_ROWS*sizeof(int32_t *))return SIZE_MAX;
#endif
        local=offsetof(aac_sbr_compact_channel_abi_t,smoothing)+table*new_table+slot;
    }
#ifdef CONFIG_YORADIO_QEMU_AAC_SMOOTHING_HISTORY_TEST
    else if(local>=offsetof(aac_sbr_channel_abi_t,frame.gain_mantissa)) {
        const size_t old_matrix=sizeof(((aac_sbr_frame_abi_t *)0)->gain_mantissa);
        const size_t new_matrix=sizeof(((aac_high_frame_t *)0)->gain_mantissa);
        size_t position=local-offsetof(aac_sbr_channel_abi_t,frame.gain_mantissa);
        size_t matrix=position/old_matrix, inside=position%old_matrix;
        if(inside>=new_matrix)return SIZE_MAX;
        local=offsetof(aac_high_channel_t,frame.gain_mantissa)+matrix*new_matrix+inside;
    }
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
    else if(local>=offsetof(aac_sbr_channel_abi_t,frame.synthesis))
        local-=offsetof(aac_sbr_channel_abi_t,frame.synthesis)-offsetof(aac_high_channel_t,frame.synthesis);
    else if(local==offsetof(aac_sbr_channel_abi_t,frame.high_real))
        local=offsetof(aac_high_channel_t,frame.high_real);
    else if(local>=offsetof(aac_sbr_channel_abi_t,frame.high_imag_history))
        return SIZE_MAX; // Packed history has no wordwise native equivalent.
#endif
    return channel*new_channel+local;
}
static void compare_initial_layout(uint8_t *ref,uint8_t *candidate) {
    for(size_t pos=0;pos<ORIGINAL_SIZE;pos+=4) {
        size_t mapped=map_offset(pos);
        if(mapped==SIZE_MAX)continue;
        uint32_t expected,actual;memcpy(&expected,ref+pos,4);memcpy(&actual,candidate+mapped,4);
        if(expected>=(uintptr_t)ref && expected<(uintptr_t)ref+ORIGINAL_SIZE) {
            size_t target=map_offset(expected-(uintptr_t)ref);assert(target!=SIZE_MAX);
            expected=(uintptr_t)candidate+target;
        }
        if(actual!=expected)ESP_LOGE(TAG,"layout mismatch offset=%x mapped=%x expected=%x actual=%x",(unsigned)pos,(unsigned)mapped,(unsigned)expected,(unsigned)actual);
        assert(actual==expected);
    }
}
void qemu_aac_smoothing_fir_test(void);
void packed_history_arithmetic_tests(void) {
    // Compare every word of the independently patched table layout first.
    // Relocation/shortened-tail correctness is checked by guarded PCM/reset.
    uint8_t *ref=calloc(1,ORIGINAL_SIZE),*candidate=calloc(1,sizeof(aac_sbr_compact_owner_abi_t));
    void *probe=calloc(1,COMPACT_SIZE);assert(probe);
    aac_sbr_control_abi_t *control1=calloc(1,sizeof(*control1)),*control2=calloc(1,sizeof(*control2));
    assert(ref && candidate && control1 && control2);
    ESP_LOGI(TAG,"SBRLAYOUT_ALLOCATOR reference_request=%u candidate_request=%u reference_block=%u candidate_block=%u guard_bytes=0",
             (unsigned)ORIGINAL_SIZE,(unsigned)COMPACT_SIZE,(unsigned)heap_caps_get_allocated_size(ref),(unsigned)heap_caps_get_allocated_size(probe));
    free(probe);
    for(unsigned down=0;down<2;++down) {
        memset(ref,0,ORIGINAL_SIZE);memset(candidate,0,sizeof(aac_sbr_compact_owner_abi_t));
        sbr_open(22050,control1,ref,down);compact5_sbr_open(22050,control2,candidate,down);
        compare_initial_layout(ref,candidate);
        assert(!memcmp(control1,control2,sizeof(*control1)));
        aac_sbr_owner_abi_t *original=(void *)ref;
        aac_sbr_compact_owner_abi_t *compact=(void *)candidate;
        original->ps=&original->embedded_ps;
        compact->ps=&compact->embedded_ps;
        ps_allocate_decoder(ref,32);compact5_ps_allocate_decoder(candidate,32);
        compare_initial_layout(ref,candidate);
    }
    free(ref);free(candidate);free(control1);free(control2);
    ESP_LOGI(TAG,"SBRLAYOUT_INITIALIZERS_PASS channel_rows=5 modes=2 PS=checked");
    qemu_aac_smoothing_fir_test();
#ifdef CONFIG_YORADIO_QEMU_AAC_SMOOTHING_HISTORY_TEST
    void qemu_aac_smoothing_history_test(void);
    qemu_aac_smoothing_history_test();
#endif
    ESP_LOGI(TAG,"SBRLAYOUT_LAYOUT_PASS compact_smoothing_tables=%u channel=%u owner=%u",
             AAC_SBR_ROWS,(unsigned)sizeof(aac_sbr_compact_channel_abi_t),(unsigned)COMPACT_SIZE);
}
void aac_sbr_layout_fail_next(size_t size) {unsigned leg=selected==1;assert(!fail_size[leg]);fail_size[leg]=size;}
void aac_sbr_layout_assert_idle(void) {
    assert(!active && !fail_size[0] && !fail_size[1]);
    for(unsigned i=0;i<4;++i)assert(!owners[i].owner);
    assert(allocations==frees);
}
