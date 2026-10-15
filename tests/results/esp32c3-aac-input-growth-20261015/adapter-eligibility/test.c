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
void *__real_media_lib_module_calloc(const char *,size_t,size_t);
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
static bool skip_prepare;
void aac_compact_owner_test_skip_prepare(bool skip) {
    assert(!context());skip_prepare=skip;
}
#endif
void aac_compact_owner_prepare(aac_compact_owner_t *state) {
    assert(state && !state->owner && !state->pending_owner && !context());
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(skip_prepare)return;
#endif
    // Reserve the actual configured compact layout, before core/PCM split
    // the heap. An unsuccessful reservation must not prohibit AAC-LC.
    state->pending_owner = calloc(1, sizeof(owner_t));
}
void aac_compact_owner_discard_pending(aac_compact_owner_t *state) {
    assert(state && !context());
    free(state->pending_owner);
    state->pending_owner = NULL;
}
#endif
void *__wrap_media_lib_module_calloc(const char *module,size_t n,size_t size) {
    aac_compact_owner_t *state=context();
    bool owner_request=state && n==1 && size==sizeof(aac_sbr_owner_abi_t);
    void *p;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(state && n==1 && size==fail_request) { fail_request=0;p=NULL; }
    else
#endif
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
    if(owner_request && state->pending_owner) {
        p=state->pending_owner;state->pending_owner=NULL;
    } else
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
