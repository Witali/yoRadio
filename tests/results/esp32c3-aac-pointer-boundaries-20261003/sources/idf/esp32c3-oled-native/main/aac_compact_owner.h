#pragma once
#include <stdbool.h>
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
#include "aac_high_history.h"
#endif

// Owned by one native AAC decoder; TLS only scopes a call into the SDK.
typedef struct {
    void *owner;
    bool ps_initialized, inside_sbr, allocation_failed;
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
    aac_high_runtime_t high_history;
#endif
} aac_compact_owner_t;

void aac_compact_owner_enter(aac_compact_owner_t *);
void aac_compact_owner_leave(void);
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY
aac_high_runtime_t *aac_compact_owner_high_context(void);
#endif
