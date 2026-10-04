// Independent int64 arithmetic oracle and hostile metadata-neighbor patterns.
#include "packed_complex_storage.h"
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

static uint32_t random_state=0x591362ab;
static uint32_t random_word(void) {
    random_state^=random_state<<13;random_state^=random_state>>17;
    random_state^=random_state<<5;return random_state;
}
static int64_t rounded(int32_t v,unsigned shift) {
    int64_t magnitude=v<0?-(int64_t)v:v,scale=INT64_C(1)<<shift;
    int64_t result=(magnitude+scale/2)/scale;
    return v<0?-result:result;
}
static void pair(int32_t real,int32_t imag) {
    unsigned shift=0;
    int64_t r=real,i=imag;
    while(shift<13 && (r>262143 || r< -262144 || i>262143 || i< -262144)) {
        ++shift;r=rounded(real,shift);i=rounded(imag,shift);
    }
    unsigned clip=(r>262143)+(i>262143);
    if(r>262143)r=262143;if(i>262143)i=262143;
    unsigned metadata,saturated;
    uint32_t word=pc_storage_pack(PC_STORAGE_SHARED19_THREE,real,imag,&metadata,&saturated);
    int32_t out_r,out_i;
    pc_storage_unpack(PC_STORAGE_SHARED19_THREE,word,metadata,&out_r,&out_i);
    assert((metadata&15)==shift && saturated==clip && metadata<1024);
    assert(out_r==r*(INT64_C(1)<<shift) && out_i==i*(INT64_C(1)<<shift));
    assert(pc_storage_max_shift(PC_STORAGE_SHARED19_THREE,metadata)==shift);
    uint32_t repeated;unsigned repeated_meta,repeated_clip;
    repeated=pc19_pack(out_r,out_i,&repeated_meta,&repeated_clip);
    int32_t again_r,again_i;pc19_unpack(repeated,repeated_meta,&again_r,&again_i);
    // Rounded values may fit a smaller exponent on repack (e.g. -524289
    // rounds to -524288). The restored value, not its encoding, is invariant.
    assert(!repeated_clip && again_r==out_r && again_i==out_i);
}
static void metadata_neighbors(void) {
    enum { COUNT=17, WORDS=6 };
    assert(pc_storage_metadata_words(PC_STORAGE_SHARED19_THREE,COUNT)==WORDS);
    for(unsigned index=0;index<COUNT;++index)for(unsigned value=0;value<1024;++value) {
        uint32_t guarded[WORDS+2],before[WORDS];
        guarded[0]=0x1b57d908;guarded[WORDS+1]=0xa56833f1;
        for(unsigned j=0;j<WORDS;++j)before[j]=guarded[j+1]=random_word();
        pc_storage_store_metadata(PC_STORAGE_SHARED19_THREE,guarded+1,index,value);
        assert(pc_storage_load_metadata(PC_STORAGE_SHARED19_THREE,guarded+1,index)==value);
        assert(guarded[0]==0x1b57d908 && guarded[WORDS+1]==0xa56833f1);
        for(unsigned j=0;j<COUNT;++j)if(j!=index)
            assert(pc_storage_load_metadata(PC_STORAGE_SHARED19_THREE,guarded+1,j)==
                   pc_storage_load_metadata(PC_STORAGE_SHARED19_THREE,before,j));
        for(unsigned j=0;j<WORDS;++j)assert((guarded[j+1]&0xc0000000)==(before[j]&0xc0000000));
    }
    assert(pc_storage_bytes(PC_STORAGE_SHARED19_THREE,288)==1536);
    assert(pc_storage_bytes(PC_STORAGE_SHARED18_FOUR,288)==1440);
}
static void split_metadata_neighbors(void) {
    enum { COUNT=33, MAIN_WORDS=9, EXTRA_WORDS=3 };
    for(unsigned index=0;index<COUNT;++index)for(unsigned value=0;value<1024;++value) {
        uint32_t main[MAIN_WORDS+2],extra[EXTRA_WORDS+2];
        unsigned before[COUNT];
        for(unsigned j=0;j<MAIN_WORDS+2;++j)main[j]=random_word();
        for(unsigned j=0;j<EXTRA_WORDS+2;++j)extra[j]=random_word();
        uint32_t guards[]={main[0],main[MAIN_WORDS+1],extra[0],extra[EXTRA_WORDS+1]};
        for(unsigned j=0;j<COUNT;++j)before[j]=pc19_split_metadata_load(main+1,extra+1,j);
        pc19_split_metadata_store(main+1,extra+1,index,value);
        for(unsigned j=0;j<COUNT;++j)
            assert(pc19_split_metadata_load(main+1,extra+1,j)==(j==index?value:before[j]));
        assert(main[0]==guards[0] && main[MAIN_WORDS+1]==guards[1]);
        assert(extra[0]==guards[2] && extra[EXTRA_WORDS+1]==guards[3]);
    }
}
int main(void) {
    static const int32_t extremes[]={INT32_MIN,INT32_MIN+1,-1073741824,-262145,-262144,-262143,
        -65536,-1,0,1,65535,262142,262143,262144,1073741824,INT32_MAX-1,INT32_MAX};
    for(unsigned i=0;i<sizeof(extremes)/sizeof(extremes[0]);++i)
        for(unsigned j=0;j<sizeof(extremes)/sizeof(extremes[0]);++j)pair(extremes[i],extremes[j]);
    // Every signed 19-bit integer must survive exactly at shift zero.
    for(int32_t v=-262144;v<=262143;++v) {
        unsigned metadata,saturated;uint32_t word=pc19_pack(v,-v-1,&metadata,&saturated);
        int32_t r,i;pc19_unpack(word,metadata,&r,&i);
        assert(!(metadata&15) && !saturated && r==v && i==-v-1);
    }
    unsigned boundary=0;
    for(unsigned shift=0;shift<=13;++shift) {
        int64_t scale=INT64_C(1)<<shift;
        for(int64_t mantissa=-262145;mantissa<=262144;mantissa+=127)
            for(int delta=-2;delta<=2;++delta) {
                int64_t value=mantissa*scale+(shift?scale/2:0)+delta;
                if(value>=INT32_MIN && value<=INT32_MAX) {pair(value,-17);++boundary;}
            }
    }
    for(unsigned n=0;n<1000000;++n) {
        uint32_t r=random_word(),i=random_word();
        // Convert portably instead of relying on out-of-range unsigned casts.
        pair((int64_t)r-(r>INT32_MAX?INT64_C(1)<<32:0),
             (int64_t)i-(i>INT32_MAX?INT64_C(1)<<32:0));
    }
    metadata_neighbors();split_metadata_neighbors();
    printf("STORAGE19_ARITHMETIC_PASS exact_pairs=524288 random_pairs=1000000 boundary_pairs=%u neighbors=17408 split_neighbors=33792 history_bytes=1536\n",boundary);
}
