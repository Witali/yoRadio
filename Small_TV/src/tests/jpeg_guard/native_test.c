/* Independent host contract: real sanitized assets, Windows SHA-256 provider,
 * strict readonly NOR transport and fresh verification after every failure. */
#include "../../storage/jpeg_guard.h"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "jpeg_layout.h"

#define FLASH_BYTES 0x400000u
#define CHECK(value) do {++checks; if (!(value)) {fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#value);exit(1);}} while (0)
static uint8_t flash_data[FLASH_BYTES];
static unsigned checks, rejected_corruptions, read_faults, hash_faults, layout_rejections;
static jpeg_guard_partition_t observed[JPEG_GUARD_MAX_PARTITIONS];
static jpeg_guard_resource_t resources[JPEG_GUARD_MAX_RESOURCES];
static jpeg_nor_extent_t allowed[JPEG_NOR_MAX_EXTENTS], protected_ranges[JPEG_NOR_MAX_EXTENTS];
static jpeg_guard_layout_t layout;
static BCRYPT_ALG_HANDLE algorithm;
static struct {
    BCRYPT_HASH_HANDLE hash;
    unsigned reads, read_bytes, fail_read, silent_read, hash_calls, fail_hash;
    unsigned begins, finishes, resets, writes;
} model;

static bool hash_call(void)
{
    /* A provider failure is separate from flash transport failure. */
    return ++model.hash_calls == model.fail_hash;
}

static int hash_begin(void *context)
{
    /* Allocate real OS SHA state; reset must release even a partial begin. */
    CHECK(context == &model && !model.hash);
    ++model.begins;
    CHECK(BCryptCreateHash(algorithm, &model.hash, NULL, 0, NULL, 0, 0) >= 0);
    return hash_call() ? -91 : 0;
}

static int hash_update(void *context, const void *data, size_t bytes)
{
    /* Exercise a streaming provider, not a hard-coded expected digest. */
    CHECK(context == &model && model.hash && bytes <= JPEG_GUARD_READ_BYTES);
    CHECK(BCryptHashData(model.hash, (PUCHAR)data, (ULONG)bytes, 0) >= 0);
    return hash_call() ? -91 : 0;
}

static int hash_finish(void *context, uint8_t digest[32])
{
    /* Even an error after computing the digest must not authorize writes. */
    CHECK(context == &model && model.hash);
    ++model.finishes;
    CHECK(BCryptFinishHash(model.hash, digest, 32, 0) >= 0);
    return hash_call() ? -91 : 0;
}

static void hash_reset(void *context)
{
    /* Idempotent ownership cleanup after every attempted resource hash. */
    CHECK(context == &model);
    if (model.hash) CHECK(BCryptDestroyHash(model.hash) >= 0);
    model.hash = NULL;
    ++model.resets;
}

static int read_flash(void *context, uint32_t address, void *data, size_t bytes)
{
    /* No read may touch a photo, scratch, unused padding, settings or boot data. */
    CHECK(context == &model && bytes && bytes <= JPEG_GUARD_READ_BYTES);
    CHECK(address <= FLASH_BYTES && bytes <= FLASH_BYTES-address);
    bool readable = false;
    for (unsigned i = 0; i < jpeg_layout.resource_count; ++i) {
        const jpeg_guard_resource_t *r = &jpeg_layout.resources[i];
        if (address >= r->offset && address-r->offset < r->bytes &&
            bytes <= r->bytes-(address-r->offset)) readable = true;
    }
    CHECK(readable);
    ++model.reads;
    model.read_bytes += (unsigned)bytes;
    if (model.reads == model.fail_read) {
        memcpy(data, flash_data+address, bytes/2);
        return -77;
    }
    memcpy(data, flash_data+address, bytes);
    if (model.reads == model.silent_read) ((uint8_t *)data)[bytes-1] ^= 1;
    return 0;
}

static int program_flash(void *context, uint32_t address, const void *data, size_t bytes)
{
    /* Guard must never issue writes; detect a forbidden call without changing flash. */
    (void)context; (void)address; (void)data; (void)bytes;
    ++model.writes;
    return -88;
}

static int erase_flash(void *context, uint32_t address)
{
    /* Same assertion for erase, including paths taken after a guard failure. */
    (void)context; (void)address;
    ++model.writes;
    return -88;
}

static jpeg_nor_device_t device(void)
{
    /* Geometry includes write callbacks specifically to prove none are used. */
    jpeg_nor_device_t result = {&model, FLASH_BYTES, 256, read_flash, program_flash, erase_flash};
    return result;
}

static jpeg_guard_sha256_t provider(void)
{
    /* Production will provide mbedTLS with the identical streaming contract. */
    jpeg_guard_sha256_t result = {&model, hash_begin, hash_update, hash_finish, hash_reset};
    return result;
}

static void reset(void)
{
    /* Descriptor mutations and failures never leak into the next boot attempt. */
    CHECK(!model.hash);
    memset(&model, 0, sizeof(model));
    layout = jpeg_layout;
    memcpy(observed, jpeg_layout.partitions, jpeg_layout.partition_count*sizeof(observed[0]));
    memcpy(resources, jpeg_layout.resources, jpeg_layout.resource_count*sizeof(resources[0]));
    memcpy(allowed, jpeg_layout.allowed, jpeg_layout.allowed_count*sizeof(allowed[0]));
    memcpy(protected_ranges, jpeg_layout.protected_ranges, jpeg_layout.protected_count*sizeof(protected_ranges[0]));
    layout.resources = resources;
    layout.allowed = allowed;
    layout.protected_ranges = protected_ranges;
}

static jpeg_guard_result_t verify(void)
{
    /* Inspect cleanup and readonly properties on every outcome. */
    jpeg_nor_device_t io = device();
    jpeg_guard_sha256_t sha = provider();
    jpeg_guard_result_t result = jpeg_guard_verify(&layout, observed, jpeg_layout.partition_count, &io, &sha);
    CHECK(!model.hash && model.resets == model.begins && !model.writes);
    return result;
}

static void reject_layout(void)
{
    /* Invalid ownership must be rejected before hashing or reading any byte. */
    CHECK(verify() == JPEG_GUARD_LAYOUT);
    CHECK(!model.reads && !model.hash_calls);
    ++layout_rejections;
}

static void test_positive(void)
{
    /* Compute actual content hashes; user/cache/settings mutations remain legal. */
    reset(); CHECK(verify() == JPEG_GUARD_OK);
    uint32_t total = 0;
    for (unsigned i = 0; i < jpeg_layout.resource_count; ++i) total += resources[i].bytes;
    CHECK(model.read_bytes == total && model.begins == 28 && model.finishes == 28);
    for (uint32_t a = 0; a < FLASH_BYTES; ++a) {
        bool immutable = false;
        for (unsigned i = 0; i < jpeg_layout.resource_count; ++i)
            if (a >= resources[i].offset && a-resources[i].offset < resources[i].bytes) immutable = true;
        if (!immutable) flash_data[a] ^= (uint8_t)(a*13u+71u);
    }
    reset(); CHECK(verify() == JPEG_GUARD_OK);
    /* SHA-256 known-answer check independently of the generated resource hashes. */
    static const uint8_t abc[32] = {0xba,0x78,0x16,0xbf,0x8f,0x01,0xcf,0xea,0x41,0x41,0x40,0xde,0x5d,0xae,0x22,0x23,
        0xb0,0x03,0x61,0xa3,0x96,0x17,0x7a,0x9c,0xb4,0x10,0xff,0x61,0xf2,0x00,0x15,0xad};
    uint8_t digest[32];
    CHECK(!hash_begin(&model) && !hash_update(&model,"abc",3) && !hash_finish(&model,digest));
    hash_reset(&model); CHECK(!memcmp(digest,abc,32));
}

static void test_corruption(void)
{
    /* First/middle/last byte in EVERY immutable animation/icon, no masked range. */
    for (unsigned i = 0; i < jpeg_layout.resource_count; ++i) {
        uint32_t positions[] = {0, jpeg_layout.resources[i].bytes/2, jpeg_layout.resources[i].bytes-1};
        for (unsigned n = 0; n < 3; ++n) {
            uint32_t a = jpeg_layout.resources[i].offset+positions[n];
            flash_data[a] ^= 1;
            reset(); CHECK(verify() == JPEG_GUARD_RESOURCE);
            CHECK(model.begins == i+1 && model.finishes == i+1);
            flash_data[a] ^= 1;
            reset(); CHECK(verify() == JPEG_GUARD_OK);
            ++rejected_corruptions;
        }
    }
}

static void test_unmarked_image(void)
{
    /* App-only upgrade over legacy assets must never gain write permission. */
    uint8_t saved[64];
    memcpy(saved,flash_data+JPEG_LAYOUT_OWNERSHIP_STAMP_ADDRESS,sizeof(saved));
    memset(flash_data+JPEG_LAYOUT_OWNERSHIP_STAMP_ADDRESS,0xff,sizeof(saved));
    reset(); CHECK(verify() == JPEG_GUARD_RESOURCE);
    memcpy(flash_data+JPEG_LAYOUT_OWNERSHIP_STAMP_ADDRESS,saved,sizeof(saved));
    reset(); CHECK(verify() == JPEG_GUARD_OK);
}

static void test_layout(void)
{
    /* The runtime map includes type/subtype/flags/label, not just two offsets. */
    for (unsigned i = 0; i < jpeg_layout.partition_count; ++i) {
        reset(); observed[i].offset += 4096; reject_layout();
        reset(); observed[i].bytes -= 4096; reject_layout();
        reset(); observed[i].type ^= 1; reject_layout();
        reset(); observed[i].subtype ^= 1; reject_layout();
        reset(); observed[i].flags = 1; reject_layout();
        reset(); observed[i].label[0] ^= 1; reject_layout();
    }
    reset(); layout.flash_bytes /= 2; reject_layout();
    reset(); layout.partition_count--; reject_layout();
    reset(); layout.partition_count = 9; reject_layout();
    reset(); layout.assets_partition = 4; reject_layout();
    reset(); layout.resource_count = 0; reject_layout();
    reset(); layout.resource_count = 33; reject_layout();
    reset(); layout.resources = NULL; reject_layout();
    reset(); layout.allowed_count = 0; reject_layout();
    reset(); layout.allowed_count = 17; reject_layout();
    reset(); layout.protected_count = 17; reject_layout();
    reset(); allowed[0].offset++; reject_layout();
    reset(); allowed[0].bytes--; reject_layout();
    reset(); allowed[0].bytes += 4096; reject_layout(); /* overlaps protected boundary */
    reset(); allowed[0].bytes -= 4096; reject_layout(); /* unclassified sector */
    reset(); allowed[1].offset = 0xfffff000; allowed[1].bytes = 8192; reject_layout();
    reset(); allowed[6].bytes -= 4096; reject_layout(); /* final boundary */
    reset(); protected_ranges[0].offset = 4096; reject_layout(); /* boot protection */
    reset(); resources[0].offset = 0x290000; reject_layout(); /* cache/immutable overlap */
    reset(); resources[0].bytes = 0xffffffff; reject_layout();
    reset(); resources[27].offset = 0x3e7000; reject_layout(); /* settings */
    reset(); resources[1].offset = resources[0].offset; reject_layout();
    /* Even a coherently reclassified sector cannot claim boot/NVS or settings. */
    reset(); protected_ranges[0].bytes -= 4096; allowed[0].offset -= 4096; allowed[0].bytes += 4096;
    reject_layout();
    reset();
    memmove(allowed+1,allowed,jpeg_layout.allowed_count*sizeof(allowed[0]));
    allowed[0] = (jpeg_nor_extent_t){0,4096}; layout.allowed_count++;
    protected_ranges[0].offset += 4096; protected_ranges[0].bytes -= 4096;
    reject_layout(); /* bootloader prefix lies outside listed partitions */
    reset(); protected_ranges[8].offset += 4096; protected_ranges[8].bytes -= 4096; allowed[6].bytes += 4096;
    reject_layout();
    reset(); protected_ranges[1].offset += 4096; protected_ranges[1].bytes -= 4096; allowed[0].bytes += 4096;
    reject_layout(); /* first photo sector cannot become scratch */
    reset();
    jpeg_nor_device_t io = device(); jpeg_guard_sha256_t sha = provider();
    CHECK(jpeg_guard_verify(&layout, observed, 3, &io, &sha) == JPEG_GUARD_LAYOUT);
    CHECK(jpeg_guard_verify(&layout, NULL, 4, &io, &sha) == JPEG_GUARD_LAYOUT);
    CHECK(jpeg_guard_verify(NULL, observed, 4, &io, &sha) == JPEG_GUARD_ARGUMENT);
    io.read = NULL;
    CHECK(jpeg_guard_verify(&layout, observed, 4, &io, &sha) == JPEG_GUARD_ARGUMENT);
    io = device(); sha.update = NULL;
    CHECK(jpeg_guard_verify(&layout, observed, 4, &io, &sha) == JPEG_GUARD_ARGUMENT);
    CHECK(!model.reads && !model.hash_calls);
}

static void test_faults(void)
{
    /* Every actual read callback can fail partially. Fresh success afterwards
     * proves hash cleanup and that a previous failure cannot poison later boots. */
    reset(); CHECK(verify() == JPEG_GUARD_OK);
    unsigned reads = model.reads, calls = model.hash_calls;
    for (unsigned n = 1; n <= reads; ++n) {
        reset(); model.fail_read = n;
        CHECK(verify() == JPEG_GUARD_IO && model.reads == n);
        ++read_faults;
    }
    /* Every SHA begin/update/finish can fail, including after finishing digest. */
    for (unsigned n = 1; n <= calls; ++n) {
        reset(); model.fail_hash = n;
        CHECK(verify() == JPEG_GUARD_HASH && model.hash_calls == n);
        ++hash_faults;
    }
    /* Success-reporting read corruption is independently rejected by SHA. */
    for (unsigned n = 1; n <= reads; n += 31) {
        reset(); model.silent_read = n;
        CHECK(verify() == JPEG_GUARD_RESOURCE);
        ++read_faults;
    }
    reset(); CHECK(verify() == JPEG_GUARD_OK);
}

int main(int argc, char **argv)
{
    /* Load only sanitized assets; never read a device or raw user flash dump. */
    CHECK(argc == 2 && BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0) >= 0);
    memset(flash_data,0xa5,sizeof(flash_data));
    FILE *file = fopen(argv[1],"rb"); CHECK(file);
    CHECK(fread(flash_data+0x200000,1,0x1e7000,file) == 0x1e7000);
    CHECK(fgetc(file) == EOF && !ferror(file)); CHECK(!fclose(file));
    test_positive(); test_corruption(); test_unmarked_image(); test_layout(); test_faults();
    CHECK(BCryptCloseAlgorithmProvider(algorithm,0) >= 0);
    printf("{\"passed\":true,\"checks\":%u,\"immutable_payloads\":27,\"ownership_stamps\":1,\"corruptions_rejected\":%u,"
           "\"layout_rejections\":%u,\"read_faults\":%u,\"hash_faults\":%u,"
           "\"max_read_bytes\":256,\"program_erase_calls\":0,\"production_linked\":false}\n",
           checks,rejected_corruptions,layout_rejections,read_faults,hash_faults);
    return 0;
}
