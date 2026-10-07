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

#define ORIGINAL_SIZE sizeof(aac_sbr_owner_abi_t)
#define COMPACT_SIZE sizeof(aac_sbr_compact_owner_abi_t)
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
    return __real_ps_read_data(ps,bits,count);
}
void __wrap_PVMP4AudioDecoderResetBuffer(void *core) {
    void *owner=((aac_core_abi_t *)core)->sbr;
    owner_t *o=find(owner);
    // This API has additional fixed offsets and a pre-existing out-of-core
    // write. It must never run against the experimental layout. The radio
    // adapter resets by destroying/reopening the decoder instead.
    assert(selected!=1 && (!o || o->variant!=1));
    __real_PVMP4AudioDecoderResetBuffer(core);
}
void packed_history_reset(unsigned run) {
    (void)run;
    for(unsigned i=0;i<4;++i)assert(!owners[i].owner);
    selected=calls=allocations=frees=ps_reads=0;
    memset(requested,0,sizeof(requested));memset(physical,0,sizeof(physical));
}
void packed_history_select(unsigned variant) {assert(variant==0||variant==1||variant==7);selected=variant;}
void packed_history_report(const char *name,unsigned variant,unsigned run,uint32_t *rows,uint32_t *changed,unsigned *shift) {
    unsigned modes=0;
    for(unsigned i=0;i<4;++i)if(owners[i].owner)check(owners+i);
    for(unsigned i=0;i<4;++i)if(owners[i].owner && owners[i].variant==1)modes|=owners[i].ps;
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
        return offset-(ORIGINAL_SIZE-COMPACT_SIZE);
    size_t channel=offset/old_channel, local=offset%old_channel;
    const size_t tables=offsetof(aac_sbr_channel_abi_t,smoothing);
    const size_t old_table=sizeof(((aac_sbr_channel_abi_t *)0)->smoothing[0]);
    const size_t new_table=sizeof(((aac_sbr_compact_channel_abi_t *)0)->smoothing[0]);
    if(local>=tables) {
        size_t table=(local-tables)/old_table, slot=(local-tables)%old_table;
        if(slot>=new_table)return SIZE_MAX;
        local=offsetof(aac_sbr_compact_channel_abi_t,smoothing)+table*new_table+slot;
    }
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
    uint8_t *ref=calloc(1,ORIGINAL_SIZE),*candidate=calloc(1,COMPACT_SIZE);
    aac_sbr_control_abi_t *control1=calloc(1,sizeof(*control1)),*control2=calloc(1,sizeof(*control2));
    assert(ref && candidate && control1 && control2);
    ESP_LOGI(TAG,"SBRLAYOUT_ALLOCATOR reference_request=%u candidate_request=%u reference_block=%u candidate_block=%u guard_bytes=0",
             (unsigned)ORIGINAL_SIZE,(unsigned)COMPACT_SIZE,(unsigned)heap_caps_get_allocated_size(ref),(unsigned)heap_caps_get_allocated_size(candidate));
    for(unsigned down=0;down<2;++down) {
        memset(ref,0,ORIGINAL_SIZE);memset(candidate,0,COMPACT_SIZE);
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
    ESP_LOGI(TAG,"SBRLAYOUT_LAYOUT_PASS compact_smoothing_tables=%u channel=%u owner=%u",
             AAC_SBR_ROWS,(unsigned)sizeof(aac_sbr_compact_channel_abi_t),(unsigned)COMPACT_SIZE);
}
void aac_sbr_layout_fail_next(size_t size) {unsigned leg=selected==1;assert(!fail_size[leg]);fail_size[leg]=size;}
void aac_sbr_layout_assert_idle(void) {
    assert(!active && !fail_size[0] && !fail_size[1]);
    for(unsigned i=0;i<4;++i)assert(!owners[i].owner);
    assert(allocations==frees);
}
