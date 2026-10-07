#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
#include "aac_scratch_reserve.h"
#include <assert.h>
#include <stdlib.h>
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
    void *p=__real_media_lib_module_calloc(module,n,size);
    // SBR OOM must be an error, not apparently successful core-only output.
    if(state && !p && n==1 && (size==55128 || size==1180))
        state->allocation_failed=true;
    return p;
}
#endif
