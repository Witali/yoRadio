/* Host binding for the REAL photo codec/cache, not a legacy decoder substitute. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include "../app/media/photo_storage.h"
#include "esp_timer.h"
#include <assert.h>

extern int native_photo_read(uint32_t,void *,size_t);
extern int native_photo_program(uint32_t,const void *,size_t);
extern int native_photo_erase(uint32_t);
static jpeg_transport_t transport;
static BCRYPT_ALG_HANDLE algorithm;
static BCRYPT_HASH_HANDLE operation;
size_t native_photo_available=SIZE_MAX;
size_t native_photo_service_free=SIZE_MAX;

bool photo_storage_service_memory(size_t *required,size_t *available)
{
    /* Simulate concurrent service allocations after job startup. */
    *required=16384;*available=native_photo_service_free;return *available>=*required;
}

size_t photo_storage_allocation_available(void)
{
    /* Fault control for the production allocator gate; OS heap is not C2 RAM. */
    return native_photo_available;
}

static uint64_t now(void *context)
{
    /* Share the native fixture's controlled monotonic clock. */
    (void)context;return (uint64_t)esp_timer_get_time();
}
static int read_flash(void *context,uint32_t at,void *data,size_t bytes)
{
    /* Same persistent physical bytes used by the existing partition adapters. */
    (void)context;return native_photo_read(at,data,bytes);
}
static int program(void *context,uint32_t at,const void *data,size_t bytes)
{
    /* Strict NOR model rejects0->1 and overrun; transport enforces capabilities. */
    (void)context;return native_photo_program(at,data,bytes);
}
static int erase(void *context,uint32_t at)
{
    /* Exactly one4KiB sector from the guard-authorized disposable maps. */
    (void)context;return native_photo_erase(at);
}
static int begin_hash(void *context)
{
    /* OS SHA-256 is independent of target PSA and the code being checked. */
    (void)context;assert(!operation);return BCryptCreateHash(algorithm,&operation,NULL,0,NULL,0,0)!=0;
}
static int update_hash(void *context,const void *data,size_t bytes)
{
    /* Production paths supply bounded blocks, no private hash implementation. */
    (void)context;return bytes>0xffffffffu || BCryptHashData(operation,(PUCHAR)data,(ULONG)bytes,0)!=0;
}
static int finish_hash(void *context,uint8_t digest[32])
{
    /* Do not release until the portable owner calls reset on every exit. */
    (void)context;return BCryptFinishHash(operation,digest,32,0)!=0;
}
static void reset_hash(void *context)
{
    /* Abort is valid after setup, partial input or finalization. */
    (void)context;if(operation){BCryptDestroyHash(operation);operation=NULL;}
}

esp_err_t photo_storage_authorize(const jpeg_guard_layout_t *layout,
                                 jpeg_transport_t **out,jpeg_guard_sha256_t *hash)
{
    /* This host map describes the fixture. SDK raw-table MD5/geometry discovery
     * is tested by the target binding, not pretended to execute on Windows. */
    const jpeg_guard_partition_t observed[]={
        {.label="nvs",.offset=0x9000,.bytes=0x6000,.type=1,.subtype=2},
        {.label="phy_init",.offset=0xf000,.bytes=0x1000,.type=1,.subtype=1},
        {.label="factory",.offset=0x10000,.bytes=0x177000,.type=0,.subtype=0},
        {.label="assets",.offset=0x200000,.bytes=0x1e7000,.type=1,.subtype=0x40}};
    if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0)!=0)return ESP_FAIL;
    jpeg_nor_device_t raw={NULL,0x400000,256,read_flash,program,erase};
    if(jpeg_transport_init(&transport,&raw,now,NULL)!=JPEG_TRANSPORT_OK)return ESP_FAIL;
    *hash=(jpeg_guard_sha256_t){NULL,begin_hash,update_hash,finish_hash,reset_hash};
    const jpeg_transport_limits_t limits={10000,0x400000,0,0,30000000};
    if(jpeg_transport_authorize(&transport,layout,observed,4,hash,&limits)!=JPEG_TRANSPORT_OK)return ESP_FAIL;
    *out=&transport;return ESP_OK;
}
