#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
#include <stdint.h>
enum { ARENA_MALLOC, ARENA_FREE, ARENA_REALLOC, ARENA_SNAPSHOT, ARENA_OPERATIONS };
typedef struct { uint32_t calls, max_us; } decoder_arena_timing_t;
#endif

typedef struct {
    size_t capacity, live, peak, blocks, free_bytes, largest;
    unsigned failures;
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
    decoder_arena_timing_t timing[ARENA_OPERATIONS];
#endif
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
