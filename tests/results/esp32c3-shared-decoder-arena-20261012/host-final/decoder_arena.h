#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "sdkconfig.h"

typedef struct {
    size_t capacity, live, peak, blocks, free_bytes, largest;
    unsigned failures;
} decoder_arena_stats_t;

#ifdef CONFIG_YORADIO_SHARED_DECODER_ARENA
bool decoder_arena_init(void);
/* Per-task selection; returns the previous selection for nested scopes. */
bool decoder_arena_select(bool selected);
bool decoder_arena_owns(const void *pointer);
decoder_arena_stats_t decoder_arena_stats(void);
#else
static inline bool decoder_arena_init(void) { return true; }
static inline bool decoder_arena_select(bool selected) { (void)selected; return false; }
#endif
