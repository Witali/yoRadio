#pragma once
// Test-only oracle: signed wide-integer division, independent of the bit packer.
#include "packed_complex_storage.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>

static int64_t pc_check_round(int32_t value, unsigned shift) {
    int64_t scale=INT64_C(1)<<shift, magnitude=value<0 ? -(int64_t)value : value;
    int64_t result=(magnitude+scale/2)/scale;
    return value<0 ? -result : result;
}
static unsigned pc_check_shift(int32_t real,int32_t imag,unsigned bits,unsigned minimum) {
    int64_t limit=INT64_C(1)<<(bits-1);
    unsigned shift=minimum,maximum=32-bits;
    while(shift<maximum && (pc_check_round(real,shift)>=limit || pc_check_round(imag,shift)>=limit ||
                            pc_check_round(real,shift)<-limit || pc_check_round(imag,shift)<-limit))++shift;
    return shift;
}
static int32_t pc_check_value(int32_t value,unsigned shift,unsigned bits,unsigned *clipped) {
    int64_t rounded=pc_check_round(value,shift),limit=INT64_C(1)<<(bits-1);
    if(rounded>=limit){rounded=limit-1;++*clipped;}
    assert(rounded>=-limit);
    return (int32_t)(rounded*(INT64_C(1)<<shift));
}
static void pc_storage_check_pair(int32_t real,int32_t imag) {
    for(unsigned format=PC_STORAGE_SHARED16;format<=PC_STORAGE_SHARED18_FOUR;++format) {
        unsigned bits=format==PC_STORAGE_SHARED18_FOUR ? 18 : format>=PC_STORAGE_SHARED17_FIVE ? 17 : 16;
        unsigned minimum=bits==16;
        unsigned real_shift=pc_check_shift(real,format==PC_STORAGE_SPLIT16 ? 0 : imag,bits,minimum);
        unsigned imag_shift=format==PC_STORAGE_SPLIT16 ? pc_check_shift(imag,0,bits,minimum) : real_shift;
        unsigned metadata,clipped,expected_clipped=0;
        uint32_t word=pc_storage_pack((pc_storage_format_t)format,real,imag,&metadata,&clipped);
        int32_t r,i;pc_storage_unpack((pc_storage_format_t)format,word,metadata,&r,&i);
        int32_t expected_r=pc_check_value(real,real_shift,bits,&expected_clipped);
        int32_t expected_i=pc_check_value(imag,imag_shift,bits,&expected_clipped);
        if(r!=expected_r || i!=expected_i) {
            printf("storage mismatch format=%u input=%ld,%ld shifts=%u,%u metadata=%u got=%ld,%ld expected=%ld,%ld\n",
                   format,(long)real,(long)imag,real_shift,imag_shift,metadata,(long)r,(long)i,(long)expected_r,(long)expected_i);
            fflush(stdout);
        }
        assert(r==expected_r && i==expected_i);
        assert(clipped==expected_clipped);
        assert(pc_storage_max_shift((pc_storage_format_t)format,metadata)==
               (real_shift>imag_shift ? real_shift : imag_shift));
    }
}
static void pc_storage_check(unsigned random_pairs) {
    uint32_t rng=UINT32_C(0x506361ac);
    for(unsigned n=0;n<random_pairs;++n) {
        rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;int32_t r=(int32_t)rng;
        rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;pc_storage_check_pair(r,(int32_t)rng);
    }
    const int32_t edges[]={INT32_MIN,INT32_MAX,-131073,-131072,-131071,-65537,-65536,-65535,-32769,-32768,-32767,-1,0,1,
                           32767,32768,32769,65535,65536,65537,131071,131072,131073};
    for(unsigned i=0;i<sizeof(edges)/sizeof(edges[0]);++i)
        for(unsigned j=0;j<sizeof(edges)/sizeof(edges[0]);++j)pc_storage_check_pair(edges[i],edges[j]);
    enum { TAIL_PAIRS=23, GUARD=0x13579abc, MAX_METADATA_WORDS=6 };
    for(unsigned f=PC_STORAGE_SHARED16;f<=PC_STORAGE_SHARED18_FOUR;++f) {
        pc_storage_format_t format=(pc_storage_format_t)f;
        uint32_t words[MAX_METADATA_WORDS+2];
        for(unsigned w=0;w<MAX_METADATA_WORDS+2;++w)words[w]=GUARD;
        unsigned expected[TAIL_PAIRS];
        for(unsigned n=0;n<TAIL_PAIRS;++n) {
            expected[n]=pc_storage_load_metadata(format,words+1,n);
        }
        for(unsigned n=0;n<TAIL_PAIRS;++n) {
            expected[n]=(n*7u+3u)&((1u<<pc_storage_entry_bits(format))-1u);
            pc_storage_store_metadata(format,words+1,n,expected[n]);
            for(unsigned k=0;k<TAIL_PAIRS;++k)
                assert(pc_storage_load_metadata(format,words+1,k)==expected[k]);
            assert(words[0]==GUARD && words[pc_storage_metadata_words(format,TAIL_PAIRS)+1]==GUARD);
        }
    }
    assert(pc_storage_bytes(PC_STORAGE_SHARED16,617)==2780);
    assert(pc_storage_bytes(PC_STORAGE_SPLIT16,617)==3088);
    assert(pc_storage_bytes(PC_STORAGE_SHARED17_FIVE,617)==2964);
    assert(pc_storage_bytes(PC_STORAGE_SHARED17_FOUR,617)==3088);
    assert(pc_storage_bytes(PC_STORAGE_SHARED18_FOUR,617)==3088);
}
