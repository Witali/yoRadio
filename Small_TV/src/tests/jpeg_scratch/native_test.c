/* Shared-sector/flat-RAM oracle, initialized prefixes, stale tokens, fault reuse. */
#include "../../storage/jpeg_scratch.h"
#include "nor_model.h"
#include "scratch_fixture.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(v) do{++checks;if(!(v)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}}while(0)
static uint64_t checks;
static unsigned random_operations,fault_cases;
static jpeg_nor_t nor;
static jpeg_scratch_t scratch;
static uint8_t expected[SCRATCH_LOGICAL_BYTES],actual[SCRATCH_LOGICAL_BYTES],input[8192];

static void open_store(void)
{
    /* A new NOR handle owns the one sector cache; scratch retains increasing IDs. */
    jpeg_nor_device_t device=scratch_model_device();
    CHECK(jpeg_nor_open(&nor,&device,scratch_extents,SCRATCH_EXTENT_COUNT,SCRATCH_LOGICAL_BYTES,
                       scratch_extents,SCRATCH_EXTENT_COUNT)==JPEG_NOR_OK);
    CHECK(jpeg_scratch_open(&scratch,&nor,scratch_model_check,NULL)==JPEG_SCRATCH_OK);
}

static void reset(unsigned page_bytes,uint64_t fail_at,unsigned mode)
{
    /* Explicitly discard temp RAM, restore deterministic physical input for unit cases. */
    jpeg_scratch_abort(&scratch);scratch_model_pristine();scratch_model_begin(page_bytes,fail_at,mode);
    scratch_model_copy_logical(expected,sizeof(expected));open_store();
}

static void test_capacity_and_coherence(void)
{
    /* Four115200-byte arrays fit exactly, sharing sector boundaries/padding. */
    reset(256,0,0);jpeg_scratch_file_t files[4],extra;
    for(unsigned i=0;i<4;++i) {
        CHECK(jpeg_scratch_allocate(&scratch,115200,&files[i])==JPEG_SCRATCH_OK);
        CHECK(scratch.files[files[i].slot].offset==i*115200u);
    }
    CHECK(scratch.active_bytes==SCRATCH_LOGICAL_BYTES && scratch.peak_files==4);
    CHECK(jpeg_scratch_allocate(&scratch,1,&extra)==JPEG_SCRATCH_CAPACITY);
    for(unsigned f=0;f<4;++f)
        for(uint32_t offset=0;offset<115200;) {
            unsigned bytes=115200-offset;if(bytes>sizeof(input))bytes=sizeof(input);
            for(unsigned i=0;i<bytes;++i)input[i]=(uint8_t)(f*43u+offset+i);
            CHECK(jpeg_scratch_write(&files[f],offset,input,bytes)==JPEG_SCRATCH_OK);
            memcpy(expected+f*115200+offset,input,bytes);offset+=bytes;
        }
    /* Adjacent file updates must not lose each other's bytes in their shared sector. */
    memset(input,0x51,512);CHECK(jpeg_scratch_write(&files[0],114688,input,512)==JPEG_SCRATCH_OK);
    memcpy(expected+114688,input,512);
    memset(input,0xa7,512);CHECK(jpeg_scratch_write(&files[1],0,input,512)==JPEG_SCRATCH_OK);
    memcpy(expected+115200,input,512);
    CHECK(jpeg_scratch_read(&files[0],114688,actual,512)==JPEG_SCRATCH_OK && !memcmp(actual,expected+114688,512));
    CHECK(jpeg_scratch_read(&files[1],0,actual,512)==JPEG_SCRATCH_OK && !memcmp(actual,expected+115200,512));
    CHECK(jpeg_nor_sync(&nor)==JPEG_NOR_OK);scratch_model_copy_logical(actual,sizeof(actual));
    CHECK(!memcmp(actual,expected,sizeof(actual)) && scratch_model_canaries());
    for(unsigned i=0;i<4;++i)CHECK(jpeg_scratch_close(&files[i])==JPEG_SCRATCH_OK);
    CHECK(!scratch.active_files && !scratch.active_bytes);
}

static uint32_t random_number(uint32_t *seed)
{
    /* Deterministic generator independent of the allocator's placement choices. */
    *seed=*seed*1664525u+1013904223u;return *seed;
}

static void test_random(unsigned page_bytes)
{
    /* Ragged file sizes force shared physical sectors; oracle tracks logical bytes. */
    reset(page_bytes,0,0);jpeg_scratch_file_t files[16];uint32_t sizes[16],prefix[16]={0};uint32_t seed=91;
    for(unsigned i=0;i<16;++i) {
        sizes[i]=3001+random_number(&seed)%13000;
        CHECK(jpeg_scratch_allocate(&scratch,sizes[i],&files[i])==JPEG_SCRATCH_OK);
    }
    for(unsigned n=0;n<2500;++n) {
        unsigned f=random_number(&seed)%16;uint32_t offset=prefix[f] ? random_number(&seed)%(prefix[f]+1) : 0;
        unsigned bytes=random_number(&seed)%1025;if(bytes>sizes[f]-offset)bytes=sizes[f]-offset;
        for(unsigned i=0;i<bytes;++i)input[i]=(uint8_t)random_number(&seed);
        CHECK(jpeg_scratch_write(&files[f],offset,input,bytes)==JPEG_SCRATCH_OK);
        memcpy(expected+scratch.files[files[f].slot].offset+offset,input,bytes);
        if(offset+bytes>prefix[f])prefix[f]=offset+bytes;
        offset=prefix[f] ? random_number(&seed)%(prefix[f]+1) : 0;
        bytes=prefix[f]-offset;if(bytes>1024)bytes=1024;
        CHECK(jpeg_scratch_read(&files[f],offset,actual,bytes)==JPEG_SCRATCH_OK);
        CHECK(!memcmp(actual,expected+scratch.files[files[f].slot].offset+offset,bytes));
        if(n%29==0) {
            CHECK(jpeg_nor_sync(&nor)==JPEG_NOR_OK);scratch_model_copy_logical(actual,sizeof(actual));
            CHECK(!memcmp(actual,expected,sizeof(actual)) && scratch_model_canaries());
        }
        ++random_operations;
    }
    CHECK(jpeg_nor_sync(&nor)==JPEG_NOR_OK);scratch_model_copy_logical(actual,sizeof(actual));
    CHECK(!memcmp(actual,expected,sizeof(actual)) && scratch_model_canaries());
}

static void test_lifecycle(void)
{
    /* Unwritten data never exposes the previous occupant's temp bytes. */
    reset(256,0,0);jpeg_scratch_file_t file,stale;CHECK(jpeg_scratch_allocate(&scratch,8192,&file)==JPEG_SCRATCH_OK);
    uint64_t calls=scratch_model_stats().calls;
    CHECK(jpeg_scratch_read(&file,0,actual,1)==JPEG_SCRATCH_UNINITIALIZED);
    CHECK(jpeg_scratch_write(&file,1,input,1)==JPEG_SCRATCH_UNINITIALIZED);
    CHECK(jpeg_scratch_read(&file,8192,NULL,0)==JPEG_SCRATCH_OK);
    CHECK(jpeg_scratch_write(&file,8192,NULL,0)==JPEG_SCRATCH_OK);
    CHECK(scratch.files[file.slot].initialized==0);
    CHECK(jpeg_scratch_write(&file,8191,input,2)==JPEG_SCRATCH_RANGE && scratch_model_stats().calls==calls);
    CHECK(jpeg_scratch_write(&file,0,input,512)==JPEG_SCRATCH_OK);stale=file;
    CHECK(jpeg_scratch_read(&file,500,actual,13)==JPEG_SCRATCH_UNINITIALIZED);
    CHECK(jpeg_scratch_read(&file,0,&scratch,16)==JPEG_SCRATCH_ARGUMENT);
    CHECK(jpeg_scratch_close(&file)==JPEG_SCRATCH_OK);
    CHECK(jpeg_scratch_allocate(&scratch,8192,&file)==JPEG_SCRATCH_OK);
    CHECK(jpeg_scratch_read(&stale,0,actual,1)==JPEG_SCRATCH_STATE && file.id!=stale.id);
    CHECK(jpeg_scratch_close(&stale)==JPEG_SCRATCH_STATE && scratch.active_files==1);
    CHECK(jpeg_scratch_read(&file,0,actual,1)==JPEG_SCRATCH_UNINITIALIZED);
    CHECK(jpeg_scratch_write(&file,0,input,512)==JPEG_SCRATCH_OK);calls=scratch_model_stats().calls;
    scratch_model_allow(false);
    CHECK(jpeg_scratch_read(&file,0,actual,16)==JPEG_SCRATCH_STOP && scratch_model_stats().calls==calls);
    CHECK(jpeg_scratch_write(&file,0,input,16)==JPEG_SCRATCH_STATE);
    CHECK(jpeg_scratch_close(&file)==JPEG_SCRATCH_OK);stale=file;jpeg_scratch_abort(&scratch);
    scratch_model_begin(256,0,0);open_store();CHECK(jpeg_scratch_allocate(&scratch,8192,&file)==JPEG_SCRATCH_OK);
    CHECK(file.id>stale.id && jpeg_scratch_read(&stale,0,actual,1)==JPEG_SCRATCH_STATE);
    scratch.next_id=UINT64_MAX;CHECK(jpeg_scratch_allocate(&scratch,1,&stale)==JPEG_SCRATCH_LIMIT);
}

static void test_fragmentation(void)
{
    /* Byte-sized holes may be reused only if the whole new file fits. */
    reset(256,0,0);jpeg_scratch_file_t a,b,c,reused,large;
    CHECK(jpeg_scratch_allocate(&scratch,3,&a)==JPEG_SCRATCH_OK);
    CHECK(jpeg_scratch_allocate(&scratch,5,&b)==JPEG_SCRATCH_OK);
    CHECK(jpeg_scratch_allocate(&scratch,7,&c)==JPEG_SCRATCH_OK);
    CHECK(jpeg_scratch_close(&b)==JPEG_SCRATCH_OK);
    CHECK(jpeg_scratch_allocate(&scratch,4,&reused)==JPEG_SCRATCH_OK && scratch.files[reused.slot].offset==3);
    CHECK(jpeg_scratch_close(&reused)==JPEG_SCRATCH_OK);
    CHECK(jpeg_scratch_allocate(&scratch,6,&large)==JPEG_SCRATCH_OK && scratch.files[large.slot].offset==15);
    CHECK(jpeg_scratch_allocate(&scratch,UINT32_MAX,&reused)==JPEG_SCRATCH_CAPACITY);
    CHECK(!scratch_model_stats().calls && scratch_model_canaries());
}

static void test_faults(void)
{
    /* Every NOR callback in a cross-sector buffered write can fail partially. */
    reset(256,0,0);jpeg_scratch_file_t file;
    CHECK(jpeg_scratch_allocate(&scratch,sizeof(input),&file)==JPEG_SCRATCH_OK);memset(input,0x5d,sizeof(input));
    CHECK(jpeg_scratch_write(&file,0,input,sizeof(input))==JPEG_SCRATCH_OK);
    uint64_t calls=scratch_model_stats().calls;
    for(unsigned mode=1;mode<=2;++mode)
        for(uint64_t n=1;n<=calls;++n) {
            reset(256,n,mode);CHECK(jpeg_scratch_allocate(&scratch,sizeof(input),&file)==JPEG_SCRATCH_OK);
            jpeg_scratch_result_t result=jpeg_scratch_write(&file,0,input,sizeof(input));
            if(result==JPEG_SCRATCH_OK) {
                CHECK(mode==2); /* overwritten corrupt cache-load bytes may be irrelevant */
                CHECK(jpeg_scratch_read(&file,0,actual,sizeof(input))==JPEG_SCRATCH_OK && !memcmp(actual,input,sizeof(input)));
            } else {
                CHECK(result==JPEG_SCRATCH_IO);uint64_t old_calls=scratch_model_stats().calls;
                CHECK(jpeg_scratch_read(&file,0,actual,1)!=JPEG_SCRATCH_OK && scratch_model_stats().calls==old_calls);
                CHECK(jpeg_scratch_close(&file)==JPEG_SCRATCH_OK);
            }
            CHECK(scratch_model_canaries());++fault_cases;
        }
}

int main(void)
{
    /* The host model's8MiB arrays are not part of firmware RAM footprint. */
    /* FIXED_TEST: exhausting the monotonic ID space is terminal for an object;
     * run that lifecycle test last, not before unrelated allocation/fault cases. */
    test_capacity_and_coherence();test_random(128);test_random(256);test_faults();test_fragmentation();test_lifecycle();jpeg_scratch_abort(&scratch);
    printf("{\"passed\":true,\"checks\":%llu,\"random_operations\":%u,\"fault_cases\":%u,\"capacity_bytes\":%u,"
           "\"max_files\":16,\"physical_hardware_tested\":false}\n",(unsigned long long)checks,random_operations,fault_cases,SCRATCH_LOGICAL_BYTES);
    return 0;
}
