// Joint residue/significand products and direct binary64 rounding capture.
#include "product.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>

static uint64_t checks,controls,invalid_rows;
#define CHECK(x) do { ++checks; assert(x); } while (0)
static uint32_t read32(FILE *f) {
    unsigned char b[4]; CHECK(fread(b,1,4,f)==4);
    return (uint32_t)b[0]|(uint32_t)b[1]<<8|(uint32_t)b[2]<<16|(uint32_t)b[3]<<24;
}
static uint64_t read64(FILE *f) {uint64_t low=read32(f);return low|((uint64_t)read32(f)<<32);}
static int32_t signed32(uint32_t word) {int32_t value;memcpy(&value,&word,4);return value;}
static void put32(FILE *f,uint32_t word) {
    unsigned char b[4]={(unsigned char)word,(unsigned char)(word>>8),(unsigned char)(word>>16),(unsigned char)(word>>24)};
    CHECK(fwrite(b,1,4,f)==4);
}
static void put64(FILE *f,uint64_t word) {put32(f,(uint32_t)word);put32(f,(uint32_t)(word>>32));}
static void shape_controls(const native_vorbis_residue_layout_t *shape,const uint32_t *sample) {
    unsigned char before[sizeof(*shape)];memcpy(before,shape,sizeof(before));
    CHECK(!native_floor0_source_valid(NULL));++controls;
    CHECK(!native_floor0_sample_valid(sample,NULL));++controls;
    CHECK(!native_floor0_sample_valid(NULL,shape));++controls;
    CHECK(native_floor0_sample_zero(NULL,0));++controls;
    CHECK(!native_floor0_sample_zero(NULL,1));++controls;
    native_vorbis_residue_layout_t bad;
    for(unsigned test=0;test<13;++test) {
        bad=*shape;
        switch(test) {
            case 0:bad.bins=0;break;case 1:bad.bins=4097;break;
            case 2:bad.channels=0;break;case 3:bad.channels=256;break;
            case 4:++bad.sample_count;break;case 5:++bad.limb_count;break;
            case 6:bad.limbs=35;break;case 7:bad.magnitude_bits=0;break;
            case 8:bad.magnitude_bits=1088;break;case 9:++bad.limbs;break;
            case 10:bad.sample_count=UINT64_MAX;break;case 11:bad.limb_count=UINT64_MAX;break;
            default:bad.limbs=0;break;
        }
        unsigned char saved[sizeof(bad)];memcpy(saved,&bad,sizeof(saved));
        CHECK(!native_floor0_source_valid(&bad));CHECK(!native_floor0_sample_valid(sample,&bad));
        CHECK(!memcmp(saved,&bad,sizeof(saved)));controls+=2;
    }
    native_vorbis_residue_layout_t zero={.bins=4096,.channels=255,.sample_count=UINT64_C(4096)*255};
    CHECK(native_floor0_source_valid(&zero));CHECK(native_floor0_sample_valid(NULL,&zero));controls+=2;
    zero.exponent=1;CHECK(!native_floor0_source_valid(&zero));++controls;
    zero.exponent=0;zero.magnitude_bits=1;CHECK(!native_floor0_source_valid(&zero));++controls;
    bad=*shape;bad.exponent=INT32_MIN;CHECK(native_floor0_source_valid(&bad));++controls;
    bad.exponent=INT32_MAX;CHECK(native_floor0_source_valid(&bad));++controls;
    CHECK(!memcmp(before,shape,sizeof(before)));
}
int main(int argc,char **argv) {
    CHECK(argc==3);FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb");CHECK(in&&out);
    unsigned char magic[8];CHECK(fread(magic,1,8,in)==8&&!memcmp(magic,"F0PRODIN",8));
    uint32_t rows=read32(in);CHECK(fwrite("F0PRODOU",1,8,out)==8);put32(out,rows);
    for(uint32_t row=0;row<rows;++row) {
        uint32_t width=read32(in),limbs=read32(in),run_controls=read32(in);
        uint64_t factor=read64(in);int32_t working_top=signed32(read32(in));
        CHECK(width>=1&&width<=1087&&limbs==(width+32)/32&&limbs<=34);
        CHECK(factor<(UINT64_C(1)<<53)&&working_top>=-1022&&working_top<=638);
        uint32_t input[NATIVE_FLOOR0_SOURCE_LIMBS+2],input_copy[NATIVE_FLOOR0_SOURCE_LIMBS+2];
        uint32_t magnitude[NATIVE_FLOOR0_PRODUCT_LIMBS+2],magnitude_copy[NATIVE_FLOOR0_PRODUCT_LIMBS];
        memset(input,0xa5,sizeof(input));memset(magnitude,0xa5,sizeof(magnitude));
        for(uint32_t i=0;i<limbs;++i)input[i+1]=read32(in);
        memcpy(input_copy,input,sizeof(input));
        native_vorbis_residue_layout_t shape={.bins=1,.channels=1,.limbs=limbs,
            .magnitude_bits=width,.sample_count=1,.limb_count=limbs};
        unsigned char shape_before[sizeof(shape)];memcpy(shape_before,&shape,sizeof(shape));
        CHECK(native_floor0_source_valid(&shape));
        bool valid=native_floor0_sample_valid(input+1,&shape),zero=native_floor0_sample_zero(input+1,limbs);
        if(run_controls)shape_controls(&shape,input+1);
        struct {uint32_t before;bool value;uint32_t after;} negative={UINT32_C(0xa5a5a5a5),false,UINT32_C(0xa5a5a5a5)};
        int32_t highest=-2;uint64_t rounded=0;
        if(valid) {
            highest=native_floor0_product(input+1,limbs,factor,magnitude+1,&negative.value);
            CHECK(highest>=-1&&highest<1140);
            memcpy(magnitude_copy,magnitude+1,sizeof(magnitude_copy));
            if(highest>=0) {
                double result=native_floor0_round(magnitude+1,(uint32_t)highest,working_top,negative.value);
                memcpy(&rounded,&result,8);
                CHECK(((rounded>>52)&2047)>=1&&((rounded>>52)&2047)<=1662);
                CHECK((rounded>>63)==(uint64_t)negative.value);
            }
            CHECK(!memcmp(magnitude_copy,magnitude+1,sizeof(magnitude_copy)));
        } else {
            ++invalid_rows;
            for(uint32_t i=0;i<NATIVE_FLOOR0_PRODUCT_LIMBS;++i)CHECK(magnitude[i+1]==UINT32_C(0xa5a5a5a5));
        }
        CHECK(!memcmp(input_copy,input,sizeof(input))&& !memcmp(shape_before,&shape,sizeof(shape)));
        CHECK(magnitude[0]==UINT32_C(0xa5a5a5a5)&&magnitude[NATIVE_FLOOR0_PRODUCT_LIMBS+1]==UINT32_C(0xa5a5a5a5));
        CHECK(negative.before==UINT32_C(0xa5a5a5a5)&&negative.after==UINT32_C(0xa5a5a5a5));
        put32(out,width);put32(out,limbs);put64(out,factor);put32(out,(uint32_t)working_top);
        put32(out,valid);put32(out,zero);put32(out,(uint32_t)highest);put32(out,negative.value);put64(out,rounded);
        for(uint32_t i=0;i<limbs;++i)put32(out,input[i+1]);
        for(uint32_t i=0;i<NATIVE_FLOOR0_PRODUCT_LIMBS;++i)put32(out,magnitude[i+1]);
    }
    CHECK(fgetc(in)==EOF);CHECK(fclose(in)==0&&fclose(out)==0);
    printf("FLOOR0_PRODUCT_CAPTURE rows=%" PRIu32 " invalid=%" PRIu64 " controls=%" PRIu64 " checks=%" PRIu64 "\n",
        rows,invalid_rows,controls,checks);return 0;
}
