#pragma once
#include <stdint.h>
#include <stdbool.h>

/* Independent literal reference uses 64-bit division/remainder, explicitly
 * reconstructs every interpolation point and packs chronological bits. */
static inline void rc_feedback_reference_frame(rc_pdm_feedback_t *p, int16_t pcm,
        uint32_t *out, unsigned bits, unsigned shift, unsigned gain,
        unsigned dither, int interpolate) {
    const int64_t full=INT64_C(1)<<29, bound=INT64_C(1)<<30;
    int64_t state=p->rc, error=p->error;
    const int64_t previous=p->previous, current=((int64_t)pcm+32768)*8192;
    const int64_t divisor=INT64_C(1)<<shift, step=full/divisor;
    const int64_t gain_divisor=INT64_C(1)<<gain;
    uint32_t word=0;unsigned pos=0;
    for(unsigned bit=0;bit<bits;++bit) {
        const int64_t desired=interpolate?previous+(current-previous)*(bit+1)/bits:current;
        int64_t noise=0;
        if(dither) {
            uint64_t r=p->random;
            r=(r^(r<<13))&UINT32_MAX;r^=r>>17;r=(r^(r<<5))&UINT32_MAX;
            p->random=(uint32_t)r;
            if(dither==1) noise=(int64_t)(r/(UINT64_C(1)<<(shift+3)))-step/2;
            else noise=((int64_t)(r%65536)+(int64_t)(r/65536)-65535)*
                       (INT64_C(1)<<(dither==3?13-shift:12-shift));
        }
        const int64_t down=state-state/divisor,up=down+step;
        const int64_t feedback=error/gain_divisor-((error<0&&error%gain_divisor)?1:0);
        const bool high=desired+feedback+noise>down+(up-down)/2;
        state=high?up:down;
        error+=desired-state;
        if(error>bound)error=bound;if(error< -bound)error= -bound;
        word=(word<<1)|(unsigned)high;
        if((bit+1)%32==0||bit+1==bits){out[pos++]=word;word=0;}
    }
    p->rc=(int32_t)state;p->error=(int32_t)error;p->previous=(int32_t)current;
}
static inline uint32_t rc_feedback_reference_sample(rc_pdm_feedback_t *p,int16_t pcm) {
    uint32_t word;rc_feedback_reference_frame(p,pcm,&word,32,4,0,2,1);return word;
}
