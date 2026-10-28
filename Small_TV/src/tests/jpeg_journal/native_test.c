/* Cold RAM recovery from actual partial NOR bytes. A strict independent model
 * enforces allowed addresses, page/bit rules, commit order and protected bytes. */
#include "../../storage/jpeg_journal.h"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <limits.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "journal_fixture.h"

#define FLASH_BYTES 0x400000u
#define FRAME_BYTES 115200u
#define COUNT(a) ((unsigned)(sizeof(a)/sizeof((a)[0])))
#define CHECK(v) do {++checks;if (!(v)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}} while(0)
static uint64_t checks;
static unsigned fault_cases, corruption_cases, boot_faults, verified_hits, rejected_cases;
static unsigned update_callbacks[2];
static uint8_t flash_data[FLASH_BYTES], initial[FLASH_BYTES], before[FLASH_BYTES];
static uint8_t old_source[5][32], old_frame[5][32], new_source[32], new_frame[32];
static jpeg_journal_t journal;
static jpeg_nor_t frame;
static BCRYPT_ALG_HANDLE algorithm;
static BCRYPT_HASH_HANDLE live_hash;
static jmp_buf power_cut;
static struct {
    unsigned page_bytes,calls,fail_at,mode,verifications,programs,erases;
    unsigned body_reads[2],erased_reads[2];
    bool restrict_writes,force_verify_failure;
    char trace[8192];
} model;

static bool inside(uint32_t address,size_t bytes,const jpeg_nor_extent_t *extents,unsigned count)
{
    /* Whole-request bounds independent of the library's logical translator. */
    for(unsigned i=0;i<count;++i)
        if(address>=extents[i].offset && address-extents[i].offset<=extents[i].bytes &&
           bytes<=extents[i].bytes-(address-extents[i].offset))return true;
    return false;
}

static int bank_at(uint32_t address)
{
    /* Metadata uses two exact sectors, even if a later layout makes them sparse. */
    for(unsigned b=0;b<2;++b)
        if(address>=fixture_config.banks[b] && address-fixture_config.banks[b]<4096)return (int)b;
    return -1;
}

static void check_address(uint32_t address,size_t bytes,bool writing)
{
    /* Check every callback and forbid writes outside metadata/current frame. */
    CHECK(address<=FLASH_BYTES && bytes<=FLASH_BYTES-address);
    CHECK(inside(address,bytes,fixture_allowed,COUNT(fixture_allowed)));
    if(writing && model.restrict_writes)
        CHECK(bank_at(address)>=0 || inside(address,bytes,cache_maps[0].extents,cache_maps[0].count));
}

static bool visit(char operation)
{
    /* Callback ordinals include data verification; power cut cannot run cleanup. */
    ++model.calls;
    CHECK(model.calls<=sizeof(model.trace));
    model.trace[model.calls-1]=operation;
    return model.calls==model.fail_at;
}

static int outcome(bool fault)
{
    /* 1=partial error,2=silent partial/corrupt read,3=full cut,4=half cut,5=before cut. */
    if(fault && model.mode>=3)longjmp(power_cut,1);
    return fault && model.mode==1 ? -77 : 0;
}

static size_t transferred(size_t bytes,bool fault)
{
    /* A cut can happen before any bit or after a partial/full operation. */
    if(!fault || model.mode==3)return bytes;
    return model.mode==5 ? 0 : bytes/2;
}

static int read_flash(void *context,uint32_t address,void *data,size_t bytes)
{
    /* NOR cache loads may read4096; journal/hash readback is bounded to256. */
    CHECK(context==&model);check_address(address,bytes,false);
    bool fault=visit('R');
    memcpy(data,flash_data+address,transferred(bytes,fault));
    if(fault && model.mode==2)((uint8_t *)data)[0]^=1;
    int bank=bank_at(address);
    if(bank>=0 && !fault) {
        unsigned local=address-fixture_config.banks[bank];
        for(unsigned offset=local;offset+256<=local+bytes;offset+=256) {
            model.erased_reads[bank]|=1u<<(offset/256);
            if(offset<512)model.body_reads[bank]|=1u<<(offset/256);
        }
    }
    return outcome(fault);
}

static int program_flash(void *context,uint32_t address,const void *data,size_t bytes)
{
    /* Enforce physical page limits/bit direction and the journal's commit order. */
    CHECK(context==&model);check_address(address,bytes,true);
    CHECK(bytes==model.page_bytes && address%bytes==0);
    int bank=bank_at(address);
    if(bank>=0) {
        unsigned local=address-fixture_config.banks[bank];
        CHECK(model.erased_reads[bank]==0xffffu);
        if(local==4096-model.page_bytes)CHECK(model.body_reads[bank]==3u);
        else {CHECK(local<512);model.body_reads[bank]=0;}
    }
    const uint8_t *input=data;
    for(size_t i=0;i<bytes;++i)CHECK((flash_data[address+i]&input[i])==input[i]);
    bool fault=visit('P');++model.programs;
    for(size_t i=0;i<transferred(bytes,fault);++i)flash_data[address+i]&=input[i];
    return outcome(fault);
}

static int erase_flash(void *context,uint32_t address)
{
    /* Interrupted erase preserves part of the actual old bank/frame sector. */
    CHECK(context==&model);check_address(address,4096,true);CHECK(address%4096==0);
    int bank=bank_at(address);
    if(bank>=0){model.erased_reads[bank]=0;model.body_reads[bank]=0;}
    bool fault=visit('E');++model.erases;
    memset(flash_data+address,0xff,transferred(4096,fault));
    return outcome(fault);
}

static jpeg_nor_device_t device(void)
{
    /* Same transport drives real NOR core and the metadata protocol. */
    jpeg_nor_device_t result={&model,FLASH_BYTES,model.page_bytes,read_flash,program_flash,erase_flash};
    return result;
}

static uint8_t pixel(unsigned slot,bool newer,uint32_t offset)
{
    /* Deterministic nonconstant full-frame content exercises every restored page. */
    return (uint8_t)((offset*37u+(offset>>7)*19u+slot*41u)^(newer ? 0x6du : 0xb2u));
}

static void hash_bytes(const void *data,size_t bytes,uint8_t out[32])
{
    /* Independent OS SHA-256, not metadata-derived expected hashes. */
    CHECK(bytes<=ULONG_MAX);
    CHECK(BCryptHash(algorithm,NULL,0,(PUCHAR)data,(ULONG)bytes,out,32)>=0);
}

static int verify_frame(void *context,unsigned slot,uint32_t bytes,const uint8_t expected[32])
{
    /* Flush THEN read physical sparse extents; no hit can trust the dirty RAM. */
    CHECK(context==&model && slot<5 && bytes==FRAME_BYTES);++model.verifications;
    if(model.force_verify_failure)return -88;
    if(frame.open && jpeg_nor_sync(&frame)!=JPEG_NOR_OK)return -1;
    CHECK(!live_hash && BCryptCreateHash(algorithm,&live_hash,NULL,0,NULL,0,0)>=0);
    uint8_t buffer[256],digest[32];uint32_t remaining=bytes;
    for(unsigned e=0;e<cache_maps[slot].count && remaining;++e) {
        uint32_t extent=cache_maps[slot].extents[e].bytes;
        if(extent>remaining)extent=remaining;
        for(uint32_t offset=0;offset<extent;) {
            uint32_t chunk=extent-offset;if(chunk>sizeof(buffer))chunk=sizeof(buffer);
            if(read_flash(&model,cache_maps[slot].extents[e].offset+offset,buffer,chunk)) {
                CHECK(BCryptDestroyHash(live_hash)>=0);live_hash=NULL;return -1;
            }
            CHECK(BCryptHashData(live_hash,buffer,chunk,0)>=0);offset+=chunk;
        }
        remaining-=extent;
    }
    CHECK(!remaining && BCryptFinishHash(live_hash,digest,32,0)>=0);
    CHECK(BCryptDestroyHash(live_hash)>=0);live_hash=NULL;
    return memcmp(digest,expected,32) ? -1 : 0;
}

static jpeg_journal_verifier_t verifier(void)
{
    /* Mandatory verification is tested both on publication and cache hits. */
    jpeg_journal_verifier_t result={&model,verify_frame};return result;
}

static void fresh_ram(unsigned page_bytes)
{
    /* Simulate cold boot: discard ALL old handles, pending flags and sector RAM. */
    /* The host OS reclaims SHA allocations lost by our simulated hard reset. */
    if(live_hash){CHECK(BCryptDestroyHash(live_hash)>=0);live_hash=NULL;}
    memset(&journal,0,sizeof(journal));memset(&frame,0,sizeof(frame));memset(&model,0,sizeof(model));
    model.page_bytes=page_bytes;
}

static void open_journal(const jpeg_journal_config_t *config)
{
    /* Open always reads the actual flash banks, not saved journal state. */
    jpeg_nor_device_t io=device();
    CHECK(jpeg_journal_open(&journal,&io,config,fixture_allowed,COUNT(fixture_allowed))==JPEG_JOURNAL_OK);
}

static void open_frame(void)
{
    /* One bounded4096-byte cache, genuine sparse115200-byte output store. */
    jpeg_nor_device_t io=device();
    CHECK(jpeg_nor_open(&frame,&io,cache_maps[0].extents,cache_maps[0].count,FRAME_BYTES,
                       fixture_allowed,COUNT(fixture_allowed))==JPEG_NOR_OK);
}

static jpeg_journal_result_t hit(unsigned slot,bool newer)
{
    /* Current source identity comes from separately generated source fixtures. */
    jpeg_journal_verifier_t verify=verifier();
    return jpeg_journal_lookup(&journal,slot,293,newer ? new_source : old_source[slot],&verify);
}

static void put_frame(unsigned slot,bool newer)
{
    /* Setup oracle scatters pixels directly; the update path must use NOR I/O. */
    uint32_t position=0;
    for(unsigned e=0;e<cache_maps[slot].count;++e)
        for(uint32_t i=0;i<cache_maps[slot].extents[e].bytes && position<FRAME_BYTES;++i)
            flash_data[cache_maps[slot].extents[e].offset+i]=pixel(slot,newer,position++);
    CHECK(position==FRAME_BYTES);
}

static void initialize(unsigned page_bytes)
{
    /* Establish five independent valid frames; later faults may touch only slot0. */
    for(uint32_t i=0;i<FLASH_BYTES;++i)flash_data[i]=(uint8_t)(i*7u+(i>>11));
    for(unsigned b=0;b<2;++b)memset(flash_data+fixture_config.banks[b],0xff,4096);
    uint8_t *pixels=malloc(FRAME_BYTES);CHECK(pixels);
    for(unsigned slot=0;slot<5;++slot) {
        for(uint32_t i=0;i<FRAME_BYTES;++i)pixels[i]=pixel(slot,false,i);
        hash_bytes(pixels,FRAME_BYTES,old_frame[slot]);put_frame(slot,false);
        uint8_t source[293];for(unsigned i=0;i<sizeof(source);++i)source[i]=(uint8_t)(slot+i*3);
        hash_bytes(source,sizeof(source),old_source[slot]);
    }
    for(uint32_t i=0;i<FRAME_BYTES;++i)pixels[i]=pixel(0,true,i);
    hash_bytes(pixels,FRAME_BYTES,new_frame);free(pixels);
    uint8_t source[293];memset(source,0xc7,sizeof(source));hash_bytes(source,sizeof(source),new_source);
    fresh_ram(page_bytes);open_journal(&fixture_config);
    jpeg_journal_verifier_t verify=verifier();
    for(unsigned slot=0;slot<5;++slot) {
        CHECK(jpeg_journal_begin(&journal,slot)==JPEG_JOURNAL_OK);
        CHECK(jpeg_journal_publish(&journal,293,old_source[slot],old_frame[slot],&verify)==JPEG_JOURNAL_OK);
    }
    CHECK(journal.generation==6);
    memcpy(initial,flash_data,sizeof(initial));
}

static jpeg_journal_result_t update(void)
{
    /* Full intended workflow: durable invalidation, data writes, flush/hash, commit. */
    jpeg_journal_result_t result=jpeg_journal_begin(&journal,0);
    if(result!=JPEG_JOURNAL_OK)return result;
    open_frame();uint8_t row[480];uint32_t position=0;
    while(position<FRAME_BYTES) {
        for(unsigned i=0;i<sizeof(row);++i)row[i]=pixel(0,true,position+i);
        if(jpeg_nor_write(&frame,position,row,sizeof(row))!=JPEG_NOR_OK)return JPEG_JOURNAL_IO;
        position+=sizeof(row);
    }
    jpeg_journal_verifier_t verify=verifier();
    return jpeg_journal_publish(&journal,293,new_source,new_frame,&verify);
}

static void protected_unchanged(void)
{
    /* Whole-flash comparison except exact two metadata sectors + slot0 extents. */
    uint32_t position=0;
    while(position<FLASH_BYTES) {
        bool writable=bank_at(position)>=0 || inside(position,4096,cache_maps[0].extents,cache_maps[0].count);
        if(!writable)CHECK(!memcmp(flash_data+position,initial+position,4096));
        position+=4096;
    }
}

static void check_recovered(unsigned page_bytes)
{
    /* A hit is valid only if every pixel matches an independent complete frame. */
    fresh_ram(page_bytes);open_journal(&fixture_config);
    bool new_ready=journal.entries[0].ready && !memcmp(journal.entries[0].source_sha256,new_source,32);
    jpeg_journal_result_t result=hit(0,new_ready);
    CHECK(result==(journal.entries[0].ready ? JPEG_JOURNAL_OK : JPEG_JOURNAL_MISS));
    if(result==JPEG_JOURNAL_OK) {
        uint32_t position=0;
        for(unsigned e=0;e<cache_maps[0].count;++e)
            for(uint32_t i=0;i<cache_maps[0].extents[e].bytes && position<FRAME_BYTES;++i)
                CHECK(flash_data[cache_maps[0].extents[e].offset+i]==pixel(0,new_ready,position++));
        CHECK(position==FRAME_BYTES);++verified_hits;
    }
    for(unsigned slot=1;slot<5;++slot)CHECK(hit(slot,false)==JPEG_JOURNAL_OK);
    protected_unchanged();
}

static void save_banks(const char *folder,const char *name)
{
    /* Preserve bounded synthetic records for an independent Python wire parser. */
    char path[2048];CHECK(snprintf(path,sizeof(path),"%s/%s",folder,name)>0);
    FILE *file=fopen(path,"wb");CHECK(file);
    for(unsigned b=0;b<2;++b)CHECK(fwrite(flash_data+fixture_config.banks[b],1,4096,file)==4096);
    CHECK(!fclose(file));
}

static void test_faults(unsigned page_bytes,const char *folder,bool quick)
{
    /* Enumerate the actual complete update trace; cut/error every callback. */
    initialize(page_bytes);fresh_ram(page_bytes);open_journal(&fixture_config);
    model.calls=0;model.restrict_writes=true;
    CHECK(update()==JPEG_JOURNAL_OK);unsigned calls=model.calls;
    update_callbacks[page_bytes==256]=calls;
    CHECK(journal.generation==8 && hit(0,true)==JPEG_JOURNAL_OK);
    save_banks(folder,page_bytes==128 ? "complete-128.bin" : "complete-256.bin");
    if(quick)return;
    for(unsigned mode=1;mode<=5;++mode)
        for(unsigned n=1;n<=calls;++n) {
            memcpy(flash_data,initial,sizeof(initial));fresh_ram(page_bytes);open_journal(&fixture_config);
            model.calls=0;model.fail_at=n;model.mode=mode;model.restrict_writes=true;
            if(setjmp(power_cut)==0) {
                jpeg_journal_result_t result=update();
                CHECK(mode<3);
                CHECK(result!=JPEG_JOURNAL_OK || mode==2);
                if(journal.failed) {
                    unsigned previous=model.calls;
                    CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_STATE);
                    CHECK(hit(1,false)==JPEG_JOURNAL_STATE && model.calls==previous);
                }
            }
            CHECK(model.calls==n || mode==2); /* silent error may need readback */
            check_recovered(page_bytes);++fault_cases;
        }
}

static void cold_probe(unsigned slot,bool ready)
{
    /* Inspect durable state while preserving the active owner's pending RAM. */
    jpeg_journal_t cold={0};jpeg_nor_device_t io=device();
    CHECK(jpeg_journal_open(&cold,&io,&fixture_config,fixture_allowed,COUNT(fixture_allowed))==JPEG_JOURNAL_OK);
    CHECK(cold.entries[slot].ready==ready);jpeg_journal_abort(&cold);
}

static void test_state(void)
{
    /* Real durable invalidation, mandatory verifier, cancellation and no-op wear. */
    memcpy(flash_data,initial,sizeof(initial));fresh_ram(256);open_journal(&fixture_config);
    unsigned current=journal.bank;memcpy(before,flash_data,sizeof(before));
    CHECK(hit(0,false)==JPEG_JOURNAL_OK);
    CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_OK);
    CHECK(!memcmp(before+fixture_config.banks[current],flash_data+fixture_config.banks[current],4096));
    cold_probe(0,false);
    unsigned calls=model.calls,erases=model.erases;
    CHECK(jpeg_journal_begin(&journal,1)==JPEG_JOURNAL_STATE && model.calls==calls);
    jpeg_journal_cancel(&journal);CHECK(model.calls==calls);
    CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_OK && model.calls==calls && model.erases==erases);
    jpeg_journal_verifier_t verify=verifier();
    CHECK(jpeg_journal_publish(&journal,293,new_source,new_frame,&verify)==JPEG_JOURNAL_VERIFY);
    CHECK(!journal.entries[0].ready && journal.pending && model.erases==erases);
    cold_probe(0,false);jpeg_journal_cancel(&journal);
    CHECK(jpeg_journal_publish(&journal,293,old_source[0],old_frame[0],&verify)==JPEG_JOURNAL_STATE);
    /* Source mismatch never runs expensive frame verification. */
    unsigned verifications=model.verifications;
    CHECK(hit(1,true)==JPEG_JOURNAL_MISS && model.verifications==verifications);
    CHECK(jpeg_journal_lookup(&journal,1,294,old_source[1],&verify)==JPEG_JOURNAL_MISS);
    model.force_verify_failure=true;
    CHECK(hit(1,false)==JPEG_JOURNAL_VERIFY && journal.entries[1].ready);
    model.force_verify_failure=false;
    CHECK(jpeg_journal_begin(&journal,1)==JPEG_JOURNAL_OK);cold_probe(1,false);
    jpeg_journal_cancel(&journal);calls=model.calls;
    jpeg_journal_abort(&journal);CHECK(model.calls==calls && hit(1,false)==JPEG_JOURNAL_STATE);
}

static void test_corruption(void)
{
    /* Every body/footer byte: corrupt newest ready snapshot, fall back to invalid. */
    memcpy(flash_data,initial,sizeof(initial));fresh_ram(256);open_journal(&fixture_config);
    CHECK(update()==JPEG_JOURNAL_OK);
    uint32_t newest=fixture_config.banks[journal.bank];
    for(unsigned part=0;part<2;++part)
        for(unsigned i=0;i<(part ? 256u : 512u);++i) {
            uint32_t address=newest+(part ? 3840u : 0u)+i;
            flash_data[address]^=0x80;
            fresh_ram(256);open_journal(&fixture_config);
            CHECK(journal.generation==7 && hit(0,true)==JPEG_JOURNAL_MISS);
            flash_data[address]^=0x80;++corruption_cases;
        }
    fresh_ram(256);open_journal(&fixture_config);CHECK(hit(0,true)==JPEG_JOURNAL_OK);
    /* Invalidating newest metadata can resurrect an OLD ready record. Its old
     * hash MUST fail against partly overwritten current data on cold boot. */
    memcpy(flash_data,initial,sizeof(initial));fresh_ram(256);open_journal(&fixture_config);
    CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_OK);newest=fixture_config.banks[journal.bank];
    open_frame();uint8_t block[4096];
    for(unsigned i=0;i<sizeof(block);++i)block[i]=pixel(0,true,i);
    CHECK(jpeg_nor_write(&frame,0,block,sizeof(block))==JPEG_NOR_OK && jpeg_nor_sync(&frame)==JPEG_NOR_OK);
    flash_data[newest]^=1;
    fresh_ram(256);open_journal(&fixture_config);
    CHECK(journal.generation==6 && journal.entries[0].ready && hit(0,false)==JPEG_JOURNAL_VERIFY);
    CHECK(journal.entries[0].ready); /* do not skip the next durable invalidation */
    CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_OK);cold_probe(0,false);
    ++corruption_cases;
}

static void test_foreign(void)
{
    /* A newer foreign snapshot hides an older matching one, never roll back IDs. */
    for(unsigned kind=0;kind<4;++kind) {
        memcpy(flash_data,initial,sizeof(initial));fresh_ram(256);
        jpeg_journal_config_t foreign=fixture_config;
        if(kind==0)foreign.layout_id[0]^=1;
        if(kind==1)foreign.codec_id[0]^=1;
        if(kind==2)foreign.source_limit--;
        if(kind==3)foreign.frame_bytes--;
        open_journal(&foreign);CHECK(!journal.matching && journal.generation==6);
        CHECK(hit(0,false)==JPEG_JOURNAL_MISS);
        CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_OK);
        fresh_ram(256);open_journal(&fixture_config);
        CHECK(journal.generation==7 && !journal.matching && hit(0,false)==JPEG_JOURNAL_MISS);
        CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_OK && journal.generation==8);
        cold_probe(0,false);++rejected_cases;
    }
}

static uint32_t oracle_crc(const uint8_t *data,size_t bytes)
{
    /* Table-driven reference, separately checked against Python zlib on outputs. */
    uint32_t table[256];
    for(unsigned n=0;n<256;++n) {
        uint32_t value=n;
        for(unsigned i=0;i<8;++i)value=(value>>1)^((value&1) ? 0xedb88320u : 0);
        table[n]=value;
    }
    uint32_t value=0xffffffffu;
    for(size_t i=0;i<bytes;++i)value=(value>>8)^table[(value^data[i])&255];
    return value^0xffffffffu;
}

static void little32(uint8_t *out,uint32_t value)
{
    /* Fixture mutation uses explicit wire offsets, never the C struct layout. */
    for(unsigned i=0;i<4;++i)out[i]=(uint8_t)(value>>(8*i));
}

static void test_sequence(void)
{
    /* Do not choose arbitrarily between tied records or wrap UINT64_MAX to zero. */
    memcpy(flash_data,initial,sizeof(initial));fresh_ram(256);open_journal(&fixture_config);
    uint32_t head=fixture_config.banks[journal.bank],other=fixture_config.banks[journal.bank^1u];
    memcpy(flash_data+other,flash_data+head,4096);fresh_ram(256);
    jpeg_nor_device_t io=device();
    CHECK(jpeg_journal_open(&journal,&io,&fixture_config,fixture_allowed,COUNT(fixture_allowed))==JPEG_JOURNAL_AMBIGUOUS);
    unsigned calls=model.calls;CHECK(hit(0,false)==JPEG_JOURNAL_STATE && model.calls==calls);
    memcpy(flash_data,initial,sizeof(initial));
    memset(flash_data+head+16,0xff,8);
    uint32_t crc=oracle_crc(flash_data+head,508);
    little32(flash_data+head+508,crc);memset(flash_data+head+3840+8,0xff,8);
    little32(flash_data+head+3840+16,crc);little32(flash_data+head+3840+20,crc^0xffffffffu);
    fresh_ram(256);open_journal(&fixture_config);CHECK(journal.generation==UINT64_MAX);
    CHECK(hit(0,false)==JPEG_JOURNAL_OK);calls=model.calls;
    CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_LIMIT && model.calls==calls);
    rejected_cases+=2;
}

static void test_arguments_and_boot(void)
{
    /* No invalid request touches flash; any boot read failure blocks fallback. */
    memcpy(flash_data,initial,sizeof(initial));fresh_ram(256);
    jpeg_nor_device_t io=device();jpeg_journal_config_t config=fixture_config;
    config.banks[1]=config.banks[0];
    CHECK(jpeg_journal_open(&journal,&io,&config,fixture_allowed,COUNT(fixture_allowed))==JPEG_JOURNAL_ARGUMENT);
    config=fixture_config;config.banks[0]=0x1000;
    CHECK(jpeg_journal_open(&journal,&io,&config,fixture_allowed,COUNT(fixture_allowed))==JPEG_JOURNAL_ARGUMENT);
    config=fixture_config;config.banks[1]++;
    CHECK(jpeg_journal_open(&journal,&io,&config,fixture_allowed,COUNT(fixture_allowed))==JPEG_JOURNAL_ARGUMENT);
    CHECK(jpeg_journal_open(&journal,&io,&fixture_config,fixture_allowed,17)==JPEG_JOURNAL_ARGUMENT);
    CHECK(!model.calls);open_journal(&fixture_config);
    unsigned calls=model.calls;CHECK(jpeg_journal_begin(&journal,5)==JPEG_JOURNAL_ARGUMENT);
    jpeg_journal_verifier_t verify=verifier();
    CHECK(jpeg_journal_lookup(&journal,0,0,old_source[0],&verify)==JPEG_JOURNAL_ARGUMENT);
    CHECK(jpeg_journal_lookup(&journal,0,293,NULL,&verify)==JPEG_JOURNAL_ARGUMENT);
    CHECK(jpeg_journal_lookup(&journal,0,293,old_source[0],NULL)==JPEG_JOURNAL_ARGUMENT);
    CHECK(model.calls==calls);
    for(unsigned n=1;n<=6;++n) {
        fresh_ram(256);io=device();model.fail_at=n;model.mode=1;
        CHECK(jpeg_journal_open(&journal,&io,&fixture_config,fixture_allowed,COUNT(fixture_allowed))==JPEG_JOURNAL_IO);
        CHECK(journal.failed && model.calls==n);
        CHECK(jpeg_journal_begin(&journal,0)==JPEG_JOURNAL_STATE && model.calls==n);++boot_faults;
    }
    rejected_cases+=8;
}

int main(int argc,char **argv)
{
    /* All flash is a RAM model; no COM ports, QEMU, SDK or physical device writes. */
    CHECK((argc==2 || (argc==3 && !strcmp(argv[2],"--quick"))) &&
          BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0)>=0);
    bool quick=argc==3;
    test_faults(128,argv[1],quick);test_faults(256,argv[1],quick);
    test_state();test_corruption();test_foreign();test_sequence();test_arguments_and_boot();
    CHECK(BCryptCloseAlgorithmProvider(algorithm,0)>=0);
    printf("{\"passed\":true,\"checks\":%llu,\"power_io_fault_cases\":%u,\"corruption_cases\":%u,"
           "\"boot_faults\":%u,\"verified_recovery_hits\":%u,\"rejected_cases\":%u,"
           "\"update_callbacks_128\":%u,\"update_callbacks_256\":%u,"
           "\"physical_hardware_tested\":false,\"production_linked\":false}\n",
           (unsigned long long)checks,fault_cases,corruption_cases,boot_faults,verified_hits,rejected_cases,
           update_callbacks[0],update_callbacks[1]);
    return 0;
}
