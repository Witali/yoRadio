/* Real resource SHA, deterministic clock, independent physical counts, bounds,
 * interleaved ports, expired epochs and exact pre/post-call budget boundaries. */
#include "../../storage/jpeg_transport.h"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "jpeg_layout.h"
#include "probe_map.h"

#define CHECK(v) do {++checks;if(!(v)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}}while(0)
static unsigned checks,cases;
static uint8_t flash_data[0x400000],buffer[512];
static jpeg_transport_t transport;
static jpeg_transport_port_t first,second;
static BCRYPT_ALG_HANDLE algorithm;
static struct {
    BCRYPT_HASH_HANDLE hash;
    uint64_t now,latency,finish_latency;
    unsigned reads,programs,erases,finishes;
    int error;
} model;
static const jpeg_transport_limits_t ample={10000,2097152,65536,32,100000};

static uint64_t clock_now(void *context)
{
    /* Tests advance time explicitly; no wall sleeps or timing races. */
    CHECK(context==&model);return model.now;
}

static int raw_read(void *context,uint32_t address,void *data,size_t bytes)
{
    /* Independently count actual issued operations, including partial failure. */
    CHECK(context==&model && address<=sizeof(flash_data) && bytes<=sizeof(flash_data)-address);
    ++model.reads;memcpy(data,flash_data+address,model.error ? bytes/2 : bytes);model.now+=model.latency;
    return model.error;
}

static int raw_program(void *context,uint32_t address,const void *data,size_t bytes)
{
    /* Driver model permits only a page-aligned1->0 request. */
    CHECK(context==&model && bytes==256 && address%256==0 && address<=sizeof(flash_data) && bytes<=sizeof(flash_data)-address);
    ++model.programs;const uint8_t *in=data;
    for(size_t i=0;i<bytes;++i)CHECK((flash_data[address+i]&in[i])==in[i]);
    for(size_t i=0;i<(model.error ? bytes/2 : bytes);++i)flash_data[address+i]&=in[i];
    model.now+=model.latency;return model.error;
}

static int raw_erase(void *context,uint32_t address)
{
    /* Exactly one authorized sector, with partial mutation on an I/O failure. */
    CHECK(context==&model && address%4096==0 && address<=sizeof(flash_data)-4096);
    ++model.erases;memset(flash_data+address,0xff,model.error ? 2048 : 4096);model.now+=model.latency;
    return model.error;
}

static int hash_begin(void *context)
{
    /* Actual SHA-256 provider shared with the independent asset manifest hashes. */
    CHECK(context==&model && !model.hash);
    return BCryptCreateHash(algorithm,&model.hash,NULL,0,NULL,0,0)<0 ? -1 : 0;
}

static int hash_update(void *context,const void *data,size_t bytes)
{
    /* Guard never bypasses the transport by hashing a cached expected digest. */
    CHECK(context==&model && model.hash && bytes<=256);
    return BCryptHashData(model.hash,(PUCHAR)data,(ULONG)bytes,0)<0 ? -1 : 0;
}

static int hash_finish(void *context,uint8_t digest[32])
{
    /* Expire time after the LAST hash too: authorization must check final time. */
    CHECK(context==&model && model.hash);
    if(++model.finishes==28)model.now+=model.finish_latency;
    return BCryptFinishHash(model.hash,digest,32,0)<0 ? -1 : 0;
}

static void hash_reset(void *context)
{
    /* Every outcome must release the real provider state. */
    CHECK(context==&model);
    if(model.hash)CHECK(BCryptDestroyHash(model.hash)>=0);
    model.hash=NULL;
}

static jpeg_transport_result_t authorize(const jpeg_transport_limits_t *limits)
{
    /* Fresh provider lifetime, stable raw flash/observed map. */
    model.finishes=0;
    jpeg_guard_sha256_t hash={&model,hash_begin,hash_update,hash_finish,hash_reset};
    jpeg_transport_result_t result=jpeg_transport_authorize(&transport,&jpeg_layout,jpeg_layout_partitions,
        jpeg_layout.partition_count,&hash,limits);
    CHECK(!model.hash);return result;
}

static void reset(void)
{
    /* No borrower survives this test-only context lifetime reset. */
    CHECK(!model.hash);memset(&transport,0,sizeof(transport));memset(&model,0,sizeof(model));
    memset(&first,0,sizeof(first));memset(&second,0,sizeof(second));model.now=100;
    jpeg_nor_device_t raw={&model,sizeof(flash_data),256,raw_read,raw_program,raw_erase};
    CHECK(jpeg_transport_init(&transport,&raw,clock_now,&model)==JPEG_TRANSPORT_OK);
    CHECK(jpeg_transport_begin(&transport,&ample)==JPEG_TRANSPORT_STATE);
    CHECK(authorize(&ample)==JPEG_TRANSPORT_OK && transport.authorized && !transport.active);
}

static jpeg_nor_device_t port(jpeg_transport_port_t *handle,const jpeg_nor_extent_t *range)
{
    /* Distinct immutable port objects live until every borrowed device is dropped. */
    jpeg_nor_device_t device;
    CHECK(jpeg_transport_port(&transport,handle,range,1,true,&device)==JPEG_TRANSPORT_OK);return device;
}

static void begin(const jpeg_transport_limits_t *limits)
{
    /* A new decoder job may reset its budget only after discarding all old RAM. */
    CHECK(jpeg_transport_begin(&transport,limits)==JPEG_TRANSPORT_OK);
}

static void test_limits(void)
{
    /* Exactly one shared call across distinct stores; no per-port quota reset. */
    reset();jpeg_transport_limits_t one={1,4,0,0,1000};begin(&one);
    jpeg_nor_device_t a=port(&first,probe_scratch);
    unsigned reads=model.reads;
    CHECK(!a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,4));
    jpeg_nor_device_t b=port(&second,probe_cache); /* creating another port cannot reset quota */
    CHECK(b.read(b.context,PROBE_CACHE_ADDRESS,buffer,1)!=0);
    CHECK(transport.last_error==JPEG_TRANSPORT_LIMIT && model.reads==reads+1 && transport.usage.calls==1);
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,1)!=0 && model.reads==reads+1);
    begin(&ample);CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,1)!=0 && transport.usage.calls==0);
    jpeg_transport_port_t next={0};a=port(&next,probe_scratch);
    CHECK(!a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,1));++cases;
    /* Byte limits independent of calls; rejected requests are not charged. */
    reset();one=ample;one.read_bytes=3;begin(&one);a=port(&first,probe_scratch);reads=model.reads;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,4)!=0 && model.reads==reads && !transport.usage.calls);++cases;
    reset();one=ample;one.program_bytes=255;begin(&one);a=port(&first,probe_scratch);
    CHECK(a.program(a.context,PROBE_SCRATCH_ADDRESS,buffer,256)!=0 && !model.programs && !transport.usage.calls);++cases;
    reset();one=ample;one.erase_calls=0;begin(&one);a=port(&first,probe_scratch);
    CHECK(a.erase_sector(a.context,PROBE_SCRATCH_ADDRESS)!=0 && !model.erases && !transport.usage.calls);++cases;
    reset();one=ample;one.calls=0;begin(&one);a=port(&first,probe_scratch);reads=model.reads;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,1)!=0 && model.reads==reads);++cases;
    reset();one=ample;one.program_bytes=256;one.erase_calls=1;begin(&one);a=port(&first,probe_scratch);
    memset(buffer,0xa5,256);
    CHECK(!a.erase_sector(a.context,PROBE_SCRATCH_ADDRESS));CHECK(!a.program(a.context,PROBE_SCRATCH_ADDRESS,buffer,256));
    CHECK(transport.usage.erase_calls==1 && transport.usage.program_bytes==256 && transport.usage.calls==2);++cases;
}

static void test_live_program_limit(void)
{
    /* Tighten without resetting any usage; stale ports and integer underflow
     * must not let an in-flight image escape the user's smaller quota. */
    reset();jpeg_transport_limits_t limits=ample;limits.program_bytes=512;
    begin(&limits);jpeg_nor_device_t a=port(&first,probe_scratch);
    memset(buffer,0,256);CHECK(!a.program(a.context,PROBE_SCRATCH_ADDRESS,buffer,256));
    CHECK(jpeg_transport_limit_program(&transport,4096)==JPEG_TRANSPORT_OK);
    CHECK(transport.limits.program_bytes==512 && transport.usage.program_bytes==256);
    CHECK(jpeg_transport_limit_program(&transport,256)==JPEG_TRANSPORT_OK);
    unsigned programs=model.programs;
    CHECK(a.program(a.context,PROBE_SCRATCH_ADDRESS,buffer,256)!=0 && model.programs==programs);
    CHECK(transport.program_limit_hit && transport.program_required==512 && transport.usage.program_bytes==256);
    CHECK(jpeg_transport_limit_program(&transport,4096)==JPEG_TRANSPORT_STATE);++cases;

    reset();begin(&ample);a=port(&first,probe_scratch);
    CHECK(!a.program(a.context,PROBE_SCRATCH_ADDRESS,buffer,256));
    CHECK(jpeg_transport_limit_program(&transport,0)==JPEG_TRANSPORT_LIMIT);
    CHECK(transport.program_limit_hit && transport.program_required==256 && !transport.active);
    CHECK(transport.limits.program_bytes==0 && transport.limits.erase_calls==0);++cases;

    reset();begin(&ample);a=port(&first,probe_scratch);
    CHECK(jpeg_transport_limit_program(&transport,0)==JPEG_TRANSPORT_OK);
    programs=model.programs;unsigned erases=model.erases;
    CHECK(a.erase_sector(a.context,PROBE_SCRATCH_ADDRESS)!=0 && model.erases==erases);
    CHECK(a.program(a.context,PROBE_SCRATCH_ADDRESS,buffer,256)!=0 && model.programs==programs);
    CHECK(!transport.usage.program_bytes && !transport.usage.erase_calls);++cases;
}

static void test_time_and_faults(void)
{
    /* Before-call deadline, after-call overrun, rollback and large timestamp. */
    reset();jpeg_transport_limits_t small=ample;small.duration_us=10;begin(&small);
    jpeg_nor_device_t a=port(&first,probe_scratch);unsigned reads=model.reads;model.now+=10;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,1)!=0 && transport.last_error==JPEG_TRANSPORT_TIME && model.reads==reads);++cases;
    reset();begin(&small);a=port(&first,probe_scratch);reads=model.reads;model.latency=10;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,1)!=0 && transport.last_error==JPEG_TRANSPORT_TIME && model.reads==reads+1 && transport.usage.calls==1);++cases;
    reset();begin(&small);model.now--;
    CHECK(jpeg_transport_check(&transport)==JPEG_TRANSPORT_CLOCK && !transport.active);++cases;
    reset();model.now=UINT64_MAX-10;begin(&small);a=port(&first,probe_scratch);model.now+=5;
    CHECK(!a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,1));++cases;
    reset();model.finish_latency=ample.duration_us;
    CHECK(authorize(&ample)==JPEG_TRANSPORT_TIME && !transport.authorized);++cases;
    reset();begin(&ample);a=port(&first,probe_scratch);reads=model.reads;model.error=-77;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,8)!=0 && transport.last_error==JPEG_TRANSPORT_IO);
    CHECK(model.reads==reads+1 && transport.usage.calls==1 && transport.usage.read_bytes==8);
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,8)!=0 && model.reads==reads+1);model.error=0;++cases;
    reset();model.error=-77;CHECK(authorize(&ample)==JPEG_TRANSPORT_IO && !transport.authorized);model.error=0;++cases;
    for(unsigned operation=0;operation<2;++operation) {
        reset();begin(&ample);a=port(&first,probe_scratch);model.error=-77;
        memset(buffer,0,256); /* legal1->0 even on previously programmed pages */
        int error=operation ? a.erase_sector(a.context,PROBE_SCRATCH_ADDRESS) : a.program(a.context,PROBE_SCRATCH_ADDRESS,buffer,256);
        CHECK(error && transport.last_error==JPEG_TRANSPORT_IO && transport.usage.calls==1 && !transport.active);
        CHECK(transport.usage.program_bytes==(operation ? 0u : 256u));
        CHECK(transport.usage.erase_calls==(operation ? 1u : 0u));model.error=0;++cases;
    }
    reset();transport.epoch=UINT64_MAX;
    CHECK(jpeg_transport_begin(&transport,&ample)==JPEG_TRANSPORT_STATE && !transport.active);++cases;
}

static void test_scopes(void)
{
    /* Whole ranges, writable ownership, readonly assets, null/alias/wrap inputs. */
    const uint32_t denied[]={0,0x9000,0x10000,0x200000,0x28f000,0x3e7000};
    reset();begin(&ample);
    for(unsigned i=0;i<sizeof(denied)/sizeof(denied[0]);++i) {
        jpeg_nor_extent_t range={denied[i],4096};jpeg_nor_device_t io;
        CHECK(jpeg_transport_port(&transport,&first,&range,1,true,&io)==JPEG_TRANSPORT_RANGE);++cases;
    }
    jpeg_nor_device_t a=port(&first,probe_scratch);unsigned reads=model.reads;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS+8191,buffer,2)!=0 && model.reads==reads && !transport.usage.calls);++cases;
    reset();begin(&ample);a=port(&first,probe_scratch);reads=model.reads;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,NULL,4)!=0 && model.reads==reads && !transport.usage.calls);++cases;
    reset();begin(&ample);a=port(&first,probe_scratch);reads=model.reads;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,&transport,4)!=0 && model.reads==reads && !transport.usage.calls);++cases;
    reset();begin(&ample);a=port(&first,probe_scratch);reads=model.reads;
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,(void *)(UINTPTR_MAX-1),8)!=0 && model.reads==reads);++cases;
    reset();begin(&ample);a=port(&first,probe_scratch);
    CHECK(a.program(a.context,PROBE_SCRATCH_ADDRESS+1,buffer,256)!=0 && !model.programs);++cases;
    reset();begin(&ample);jpeg_nor_extent_t photo={0x200123,293};
    CHECK(jpeg_transport_port(&transport,&first,&photo,1,false,&a)==JPEG_TRANSPORT_OK);
    CHECK(!a.read(a.context,photo.offset,buffer,293));
    CHECK(a.erase_sector(a.context,0x200000)!=0 && !model.erases);++cases;
    reset();begin(&ample);photo=(jpeg_nor_extent_t){0x200000,4096};
    CHECK(jpeg_transport_port(&transport,&first,&photo,1,false,&a)==JPEG_TRANSPORT_OK);
    CHECK(a.erase_sector(a.context,photo.offset)!=0 && !model.erases && !transport.usage.calls);++cases;
    reset();begin(&ample);a=port(&first,probe_scratch);
    uint32_t stamp=JPEG_LAYOUT_OWNERSHIP_STAMP_ADDRESS;
    flash_data[stamp]^=1;
    CHECK(authorize(&ample)==JPEG_TRANSPORT_GUARD && !transport.authorized);
    CHECK(a.read(a.context,PROBE_SCRATCH_ADDRESS,buffer,1)!=0);flash_data[stamp]^=1;++cases;
    reset();begin(&ample);jpeg_transport_revoke(&transport);
    CHECK(jpeg_transport_check(&transport)==JPEG_TRANSPORT_STATE);++cases;
}

int main(int argc,char **argv)
{
    /* Sanitized build assets only; no COM ports, SDK or physical device access. */
    CHECK(argc==2 && BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0)>=0);
    memset(flash_data,0xff,sizeof(flash_data));FILE *file=fopen(argv[1],"rb");CHECK(file);
    CHECK(fread(flash_data+0x200000,1,0x1e7000,file)==0x1e7000 && fgetc(file)==EOF);CHECK(!fclose(file));
    test_limits();test_live_program_limit();test_time_and_faults();test_scopes();CHECK(!model.hash);
    CHECK(BCryptCloseAlgorithmProvider(algorithm,0)>=0);
    printf("{\"passed\":true,\"checks\":%u,\"cases\":%u,\"physical_hardware_tested\":false}\n",checks,cases);
    return 0;
}
