#include "sdkconfig.h"
#include "aac_profile.h"
#include "aac_sbr_abi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>

#if defined(CONFIG_YORADIO_AAC_COMPACT_SBR)
#include "aac_compact_owner.h"
#elif defined(CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE)
#include "aac_scratch_reserve.h"
#elif defined(CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE)
#include "aac_sbr_reserve.h"
#endif

enum { AAC_PROFILE_TLS_SLOT=1 };
_Static_assert(CONFIG_FREERTOS_THREAD_LOCAL_STORAGE_POINTERS>AAC_PROFILE_TLS_SLOT,
               "Use the existing AAC TLS slot; do not overwrite pthread state");

// The mutually exclusive build variants already scope their state in slot 1.
// Reuse that state instead of allocating another TLS slot or global registry.
static aac_profile_state_t *current_profile(void) {
    void *state=pvTaskGetThreadLocalStoragePointer(NULL,AAC_PROFILE_TLS_SLOT);
    if(!state)return NULL;
#if defined(CONFIG_YORADIO_AAC_COMPACT_SBR)
    return &((aac_compact_owner_t *)state)->profile;
#elif defined(CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE)
    return &((aac_scratch_reserve_t *)state)->profile;
#elif defined(CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE)
    return &((aac_sbr_reserve_t *)state)->profile;
#else
    return state;
#endif
}
void aac_profile_enter(aac_profile_state_t *state) {
    assert(state && !pvTaskGetThreadLocalStoragePointer(NULL,AAC_PROFILE_TLS_SLOT));
    vTaskSetThreadLocalStoragePointer(NULL,AAC_PROFILE_TLS_SLOT,state);
}
void aac_profile_leave(void) {
    assert(pvTaskGetThreadLocalStoragePointer(NULL,AAC_PROFILE_TLS_SLOT));
    vTaskSetThreadLocalStoragePointer(NULL,AAC_PROFILE_TLS_SLOT,NULL);
}
void aac_profile_observe(const void *opaque,int result) {
    aac_profile_state_t *profile=current_profile();if(!profile)return;
    *profile=AAC_PROFILE_UNKNOWN;
    if(result || !opaque)return;
    const aac_core_abi_t *core=opaque;
    *profile=core->plus_enabled && core->sbr_present ?
        (core->ps_present ? AAC_PROFILE_PS : AAC_PROFILE_SBR) : AAC_PROFILE_BASE;
    unsigned channels=*profile==AAC_PROFILE_PS ? 2 : core->encoded_channels;
    if(channels==1 || channels==2)
        *profile |= channels << AAC_PROFILE_CHANNEL_SHIFT;
}

#if !defined(CONFIG_YORADIO_AAC_COMPACT_SBR) && !defined(CONFIG_YORADIO_QEMU_AAC_SMOOTHING_TEST)
int __real_PVMP4AudioDecodeFrame(void *,void *);
int __wrap_PVMP4AudioDecodeFrame(void *external,void *core) {
    int result=__real_PVMP4AudioDecodeFrame(external,core);
    aac_profile_observe(core,result);return result;
}
#endif
