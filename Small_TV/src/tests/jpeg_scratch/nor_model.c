/* HOST ONLY: independent strict4MiB physical model, never a firmware allocation. */
#include "nor_model.h"
#include "scratch_fixture.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint8_t flash_data[0x400000],canaries[0x400000];
static scratch_model_stats_t stats;
static bool initialized;
#define REQUIRE(v) do{if(!(v)){fprintf(stderr,"MODEL FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}}while(0)

static void address(uint32_t start,size_t bytes)
{
    /* Callback requests must stay wholly in a real scratch extent. */
    REQUIRE(start<=sizeof(flash_data) && bytes<=sizeof(flash_data)-start && bytes);
    bool owned=false;
    for(unsigned i=0;i<SCRATCH_EXTENT_COUNT;++i)
        if(start>=scratch_extents[i].offset && start-scratch_extents[i].offset<scratch_extents[i].bytes &&
            bytes<=scratch_extents[i].bytes-(start-scratch_extents[i].offset))owned=true;
    REQUIRE(owned);
}

static bool visit(void)
{
    /* Unit tests sweep physical callback ordinals; real decoder gets same model. */
    bool fail=++stats.calls==stats.fail_at;if(fail)++stats.hits;return fail;
}

static int read_model(void *context,uint32_t start,void *out,size_t bytes)
{
    /* An error or silent short read really returns only part of the requested bytes. */
    REQUIRE(context==&stats);address(start,bytes);bool fail=visit();stats.read_bytes+=bytes;
    memcpy(out,flash_data+start,fail ? bytes/2 : bytes);
    if(fail && stats.mode==2)((uint8_t *)out)[0]^=1;
    return fail && stats.mode==1 ? -77 : 0;
}

static int program_model(void *context,uint32_t start,const void *data,size_t bytes)
{
    /* Reject page crossing/0->1 requests independently of the NOR algorithm. */
    REQUIRE(context==&stats);address(start,bytes);
    REQUIRE(bytes==stats.page_bytes && start%bytes==0);const uint8_t *in=data;
    for(size_t i=0;i<bytes;++i)REQUIRE((flash_data[start+i]&in[i])==in[i]);
    bool fail=visit();stats.program_bytes+=bytes;
    for(size_t i=0;i<(fail ? bytes/2 : bytes);++i)flash_data[start+i]&=in[i];
    return fail && stats.mode==1 ? -77 : 0;
}

static int erase_model(void *context,uint32_t start)
{
    /* Partial erase leaves actual old bytes; no rollback to a fake pristine image. */
    REQUIRE(context==&stats);address(start,4096);REQUIRE(start%4096==0);
    bool fail=visit();++stats.erases;memset(flash_data+start,0xff,fail ? 2048 : 4096);
    return fail && stats.mode==1 ? -77 : 0;
}

void scratch_model_pristine(void)
{
    /* Both scratch and protected bytes start non-FF, exposing needless erase bugs. */
    for(size_t i=0;i<sizeof(flash_data);++i)flash_data[i]=(uint8_t)(i*13u+(i>>10));
    memcpy(canaries,flash_data,sizeof(canaries));initialized=true;
}

void scratch_model_begin(unsigned page_bytes,uint64_t fail_at,unsigned mode)
{
    /* New operation counters/checkpoint; keep previous decode's physical temp data. */
    if(!initialized)scratch_model_pristine();
    memset(&stats,0,sizeof(stats));stats.page_bytes=page_bytes;stats.fail_at=fail_at;stats.mode=mode;stats.allowed=true;
}

jpeg_nor_device_t scratch_model_device(void)
{
    /* Same callback API consumed by the actual portable NOR core. */
    jpeg_nor_device_t device={&stats,sizeof(flash_data),stats.page_bytes,read_model,program_model,erase_model};return device;
}

int scratch_model_check(void *context)
{
    /* Exercise buffered reads/writes refusing a globally stopped decode. */
    (void)context;return stats.allowed ? 0 : -1;
}

scratch_model_stats_t scratch_model_stats(void)
{
    /* Independent issued physical operation/byte counters, not endurance. */
    return stats;
}

void scratch_model_allow(bool allowed)
{
    /* No I/O: model the deadline/transport checkpoint becoming unavailable. */
    stats.allowed=allowed;
}

bool scratch_model_canaries(void)
{
    /* Compare every other physical byte, including sparse holes and settings. */
    uint32_t start=0;
    for(unsigned i=0;i<SCRATCH_EXTENT_COUNT;++i) {
        if(memcmp(flash_data+start,canaries+start,scratch_extents[i].offset-start))return false;
        start=scratch_extents[i].offset+scratch_extents[i].bytes;
    }
    return !memcmp(flash_data+start,canaries+start,sizeof(flash_data)-start);
}

void scratch_model_copy_logical(void *out,uint32_t bytes)
{
    /* Flat independent oracle: concatenate extents without using NOR translation. */
    REQUIRE(bytes<=SCRATCH_LOGICAL_BYTES);uint8_t *p=out;
    for(unsigned i=0;i<SCRATCH_EXTENT_COUNT && bytes;++i) {
        uint32_t block=scratch_extents[i].bytes;if(block>bytes)block=bytes;
        memcpy(p,flash_data+scratch_extents[i].offset,block);p+=block;bytes-=block;
    }
    REQUIRE(!bytes);
}
