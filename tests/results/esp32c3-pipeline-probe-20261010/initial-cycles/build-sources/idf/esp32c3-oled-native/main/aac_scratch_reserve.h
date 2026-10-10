#pragma once
#include <stdbool.h>
#include "sdkconfig.h"
#include "aac_profile.h"
typedef struct {
    void *pending;
    bool allocation_failed;
#ifdef YORADIO_AAC_PROFILE_METADATA
    aac_profile_state_t profile;
#endif
#ifdef CONFIG_YORADIO_AAC_RELOCATE_PS
    unsigned char *owner;
    bool ps_active, inside_sbr;
#ifdef CONFIG_YORADIO_AAC_PS_PC16
    bool ps_packed;
#endif
#endif
} aac_scratch_reserve_t;
void aac_scratch_reserve_prepare(aac_scratch_reserve_t *);
void aac_scratch_reserve_discard(aac_scratch_reserve_t *);
void aac_scratch_reserve_enter(aac_scratch_reserve_t *);
void aac_scratch_reserve_leave(void);
