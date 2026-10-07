// SPDX-License-Identifier: MIT
// Trace model only: physical flash tags, no prefetch, timing or writeback.
#ifndef YORADIO_CACHE_MODEL_H
#define YORADIO_CACHE_MODEL_H
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

enum { CACHE_LINE = 32, CACHE_SETS = 64, CACHE_WAYS = 8 };
typedef struct { uint32_t tag; uint64_t age; bool valid; } cache_line_t;
typedef struct {
    cache_line_t lines[CACHE_SETS][CACHE_WAYS];
    uint64_t clock;
    bool fifo;
} cache_model_t;
typedef struct { uint64_t accesses[2], misses[2], evictions; } cache_stats_t;

static inline void cache_clear(cache_model_t *cache) {
    bool fifo = cache->fifo;
    memset(cache, 0, sizeof(*cache));
    cache->fifo = fifo;
}

static inline void cache_access(cache_model_t *cache, cache_stats_t *stats,
                                uint32_t address, unsigned size, bool data) {
    uint32_t first = address / CACHE_LINE;
    uint32_t last = (address + size - 1) / CACHE_LINE;
    for (uint32_t block = first; block <= last; ++block) {
        cache_line_t *set = cache->lines[block % CACHE_SETS];
        unsigned victim = 0;
        bool hit = false;
        ++cache->clock;
        if (stats) ++stats->accesses[data];
        for (unsigned way = 0; way < CACHE_WAYS; ++way) {
            if (set[way].valid && set[way].tag == block) {
                if (!cache->fifo) set[way].age = cache->clock;
                hit = true;
                break;
            }
            if (set[way].age < set[victim].age) victim = way;
        }
        if (hit) continue;
        if (stats) {
            ++stats->misses[data];
            stats->evictions += set[victim].valid;
        }
        set[victim] = (cache_line_t){.tag = block, .age = cache->clock, .valid = true};
    }
}

// The C3 has one 128-entry MMU shared by the IROM and DROM aliases.
static inline bool flash_offset(uint64_t virtual_address, const uint32_t mmu[128],
                                uint32_t *physical) {
    uint32_t offset;
    if (virtual_address >= 0x42000000 && virtual_address < 0x42800000)
        offset = virtual_address - 0x42000000;
    else if (virtual_address >= 0x3c000000 && virtual_address < 0x3c800000)
        offset = virtual_address - 0x3c000000;
    else return false;
    uint32_t entry = mmu[offset >> 16];
    if (entry & 0x100) return false;
    *physical = ((entry & 0xff) << 16) | (offset & 0xffff);
    return true;
}
#endif
