#pragma once
#include <stdbool.h>
typedef struct { void *pending; bool allocation_failed; } aac_scratch_reserve_t;
void aac_scratch_reserve_prepare(aac_scratch_reserve_t *);
void aac_scratch_reserve_discard(aac_scratch_reserve_t *);
void aac_scratch_reserve_enter(aac_scratch_reserve_t *);
void aac_scratch_reserve_leave(void);
