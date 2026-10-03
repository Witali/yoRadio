#pragma once
#include <stdbool.h>

// Owned by one native AAC decoder; TLS only scopes a call into the SDK.
typedef struct {
    void *owner;
    bool ps_initialized, inside_sbr, allocation_failed;
} aac_compact_owner_t;

void aac_compact_owner_enter(aac_compact_owner_t *);
void aac_compact_owner_leave(void);
