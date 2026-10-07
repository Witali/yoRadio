#include <stdio.h>
#include "packed_complex_storage_check.h"
int main(void) {
    enum { RANDOM_PAIRS=1000000 };
    pc_storage_check(RANDOM_PAIRS);
    unsigned boundary_cases=0;
    for(unsigned bits=16;bits<=18;++bits)for(unsigned shift=(bits==16);shift<=32-bits;++shift) {
        int64_t mantissa_limit=INT64_C(1)<<(bits-1);
        for(int64_t mantissa=-mantissa_limit;mantissa<mantissa_limit;mantissa+=127) {
            int64_t center=mantissa*(INT64_C(1)<<shift);
            for(int delta=-1;delta<=1;++delta) {
                int64_t value=center+delta;
                if(value>=INT32_MIN && value<=INT32_MAX){pc_storage_check_pair((int32_t)value,53);++boundary_cases;}
            }
        }
    }
    // Cover every signed 18-bit mantissa and all high-bit/sign combinations.
    unsigned exact18=0;
    for(int32_t value=PC18_MANTISSA_MIN;value<=PC18_MANTISSA_MAX;++value) {
        unsigned metadata,clipped;
        uint32_t word=pc18_pack(value,-value-1,&metadata,&clipped);
        int32_t real,imag;pc18_unpack(word,metadata,&real,&imag);
        assert(!(metadata&PC_EXPONENT_MASK) && !clipped);
        assert(real==value && imag==-value-1);++exact18;
    }
    unsigned metadata,clipped;
    assert(pc18_pack(0x12345,-0x12345,&metadata,&clipped)==UINT32_C(0xdcbb2345));
    assert(metadata==0x90 && !clipped); // Re high=01, Im high=10, shift=0.
    printf("STORAGE_18BIT_EXACT_PASS pairs=%u golden_word=dcbb2345 golden_metadata=90\n",exact18);
    printf("STORAGE_ARITHMETIC_PASS random_pairs=%u boundary_pairs=%u formats=5 metadata_neighbors=pass tails=pass\n",
           RANDOM_PAIRS,boundary_cases);
}
