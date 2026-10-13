#pragma once
#include <stdbool.h>
#include "aac_profile.h"
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
#include "aac_high_history.h"
#endif

// Owned by one native AAC decoder; TLS only scopes a call into the SDK.
typedef struct {
    void *owner;
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
    void *pending_owner; // Unclaimed zeroed storage; never exposed as a live SDK owner.
#endif
    bool ps_initialized, inside_sbr, allocation_failed;
#ifdef YORADIO_AAC_PROFILE_METADATA
    aac_profile_state_t profile;
#endif
#ifdef CONFIG_YORADIO_AAC_LATE_SBR
    void *late_core; // Valid only inside the scoped native frame call.
    bool late_disabled; // Per-decoder unmodified-controller PCM control.
#endif
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
    aac_high_runtime_t high_history;
#endif
} aac_compact_owner_t;

void aac_compact_owner_enter(aac_compact_owner_t *);
void aac_compact_owner_leave(void);
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
void aac_compact_owner_prepare(aac_compact_owner_t *);
void aac_compact_owner_discard_pending(aac_compact_owner_t *);
#endif
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
aac_high_runtime_t *aac_compact_owner_high_context(void);
#ifdef AAC_HIGH_HISTORY_PC19_SIDECAR
unsigned aac_compact_owner_high_channel(const aac_high_frame_t *);
#endif
#endif
