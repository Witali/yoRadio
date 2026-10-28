#include "jpeg_coefficients.h"
#include <string.h>

static bool valid(const void *output,const void *input,size_t bytes,uint32_t offset)
{
    /* Validate before the first store, including overlapping/wrapped buffers. */
    if((bytes|offset)&1u || bytes>UINT32_MAX-offset)return false;
    if(!bytes)return true;
    uintptr_t out=(uintptr_t)output,in=(uintptr_t)input;
    if(!output || !input || bytes-1>UINTPTR_MAX-out || bytes-1>UINTPTR_MAX-in)return false;
    return out==in || (out>in ? out-in>=bytes : in-out>=bytes);
}

static bool transform(void *output,const void *input,size_t bytes,uint32_t offset,bool packing)
{
    /* Work a single coefficient at a time; memcpy accepts unaligned native words.
     * DC and AC have different refinement rules for negative coefficients.
     * Treating negative DC as magnitude would reintroduce erase operations. */
    if(!valid(output,input,bytes,offset))return false;
    uint8_t *out=output;const uint8_t *in=input;unsigned phase=offset%128u;
    for(size_t i=0;i<bytes;i+=2,phase=(phase+2u)%128u) {
        if(packing) {
            int16_t value;memcpy(&value,in+i,sizeof(value));
            uint16_t word=(uint16_t)value;
            if(phase && value<0)word=(uint16_t)(0x8000u|((uint32_t)(-(int32_t)value)&0x7fffu));
            word=(uint16_t)~word;out[i]=(uint8_t)word;out[i+1]=(uint8_t)(word>>8);
        } else {
            uint16_t word=(uint16_t)~((uint16_t)in[i]|((uint16_t)in[i+1]<<8));
            int32_t value=word;
            if(word&0x8000u) {
                if(!phase)value-=65536;
                else value=(word&0x7fffu) ? -(int32_t)(word&0x7fffu) : INT16_MIN;
            }
            int16_t native=(int16_t)value;memcpy(out+i,&native,sizeof(native));
        }
    }
    return true;
}

bool jpeg_coefficients_pack(void *output,const void *input,size_t bytes,uint32_t offset)
{
    /* Preserve coefficient bits while choosing a NOR-friendly storage encoding. */
    return transform(output,input,bytes,offset,true);
}

bool jpeg_coefficients_unpack(void *output,const void *input,size_t bytes,uint32_t offset)
{
    /* Restore exact native JCOEF values, without clipping or approximation. */
    return transform(output,input,bytes,offset,false);
}
