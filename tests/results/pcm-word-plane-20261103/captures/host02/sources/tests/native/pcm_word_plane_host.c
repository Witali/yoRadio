/* Exact storage-contract checks. Word-plane memory is touched only as words;
 * byte packing/comparisons below apply exclusively to normal caller DRAM. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "pcm_word_plane.h"

enum { MAX_SAMPLES=5761, MAX_WORDS=(MAX_SAMPLES+1)/2, GUARDS=4 };
static _Alignas(4) volatile uint32_t storage[MAX_WORDS+GUARDS*2];
static _Alignas(4) uint8_t input[MAX_SAMPLES*2+3], saved[MAX_SAMPLES*2+3];
static _Alignas(4) uint8_t output[MAX_SAMPLES*2+3];
static unsigned groups;
static uint64_t checked_samples;
static uint32_t sentinel(size_t index) {return UINT32_C(0xc5a73e91) ^ (uint32_t)(index*UINT32_C(0x01010101));}
static volatile uint32_t *prepare(size_t samples) {
    assert(samples<=MAX_SAMPLES);
    for(size_t index=0;index<MAX_WORDS+GUARDS*2;++index)storage[index]=sentinel(index);
    volatile uint32_t *plane=storage+GUARDS;pcm_word_plane_clear(plane,(samples+1)/2);
    for(size_t index=0;index<(samples+1)/2;++index)assert(plane[index]==0);
    return plane;
}
static void guards(size_t samples) {
    size_t used=(samples+1)/2;
    for(size_t index=0;index<GUARDS;++index)assert(storage[index]==sentinel(index));
    for(size_t index=GUARDS+used;index<MAX_WORDS+GUARDS*2;++index)assert(storage[index]==sentinel(index));
}
static uint16_t dram_sample(size_t index) {return (uint16_t)((unsigned)input[1+2*index]+256U*input[2+2*index]);}
static void source(size_t samples,unsigned seed) {
    for(size_t index=0;index<sizeof(input);++index)input[index]=(uint8_t)(index*73U+seed*19U);
    for(size_t index=0;index<samples;++index) {
        uint16_t bits=(uint16_t)(index*40503U+seed*7919U);
        if(index%7==0)bits=UINT16_C(0x8000);
        if(index%11==0)bits=UINT16_C(0xffff);
        input[1+2*index]=(uint8_t)bits;input[2+2*index]=(uint8_t)(bits/256U);
    }
    memcpy(saved,input,sizeof(input));
}
static void verify_words(const volatile uint32_t *plane,size_t samples) {
    for(size_t index=0;index<(samples+1)/2;++index) {
        uint32_t expected=dram_sample(index*2);
        if(index*2+1<samples)expected+=UINT32_C(65536)*dram_sample(index*2+1);
        assert(plane[index]==expected);
    }
}
static void fixed_and_exhaustive(void) {
    static const uint16_t pairs[][2]={{0,0xffff},{0x8000,0x7fff},{0x0123,0xabcd},{0xffff,0x8000}};
    static const uint32_t expected[]={UINT32_C(0xffff0000),UINT32_C(0x7fff8000),UINT32_C(0xabcd0123),UINT32_C(0x8000ffff)};
    volatile uint32_t *plane=prepare(2);
    for(size_t index=0;index<sizeof(pairs)/sizeof(pairs[0]);++index) {
        pcm_word_plane_store(plane,0,pairs[index][0]);pcm_word_plane_store(plane,1,pairs[index][1]);
        assert(plane[0]==expected[index]);
        assert(pcm_word_plane_load(plane,0)==pairs[index][0]&&pcm_word_plane_load(plane,1)==pairs[index][1]);
        checked_samples+=2;
    }
    for(uint32_t value=0;value<=UINT16_MAX;++value) {
        uint16_t previous_high=pcm_word_plane_load(plane,1);
        pcm_word_plane_store(plane,0,(uint16_t)value);
        assert(pcm_word_plane_load(plane,0)==value&&pcm_word_plane_load(plane,1)==previous_high);
        assert(plane[0]==value+UINT32_C(65536)*previous_high);
        pcm_word_plane_store(plane,1,(uint16_t)value);
        assert(pcm_word_plane_load(plane,0)==value&&pcm_word_plane_load(plane,1)==value);
        assert(plane[0]==value+UINT32_C(65536)*value);checked_samples+=2;
    }
    guards(2);++groups;
}
static void ordinary_shapes(void) {
    static const size_t counts[]={0,1,2,3,5,7,17,119,120,127,128,129,2047,2048,2049,5759,5760,5761};
    pcm_word_plane_clear(NULL,0); // Empty clear must not access a pointer.
    for(size_t shape=0;shape<sizeof(counts)/sizeof(counts[0]);++shape)for(unsigned seed=0;seed<7;++seed) {
        size_t samples=counts[shape];volatile uint32_t *plane=prepare(samples);source(samples,seed);
        assert(((uintptr_t)(input+1)&3U)==1U&&((uintptr_t)(output+1)&3U)==1U);
        // Reverse odd-first/even-second publication exercises partial RMW and
        // neighbor preservation rather than relying only on inverse helpers.
        for(size_t index=1;index<samples;index+=2)pcm_word_plane_store(plane,index,dram_sample(index));
        for(size_t index=0;index<samples;index+=2)assert(pcm_word_plane_load(plane,index)==0);
        for(size_t index=0;index<samples;index+=2)pcm_word_plane_store(plane,index,dram_sample(index));
        verify_words(plane,samples);
        memset(output,0x6d,sizeof(output));
        for(size_t end=samples;end;--end) {
            size_t index=end-1;uint16_t bits=pcm_word_plane_load(plane,index);
            output[1+2*index]=(uint8_t)bits;output[2+2*index]=(uint8_t)(bits/256U);++checked_samples;
        }
        assert(output[0]==0x6d&&output[1+2*samples]==0x6d);
        assert(!memcmp(output+1,input+1,samples*2)&&!memcmp(saved,input,sizeof(input)));
        guards(samples);
        // Reuse with a fresh clear: every old value and an odd spare lane go
        // to zero before disjoint odd-sized writes restore selected samples.
        pcm_word_plane_clear(plane,(samples+1)/2);
        for(size_t index=0;index<(samples+1)/2;++index)assert(plane[index]==0);
        for(size_t first=1;first<samples;first+=7) {
            size_t count=samples-first;if(count>3)count=3;
            for(size_t index=first;index<first+count;++index)pcm_word_plane_store(plane,index,dram_sample(index));
        }
        for(size_t index=0;index<samples;++index) {
            bool written=index>=1&&(index-1)%7<3;
            assert(pcm_word_plane_load(plane,index)==(written?dram_sample(index):0));++checked_samples;
        }
        if(samples&1U)assert(pcm_word_plane_load(plane,samples)==0);
        assert(!memcmp(saved,input,sizeof(input)));guards(samples);++groups;
    }
}
int main(void) {
    fixed_and_exhaustive();ordinary_shapes();
    printf("{\"passed\":true,\"groups\":%u,\"exhaustive_bit_patterns\":65536,\"checked_samples\":%llu,\"immutable_DRAM\":true,\"word_canaries\":true,\"timer_dependency\":false,\"native_memory_access_qualified\":false}\n",groups,(unsigned long long)checked_samples);
}
