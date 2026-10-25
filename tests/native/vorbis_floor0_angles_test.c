// New original-angle API adapter. Binary fields are explicit little-endian.
#include "native_vorbis_floor0.h"
#include <assert.h>
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

_Static_assert(sizeof(double)==8 && DBL_MANT_DIG==53, "IEEE binary64 adapter");
static const uint64_t CANARY=UINT64_C(0x53c2a91e7b640fd8);
typedef struct { uint64_t left; double values[255]; uint64_t right; } angles_t;
typedef struct { uint64_t left; native_vorbis_scaled_t value; uint64_t right; } denominator_t;
typedef struct { uint64_t left; native_vorbis_floor0_gain_t value; uint64_t right; } gain_t;
static uint64_t get(FILE *file,unsigned count) {
    uint64_t value=0;
    for(unsigned i=0;i<count;++i) { int c=fgetc(file);assert(c!=EOF);value|=(uint64_t)(unsigned)c<<(8*i); }
    return value;
}
static void put(FILE *file,uint64_t value,unsigned count) {
    for(unsigned i=0;i<count;++i) assert(fputc((int)((value>>(8*i))&255),file)!=EOF);
}
static double number(uint64_t bits) { double value;memcpy(&value,&bits,8);return value; }
static uint64_t bits(double value) { uint64_t result;memcpy(&result,&value,8);return result; }
static void scaled(FILE *file,native_vorbis_scaled_t value) {
    put(file,bits(value.mantissa),8);put(file,(uint32_t)value.exponent,4);
}
static unsigned controls(void) {
    angles_t angles;memset(&angles,0,sizeof(angles));angles.left=angles.right=CANARY;
    denominator_t d;memset(&d,0xa5,sizeof(d));d.left=d.right=CANARY;
    gain_t g;memset(&g,0xa5,sizeof(g));g.left=g.right=CANARY;
    native_vorbis_floor0_amplitude_t amplitude={1,1,255};
    unsigned count=0;
#define INVALID(call,object) do { \
    unsigned char saved[sizeof(object)];memcpy(saved,&(object),sizeof(object)); \
    assert((call)==NATIVE_VORBIS_NUMERIC_INVALID); \
    assert(!memcmp(saved,&(object),sizeof(object)));++count; \
} while(0)
    INVALID(native_vorbis_floor0_denominator_at_bin(NULL,1,0,1,&d.value),d);
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,0,0,1,&d.value),d);
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,256,0,1,&d.value),d);
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,1,0,0,&d.value),d);
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,1,0,65536,&d.value),d);
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,1,1,1,&d.value),d);
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,1,0,1,NULL),d);
    angles.values[1]=NAN;
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,2,0,1,&d.value),d);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,2,0,1,&g.value),g);
    angles.values[1]=INFINITY;
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,2,0,1,&d.value),d);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,2,0,1,&g.value),g);
    angles.values[1]=-INFINITY;
    INVALID(native_vorbis_floor0_denominator_at_bin(angles.values,2,0,1,&d.value),d);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,2,0,1,&g.value),g);
    angles.values[1]=0;
    INVALID(native_vorbis_floor0_gain_from_angles(NULL,angles.values,1,0,1,&g.value),g);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,NULL,1,0,1,&g.value),g);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,0,0,1,&g.value),g);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,256,0,1,&g.value),g);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,1,0,0,&g.value),g);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,1,0,65536,&g.value),g);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,1,1,1,&g.value),g);
    INVALID(native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,1,0,1,NULL),g);
    native_vorbis_floor0_amplitude_t bad[]={{1,0,1},{2,1,1},{1,64,1},{1,1,256}};
    for(unsigned i=0;i<4;++i)
        INVALID(native_vorbis_floor0_gain_from_angles(&bad[i],angles.values,1,0,1,&g.value),g);
    native_vorbis_floor0_amplitude_t absent={0,0,255},copy=absent;
    assert(native_vorbis_floor0_gain_from_angles(&absent,NULL,1,0,1,&g.value)==0);
    assert(g.value.kind==NATIVE_VORBIS_FLOOR0_ABSENT && !memcmp(&absent,&copy,sizeof(copy)));++count;
    INVALID(native_vorbis_floor0_gain_from_angles(&absent,NULL,0,0,1,&g.value),g);
    INVALID(native_vorbis_floor0_gain_from_angles(&absent,NULL,1,1,1,&g.value),g);
#undef INVALID
    assert(angles.left==CANARY && angles.right==CANARY && d.left==CANARY && d.right==CANARY);
    assert(g.left==CANARY && g.right==CANARY);
    return count;
}

int main(int argc,char **argv) {
    assert(argc==3);FILE *input=fopen(argv[1],"rb"),*output=fopen(argv[2],"wb");assert(input&&output);
    unsigned char magic[8];assert(fread(magic,1,8,input)==8 && !memcmp(magic,"F0ANG001",8));
    uint32_t count=(uint32_t)get(input,4);assert(count>0 && count<=10000);
    assert(fwrite("F0ANGOUT",1,8,output)==8);put(output,count,4);put(output,controls(),4);
    for(uint32_t i=0;i<count;++i) {
        uint32_t length=(uint32_t)get(input,4);assert(length>=1 && length<=63);
        for(uint32_t j=0;j<length;++j) {
            unsigned c=(unsigned)get(input,1);
            assert((c>='A'&&c<='Z') || (c>='a'&&c<='z') ||
                   (c>='0'&&c<='9') || c=='_' || c=='-');
        }
        uint64_t raw=get(input,8);uint32_t amplitude_bits=(uint32_t)get(input,4);
        uint32_t offset=(uint32_t)get(input,4);
        uint32_t order=(uint32_t)get(input,4);
        uint32_t bin=(uint32_t)get(input,4);
        uint32_t map_size=(uint32_t)get(input,4);
        assert(order>=1 && order<=255);
        angles_t angles,saved;memset(&angles,0xa5,sizeof(angles));angles.left=angles.right=CANARY;
        for(uint32_t j=0;j<order;++j) angles.values[j]=number(get(input,8));
        memcpy(&saved,&angles,sizeof(saved));
        native_vorbis_floor0_amplitude_t amplitude={raw,amplitude_bits,offset},amplitude_copy=amplitude;
        denominator_t d;memset(&d,0xa5,sizeof(d));d.left=d.right=CANARY;
        gain_t gain,repeated;memset(&gain,0xa5,sizeof(gain));gain.left=gain.right=CANARY;
        memset(&repeated,0xa5,sizeof(repeated));repeated.left=repeated.right=CANARY;
        int ds=native_vorbis_floor0_denominator_at_bin(angles.values,order,bin,map_size,&d.value);
        int gs=native_vorbis_floor0_gain_from_angles(&amplitude,angles.values,order,bin,map_size,&gain.value);
        assert(ds==0 && gs==0);
        native_vorbis_scaled_t dcopy=d.value;
        assert(native_vorbis_floor0_gain_from_denominator(&amplitude,&d.value,&repeated.value)==gs);
        assert(bits(d.value.mantissa)==bits(dcopy.mantissa) && d.value.exponent==dcopy.exponent);
        assert(gain.value.kind==repeated.value.kind &&
               bits(gain.value.log2_gain.mantissa)==bits(repeated.value.log2_gain.mantissa) &&
               gain.value.log2_gain.exponent==repeated.value.log2_gain.exponent);
        assert(!memcmp(&angles,&saved,sizeof(saved)) && !memcmp(&amplitude,&amplitude_copy,sizeof(amplitude)));
        assert(angles.left==CANARY && angles.right==CANARY && d.left==CANARY && d.right==CANARY);
        assert(gain.left==CANARY && gain.right==CANARY && repeated.left==CANARY && repeated.right==CANARY);
        put(output,i,4);put(output,(uint32_t)ds,4);scaled(output,d.value);
        put(output,(uint32_t)gs,4);put(output,(uint32_t)gain.value.kind,4);scaled(output,gain.value.log2_gain);
        put(output,7,4);
    }
    assert(fgetc(input)==EOF && !fclose(input) && !fclose(output));return 0;
}
