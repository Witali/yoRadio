#pragma once
#include "packed_complex16.h"
#include <assert.h>
#include <stdbool.h>

// Four independent streams: main/sub delays and three all-pass links. Every
// complex index must always use the same stream during one cache lifetime.
// Initialize once per decorrelation call; no state survives an owner change.
// Each line caches eight RECONSTRUCTED pairs. Writes go straight to packed
// storage and invalidate the affected entry, never retain pre-rounding values.
typedef struct {
    uint32_t block, valid;
    int32_t real[8], imag[8];
} pc16_cache_line_t;
typedef struct { pc16_cache_line_t lines[4]; } pc16_cache_t;
_Static_assert(sizeof(pc16_cache_t)==288,"Bounded decoded-value cache");

static inline void pc16_cache_init(pc16_cache_t *cache) {
    for(unsigned slot=0;slot<4;++slot) {
        cache->lines[slot].block=UINT32_MAX;
        cache->lines[slot].valid=0;
    }
}

// True means a cache hit. Fill only the existing tail; no padded input needed.
static inline bool pc16_cache_load(pc16_cache_t *cache,unsigned slot,
                                  const uint32_t *mantissas,const uint32_t *exponents,
                                  size_t count,size_t n,int32_t *real,int32_t *imag) {
    assert(slot<4 && n<count);
    pc16_cache_line_t *line=&cache->lines[slot];
    unsigned lane=n&7u;uint32_t block=n/8u;
    bool hit=line->block==block && (line->valid&(1u<<lane));
    if(!hit) {
        size_t begin=n&~(size_t)7u;
        unsigned length=count-begin<8?count-begin:8;
        uint32_t word=exponents[block];
        for(unsigned k=0;k<length;++k) {
            pc16_unpack(mantissas[begin+k],word,&line->real[k],&line->imag[k]);
            word>>=4;
        }
        line->block=block;line->valid=(1u<<length)-1;
    }
    *real=line->real[lane];*imag=line->imag[lane];
    return hit;
}

// Call after every packed write, using the same stream as reads of that index.
static inline void pc16_cache_invalidate(pc16_cache_t *cache,unsigned slot,size_t n) {
    assert(slot<4);
    pc16_cache_line_t *line=&cache->lines[slot];
    if(line->block==n/8u)line->valid&=~(1u<<(n&7u));
}
