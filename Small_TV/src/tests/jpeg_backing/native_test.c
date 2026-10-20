/* Real adapter/NOR, native-coefficient oracle and strict physical model. */
#include "jpeg_backing.h"
#include "nor_model.h"
#include "scratch_fixture.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(v) do{++checks;if(!(v)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}}while(0)
static uint64_t checks;
static unsigned faults;
static jpeg_nor_t nor;
static jpeg_backing_t backing;
static uint8_t bitmap[(SCRATCH_LOGICAL_BYTES/4096u+8u)/8u];
static jpeg_decode_backing_t api;
static int16_t input[4096],output[4096];

static void begin(bool pristine,uint64_t fault,unsigned mode)
{
    /* IDs survive jobs, physical bytes survive unless the test explicitly resets. */
    jpeg_backing_abort(&backing);if(pristine)scratch_model_pristine();scratch_model_begin(256,fault,mode);
    jpeg_nor_device_t device=scratch_model_device();
    CHECK(jpeg_nor_open(&nor,&device,scratch_extents,SCRATCH_EXTENT_COUNT,SCRATCH_LOGICAL_BYTES,scratch_extents,SCRATCH_EXTENT_COUNT)==JPEG_NOR_OK);
    CHECK(jpeg_backing_begin(&backing,&nor,scratch_model_check,NULL,bitmap,sizeof(bitmap))==JPEG_SCRATCH_OK);
    api=jpeg_backing_callbacks(&backing);
}

static void fill(unsigned file,uint32_t offset,unsigned al,size_t bytes)
{
    /* Independent correct DC floor / AC toward-zero successive approximation. */
    for(unsigned i=0;i<bytes/2;++i) {
        int32_t target=(int32_t)(((offset/2u+i)*137u+file*59u)%8192u)-4096;
        int32_t step=1<<al,value=target/step;
        if(((offset/2u+i)%64u)==0 && target<0)value=(target-step+1)/step;
        input[i]=(int16_t)(value*step);
    }
}

static void packed_matrix(void)
{
    /* Four arrays share sector boundaries; no extra cache or per-array padding. */
    begin(true,0,0);uint64_t files[4];
    for(unsigned f=0;f<4;++f)CHECK(api.open(api.context,115200,true,&files[f])==JPEG_SCRATCH_OK);
    for(int al=3;al>=0;--al) {
        for(uint32_t row=0;row<30;++row)
            for(unsigned f=0;f<4;++f)
                for(uint32_t at=0;at<3840;at+=256) {
                    uint32_t offset=row*3840u+at;fill(f,offset,(unsigned)al,256);
                    CHECK(api.write(api.context,files[f],offset,input,256)==JPEG_SCRATCH_OK);
                }
        CHECK(jpeg_nor_sync(&nor)==JPEG_NOR_OK);
        for(unsigned f=0;f<4;++f)
            for(uint32_t offset=0;offset<115200;offset+=256) {
                fill(f,offset,(unsigned)al,256);
                CHECK(api.read(api.context,files[f],offset,output,256)==JPEG_SCRATCH_OK && !memcmp(input,output,256));
            }
        CHECK(scratch_model_canaries());
        CHECK(scratch_model_stats().erases<=113);
    }
    uint64_t calls=scratch_model_stats().calls;
    for(unsigned f=0;f<4;++f)CHECK(api.close(api.context,files[f])==JPEG_SCRATCH_OK);
    CHECK(!backing.scratch.active_files);jpeg_backing_abort(&backing);
    CHECK(scratch_model_stats().calls==calls);
}

static void invalid_and_lifecycle(void)
{
    /* Invalid buffers must not trigger first-use clearing or corrupt owner state. */
    begin(false,0,0);uint64_t file,stale;CHECK(api.open(api.context,4096,true,&file)==0);stale=file;
    uint64_t calls=scratch_model_stats().calls;
    CHECK(api.read(api.context,file,0,output,128)==JPEG_SCRATCH_UNINITIALIZED);
    CHECK(api.write(api.context,file,128,input,128)==JPEG_SCRATCH_UNINITIALIZED);
    CHECK(api.write(api.context,file,0,input,127)==JPEG_SCRATCH_ARGUMENT);
    CHECK(api.write(api.context,file,1,input,128)==JPEG_SCRATCH_ARGUMENT);
    CHECK(api.write(api.context,file,4096,input,128)==JPEG_SCRATCH_RANGE);
    CHECK(api.write(api.context,file,0,&backing,128)==JPEG_SCRATCH_ARGUMENT);
    CHECK(api.write(api.context,file,0,&nor,128)==JPEG_SCRATCH_ARGUMENT);
    CHECK(api.write(api.context,file,0,bitmap,128)==JPEG_SCRATCH_ARGUMENT);
    CHECK(api.write(api.context,file,0,(void *)UINTPTR_MAX,128)==JPEG_SCRATCH_ARGUMENT);
    CHECK(api.open(api.context,128,true,(uint64_t *)bitmap)==JPEG_SCRATCH_ARGUMENT);
    CHECK(api.open(api.context,128,false,&stale)==JPEG_SCRATCH_ARGUMENT);
    CHECK(scratch_model_stats().calls==calls);
    fill(0,0,0,128);CHECK(api.write(api.context,file,0,input,128)==0);calls=scratch_model_stats().calls;
    scratch_model_allow(false);CHECK(api.read(api.context,file,0,output,128)==JPEG_SCRATCH_STOP);
    CHECK(scratch_model_stats().calls==calls && api.close(api.context,file)==0);stale=file;
    jpeg_backing_abort(&backing);CHECK(scratch_model_stats().calls==calls);
    begin(false,0,0);CHECK(api.open(api.context,128,true,&file)==0 && file>stale);
    CHECK(api.read(api.context,stale,0,output,128)==JPEG_SCRATCH_STATE);
    CHECK(api.close(api.context,stale)==JPEG_SCRATCH_STATE && backing.scratch.active_files==1);
    CHECK(api.close(api.context,file)==0);jpeg_backing_abort(&backing);
    CHECK(jpeg_backing_bitmap_bytes(UINT32_MAX)==131072u && jpeg_backing_bitmap_bytes(0)==0);
    /* A stopped job must not clear even a previously untouched dirty sector. */
    begin(true,0,0);CHECK(api.open(api.context,128,true,&file)==0);
    calls=scratch_model_stats().calls;scratch_model_allow(false);
    CHECK(api.write(api.context,file,0,input,128)==JPEG_SCRATCH_STOP);
    CHECK(scratch_model_stats().calls==calls && api.close(api.context,file)==0);
    jpeg_backing_abort(&backing);CHECK(scratch_model_stats().calls==calls);
}

static void raw_and_rejected_begin(void)
{
    /* Raw byte arrays do not invoke coefficient initialization/conversion. */
    begin(false,0,0);uint64_t file;CHECK(api.open(api.context,513,false,&file)==0);
    memset(input,0x51,513);CHECK(api.write(api.context,file,0,input,513)==0);
    CHECK(api.read(api.context,file,0,output,513)==0 && !memcmp(input,output,513));
    CHECK(api.close(api.context,file)==0);jpeg_backing_abort(&backing);
    jpeg_nor_device_t device=scratch_model_device();jpeg_nor_extent_t extent={scratch_extents[0].offset,4096};
    CHECK(jpeg_nor_open(&nor,&device,&extent,1,4096,&extent,1)==0);
    uint64_t calls=scratch_model_stats().calls;
    CHECK(jpeg_backing_begin(&backing,&nor,scratch_model_check,NULL,bitmap,sizeof(bitmap))==JPEG_SCRATCH_ARGUMENT);
    CHECK(!backing.active && nor.open && backing.capacity==SCRATCH_LOGICAL_BYTES && scratch_model_stats().calls==calls);
    jpeg_nor_abort(&nor);
}

static void physical_faults(void)
{
    /* Partial/error and silent-short physical writes operate on the actual NOR. */
    begin(true,0,0);uint64_t file;fill(0,0,0,sizeof(input));CHECK(api.open(api.context,sizeof(input),true,&file)==0);
    CHECK(api.write(api.context,file,0,input,sizeof(input))==0);uint64_t count=scratch_model_stats().calls;
    for(unsigned mode=1;mode<=2;++mode)for(uint64_t at=1;at<=count;++at) {
        begin(true,at,mode);CHECK(api.open(api.context,sizeof(input),true,&file)==0);
        int result=api.write(api.context,file,0,input,sizeof(input));
        if(!result){CHECK(mode==2);CHECK(api.read(api.context,file,0,output,sizeof(input))==0 && !memcmp(input,output,sizeof(input)));}
        else {
            CHECK(result==JPEG_SCRATCH_IO);uint64_t calls=scratch_model_stats().calls;
            CHECK(api.read(api.context,file,0,output,128)!=0 && scratch_model_stats().calls==calls);
        }
        CHECK(api.close(api.context,file)==0 && scratch_model_canaries());++faults;
    }
    jpeg_backing_abort(&backing);
}

int main(void)
{
    /* The independent8MiB model is host-only, not this adapter's RAM footprint. */
    packed_matrix();invalid_and_lifecycle();raw_and_rejected_begin();physical_faults();
    printf("{\"passed\":true,\"checks\":%llu,\"physical_fault_cases\":%u,\"capacity\":%u,\"bitmap_bytes\":%zu}\n",
        (unsigned long long)checks,faults,SCRATCH_LOGICAL_BYTES,jpeg_backing_bitmap_bytes(SCRATCH_LOGICAL_BYTES));return 0;
}
