/* Cache producer/storage contract with independent physical bytes and OS SHA. */
#include "jpeg_cache_layout.h"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FLASH_BYTES 0x400000u
#define CHECK(v) do{++checks;if(!(v)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}}while(0)
static uint64_t checks;
static unsigned fault_cases,stop_cases,hash_fault_cases;
static uint8_t flash_data[FLASH_BYTES],baseline[FLASH_BYTES];
static jpeg_cache_t cache;
static BCRYPT_ALG_HANDLE algorithm;
static BCRYPT_HASH_HANDLE live_hash;
static jmp_buf cut;
static unsigned roles[]={0,1,2,3};
static struct {
    unsigned calls,programs,erases,fail_at,mode,hits,active_slot,hash_calls,hash_fail,hash_hits,stop_at;
    uint64_t read_bytes,program_bytes,role_calls[4],role_program_bytes[4];
    uint64_t hash_bytes,hash_frame_bytes;
    bool require_physical_hash;
    bool allowed,frame_checked;
} model;
static jpeg_guard_sha256_t hash_provider;
static jpeg_cache_devices_t devices;

static bool inside(uint32_t at,size_t bytes,const jpeg_nor_extent_t *ranges,unsigned count)
{
    /* Independent whole-request role bounds; source cannot write by construction. */
    for(unsigned i=0;i<count;++i)
        if(at>=ranges[i].offset && at-ranges[i].offset<=ranges[i].bytes && bytes<=ranges[i].bytes-(at-ranges[i].offset))return true;
    return false;
}

static void address(unsigned role,uint32_t at,size_t bytes,bool writing)
{
    /* Every operation belongs to one of readonly source, frame, two metadata banks. */
    CHECK(at<=FLASH_BYTES && bytes && bytes<=FLASH_BYTES-at);bool valid=false;
    if(role==0) {
        CHECK(!writing);
        for(unsigned s=0;s<5;++s) {
            uint32_t start=jpeg_cache_layout.source_offsets[s];
            if(at>=start && at-start<=jpeg_cache_layout.journal.source_limit && bytes<=jpeg_cache_layout.journal.source_limit-(at-start))valid=true;
        }
    } else if(role==1) {
        for(unsigned s=0;s<5;++s)
            if((!writing || s==model.active_slot) && inside(at,bytes,jpeg_cache_layout.frames[s].extents,jpeg_cache_layout.frames[s].count))valid=true;
    } else if(role==3) {
        valid=inside(at,bytes,jpeg_cache_scratch_extents,JPEG_CACHE_SCRATCH_EXTENTS);
    } else {
        CHECK(role==2);
        for(unsigned b=0;b<2;++b) {
            uint32_t start=jpeg_cache_layout.journal.banks[b];
            if(at>=start && at-start<=4096 && bytes<=4096-(at-start))valid=true;
        }
    }
    CHECK(valid);
}

static uint32_t word(const uint8_t *p)
{
    /* Independent wire reader, never a native journal struct cast. */
    return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

static void before_frame_write(void)
{
    /* Independently require a complete committed INVALID record on physical
     * flash before first frame mutation; RAM ready flags are insufficient. */
    if(model.frame_checked)return;
    uint64_t generation=0;const uint8_t *selected=NULL;
    for(unsigned b=0;b<2;++b) {
        const uint8_t *body=flash_data+jpeg_cache_layout.journal.banks[b],*footer=body+3840;
        uint32_t crc=UINT32_MAX;
        for(unsigned i=0;i<508;++i){crc^=body[i];for(unsigned bit=0;bit<8;++bit)crc=(crc>>1)^((crc&1) ? 0xedb88320u:0);}
        crc^=UINT32_MAX;
        uint64_t seq=word(body+16)|((uint64_t)word(body+20)<<32);
        if(!memcmp(body,"STVJC01",8) && crc==word(body+508) && !memcmp(footer,"STVCMT1",8) &&
           seq==(word(footer+8)|((uint64_t)word(footer+12)<<32)) && crc==word(footer+16) && (crc^UINT32_MAX)==word(footer+20) && seq>generation) {
            generation=seq;selected=body;
        }
    }
    CHECK(selected && !word(selected+112+model.active_slot*72));model.frame_checked=true;
}

static bool fault(void)
{
    /* A physical failure changes real bytes before returning or losing RAM. */
    bool hit=++model.calls==model.fail_at;if(hit)++model.hits;return hit;
}

static size_t transferred(size_t bytes,bool hit)
{
    /*1partial error,2silent partial,3full cut,4half cut,5before-operation cut. */
    return !hit || model.mode==3 || model.mode==6 ? bytes : model.mode==5 ? 0:bytes/2;
}

static int outcome(bool hit)
{
    /* Revocation also occurs after individual physical callbacks, as in transport. */
    if(hit && model.mode>=3 && model.mode<=5)longjmp(cut,1);
    if(model.stop_at && model.calls>=model.stop_at)model.allowed=false;
    return hit && model.mode==1 ? -77:!model.allowed ? -78:0;
}

static int read_device(void *context,uint32_t at,void *data,size_t bytes)
{
    /* A revoked wrapper never issues another physical operation. */
    if(!model.allowed)return -78;
    unsigned role=*(unsigned *)context;address(role,at,bytes,false);bool hit=fault();
    model.read_bytes+=bytes;++model.role_calls[role];
    if(live_hash && role==1)model.hash_frame_bytes+=bytes;
    memcpy(data,flash_data+at,transferred(bytes,hit));if(hit && model.mode==2)((uint8_t *)data)[0]^=1;
    if(hit && model.mode==6)((uint8_t *)data)[bytes/2]^=1;
    return outcome(hit);
}

static int program_device(void *context,uint32_t at,const void *data,size_t bytes)
{
    /* Strict256byte pages and one-way bits; no magical overwrite of NOR cells. */
    if(!model.allowed)return -78;
    unsigned role=*(unsigned *)context;address(role,at,bytes,true);
    CHECK(bytes==256 && at%256==0);if(role==1)before_frame_write();
    const uint8_t *in=data;for(size_t i=0;i<bytes;++i)CHECK((flash_data[at+i]&in[i])==in[i]);
    bool hit=fault();++model.programs;model.program_bytes+=bytes;model.role_program_bytes[role]+=bytes;++model.role_calls[role];
    for(size_t i=0;i<transferred(bytes,hit);++i)flash_data[at+i]&=in[i];return outcome(hit);
}

static int erase_device(void *context,uint32_t at)
{
    /* Partial erase really leaves old suffix bytes behind. */
    if(!model.allowed)return -78;
    unsigned role=*(unsigned *)context;address(role,at,4096,true);CHECK(at%4096==0);if(role==1)before_frame_write();
    bool hit=fault();++model.erases;++model.role_calls[role];memset(flash_data+at,0xff,transferred(4096,hit));return outcome(hit);
}

static bool hash_fault(void)
{
    /* Crypto failure never silently publishes unhashed output. */
    bool hit=++model.hash_calls==model.hash_fail;if(hit)++model.hash_hits;return hit;
}

static int hash_begin(void *context)
{
    /* Create real provider state even when a partial setup is made to fail. */
    (void)context;CHECK(!live_hash && BCryptCreateHash(algorithm,&live_hash,NULL,0,NULL,0,0)>=0);
    model.hash_bytes=0;model.hash_frame_bytes=0;model.require_physical_hash=!cache.journal.pending || cache.writing;
    return hash_fault() ? -90:0;
}

static int hash_update(void *context,const void *data,size_t bytes)
{
    /* Feed actual bounded bytes, not a synthetic expected digest callback. */
    (void)context;CHECK(live_hash && bytes<=ULONG_MAX && BCryptHashData(live_hash,(PUCHAR)data,(ULONG)bytes,0)>=0);
    model.hash_bytes+=bytes;return hash_fault() ? -91:0;
}

static int hash_finish(void *context,uint8_t digest[32])
{
    /* Actual OS SHA is independent of journal wire encoding and C row producer. */
    (void)context;CHECK(live_hash && BCryptFinishHash(live_hash,digest,32,0)>=0);
    if(model.require_physical_hash && model.hash_bytes==115200u)CHECK(model.hash_frame_bytes==115200u);
    return hash_fault() ? -92:0;
}

static void hash_reset(void *context)
{
    /* Releasing provider state cannot perform flash I/O or depend on time budget. */
    (void)context;if(live_hash){CHECK(BCryptDestroyHash(live_hash)>=0);live_hash=NULL;}
}

static int check(void *context)
{
    /* RAM row copies, hashes and cleanup exercise the same stop state. */
    (void)context;return model.allowed ? 0:-1;
}

static void fresh(unsigned fail,unsigned mode,unsigned stop,unsigned hash_fail)
{
    /* Model a reset: drop all RAM caches without executing target cleanup. */
    hash_reset(NULL);memset(&cache,0,sizeof(cache));memset(&model,0,sizeof(model));
    model.allowed=true;model.fail_at=fail;model.mode=mode;model.stop_at=stop;model.hash_fail=hash_fail;
}

static jpeg_cache_result_t open_cache(void)
{
    /* Real cache+NOR+journal, with per-role independent capabilities. */
    return jpeg_cache_open(&cache,&jpeg_cache_layout,&devices,&hash_provider,check,NULL);
}

static uint16_t pixel(unsigned slot,bool newer,uint32_t x,uint32_t y)
{
    /* Independent synthetic row producer, not a claim of JPEG semantic decoding. */
    return (uint16_t)((x*177u+y*91u+slot*723u)^(newer ? 0x9c71u:0x1b35u));
}

static jpeg_cache_result_t update(unsigned slot,bool newer)
{
    /* Production owner sequence: invalidate, bounded rows, verified publication. */
    model.active_slot=slot;model.frame_checked=false;
    jpeg_cache_result_t result=jpeg_cache_begin(&cache,slot,1023);if(result)return result;
    uint16_t pixels[240];
    for(uint32_t y=0;y<240;++y) {
        for(uint32_t x=0;x<240;++x)pixels[x]=pixel(slot,newer,x,y);
        result=jpeg_cache_write_row(&cache,y,pixels,240);if(result)return result;
    }
    return jpeg_cache_commit(&cache);
}

static void verify_rows(unsigned slot,bool newer)
{
    /* Verify EVERY sample; a mixture of old/new rows is never an accepted frame. */
    uint16_t pixels[240];
    for(uint32_t y=0;y<240;++y) {
        CHECK(jpeg_cache_read_row(&cache,y,pixels,240)==JPEG_CACHE_OK);
        for(uint32_t x=0;x<240;++x)CHECK(pixels[x]==pixel(slot,newer,x,y));
    }
}

static void abort_cache(void)
{
    /* Cleanup after any error/deadline must not issue one more physical callback. */
    unsigned calls=model.calls;jpeg_cache_abort(&cache);CHECK(model.calls==calls && !live_hash);
}

static void protected_bytes(void)
{
    /* Compare every sector outside this one frame and the metadata pair. */
    const jpeg_cache_map_t *map=&jpeg_cache_layout.frames[0];
    for(uint32_t at=0;at<FLASH_BYTES;at+=4096) {
        bool writable=inside(at,4096,map->extents,map->count);
        for(unsigned b=0;b<2;++b)if(at==jpeg_cache_layout.journal.banks[b])writable=true;
        if(!writable)CHECK(!memcmp(flash_data+at,baseline+at,4096));
    }
}

static void lifecycle(void)
{
    /* Populate all five sparse frames and prove actual readonly hits after reset. */
    for(unsigned s=0;s<5;++s) {
        fresh(0,0,0,0);CHECK(open_cache()==0 && update(s,false)==0);verify_rows(s,false);abort_cache();
    }
    memcpy(baseline,flash_data,FLASH_BYTES);
    for(unsigned s=0;s<5;++s) {
        fresh(0,0,0,0);CHECK(open_cache()==0 && jpeg_cache_lookup(&cache,s,1023)==0);
        verify_rows(s,false);CHECK(!model.programs && !model.erases);abort_cache();
    }
    /* Invalid calls cannot touch storage, including owner-alias and wrap ranges. */
    fresh(0,0,0,0);CHECK(open_cache()==0);unsigned calls=model.calls;uint16_t row[240];
    CHECK(jpeg_cache_write_row(&cache,0,row,240)==JPEG_CACHE_STATE);
    CHECK(jpeg_cache_read_row(&cache,0,row,240)==JPEG_CACHE_STATE);
    CHECK(jpeg_cache_begin(&cache,5,1023)==JPEG_CACHE_ARGUMENT && jpeg_cache_begin(&cache,0,0)==JPEG_CACHE_ARGUMENT);
    CHECK(jpeg_cache_begin(&cache,0,102401)==JPEG_CACHE_SOURCE_LIMIT && cache.required==102401 && cache.available==102400 && model.calls==calls);
    CHECK(model.calls==calls && jpeg_cache_begin(&cache,0,1023)==0);calls=model.calls;
    CHECK(jpeg_cache_write_row(&cache,1,row,240)==JPEG_CACHE_ARGUMENT);
    CHECK(jpeg_cache_write_row(&cache,0,row,239)==JPEG_CACHE_ARGUMENT);
    CHECK(jpeg_cache_write_row(&cache,0,(uint16_t *)&cache,240)==JPEG_CACHE_ARGUMENT);
    CHECK(jpeg_cache_read_source(&cache,1023,row,1)==JPEG_CACHE_ARGUMENT);
    CHECK(jpeg_cache_read_source(&cache,0,(void *)UINTPTR_MAX,4)==JPEG_CACHE_ARGUMENT);
    CHECK(jpeg_cache_read_source(&cache,0,&cache,16)==JPEG_CACHE_ARGUMENT);
    CHECK(jpeg_cache_commit(&cache)==JPEG_CACHE_STATE && model.calls==calls);abort_cache();
    memcpy(flash_data,baseline,FLASH_BYTES);
    /* A same-length physical source change must invalidate the cache identity. */
    flash_data[jpeg_cache_layout.source_offsets[0]+37]^=1;fresh(0,0,0,0);CHECK(open_cache()==0);
    CHECK(jpeg_cache_lookup(&cache,0,1023)==JPEG_CACHE_MISS && !model.programs && !model.erases);
    calls=model.calls;CHECK(jpeg_cache_read_row(&cache,0,row,240)==JPEG_CACHE_STATE && model.calls==calls);abort_cache();
    memcpy(flash_data,baseline,FLASH_BYTES);
    /* A previously cached RAM sector cannot hide later physical corruption. */
    fresh(0,0,0,0);CHECK(open_cache()==0 && jpeg_cache_lookup(&cache,0,1023)==0);
    CHECK(jpeg_cache_read_row(&cache,0,row,240)==0);
    flash_data[jpeg_cache_layout.frames[0].extents[0].offset+91]^=1;
    CHECK(jpeg_cache_lookup(&cache,0,1023)==JPEG_CACHE_VERIFY);
    calls=model.calls;CHECK(jpeg_cache_read_row(&cache,0,row,240)==JPEG_CACHE_STATE && model.calls==calls);abort_cache();
    memcpy(flash_data,baseline,FLASH_BYTES);
    /* Simulate source modification during row generation; never publish it. */
    fresh(0,0,0,0);CHECK(open_cache()==0 && jpeg_cache_begin(&cache,0,1023)==0);
    model.active_slot=0;
    for(unsigned y=0;y<240;++y){for(unsigned x=0;x<240;++x)row[x]=pixel(0,true,x,y);CHECK(jpeg_cache_write_row(&cache,y,row,240)==0);}
    flash_data[jpeg_cache_layout.source_offsets[0]+31]^=1;
    CHECK(jpeg_cache_commit(&cache)==JPEG_CACHE_SOURCE_CHANGED && !cache.journal.entries[0].ready);abort_cache();
    memcpy(flash_data,baseline,FLASH_BYTES);
    /* Damaged latest invalid record must not authorize a stale ready fallback. */
    fresh(0,0,0,0);CHECK(open_cache()==0 && jpeg_cache_invalidate(&cache,0)==0);
    unsigned newest=cache.journal.bank;abort_cache();
    flash_data[jpeg_cache_layout.journal.banks[newest]+200]^=1;
    flash_data[jpeg_cache_layout.frames[0].extents[0].offset+91]^=1;
    fresh(0,0,0,0);CHECK(open_cache()==0 && cache.journal.entries[0].ready);
    CHECK(jpeg_cache_lookup(&cache,0,1023)==JPEG_CACHE_VERIFY);abort_cache();
    memcpy(flash_data,baseline,FLASH_BYTES);
}

static void invalid_layouts(void)
{
    /* Reject bad later slots and borrowed descriptor aliases before metadata I/O. */
    for(unsigned change=0;change<15;++change) {
        fresh(0,0,0,0);jpeg_cache_layout_t l=jpeg_cache_layout;jpeg_cache_devices_t d=devices;
        jpeg_guard_sha256_t h=hash_provider;jpeg_nor_extent_t maps[5][JPEG_NOR_MAX_EXTENTS],allowed[JPEG_NOR_MAX_EXTENTS];
        memcpy(allowed,l.allowed,l.allowed_count*sizeof(*allowed));l.allowed=allowed;
        for(unsigned s=0;s<5;++s){memcpy(maps[s],l.frames[s].extents,l.frames[s].count*sizeof(maps[s][0]));l.frames[s].extents=maps[s];}
        switch(change) {
        case 0:l.width=0;break;
        case 1:l.height=241;break;
        case 2:++l.journal.frame_bytes;break;
        case 3:++l.source_offsets[3];break;
        case 4:l.source_offsets[4]=UINT32_MAX;break;
        case 5:l.journal.banks[1]=l.journal.banks[0];break;
        case 6:maps[4][0].offset=l.source_offsets[0];break;
        case 7:l.frames[4]=l.frames[0];break;
        case 8:l.frames[4].count=17;break;
        case 9:l.frames[4].extents=NULL;break;
        case 10:l.allowed_count=0;break;
        case 11:l.allowed_count=17;break;
        case 12:allowed[1]=allowed[0];break;
        case 13:--d.source.flash_bytes;break;
        case 14:h.reset=NULL;break;
        }
        CHECK(jpeg_cache_open(&cache,&l,&d,&h,check,NULL)==JPEG_CACHE_ARGUMENT && !cache.open && !model.calls && !live_hash);
    }
    fresh(0,0,0,0);jpeg_cache_layout_t l=jpeg_cache_layout;
    memcpy(cache.frame.extents,l.allowed,l.allowed_count*sizeof(jpeg_nor_extent_t));l.allowed=cache.frame.extents;
    CHECK(jpeg_cache_open(&cache,&l,&devices,&hash_provider,check,NULL)==JPEG_CACHE_ARGUMENT && !model.calls);
    fresh(0,0,0,0);l=jpeg_cache_layout;
    memcpy(cache.frame.extents,l.frames[4].extents,l.frames[4].count*sizeof(jpeg_nor_extent_t));l.frames[4].extents=cache.frame.extents;
    CHECK(jpeg_cache_open(&cache,&l,&devices,&hash_provider,check,NULL)==JPEG_CACHE_ARGUMENT && !model.calls);
    fresh(0,0,0,0);cache.devices=devices;
    CHECK(jpeg_cache_open(&cache,&jpeg_cache_layout,&cache.devices,&hash_provider,check,NULL)==JPEG_CACHE_ARGUMENT && !model.calls);
    fresh(0,0,0,0);cache.hash=hash_provider;
    CHECK(jpeg_cache_open(&cache,&jpeg_cache_layout,&devices,&cache.hash,check,NULL)==JPEG_CACHE_ARGUMENT && !model.calls);
    fresh(0,0,0,0);model.allowed=false;
    CHECK(open_cache()==JPEG_CACHE_STOP && !model.calls);abort_cache();
    fresh(0,0,0,0);CHECK(open_cache()==0 && jpeg_cache_lookup(&cache,0,1023)==0);
    uint16_t row[240];unsigned calls=model.calls;model.allowed=false;
    CHECK(jpeg_cache_read_row(&cache,0,row,240)==JPEG_CACHE_STOP && model.calls==calls);abort_cache();
}

static void recovery(void)
{
    /* Cold source+frame verification admits only a whole old/new producer frame. */
    fresh(0,0,0,0);CHECK(open_cache()==0);
    jpeg_cache_result_t found=jpeg_cache_lookup(&cache,0,1023);
    if(found==JPEG_CACHE_OK) {
        uint16_t row[240];CHECK(jpeg_cache_read_row(&cache,0,row,240)==0);
        bool newer=row[0]==pixel(0,true,0,0);CHECK(newer || row[0]==pixel(0,false,0,0));verify_rows(0,newer);
    } else CHECK(found==JPEG_CACHE_MISS || found==JPEG_CACHE_VERIFY);
    CHECK(!model.programs && !model.erases);abort_cache();protected_bytes();
}

static void failures(bool quick)
{
    /* Sweep every physical callback, actual crypto phase, and power-cut position. */
    memcpy(flash_data,baseline,FLASH_BYTES);fresh(0,0,0,0);CHECK(open_cache()==0 && update(0,true)==0);
    unsigned calls=model.calls,hashes=model.hash_calls;abort_cache();
    unsigned step=quick ? calls/13u:1u;if(!step)step=1;
    for(unsigned mode=1;mode<=5;++mode)for(unsigned at=1;at<=calls;at+=step) {
        memcpy(flash_data,baseline,FLASH_BYTES);fresh(at,mode,0,0);
        if(!setjmp(cut)) {
            jpeg_cache_result_t result=open_cache();if(!result)result=update(0,true);
            if(result==JPEG_CACHE_OK)CHECK(mode==2);
            else if(cache.failed){unsigned n=model.calls;CHECK(jpeg_cache_lookup(&cache,0,1023)==JPEG_CACHE_STATE && model.calls==n);}
            abort_cache();
        }
        CHECK(model.hits==1);++fault_cases;protected_bytes();recovery();
    }
    for(unsigned at=1;at<=hashes;at+=quick ? 71u:1u) {
        memcpy(flash_data,baseline,FLASH_BYTES);fresh(0,0,0,at);
        jpeg_cache_result_t result=open_cache();if(!result)result=update(0,true);
        CHECK(result==JPEG_CACHE_HASH && model.hash_hits==1);abort_cache();++hash_fault_cases;recovery();
    }
    for(unsigned at=1;at<=calls;at+=quick ? step:1u) {
        memcpy(flash_data,baseline,FLASH_BYTES);fresh(0,0,at,0);
        jpeg_cache_result_t result=open_cache();if(!result)result=update(0,true);
        CHECK(result!=JPEG_CACHE_OK && model.calls==at && !model.allowed);abort_cache();++stop_cases;recovery();
    }
    printf("\"update_physical_calls\":%u,\"update_hash_callbacks\":%u,",calls,hashes);
}

int main(int argc,char **argv)
{
    /* Large arrays are an independent host model, not firmware/cache allocations. */
    CHECK(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0)>=0);
    for(size_t i=0;i<sizeof(flash_data);++i)flash_data[i]=(uint8_t)(i*17u+(i>>9));
    for(unsigned b=0;b<2;++b)memset(flash_data+jpeg_cache_layout.journal.banks[b],0xff,4096);
    hash_provider=(jpeg_guard_sha256_t){NULL,hash_begin,hash_update,hash_finish,hash_reset};
    devices=(jpeg_cache_devices_t){
        {&roles[0],FLASH_BYTES,256,read_device,NULL,NULL},
        {&roles[1],FLASH_BYTES,256,read_device,program_device,erase_device},
        {&roles[2],FLASH_BYTES,256,read_device,program_device,erase_device}};
    lifecycle();invalid_layouts();printf("{");failures(argc==2 && !strcmp(argv[1],"--quick"));
    CHECK(BCryptCloseAlgorithmProvider(algorithm,0)>=0);
    printf("\"passed\":true,\"checks\":%llu,\"physical_fault_cases\":%u,\"hash_fault_cases\":%u,\"stop_cases\":%u}\n",
        (unsigned long long)checks,fault_cases,hash_fault_cases,stop_cases);return 0;
}
