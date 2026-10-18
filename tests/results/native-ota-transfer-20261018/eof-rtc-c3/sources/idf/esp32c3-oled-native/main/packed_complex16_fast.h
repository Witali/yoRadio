#pragma once
#include "packed_complex16.h"

// Same nearest/ties-away representation as pc16_pack. Estimate from signed
// magnitude width, then check at most two rounding steps. Start one bit below
// the truncation estimate: negative values just beyond -32768 can round back
// into range, so a floor-based estimate alone can discard a precision bit.
static inline uint32_t pc16_pack_fast(int32_t real,int32_t imag,
                                     unsigned *exponent,unsigned *saturations) {
    uint32_t width=(real<0?~(uint32_t)real:(uint32_t)real) |
                   (imag<0?~(uint32_t)imag:(uint32_t)imag);
    unsigned shift=width<65536u?1u:16u-(unsigned)__builtin_clz(width);
    int32_t r=pc16_round(real,shift),i=pc16_round(imag,shift);
    while(shift<16 && (r>32767 || i>32767 || r< -32768 || i< -32768)) {
        ++shift;r=pc16_round(real,shift);i=pc16_round(imag,shift);
    }
    unsigned clipped=(r>32767)+(i>32767);
    if(r>32767)r=32767;
    if(i>32767)i=32767;
    *exponent=shift-1;
    if(saturations)*saturations=clipped;
    return (((uint32_t)i&0xffffu)<<16)|((uint32_t)r&0xffffu);
}
