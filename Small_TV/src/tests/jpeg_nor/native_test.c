/* Black-box NOR contract: independent flat RAM oracle and strict physical I/O.
 * The model enforces page boundaries and 1->0, injects partial operations,
 * and compares every protected byte. No firmware/device flash is written. */
#include "../../storage/jpeg_nor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "plan_fixture.h"

#define FLASH_BYTES 0x400000u
#define LOGICAL_BYTES (3u * JPEG_NOR_SECTOR_BYTES - 37u)
#define CHECK(value) do { ++checks; if (!(value)) {fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#value);exit(1);} } while (0)
static unsigned checks, random_operations, fault_scenarios, layout_stores;
static uint64_t random_erases, random_programs;
static uint8_t flash_data[FLASH_BYTES], reference[FLASH_BYTES], initial[FLASH_BYTES];
static uint8_t logical[460800], received[460800], payload[8192];
static jpeg_nor_t store;
static const jpeg_nor_extent_t fixture[] = {{0x187000,8192},{0x290000,4096}};
static const jpeg_nor_extent_t allowed[] = {{0x187000,0x79000},{0x290000,0x1f000}};
static struct {
    const jpeg_nor_extent_t *capabilities;
    unsigned count, page_bytes, calls, fail_at, fault_mode, reads, programs, erases;
    char trace[256];
} model;

static void check_address(uint32_t address, size_t bytes)
{
    /* The transport independently rejects every access outside this store. */
    CHECK(address <= FLASH_BYTES && bytes <= FLASH_BYTES-address);
    bool valid = false;
    for (unsigned i=0;i<model.count;++i)
        if (address >= model.capabilities[i].offset &&
            address-model.capabilities[i].offset <= model.capabilities[i].bytes &&
            bytes <= model.capabilities[i].bytes-(address-model.capabilities[i].offset))
            valid=true;
    CHECK(valid);
}

static bool visit(char operation)
{
    /* Keep all callback ordinals for exhaustive single-fault injection. */
    ++model.calls;
    if (model.calls <= sizeof(model.trace))
        model.trace[model.calls-1]=operation;
    return model.fail_at && model.calls==model.fail_at;
}

static int read_flash(void *context, uint32_t address, void *data, size_t bytes)
{
    /* A failing read really fills only part of the caller's buffer. */
    CHECK(context==&model);check_address(address,bytes);++model.reads;
    bool fail=visit('R');
    memcpy(data,flash_data+address,fail && model.fault_mode==1 ? bytes/2 : bytes);
    return fail && model.fault_mode==1 ? -77 : 0;
}

static int program_flash(void *context, uint32_t address, const void *data, size_t bytes)
{
    /* Reject illegal 0->1 requests even if a real chip might silently AND them. */
    CHECK(context==&model);check_address(address,bytes);
    CHECK(bytes==model.page_bytes && address%model.page_bytes==0);
    const uint8_t *in=data;
    bool legal=true;
    for (size_t i=0;i<bytes;++i)
        if ((flash_data[address+i]&in[i])!=in[i])legal=false;
    CHECK(legal);++model.programs;
    bool fail=visit('P');
    size_t count=fail ? bytes/2 : bytes;
    for(size_t i=0;i<count;++i)flash_data[address+i]&=in[i];
    return fail && model.fault_mode==1 ? -77 : 0;
}

static int erase_flash(void *context, uint32_t address)
{
    /* Model an interrupted erase, including a device falsely reporting success. */
    CHECK(context==&model);check_address(address,JPEG_NOR_SECTOR_BYTES);
    CHECK(address%JPEG_NOR_SECTOR_BYTES==0);++model.erases;
    bool fail=visit('E');
    memset(flash_data+address,0xff,fail ? JPEG_NOR_SECTOR_BYTES/2 : JPEG_NOR_SECTOR_BYTES);
    return fail && model.fault_mode==1 ? -77 : 0;
}

static jpeg_nor_device_t device(void)
{
    /* Build the same callback contract used by the future ESP-IDF adapter. */
    jpeg_nor_device_t result={&model,FLASH_BYTES,model.page_bytes,read_flash,program_flash,erase_flash};
    return result;
}

static void reset(unsigned page_bytes)
{
    /* Restore deterministic old data efficiently; no state leaks between faults. */
    memset(&store,0,sizeof(store));memset(&model,0,sizeof(model));
    memcpy(flash_data,initial,sizeof(flash_data));memcpy(reference,initial,sizeof(reference));
    model.capabilities=fixture;model.count=2;model.page_bytes=page_bytes;
}

static void open_fixture(void)
{
    /* Open a sparse three-sector logical file within the real candidate ranges. */
    jpeg_nor_device_t io=device();
    CHECK(jpeg_nor_open(&store,&io,fixture,2,LOGICAL_BYTES,allowed,2)==JPEG_NOR_OK);
    CHECK(model.calls==0);
}

static void gather(const jpeg_nor_extent_t *extents, unsigned count,
                   uint32_t bytes, uint8_t *out, const uint8_t *physical)
{
    /* Independent oracle: concatenate whole extents, rather than translate requests. */
    uint32_t position=0;
    for(unsigned i=0;i<count && position<bytes;++i) {
        uint32_t block=extents[i].bytes;
        if(block>bytes-position)block=bytes-position;
        memcpy(out+position,physical+extents[i].offset,block);position+=block;
    }
    CHECK(position==bytes);
}

static void scatter(const jpeg_nor_extent_t *extents, unsigned count,
                    uint32_t bytes, const uint8_t *in)
{
    /* Construct a complete expected flash image, retaining logical-end padding. */
    uint32_t position=0;
    for(unsigned i=0;i<count && position<bytes;++i) {
        uint32_t block=extents[i].bytes;
        if(block>bytes-position)block=bytes-position;
        memcpy(reference+extents[i].offset,in+position,block);position+=block;
    }
    CHECK(position==bytes);
}

static uint32_t random_number(uint32_t *state)
{
    /* Reproducible property inputs independent of the storage implementation. */
    *state=*state*1664525u+1013904223u;return *state;
}

static void test_random(unsigned page_bytes)
{
    /* Exercise sparse/sector/page crossings, overwrite and dirty read-after-write. */
    reset(page_bytes);open_fixture();gather(fixture,2,LOGICAL_BYTES,logical,flash_data);
    uint32_t seed=0x18ab39u;
    for(unsigned iteration=0;iteration<1500;++iteration) {
        uint32_t offset=random_number(&seed)%LOGICAL_BYTES;
        size_t bytes=random_number(&seed)%sizeof(payload)+1;
        if(bytes>LOGICAL_BYTES-offset)bytes=LOGICAL_BYTES-offset;
        for(size_t i=0;i<bytes;++i)payload[i]=(uint8_t)(random_number(&seed)>>24);
        CHECK(jpeg_nor_write(&store,offset,payload,bytes)==JPEG_NOR_OK);
        memcpy(logical+offset,payload,bytes);
        uint32_t read_offset=random_number(&seed)%LOGICAL_BYTES;
        size_t read_bytes=random_number(&seed)%sizeof(payload)+1;
        if(read_bytes>LOGICAL_BYTES-read_offset)read_bytes=LOGICAL_BYTES-read_offset;
        CHECK(jpeg_nor_read(&store,read_offset,received,read_bytes)==JPEG_NOR_OK);
        CHECK(!memcmp(received,logical+read_offset,read_bytes));
        if(iteration%23==0) {
            CHECK(jpeg_nor_sync(&store)==JPEG_NOR_OK);
            scatter(fixture,2,LOGICAL_BYTES,logical);
            CHECK(!memcmp(flash_data,reference,sizeof(flash_data)));
        }
        ++random_operations;
    }
    CHECK(jpeg_nor_close(&store)==JPEG_NOR_OK);
    scatter(fixture,2,LOGICAL_BYTES,logical);CHECK(!memcmp(flash_data,reference,sizeof(flash_data)));
    CHECK(store.stats.erase_calls==model.erases && store.stats.program_calls==model.programs);
    CHECK(store.stats.read_calls==model.reads);
    random_erases+=model.erases;random_programs+=model.programs;
}

static void test_wear(void)
{
    /* Prove no-op/coalesced writes do not erase/program, and 1->0 needs no erase. */
    reset(256);
    for(unsigned i=0;i<2;++i)memset(flash_data+fixture[i].offset,0xff,fixture[i].bytes);
    open_fixture();uint8_t value=0xfe;
    CHECK(jpeg_nor_write(&store,17,&value,1)==JPEG_NOR_OK);
    CHECK(model.programs==0 && model.erases==0);
    CHECK(jpeg_nor_sync(&store)==JPEG_NOR_OK);
    CHECK(model.programs==1 && model.erases==0);
    unsigned calls=model.calls;
    CHECK(jpeg_nor_write(&store,17,&value,1)==JPEG_NOR_OK && jpeg_nor_sync(&store)==JPEG_NOR_OK);
    CHECK(model.calls==calls);
    value=0xff;CHECK(jpeg_nor_write(&store,17,&value,1)==JPEG_NOR_OK);
    CHECK(jpeg_nor_sync(&store)==JPEG_NOR_OK && model.programs==1 && model.erases==1);
    value=0xaa;CHECK(jpeg_nor_write(&store,17,&value,1)==JPEG_NOR_OK);
    value=0xff;CHECK(jpeg_nor_write(&store,17,&value,1)==JPEG_NOR_OK);
    CHECK(jpeg_nor_sync(&store)==JPEG_NOR_OK && model.programs==1 && model.erases==1);
    CHECK(jpeg_nor_close(&store)==JPEG_NOR_OK);
}

static void test_invalid(void)
{
    /* Invalid capabilities, integer bounds, nulls and handle aliasing have no I/O. */
    reset(256);jpeg_nor_device_t io=device();
    jpeg_nor_extent_t invalid[]={{0,4096},{4096,4096}};
    CHECK(jpeg_nor_open(&store,&io,invalid,1,4096,allowed,2)==JPEG_NOR_RANGE);
    invalid[0]=(jpeg_nor_extent_t){0x187001,4096};
    CHECK(jpeg_nor_open(&store,&io,invalid,1,4096,allowed,2)==JPEG_NOR_RANGE);
    invalid[0]=(jpeg_nor_extent_t){0xfffff000u,8192};
    CHECK(jpeg_nor_open(&store,&io,invalid,1,8192,allowed,2)==JPEG_NOR_RANGE);
    invalid[0]=invalid[1]=fixture[0];
    CHECK(jpeg_nor_open(&store,&io,invalid,2,16384,allowed,2)==JPEG_NOR_RANGE);
    invalid[0]=(jpeg_nor_extent_t){0x1ff000,8192};
    CHECK(jpeg_nor_open(&store,&io,invalid,1,8192,allowed,2)==JPEG_NOR_RANGE);
    /* FIXED_TEST: cover the final allowlist boundary too. The mutation removing
     * covered()'s final remaining-byte check escaped the earlier gap-only cases. */
    invalid[0]=(jpeg_nor_extent_t){0x2ae000,8192};
    CHECK(jpeg_nor_open(&store,&io,invalid,1,8192,allowed,2)==JPEG_NOR_RANGE);
    invalid[0]=(jpeg_nor_extent_t){0x2b0000,4096};
    CHECK(jpeg_nor_open(&store,&io,invalid,1,4096,allowed,2)==JPEG_NOR_RANGE);
    CHECK(jpeg_nor_open(&store,&io,fixture,2,4096,allowed,2)==JPEG_NOR_RANGE);
    CHECK(jpeg_nor_open(&store,&io,NULL,2,LOGICAL_BYTES,allowed,2)==JPEG_NOR_RANGE);
    CHECK(jpeg_nor_open(&store,&io,fixture,17,LOGICAL_BYTES,allowed,2)==JPEG_NOR_RANGE);
    CHECK(jpeg_nor_open(&store,&io,fixture,2,LOGICAL_BYTES,NULL,2)==JPEG_NOR_RANGE);
    io.page_bytes=64;CHECK(jpeg_nor_open(&store,&io,fixture,2,LOGICAL_BYTES,allowed,2)==JPEG_NOR_ARGUMENT);
    jpeg_nor_t unchanged={0};
    CHECK(!memcmp(&store,&unchanged,sizeof(store)) && model.calls==0);open_fixture();
    CHECK(jpeg_nor_open(&store,&io,fixture,2,LOGICAL_BYTES,allowed,2)!=JPEG_NOR_OK);
    CHECK(jpeg_nor_read(&store,UINT32_MAX,received,1)==JPEG_NOR_RANGE);
    CHECK(jpeg_nor_write(&store,0,payload,SIZE_MAX)==JPEG_NOR_RANGE);
    CHECK(jpeg_nor_write(&store,LOGICAL_BYTES,payload,1)==JPEG_NOR_RANGE);
    CHECK(jpeg_nor_read(&store,0,NULL,1)==JPEG_NOR_ARGUMENT);
    CHECK(jpeg_nor_write(&store,0,&store,1)==JPEG_NOR_ARGUMENT);
    CHECK(jpeg_nor_read(&store,0,&store.device,sizeof(store.device))==JPEG_NOR_ARGUMENT);
    CHECK(jpeg_nor_read(&store,0,(void *)(uintptr_t)(UINTPTR_MAX-1),3)==JPEG_NOR_ARGUMENT);
    CHECK(jpeg_nor_read(&store,LOGICAL_BYTES,NULL,0)==JPEG_NOR_OK);
    CHECK(jpeg_nor_write(&store,LOGICAL_BYTES,NULL,0)==JPEG_NOR_OK);
    CHECK(model.calls==0);jpeg_nor_abort(&store);CHECK(model.calls==0);
    CHECK(jpeg_nor_sync(&store)==JPEG_NOR_STATE);
}

static void test_abort_and_adjacent_capabilities(void)
{
    /* Abort is not an implicit commit; adjacent capabilities can cover one extent. */
    reset(256);
    const jpeg_nor_extent_t split[]={{0x187000,4096},{0x188000,4096},{0x290000,4096}};
    jpeg_nor_device_t io=device();
    CHECK(jpeg_nor_open(&store,&io,fixture,2,LOGICAL_BYTES,split,3)==JPEG_NOR_OK);
    uint8_t value=(uint8_t)~flash_data[fixture[0].offset];
    CHECK(jpeg_nor_write(&store,0,&value,1)==JPEG_NOR_OK);
    unsigned calls=model.calls;jpeg_nor_abort(&store);
    CHECK(model.calls==calls && !memcmp(flash_data,initial,sizeof(flash_data)));
    CHECK(jpeg_nor_open(&store,&io,fixture,2,LOGICAL_BYTES,split,3)==JPEG_NOR_OK);
    CHECK(jpeg_nor_read(&store,0,received,1)==JPEG_NOR_OK);
    CHECK(received[0]==initial[fixture[0].offset]);
    CHECK(jpeg_nor_close(&store)==JPEG_NOR_OK);
}

static void check_protected(void)
{
    /* Check every byte outside the mapped sectors, including large sparse holes. */
    uint32_t cursor=0;
    for(unsigned i=0;i<2;++i) {
        CHECK(!memcmp(flash_data+cursor,initial+cursor,fixture[i].offset-cursor));
        cursor=fixture[i].offset+fixture[i].bytes;
    }
    CHECK(!memcmp(flash_data+cursor,initial+cursor,FLASH_BYTES-cursor));
}

static void test_faults(void)
{
    /* Enumerate every physical callback in a real RMW; include silent short erase/program. */
    reset(256);open_fixture();uint8_t changed[11];
    for(unsigned i=0;i<sizeof(changed);++i)changed[i]=(uint8_t)~flash_data[fixture[0].offset+13+i];
    CHECK(jpeg_nor_write(&store,13,changed,sizeof(changed))==JPEG_NOR_OK);
    CHECK(jpeg_nor_sync(&store)==JPEG_NOR_OK);
    unsigned ordinals=model.calls;char trace[256];memcpy(trace,model.trace,sizeof(trace));
    CHECK(ordinals<sizeof(trace) && model.erases==1 && model.programs==16);
    for(unsigned mode=1;mode<=2;++mode)for(unsigned ordinal=1;ordinal<=ordinals;++ordinal) {
        if(mode==2 && trace[ordinal-1]!='P' && trace[ordinal-1]!='E')continue;
        reset(256);open_fixture();model.fail_at=ordinal;model.fault_mode=mode;
        jpeg_nor_result_t result=jpeg_nor_write(&store,13,changed,sizeof(changed));
        if(result==JPEG_NOR_OK)result=jpeg_nor_sync(&store);
        CHECK(result==(mode==1 ? JPEG_NOR_IO : JPEG_NOR_VERIFY));
        CHECK(store.failed);unsigned calls=model.calls;
        CHECK(jpeg_nor_read(&store,0,received,1)==JPEG_NOR_STATE);
        CHECK(jpeg_nor_write(&store,0,changed,1)==JPEG_NOR_STATE);
        CHECK(jpeg_nor_sync(&store)==JPEG_NOR_STATE && jpeg_nor_close(&store)==JPEG_NOR_STATE);
        CHECK(model.calls==calls);jpeg_nor_abort(&store);CHECK(model.calls==calls);
        check_protected();
        /* Cold recovery must read actual partial flash, never the failed RAM image. */
        memset(&store,0,sizeof(store));model.fail_at=0;
        jpeg_nor_device_t io=device();
        CHECK(jpeg_nor_open(&store,&io,fixture,2,LOGICAL_BYTES,allowed,2)==JPEG_NOR_OK);
        gather(fixture,2,LOGICAL_BYTES,logical,flash_data);
        CHECK(jpeg_nor_read(&store,0,received,LOGICAL_BYTES)==JPEG_NOR_OK);
        CHECK(!memcmp(received,logical,LOGICAL_BYTES));
        CHECK(jpeg_nor_close(&store)==JPEG_NOR_OK);++fault_scenarios;
    }
}

static void test_plan(void)
{
    /* Apply boundary/cross-extent writes to every store in the actual generated plan. */
    for(unsigned s=0;s<sizeof(plan_stores)/sizeof(plan_stores[0]);++s) {
        reset(256);model.capabilities=plan_stores[s].extents;model.count=plan_stores[s].count;
        jpeg_nor_device_t io=device();uint32_t bytes=plan_stores[s].logical_bytes;
        CHECK(bytes<=sizeof(logical));
        CHECK(jpeg_nor_open(&store,&io,plan_stores[s].extents,plan_stores[s].count,bytes,
            plan_allowed,(unsigned)(sizeof(plan_allowed)/sizeof(plan_allowed[0])))==JPEG_NOR_OK);
        gather(plan_stores[s].extents,plan_stores[s].count,bytes,logical,flash_data);
        uint8_t value=0x9c;CHECK(jpeg_nor_write(&store,0,&value,1)==JPEG_NOR_OK);logical[0]=value;
        value=0x37;CHECK(jpeg_nor_write(&store,bytes-1,&value,1)==JPEG_NOR_OK);logical[bytes-1]=value;
        uint32_t cursor=0;
        for(unsigned e=0;e+1<plan_stores[s].count;++e) {
            cursor+=plan_stores[s].extents[e].bytes;
            uint8_t crossing[]={0,255,0x5a,0xa5,0x7f,0x80};
            CHECK(cursor>=3 && cursor+3<=bytes);
            CHECK(jpeg_nor_write(&store,cursor-3,crossing,sizeof(crossing))==JPEG_NOR_OK);
            memcpy(logical+cursor-3,crossing,sizeof(crossing));
        }
        CHECK(jpeg_nor_read(&store,0,received,bytes)==JPEG_NOR_OK);
        CHECK(!memcmp(received,logical,bytes));CHECK(jpeg_nor_close(&store)==JPEG_NOR_OK);
        scatter(plan_stores[s].extents,plan_stores[s].count,bytes,logical);
        CHECK(!memcmp(flash_data,reference,sizeof(flash_data)));++layout_stores;
    }
}

int main(void)
{
    /* Retain non-FF neighbours so missing RMW restoration cannot pass accidentally. */
    for(uint32_t i=0;i<FLASH_BYTES;++i)initial[i]=(uint8_t)(i*37u+(i>>9)*7u);
    test_invalid();test_wear();test_abort_and_adjacent_capabilities();
    test_random(256);test_random(128);test_faults();test_plan();
    printf("{\"passed\":true,\"checks\":%u,\"random_operations\":%u,\"fault_scenarios\":%u,\"real_layout_stores\":%u,\"sector_cache_bytes\":%u,\"handle_bytes\":%zu,\"random_model_erase_calls\":%llu,\"random_model_program_calls\":%llu,\"physical_hardware_tested\":false}\n",
        checks,random_operations,fault_scenarios,layout_stores,JPEG_NOR_SECTOR_BYTES,sizeof(store),
        (unsigned long long)random_erases,(unsigned long long)random_programs);
    return 0;
}
