#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER 1
#define CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST 1
#define CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT 1
// Only allocator ownership is exercised here; ABI and DSP are not emulated.
typedef struct { char bytes[96]; } aac_sbr_owner_abi_t;
typedef struct { char bytes[32]; } owner_t;
typedef struct { char bytes[16]; } aac_sbr_control_abi_t;
typedef struct { void *owner, *pending_owner; bool ps_initialized, inside_sbr, allocation_failed; } aac_compact_owner_t;
static aac_compact_owner_t *current;
static aac_compact_owner_t *context(void) { return current; }
static size_t fail_request;
static unsigned live_owners, live, calls, fail_alloc, audit_live;
static void *alloc(size_t n,size_t size) {
    ++calls;if(fail_alloc){--fail_alloc;return NULL;}
    void *p=calloc(n,size);assert(p);++live;return p;
}
static void release(void *p) { if(p){assert(live);--live;free(p);} }
static void aac_pointer_audit_allocate(void *p,size_t bytes,aac_compact_owner_t *state) {
    if(p && state){assert(bytes);++audit_live;}
}
static void aac_pointer_audit_free(void *p,aac_compact_owner_t *state) {
    if(p && state){assert(audit_live);--audit_live;}
}
void *__real_media_lib_module_calloc(const char *module,size_t n,size_t size) {
    (void)module;return alloc(n,size);
}
void __real_media_lib_free(void *p) {release(p);}
#define calloc alloc
#define free release
/* PRODUCTION_RESERVE_AND_WRAPPERS */
#undef calloc
#undef free
static void enter(aac_compact_owner_t *s) { assert(!current);current=s;s->allocation_failed=false; }
static void leave(void) { assert(current);current=NULL; }
int main(void) {
    aac_compact_owner_t a={0},b={0};
    aac_compact_owner_prepare(&a);aac_compact_owner_prepare(&b);
    assert(live==2 && !audit_live);
    for(size_t i=0;i<sizeof(owner_t);++i)assert(!((uint8_t*)a.pending_owner)[i]);
    void *pending=a.pending_owner;unsigned before=calls;
    // Without this decoder's TLS scope the pending block cannot be stolen.
    void *p=__wrap_media_lib_module_calloc("other",1,sizeof(aac_sbr_owner_abi_t));
    assert(p!=pending && a.pending_owner==pending);__wrap_media_lib_free(p);
    enter(&b);p=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
    assert(p==b.owner && !b.pending_owner);__wrap_media_lib_free(p);leave();
    enter(&a);p=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
    assert(p==pending && a.owner==p && !a.pending_owner && calls==before+1);
    __wrap_media_lib_free(p);leave();assert(!a.owner && !b.owner && !audit_live && !live_owners);
    aac_compact_owner_discard_pending(&a);aac_compact_owner_discard_pending(&b);assert(!live);
    // LC, cancellation and failed-open cleanup release an unclaimed block.
    aac_compact_owner_prepare(&a);aac_compact_owner_discard_pending(&a);
    aac_compact_owner_discard_pending(&a);assert(!live);
    // Failed reservation permits the normal late-SBR allocation path.
    fail_alloc=1;aac_compact_owner_prepare(&a);assert(!a.pending_owner);
    enter(&a);p=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
    assert(p && !a.allocation_failed);__wrap_media_lib_free(p);leave();
    // Injected SDK owner failure preserves pending ownership for destroy.
    aac_compact_owner_prepare(&a);pending=a.pending_owner;
    enter(&a);fail_request=sizeof(aac_sbr_owner_abi_t);
    p=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
    assert(!p && a.allocation_failed && a.pending_owner==pending && !a.owner);leave();
    aac_compact_owner_discard_pending(&a);
    // Same total bytes with different n/size cannot claim the reserved owner.
    aac_compact_owner_prepare(&a);pending=a.pending_owner;enter(&a);
    p=__wrap_media_lib_module_calloc("AAC",2,sizeof(aac_sbr_owner_abi_t)/2);
    assert(p && a.pending_owner==pending);__wrap_media_lib_free(p);
    fail_alloc=1;p=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_control_abi_t));
    assert(!p && a.allocation_failed);leave();aac_compact_owner_discard_pending(&a);
    assert(!live && !audit_live && !live_owners && !fail_request);
    puts("PASS compact reservation: zeroing, transfer, task isolation, late retry, injected owner/control failures, repeated cleanup; DSP mocked");
}
