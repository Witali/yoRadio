#include "aac_sbr_reserve.h"
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
#include <assert.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Pinned esp_audio_codec 2.6.2 owner size. Reserve before core/PCM allocations
// split the largest available block. This changes placement, not decoder RAM.
#define SBR_BYTES 55128u
#define AAC_TLS_SLOT 1
_Static_assert(CONFIG_FREERTOS_THREAD_LOCAL_STORAGE_POINTERS > AAC_TLS_SLOT,
               "AAC reserve needs TLS slot 1; slot 0 belongs to pthreads");

void aac_sbr_reserve_prepare(aac_sbr_reserve_t *reserve) {
    assert(!reserve->pending);
    reserve->pending=calloc(1,SBR_BYTES);
    reserve->allocation_failed=false;
    // A failed early reservation does not prohibit LC. The actual SBR request
    // retries normally and records an error if full-rate decoding cannot fit.
}
void aac_sbr_reserve_discard(aac_sbr_reserve_t *reserve) {
    free(reserve->pending);reserve->pending=NULL;
}
void aac_sbr_reserve_enter(aac_sbr_reserve_t *reserve) {
    assert(!pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT));
    reserve->allocation_failed=false;
    vTaskSetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT,reserve);
}
void aac_sbr_reserve_leave(void) {
    vTaskSetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT,NULL);
}

void *__real_media_lib_module_calloc(const char *,size_t,size_t);
void *__wrap_media_lib_module_calloc(const char *module,size_t n,size_t size) {
    aac_sbr_reserve_t *reserve=pvTaskGetThreadLocalStoragePointer(NULL,AAC_TLS_SLOT);
    if(reserve && n==1 && size==SBR_BYTES && reserve->pending) {
        void *p=reserve->pending;reserve->pending=NULL;return p;
    }
    void *p=__real_media_lib_module_calloc(module,n,size);
    // Both allocations are required for SBR. Never emit core-only PCM as
    // successful HE playback when the SDK silently disables AAC Plus on OOM.
    if(reserve && !p && n==1 && (size==SBR_BYTES || size==1180))
        reserve->allocation_failed=true;
    return p;
}
#endif
