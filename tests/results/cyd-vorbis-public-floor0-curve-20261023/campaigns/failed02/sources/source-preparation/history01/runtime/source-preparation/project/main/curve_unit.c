/* Owned arrays driving the exact public Tremor curve function, never PCM. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "public/misc.h"
#include "data.h"

extern void vorbis_lsp_to_curve(ogg_int32_t *,int,int,ogg_int32_t *,int,
                               ogg_int32_t,ogg_int32_t,ogg_int32_t);
_Static_assert(sizeof(int)==4 && sizeof(long)==4 && sizeof(void*)==4, "Xtensa ILP32");
_Static_assert(sizeof(ogg_int32_t)==4 && sizeof(ogg_int64_t)==8, "Public exact types");
_Static_assert((-1>>1)==-1, "Public signed arithmetic right shift context");
_Static_assert(CURVE_CASES==6 && CURVE_PACKETS==84 && CURVE_CALLS==168, "Full original fixture scope");
#if defined(_LOW_ACCURACY_) || defined(_ARM_ASSEM_) || defined(_V_LSP_MATH_ASM)
#error Only unchanged full-accuracy public C path on Xtensa is permitted
#endif
#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error Public union multiply path requires actual little endian profile
#endif

#define GUARD UINT32_C(0xa7d14c39)
static struct { uint32_t before; ogg_int32_t values[1024]; uint32_t after; } output;
static struct { uint32_t before; ogg_int32_t values[6]; uint32_t after; } angles;

static void require(int ok, const char *reason) {
    if(!ok) { printf("CYD_PUBLIC_TREMOR_CURVE_FAILURE reason=%s core=%d\n",reason,xPortGetCoreID());fflush(stdout);abort(); }
}
static uint32_t append_word(uint32_t h,int32_t value) {
    uint32_t bits=(uint32_t)value;
    for(unsigned b=0;b<4;b++) { h=(h^(bits&255u))*UINT32_C(16777619);bits>>=8; }
    return h;
}
static uint32_t checksum(const int32_t *values,unsigned count) {
    uint32_t hash=UINT32_C(2166136261);
    for(unsigned i=0;i<count;i++) hash=append_word(hash,values[i]);
    return hash;
}
static uint32_t output_checksum(unsigned count) {
    uint32_t hash=UINT32_C(2166136261);
    for(unsigned i=0;i<count;i++) hash=append_word(hash,(int32_t)output.values[i]);
    return hash;
}
static void initialize(const int32_t *row,int zero) {
    output.before=output.after=angles.before=angles.after=GUARD;
    for(unsigned i=0;i<1024;i++) output.values[i]=(int32_t)GUARD;
    for(int i=0;i<row[3];i++) output.values[i]=(!zero && i<16)?row[15+i]:0;
    for(unsigned i=0;i<6;i++) angles.values[i]=(ogg_int32_t)row[9+i];
}
static void check_bounds(const int32_t *row) {
    require(output.before==GUARD && output.after==GUARD && angles.before==GUARD && angles.after==GUARD,"canary");
    for(unsigned i=0;i<6;i++) require(angles.values[i]==row[9+i],"LSP_input_changed");
    for(int i=row[3];i<1024;i++) require((uint32_t)output.values[i]==GUARD,"past_halfblock_write");
    for(int i=16;i<row[3];i++) require(output.values[i]==0,"zero_residue_tail_changed");
    for(unsigned i=0;i<16;i++) {
        int64_t magnitude=row[15+i]<0?-(int64_t)row[15+i]:row[15+i];
        int64_t bound=(magnitude*INT32_MAX+32767)/32768;
        require((int64_t)output.values[i]>=-bound && (int64_t)output.values[i]<=bound,"bounded_Q24_output");
    }
}
static void controls(void) {
    static const int32_t inputs[5]={-768,-256,0,256,768};
    for(unsigned i=0;i<5;i++) {
        int64_t product=(int64_t)inputs[i]*INT32_MAX;
        int32_t expected=(int32_t)(product>=0?product/32768:-((-product+32767)/32768));
        int32_t actual=MULT31_SHIFT15(inputs[i],INT32_MAX);
        require(actual==expected,"public_multiply_shift15");
        printf("CYD_PUBLIC_TREMOR_CURVE_CONTROL multiply=%u input=%" PRId32 " output=%" PRId32 " core=%d\n",i,inputs[i],actual,xPortGetCoreID());
    }
    const int32_t *row=curve_inputs[0];initialize(row,1);
    vorbis_lsp_to_curve(output.values,row[3],row[5],angles.values,row[4],row[6],row[7],row[8]);
    check_bounds(row);
    for(int i=0;i<row[3];i++) require(output.values[i]==0,"valid_zero_residue_identity");
    printf("CYD_PUBLIC_TREMOR_CURVE_CONTROL zero_residue=1 bins=%" PRId32 " core=%d\n",row[3],xPortGetCoreID());
}

void app_main(void) {
    require(xPortGetCoreID()==0,"main_core0");
    printf("CYD_PUBLIC_TREMOR_CURVE_BEGIN cases=%d packets=%d calls=%d bins=%d model=%s core=0\n",CURVE_CASES,CURVE_PACKETS,CURVE_CALLS,CURVE_BINS,CURVE_MODEL_SHA);
    controls();
    unsigned total=0;
    for(unsigned call=0;call<CURVE_CALLS;call++) {
        const int32_t *row=curve_inputs[call];
        require(checksum(row,31)==curve_input_fnv[call],"descriptor_checksum");
        initialize(row,0);
        printf("CYD_PUBLIC_TREMOR_CURVE_CALL call=%u case=%" PRId32 " packet=%" PRId32 " channel=%" PRId32 " n=%" PRId32 " m=%" PRId32 " ln=%" PRId32 " amp_q4=%" PRId32 " input=%08" PRIx32 " core=%d\n",call,row[0],row[1],row[2],row[3],row[4],row[5],row[6],curve_input_fnv[call],xPortGetCoreID());
        vorbis_lsp_to_curve(output.values,row[3],row[5],angles.values,row[4],row[6],row[7],row[8]);
        check_bounds(row);
        for(int offset=0;offset<row[3];offset+=16) {
            printf("CYD_PUBLIC_TREMOR_CURVE_OUT call=%u offset=%d count=16 hex=",call,offset);
            for(unsigned j=0;j<16;j++) {
                uint32_t word=(uint32_t)output.values[offset+j];
                for(unsigned b=0;b<4;b++) { printf("%02x",(unsigned)(word&255u));word>>=8; }
            }
            printf(" core=%d\n",xPortGetCoreID());
            if((offset&255)==240) vTaskDelay(1);
        }
        printf("CYD_PUBLIC_TREMOR_CURVE_END call=%u bins=%" PRId32 " output=%08" PRIx32 " canary=1 lsp=1 tail=1 core=%d\n",call,row[3],output_checksum((unsigned)row[3]),xPortGetCoreID());
        total+=(unsigned)row[3];
        vTaskDelay(1); /* Permit the SDK idle task while retaining main core0. */
    }
    require(total==CURVE_BINS,"all_bins");
    printf("CYD_PUBLIC_TREMOR_CURVE_COMPLETE calls=%d bins=%u core=%d\n",CURVE_CALLS,total,xPortGetCoreID());
    fflush(stdout);
    /* Return to the SDK idle tasks; the owning controller alone quits QEMU. */
}
