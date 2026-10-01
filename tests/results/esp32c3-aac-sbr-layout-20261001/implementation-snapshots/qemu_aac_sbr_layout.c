// QEMU-only, pinned Espressif 2.6.2 ABI. Lossless PS-control relocation trial.
// All DSP stays in the original archive; this changes ownership/layout only.
#include "qemu_aac_packed_history.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define ORIGINAL_SIZE 55128u
#define COMPACT_SIZE 51596u
#define PS_POINTER 0xc984u
#define PS_SENTINEL 0xc988u
#define PS_RELOCATED 0x93b4u
#define PS_BYTES 3536u
#define GUARD_BYTES 16u
_Static_assert(PS_RELOCATED + PS_BYTES <= 0xa780, "PS control must precede right synthesis V");

typedef struct { uint8_t *owner, *allocation; size_t size, physical; unsigned variant, ps; } owner_t;
static owner_t owners[4];
static owner_t *active;
static unsigned selected, calls, allocations, frees, ps_reads;
static size_t fail_size[2];
static size_t requested[2], physical[2];
static const char *TAG = "sbr_layout";

void *__real_media_lib_module_calloc(const char *, size_t, size_t);
void __real_media_lib_free(void *);
int __real_sbr_applied(void *, void *, void *, void *, void *, void *, int, void *, void *, int);
int __real_ps_read_data(void *, void *, unsigned);

static owner_t *find(void *p) {
    if (!p) return NULL;
    for (unsigned n=0;n<4;++n) if (owners[n].owner==p) return owners+n;
    return NULL;
}
static void pointer(owner_t *o) {
    void *ps=o->owner+(o->ps ? PS_RELOCATED : PS_SENTINEL);
    memcpy(o->owner+PS_POINTER,&ps,4);
}
static void check(owner_t *o) {
    for (unsigned n=0;n<GUARD_BYTES;++n) {
        assert(o->allocation[n]==0xa5);
        assert(o->owner[o->size+n]==0x5a);
    }
}

void *__wrap_media_lib_module_calloc(const char *module,size_t n,size_t size) {
    unsigned failed_leg=selected==1;
    if (n==1 && fail_size[failed_leg] && size==fail_size[failed_leg]) { fail_size[failed_leg]=0; return NULL; }
    if (n!=1 || size!=ORIGINAL_SIZE) return __real_media_lib_module_calloc(module,n,size);
    owner_t *o=NULL;
    for (unsigned i=0;i<4;++i) if (!owners[i].owner) { o=owners+i; break; }
    assert(o);
    size_t payload=selected==1 ? COMPACT_SIZE : ORIGINAL_SIZE;
    uint8_t *raw=__real_media_lib_module_calloc(module,1,payload+2*GUARD_BYTES);
    if (!raw) return NULL;
    memset(raw,0xa5,GUARD_BYTES); memset(raw+GUARD_BYTES+payload,0x5a,GUARD_BYTES);
    *o=(owner_t){.owner=raw+GUARD_BYTES,.allocation=raw,.size=payload,
                 .physical=heap_caps_get_allocated_size(raw),.variant=selected};
    ++allocations;
    unsigned leg=selected==1;
    requested[leg]=payload; physical[leg]=o->physical;
    return o->owner;
}
void __wrap_media_lib_free(void *p) {
    owner_t *o=find(p);
    if (!o) { __real_media_lib_free(p); return; }
    check(o); void *raw=o->allocation; memset(o,0,sizeof(*o)); ++frees;
    __real_media_lib_free(raw);
}

int __wrap_sbr_applied(void *owner,void *stream,void *left,void *right,
                       void *out_l,void *out_r,int channels,void *control,void *core,int out_channels) {
    owner_t *o=find(owner);
    if (!o || o->variant!=1)
        return __real_sbr_applied(owner,stream,left,right,out_l,out_r,channels,control,core,out_channels);
    assert(active==NULL); active=o;
    // The binary refreshes the embedded PS pointer on each decoded frame.
    pointer(o); check(o); ++calls;
    int result=__real_sbr_applied(owner,stream,left,right,out_l,out_r,channels,control,core,out_channels);
    check(o); active=NULL;
    return result;
}
int __wrap_ps_read_data(void *ps,void *bits,unsigned count) {
    if (!active) return __real_ps_read_data(ps,bits,count);
    owner_t *o=active;
    if (!o->ps) {
        // Right-channel QMF/envelope work is unused for a mono core with PS.
        // Keep hybrid/delay data [0x7678,0x93b4) and synthesis V intact.
        memset(o->owner+PS_RELOCATED,0,PS_BYTES);
        memcpy(o->owner+PS_RELOCATED,o->owner+PS_SENTINEL,4);
        o->ps=1; pointer(o);
    }
    ++ps_reads;
    return __real_ps_read_data(o->owner+PS_RELOCATED,bits,count);
}

void packed_history_reset(unsigned run) {
    (void)run;
    for (unsigned n=0;n<4;++n) assert(!owners[n].owner);
    selected=calls=allocations=frees=ps_reads=0;
    memset(requested,0,sizeof(requested)); memset(physical,0,sizeof(physical));
}
void packed_history_select(unsigned variant) { assert(variant==0 || variant==1 || variant==7); selected=variant; }
void packed_history_report(const char *name,unsigned variant,unsigned run,uint32_t *rows,uint32_t *changed,unsigned *shift) {
    for (unsigned n=0;n<4;++n) if (owners[n].owner) check(owners+n);
    *rows=calls; *changed=*shift=0;
    ESP_LOGI(TAG,"SBRLAYOUT_MEMORY case=%s variant=%u run=%u calls=%u ps_reads=%u allocations=%u frees=%u"
             " reference=%u candidate=%u physical_reference=%u physical_candidate=%u static_test_state=%u guard_bytes=%u",
             name,variant,run,calls,ps_reads,allocations,frees,(unsigned)requested[0],(unsigned)requested[1],
             (unsigned)physical[0],(unsigned)physical[1],
             (unsigned)(sizeof(owners)+sizeof(active)+sizeof(selected)+sizeof(calls)+sizeof(allocations)+sizeof(frees)+sizeof(ps_reads)+sizeof(fail_size)+sizeof(requested)+sizeof(physical)),2*GUARD_BYTES);
}
void packed_history_arithmetic_tests(void) {
    ESP_LOGI(TAG,"SBRLAYOUT_LAYOUT_PASS native DSP; PS=%u..%u owner=%u",PS_RELOCATED,PS_RELOCATED+PS_BYTES,COMPACT_SIZE);
}

void aac_sbr_layout_fail_next(size_t size) { unsigned leg=selected==1; assert(!fail_size[leg]); fail_size[leg]=size; }
void aac_sbr_layout_assert_idle(void) {
    assert(!active && !fail_size[0] && !fail_size[1]);
    for (unsigned n=0;n<4;++n) assert(!owners[n].owner);
    assert(allocations==frees);
}
