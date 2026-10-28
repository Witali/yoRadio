#ifndef SMALL_TV_PROBE_BACKING_H
#define SMALL_TV_PROBE_BACKING_H
#include "probe_memory.h"
/* Separate logical backing transport from the common hard-capped pool allocator. */
void probe_backing_reset(probe_memory_stats *stats);
void probe_backing_snapshot(probe_memory_stats *stats);
#endif
