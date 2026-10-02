#include <stdio.h>
#include "packed_complex_storage_check.h"
int main(void) {
    enum { RANDOM_PAIRS=1000000 };
    pc_storage_check(RANDOM_PAIRS);
    unsigned boundary_cases=0;
    for(unsigned bits=16;bits<=17;++bits)for(unsigned shift=(bits==16);shift<=32-bits;++shift) {
        int64_t mantissa_limit=INT64_C(1)<<(bits-1);
        for(int64_t mantissa=-mantissa_limit;mantissa<mantissa_limit;mantissa+=127) {
            int64_t center=mantissa*(INT64_C(1)<<shift);
            for(int delta=-1;delta<=1;++delta) {
                int64_t value=center+delta;
                if(value>=INT32_MIN && value<=INT32_MAX){pc_storage_check_pair((int32_t)value,53);++boundary_cases;}
            }
        }
    }
    printf("STORAGE_ARITHMETIC_PASS random_pairs=%u boundary_pairs=%u formats=4 metadata_neighbors=pass tails=pass\n",
           RANDOM_PAIRS,boundary_cases);
}
