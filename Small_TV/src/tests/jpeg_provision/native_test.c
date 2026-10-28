/* Actual OS SHA, strict NOR, complete4MiB preservation and bootstrap capabilities. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "jpeg_transport.h"
#include "jpeg_layout.h"

#define FLASH_BYTES 0x400000u
#define STAMP JPEG_LAYOUT_OWNERSHIP_STAMP_ADDRESS
#define CHECK(v) do{++checks;if(!(v)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}}while(0)
static unsigned checks,cases,occupied_cases,silent_cases,cuts,io_cases,quota_cases,hash_cases,incompatible_cases;
static uint8_t flash[FLASH_BYTES],legacy[FLASH_BYTES];
static BCRYPT_ALG_HANDLE algorithm;
static jpeg_transport_t transport;
static jpeg_guard_layout_t layout;
static jpeg_guard_resource_t resources[JPEG_GUARD_MAX_RESOURCES];
static jpeg_guard_partition_t parts[JPEG_GUARD_MAX_PARTITIONS];
static jpeg_provision_stamp_t stamp;
static jpeg_provision_diagnostic_t diagnostic;
static const jpeg_transport_limits_t ample={30000,0x800000,64,0,1000000};
static struct {
    BCRYPT_HASH_HANDLE hash;
    uint64_t now,latency;
    unsigned reads,programs,erases,hash_calls,hash_resets,hash_begins;
    unsigned fail_read,silent_read,fail_hash,partial_bits,cut_program;
    uint32_t hide_address;
    unsigned hide_occurrence,hide_seen;
    bool program_error,program_corrupt,mutate_resource;
} model;

static uint64_t now(void *context)
{
    /* Advance only in actual physical callbacks; observer time cannot pass tests. */
    CHECK(context==&model);return model.now;
}

static bool immutable(uint32_t at,size_t bytes)
{
    /* Independent permitted read set excludes photos, preferences and boot data. */
    for(unsigned i=0;i<jpeg_layout.resource_count;++i) {
        const jpeg_guard_resource_t *r=&jpeg_layout.resources[i];
        if(at>=r->offset && at-r->offset<r->bytes && bytes<=r->bytes-(at-r->offset))return true;
    }
    return false;
}

static bool candidate(uint32_t at,size_t bytes)
{
    /* Exactly the generated complete sectors, not merely arbitrary FF bytes. */
    for(unsigned i=0;i<jpeg_layout.allowed_count;++i) {
        const jpeg_nor_extent_t *r=&jpeg_layout.allowed[i];
        if(at>=r->offset && at-r->offset<r->bytes && bytes<=r->bytes-(at-r->offset))return true;
    }
    return false;
}

static int read_flash(void *context,uint32_t at,void *data,size_t bytes)
{
    /* Inject partial I/O and one silent read independently of the module's checks. */
    CHECK(context==&model && bytes && bytes<=256 && at<=FLASH_BYTES && bytes<=FLASH_BYTES-at);
    CHECK(immutable(at,bytes) || candidate(at,bytes));
    ++model.reads;model.now+=model.latency;
    memcpy(data,flash+at,model.reads==model.fail_read ? bytes/2:bytes);
    if(model.reads==model.fail_read)return -77;
    if(model.reads==model.silent_read)((uint8_t *)data)[0]^=1;
    if(at==model.hide_address && ++model.hide_seen==model.hide_occurrence)memset(data,255,bytes);
    return 0;
}

static int program_flash(void *context,uint32_t at,const void *data,size_t bytes)
{
    /* Only identity then commit-header spans; no RMW of neighboring animation. */
    CHECK(context==&model && ((at==STAMP+8 && bytes==32) || (at==STAMP && bytes==8)));
    CHECK(!memcmp(data,jpeg_layout_stamp.bytes+at-STAMP,bytes));
    CHECK(at/256==(at+(uint32_t)bytes-1u)/256);
    ++model.programs;model.now+=model.latency;unsigned zeros=0;
    bool cutting=model.programs==model.cut_program;
    for(unsigned i=0;i<bytes;++i) {
        uint8_t target=((const uint8_t *)data)[i];CHECK((flash[at+i]&target)==target);
        for(unsigned bit=0;bit<8;++bit)if(!(target&(1u<<bit))) {
            if(zeros++<(cutting ? model.partial_bits:UINT_MAX))flash[at+i]&=(uint8_t)~(1u<<bit);
        }
    }
    if(model.program_corrupt) {
        bool corrupted=false;
        for(unsigned i=0;i<bytes && !corrupted;++i)for(unsigned bit=0;bit<8 && !corrupted;++bit)
            if(((const uint8_t *)data)[i]&(1u<<bit)){flash[at+i]&=(uint8_t)~(1u<<bit);corrupted=true;}
        CHECK(corrupted);
    }
    if(model.mutate_resource && model.programs==1)flash[jpeg_layout.resources[0].offset]^=1;
    return cutting && model.program_error ? -88:0;
}

static int erase_flash(void *context,uint32_t at)
{
    /* Even rejection/recovery may never erase anything. */
    (void)context;(void)at;++model.erases;CHECK(false);return -99;
}

static bool hash_failure(void)
{
    /* Every provider stage can fail while holding an actual OS hash handle. */
    return ++model.hash_calls==model.fail_hash;
}

static int hash_begin(void *context)
{
    /* Use OS SHA-256, independent of target PSA and generated Python digests. */
    CHECK(context==&model && !model.hash);++model.hash_begins;
    CHECK(BCryptCreateHash(algorithm,&model.hash,NULL,0,NULL,0,0)==0);
    return hash_failure() ? -91:0;
}

static int hash_update(void *context,const void *data,size_t bytes)
{
    /* All input is physically read bytes, or the explicitly named future stamp. */
    CHECK(context==&model && model.hash && bytes<=256);
    CHECK(BCryptHashData(model.hash,(PUCHAR)data,(ULONG)bytes,0)==0);
    return hash_failure() ? -91:0;
}

static int hash_finish(void *context,uint8_t digest[32])
{
    /* Failed finalization must not publish bootstrap authority. */
    CHECK(context==&model && model.hash);CHECK(BCryptFinishHash(model.hash,digest,32,0)==0);
    return hash_failure() ? -91:0;
}

static void hash_reset(void *context)
{
    /* Cleanup after every attempted begin, including failure after allocation. */
    CHECK(context==&model);if(model.hash)CHECK(BCryptDestroyHash(model.hash)==0);
    model.hash=NULL;++model.hash_resets;
}

static void reset(void)
{
    /* Each simulated boot starts from an independently retained legacy image. */
    CHECK(!model.hash);memset(&model,0,sizeof(model));model.partial_bits=UINT_MAX;
    memcpy(flash,legacy,sizeof(flash));memset(&transport,0,sizeof(transport));
    layout=jpeg_layout;stamp=jpeg_layout_stamp;
    memcpy(resources,jpeg_layout.resources,sizeof(*resources)*jpeg_layout.resource_count);layout.resources=resources;
    memcpy(parts,jpeg_layout.partitions,sizeof(*parts)*jpeg_layout.partition_count);
    jpeg_nor_device_t raw={&model,FLASH_BYTES,256,read_flash,program_flash,erase_flash};
    CHECK(jpeg_transport_init(&transport,&raw,now,&model)==JPEG_TRANSPORT_OK);
}

static jpeg_transport_result_t provision(const jpeg_transport_limits_t *limits)
{
    /* Verify actual cleanup/revocation, not just the top-level return code. */
    jpeg_guard_sha256_t hash={&model,hash_begin,hash_update,hash_finish,hash_reset};
    jpeg_transport_result_t result=jpeg_transport_provision(&transport,&layout,parts,jpeg_layout.partition_count,
        &hash,&stamp,&diagnostic,limits);
    CHECK(!model.hash && model.hash_resets==model.hash_begins && !model.erases);
    CHECK(transport.authorized==(result==JPEG_TRANSPORT_OK));CHECK(!transport.active && !transport.verifying);
    ++cases;return result;
}

static void preserved(void)
{
    /* Complete physical compare: ONLY the exact64 stamp bytes can differ. */
    CHECK(!memcmp(flash,legacy,STAMP));
    CHECK(!memcmp(flash+STAMP+64,legacy+STAMP+64,FLASH_BYTES-STAMP-64));
}

static unsigned target_zeros(unsigned offset,unsigned bytes)
{
    /* Enumerate every physically meaningful1->0 transition in the stamp. */
    unsigned result=0;
    for(unsigned i=offset;i<offset+bytes;++i)for(unsigned bit=0;bit<8;++bit)result+=!(jpeg_layout_stamp.bytes[i]&(1u<<bit));
    return result;
}

static void test_positive(void)
{
    /* Legacy adoption preserves all data; subsequent nonempty owned cache is legal. */
    reset();CHECK(provision(&ample)==JPEG_TRANSPORT_OK);
    CHECK(diagnostic.status==JPEG_PROVISION_INSTALLED && diagnostic.program_attempted && model.programs==2);
    CHECK(transport.usage.program_bytes==40);
    CHECK(!memcmp(flash+STAMP,jpeg_layout_stamp.bytes,64));preserved();
    unsigned programs=model.programs;
    for(unsigned i=0;i<jpeg_layout.allowed_count;++i)memset(flash+jpeg_layout.allowed[i].offset,0x35,jpeg_layout.allowed[i].bytes);
    CHECK(provision(&ample)==JPEG_TRANSPORT_OK && diagnostic.status==JPEG_PROVISION_ALREADY);
    CHECK(!diagnostic.program_attempted && model.programs==programs);
    reset();memcpy(flash+STAMP+8,stamp.bytes+8,32);
    CHECK(provision(&ample)==JPEG_TRANSPORT_OK && model.programs==1 && transport.usage.program_bytes==8);
    preserved();
}

static void test_occupied(void)
{
    /* Every candidate sector: first/middle/last byte; never repair by erasing. */
    for(unsigned i=0;i<jpeg_layout.allowed_count;++i) {
        const jpeg_nor_extent_t *range=&jpeg_layout.allowed[i];
        for(uint32_t offset=0;offset<range->bytes;offset+=4096)for(unsigned p=0;p<3;++p) {
            reset();uint32_t at=range->offset+offset+(p==0 ? 0:p==1 ? 2048:4095);flash[at]=0xfe;
            CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD && diagnostic.status==JPEG_PROVISION_OCCUPIED);
            CHECK(diagnostic.offset==at && !model.programs);flash[at]=0xff;preserved();++occupied_cases;
        }
    }
}

static void test_silent_reads(void)
{
    /* A hidden occupied byte on EITHER read must fail for every candidate sector. */
    for(unsigned i=0;i<jpeg_layout.allowed_count;++i) {
        const jpeg_nor_extent_t *range=&jpeg_layout.allowed[i];
        for(uint32_t offset=0;offset<range->bytes;offset+=4096)for(unsigned hidden=1;hidden<=2;++hidden) {
            reset();uint32_t at=range->offset+offset;flash[at]=0xfe;
            model.hide_address=at;model.hide_occurrence=hidden;
            CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD);
            CHECK(diagnostic.status==JPEG_PROVISION_VERIFY || diagnostic.status==JPEG_PROVISION_OCCUPIED);
            CHECK(!model.programs);flash[at]=0xff;preserved();++silent_cases;
        }
    }
}

static void test_torn_stamp(void)
{
    /* Every partial bit prefix, reported failure OR silent success; same bytes
     * must safely resume after a new bootstrap, without touching another byte. */
    for(unsigned phase=1;phase<=2;++phase)for(unsigned error=0;error<2;++error) {
      unsigned zeros=target_zeros(phase==1 ? 8:0,phase==1 ? 32:8);
      for(unsigned bits=0;bits<=zeros;++bits) {
        reset();model.cut_program=phase;model.partial_bits=bits;model.program_error=error!=0;
        jpeg_transport_result_t result=provision(&ample);
        if(bits==zeros && !error)CHECK(result==JPEG_TRANSPORT_OK);
        else {
            CHECK(result!=JPEG_TRANSPORT_OK && !transport.authorized);
            CHECK(diagnostic.status==(error ? JPEG_PROVISION_IO:JPEG_PROVISION_VERIFY));
        }
        preserved();model.cut_program=0;model.partial_bits=UINT_MAX;model.program_error=false;
        CHECK(provision(&ample)==JPEG_TRANSPORT_OK);
        CHECK(!memcmp(flash+STAMP,jpeg_layout_stamp.bytes,64));preserved();++cuts;
      }
    }
    for(unsigned seed=0;seed<128;++seed) {
        reset();uint32_t random=seed+1;
        if(seed&1u)memcpy(flash+STAMP+8,stamp.bytes+8,32);
        unsigned start=seed&1u ? 0:8,bytes=seed&1u ? 8:32;
        for(unsigned i=start;i<start+bytes;++i) {
            random=random*1664525u+1013904223u;
            flash[STAMP+i]=(uint8_t)(stamp.bytes[i]|(random>>24));
        }
        CHECK(provision(&ample)==JPEG_TRANSPORT_OK);preserved();++cuts;
    }
    reset();model.program_corrupt=true;CHECK(provision(&ample)!=JPEG_TRANSPORT_OK);
    CHECK(diagnostic.status==JPEG_PROVISION_VERIFY);model.program_corrupt=false;
    unsigned programs=model.programs;CHECK(provision(&ample)!=JPEG_TRANSPORT_OK);
    CHECK(diagnostic.status==JPEG_PROVISION_STAMP && model.programs==programs);preserved();
}

static void test_guards(void)
{
    /* Physical immutable mismatch, descriptor mismatch, and late corruption all
     * remain failures; the prospective stamp is never a capability token. */
    for(unsigned i=0;i<jpeg_layout.resource_count;++i)if(i!=stamp.resource_index) {
        reset();flash[resources[i].offset]^=1;
        CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD && !model.programs);
        CHECK(diagnostic.guard==JPEG_GUARD_RESOURCE);flash[resources[i].offset]^=1;preserved();
    }
    reset();stamp.bytes[9]^=1;CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD && !model.programs);
    reset();memcpy(flash+STAMP,stamp.bytes,64);stamp.bytes[9]^=1;
    CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD && !model.programs);
    reset();memcpy(flash+STAMP,stamp.bytes,8);
    /* A complete ownership header with another compatible ID is foreign,
     * not permission to finish a stamp under an unknown prior write order. */
    CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD && diagnostic.status==JPEG_PROVISION_STAMP && !model.programs);
    reset();parts[3].flags=1;CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD && !model.reads && !model.programs);
    reset();resources[stamp.resource_index].bytes=63;
    CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD && !model.reads && !model.programs);
    reset();model.mutate_resource=true;CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD);
    CHECK(diagnostic.guard==JPEG_GUARD_RESOURCE && model.programs==2);
    flash[resources[0].offset]^=1;preserved();
    for(unsigned i=0;i<64;++i)for(unsigned bit=0;bit<8;++bit)if(jpeg_layout_stamp.bytes[i]&(1u<<bit)) {
        reset();flash[STAMP+i]&=(uint8_t)~(1u<<bit);
        CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD && diagnostic.status==JPEG_PROVISION_STAMP);
        CHECK(!model.programs);preserved();++incompatible_cases;
    }
}

static void test_epochs(void)
{
    /* Failed adoption must revoke already-issued ordinary ports. A subsequent
     * successful guard cannot revive those ports, including a new live job. */
    reset();CHECK(provision(&ample)==JPEG_TRANSPORT_OK);
    jpeg_transport_limits_t read_only={4,16,0,0,100000};
    CHECK(jpeg_transport_begin(&transport,&read_only)==JPEG_TRANSPORT_OK);
    jpeg_transport_port_t port;jpeg_nor_device_t old;
    CHECK(jpeg_transport_port(&transport,&port,jpeg_layout.allowed,1,false,&old)==JPEG_TRANSPORT_OK);
    parts[3].flags=1;CHECK(provision(&ample)==JPEG_TRANSPORT_GUARD);
    unsigned reads=model.reads;uint8_t value[4];
    CHECK(old.read(old.context,jpeg_layout.allowed[0].offset,value,4)!=0 && model.reads==reads);
    parts[3].flags=0;jpeg_transport_limits_t no_writes=ample;no_writes.program_bytes=0;
    CHECK(provision(&no_writes)==JPEG_TRANSPORT_OK && diagnostic.status==JPEG_PROVISION_ALREADY);
    CHECK(jpeg_transport_begin(&transport,&read_only)==JPEG_TRANSPORT_OK);reads=model.reads;
    CHECK(old.read(old.context,jpeg_layout.allowed[0].offset,value,4)!=0 && model.reads==reads);
    jpeg_transport_end(&transport);preserved();
}

static void test_io_and_budget(void)
{
    /* Stage-spanning faults and exact shared budget boundaries, including after
     * a physically completed stamp program. No fallback can reset the budget. */
    reset();model.latency=1;CHECK(provision(&ample)==JPEG_TRANSPORT_OK);
    jpeg_transport_usage_t usage=transport.usage;unsigned reads=model.reads,hashes=model.hash_calls;
    uint64_t elapsed=model.now;
    for(unsigned i=1;i<=reads;++i) {
        reset();model.fail_read=i;CHECK(provision(&ample)!=JPEG_TRANSPORT_OK);preserved();++io_cases;
    }
    for(unsigned i=1;i<=hashes;++i) {
        reset();model.fail_hash=i;CHECK(provision(&ample)!=JPEG_TRANSPORT_OK);preserved();++hash_cases;
    }
    jpeg_transport_limits_t exact={usage.calls,usage.read_bytes,usage.program_bytes,0,elapsed+1};
    reset();model.latency=1;CHECK(provision(&exact)==JPEG_TRANSPORT_OK);
    for(unsigned kind=0;kind<4;++kind) {
        reset();model.latency=1;jpeg_transport_limits_t limit=exact;
        if(kind==0)--limit.calls;else if(kind==1)--limit.read_bytes;
        else if(kind==2)--limit.program_bytes;else --limit.duration_us;
        CHECK(provision(&limit)==(kind==3 ? JPEG_TRANSPORT_TIME:JPEG_TRANSPORT_LIMIT));preserved();++quota_cases;
    }
    reset();model.fail_read=reads;CHECK(provision(&ample)!=JPEG_TRANSPORT_OK);preserved();++io_cases;
    reset();model.fail_hash=hashes;CHECK(provision(&ample)!=JPEG_TRANSPORT_OK);preserved();++hash_cases;
}

int main(int argc,char **argv)
{
    /* Only synthetic mutable bytes surround real public/sanitized immutable assets. */
    CHECK(argc==2);memset(legacy,255,sizeof(legacy));FILE *file=fopen(argv[1],"rb");CHECK(file);
    CHECK(fread(legacy+0x200000,1,0x1e7000,file)==0x1e7000 && fgetc(file)==EOF);fclose(file);
    for(unsigned i=0;i<0x187000;++i)legacy[i]=(uint8_t)(i*13u+71u);
    for(unsigned i=0x200000;i<0x27d000;++i)legacy[i]=(uint8_t)(i*17u+113u);
    for(unsigned i=0x3e7000;i<FLASH_BYTES;++i)legacy[i]=(uint8_t)(i*23u+97u);
    memset(legacy+STAMP,255,64);CHECK(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0)==0);
    test_positive();test_occupied();test_silent_reads();test_torn_stamp();test_guards();test_epochs();test_io_and_budget();
    CHECK(BCryptCloseAlgorithmProvider(algorithm,0)==0);
    printf("{\"passed\":true,\"assertions\":%u,\"cases\":%u,\"occupied\":%u,\"silent_reads\":%u,\"torn_stamp_recoveries\":%u,\"read_faults\":%u,\"hash_faults\":%u,\"quota_boundaries\":%u,\"incompatible_stamps\":%u}\n",
        checks,cases,occupied_cases,silent_cases,cuts,io_cases,hash_cases,quota_cases,incompatible_cases);
    return 0;
}
