#pragma once
#include <stdbool.h>
#include <stddef.h>

// The pending allocation belongs to the adapter until the SDK takes it.
// After transfer the SDK's ordinary free path owns the same unchanged pointer.
typedef struct { void *pending; bool allocation_failed; } aac_sbr_reserve_t;
void aac_sbr_reserve_prepare(aac_sbr_reserve_t *reserve);
void aac_sbr_reserve_discard(aac_sbr_reserve_t *reserve);
void aac_sbr_reserve_enter(aac_sbr_reserve_t *reserve);
void aac_sbr_reserve_leave(void);
