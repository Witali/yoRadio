/* Exhaustive bijection and independent JPEG progressive-refinement sequences. */
#include "jpeg_coefficients.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(v) do{++checks;if(!(v)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}}while(0)
static uint64_t checks,values,transitions;

static uint16_t packed(int16_t value,uint32_t offset)
{
    /* Read wire bytes independently of machine endianness. */
    uint8_t bytes[2];CHECK(jpeg_coefficients_pack(bytes,&value,2,offset));
    return (uint16_t)(bytes[0]|((uint16_t)bytes[1]<<8));
}

static void exhaustive(void)
{
    /* Test every signed16 value at all64 block positions, with unaligned buffers. */
    for(int32_t value=INT16_MIN;value<=INT16_MAX;++value) {
        int16_t original=(int16_t)value;
        for(unsigned position=0;position<64;++position) {
            uint8_t input[4]={0x51,0,0,0xa7},wire[4]={0x91,0,0,0x42},output[4]={0x37,0,0,0x98};
            memcpy(input+1,&original,2);
            CHECK(jpeg_coefficients_pack(wire+1,input+1,2,position*2));
            CHECK(jpeg_coefficients_unpack(output+1,wire+1,2,position*2));
            CHECK(!memcmp(input+1,output+1,2) && wire[0]==0x91 && wire[3]==0x42 && output[0]==0x37 && output[3]==0x98);
            CHECK(jpeg_coefficients_unpack(wire+1,wire+1,2,position*2) && !memcmp(wire+1,input+1,2));
            ++values;
        }
    }
    CHECK(packed(0,0)==0xffff && packed(0,2)==0xffff);
    CHECK(packed(3,0)==0xfffc && packed(3,2)==0xfffc);
    CHECK(packed(-3,0)==0x0002 && packed(-3,2)==0x7ffc);
    CHECK(packed(INT16_MIN,0)==0x7fff && packed(INT16_MIN,2)==0x7fff);
}

static void refinements(void)
{
    /* DC rounds negative coarse values downward; AC starts toward zero then
     * refines magnitude. Neither valid sequence needs a stored0->1 transition. */
    for(int32_t target=INT16_MIN;target<=INT16_MAX;++target) {
        uint16_t previous_dc=0xffff,previous_ac=0xffff;
        for(int al=14;al>=0;--al) {
            int32_t step=1<<al;
            int32_t dc=(target<0 ? (target-step+1)/step : target/step)*step;
            int32_t ac=(target/step)*step;
            uint16_t next_dc=packed((int16_t)dc,0),next_ac=packed((int16_t)ac,2);
            CHECK((previous_dc&next_dc)==next_dc && (previous_ac&next_ac)==next_ac);
            previous_dc=next_dc;previous_ac=next_ac;++transitions;
        }
    }
}

static void boundaries(void)
{
    /* Whole-block/chunk offsets and in-place decode agree; invalid requests do no writes. */
    int16_t input[128],output[128];uint8_t wire[256],split[256];
    for(unsigned i=0;i<128;++i)input[i]=(int16_t)((int)i*509-32768);
    CHECK(jpeg_coefficients_pack(wire,input,sizeof(input),0));
    for(unsigned i=0;i<sizeof(input);i+=2)CHECK(jpeg_coefficients_pack(split+i,(uint8_t *)input+i,2,i));
    CHECK(!memcmp(wire,split,sizeof(wire)));
    CHECK(jpeg_coefficients_unpack(output,wire,sizeof(wire),0) && !memcmp(output,input,sizeof(input)));
    memset(wire,0x5a,sizeof(wire));memcpy(split,wire,sizeof(wire));
    CHECK(!jpeg_coefficients_pack(wire,input,3,0));
    CHECK(!jpeg_coefficients_pack(wire,input,2,1));
    CHECK(!jpeg_coefficients_pack(wire,input,2,UINT32_MAX-1));
    CHECK(!jpeg_coefficients_pack(wire,NULL,2,0));
    CHECK(!jpeg_coefficients_pack(wire+1,wire,2,0));
    CHECK(!jpeg_coefficients_pack(wire,(void *)UINTPTR_MAX,2,0));
    CHECK(!memcmp(wire,split,sizeof(wire)));
    CHECK(jpeg_coefficients_pack(NULL,NULL,0,0));
    CHECK(jpeg_coefficients_unpack(NULL,NULL,0,0));
}

int main(void)
{
    /* No codec/model linkage: these invariants independently constrain the representation. */
    exhaustive();refinements();boundaries();
    printf("{\"passed\":true,\"checks\":%llu,\"value_positions\":%llu,\"refinement_steps\":%llu}\n",
           (unsigned long long)checks,(unsigned long long)values,(unsigned long long)transitions);
    return 0;
}
