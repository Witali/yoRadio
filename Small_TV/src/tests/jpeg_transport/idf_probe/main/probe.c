/* Target-only storage gate: real SDK flash/partition/PSA APIs, no network/LCD. */
#include "jpeg_espidf.h"
#include "jpeg_nor.h"
#include "jpeg_layout.h"
#include "probe_map.h"
#include <stdio.h>
#include <string.h>

static jpeg_espidf_t storage;
static jpeg_nor_t scratch,cache;
static jpeg_transport_port_t scratch_port,cache_port;
static unsigned checks;
#define CHECK(v) do {++checks;if(!(v)){printf("JPEG_TRANSPORT_PROBE {\"event\":\"failure\",\"line\":%d,\"error\":%u}\n",__LINE__,storage.transport.last_error);return;}} while(0)

void app_main(void)
{
    /* Authorize, exercise real cross-sector RMW, then prove global revocation.
     * A second cold boot verifies persisted bytes without rewriting the data. */
    esp_err_t initialized=jpeg_espidf_init(&storage);
    if(initialized!=ESP_OK){printf("JPEG_TRANSPORT_PROBE {\"event\":\"init\",\"error\":%d}\n",initialized);return;}
    jpeg_transport_limits_t startup={8192,1048576,0,0,60000000};
    CHECK(jpeg_transport_begin(&storage.transport,&startup)==JPEG_TRANSPORT_STATE);
    jpeg_transport_result_t authorized=jpeg_espidf_authorize(&storage,&jpeg_layout,&startup);
    printf("JPEG_TRANSPORT_PROBE {\"event\":\"authorization\",\"authorized\":%s,\"result\":%u,\"discovery_error\":%d,\"physical_bytes\":%u,\"configured_bytes\":%u}\n",
        authorized==JPEG_TRANSPORT_OK ? "true" : "false",authorized,storage.discovery_error,
        (unsigned)storage.physical_bytes,(unsigned)storage.configured_bytes);
    if(authorized!=JPEG_TRANSPORT_OK)return;
    jpeg_transport_limits_t work={2048,65536,32768,8,20000000};
    CHECK(jpeg_transport_begin(&storage.transport,&work)==JPEG_TRANSPORT_OK);
    jpeg_nor_device_t scratch_io,cache_io;
    CHECK(jpeg_transport_port(&storage.transport,&scratch_port,probe_scratch,1,true,&scratch_io)==JPEG_TRANSPORT_OK);
    CHECK(jpeg_transport_port(&storage.transport,&cache_port,probe_cache,1,true,&cache_io)==JPEG_TRANSPORT_OK);
    CHECK(jpeg_nor_open(&scratch,&scratch_io,probe_scratch,1,8192,probe_scratch,1)==JPEG_NOR_OK);
    CHECK(jpeg_nor_open(&cache,&cache_io,probe_cache,1,4096,probe_cache,1)==JPEG_NOR_OK);
    uint8_t expected[32],actual[32],cache_expected[8],cache_actual[8];
    for(unsigned i=0;i<sizeof(expected);++i)expected[i]=(uint8_t)(i+1);
    memset(expected,0xff,5);
    for(unsigned i=0;i<sizeof(cache_expected);++i)cache_expected[i]=(uint8_t)(37+i);
    CHECK(jpeg_nor_read(&scratch,4090,actual,sizeof(actual))==JPEG_NOR_OK);
    CHECK(jpeg_nor_read(&cache,0,cache_actual,sizeof(cache_actual))==JPEG_NOR_OK);
    bool cold=!memcmp(expected,actual,sizeof(actual)) && !memcmp(cache_expected,cache_actual,sizeof(cache_actual));
    if(!cold) {
        uint8_t first[32];for(unsigned i=0;i<sizeof(first);++i)first[i]=(uint8_t)(i+1);
        CHECK(jpeg_nor_write(&scratch,4090,first,sizeof(first))==JPEG_NOR_OK);
        CHECK(jpeg_nor_sync(&scratch)==JPEG_NOR_OK);
        CHECK(jpeg_nor_write(&scratch,4090,expected,5)==JPEG_NOR_OK); /* actual0->1 RMW */
        CHECK(jpeg_nor_sync(&scratch)==JPEG_NOR_OK);
        CHECK(jpeg_nor_write(&cache,0,cache_expected,sizeof(cache_expected))==JPEG_NOR_OK);
        CHECK(jpeg_nor_sync(&cache)==JPEG_NOR_OK);
    }
    CHECK(jpeg_nor_read(&scratch,4090,actual,sizeof(actual))==JPEG_NOR_OK && !memcmp(expected,actual,sizeof(actual)));
    CHECK(jpeg_nor_read(&cache,0,cache_actual,sizeof(cache_actual))==JPEG_NOR_OK && !memcmp(cache_expected,cache_actual,sizeof(cache_actual)));
    CHECK(jpeg_nor_close(&scratch)==JPEG_NOR_OK && jpeg_nor_close(&cache)==JPEG_NOR_OK);
    jpeg_transport_usage_t data_usage=storage.transport.usage;
    /* Every protected capability request is rejected before any device call. */
    const uint32_t denied[]={0,0x10000,0x200000,0x28f000,0x3e7000};
    for(unsigned i=0;i<sizeof(denied)/sizeof(denied[0]);++i) {
        jpeg_nor_extent_t range={denied[i],4096};jpeg_transport_port_t rejected;jpeg_nor_device_t device;
        CHECK(jpeg_transport_port(&storage.transport,&rejected,&range,1,true,&device)==JPEG_TRANSPORT_RANGE);
    }
    CHECK(storage.transport.usage.calls==data_usage.calls);
    jpeg_transport_limits_t quota={1,4,0,0,1000000};
    CHECK(jpeg_transport_begin(&storage.transport,&quota)==JPEG_TRANSPORT_OK);
    CHECK(scratch_io.read(scratch_io.context,PROBE_SCRATCH_ADDRESS,actual,4)!=0); /* old epoch */
    CHECK(storage.transport.usage.calls==0);
    CHECK(jpeg_transport_port(&storage.transport,&scratch_port,probe_scratch,1,true,&scratch_io)==JPEG_TRANSPORT_OK);
    CHECK(jpeg_transport_port(&storage.transport,&cache_port,probe_cache,1,true,&cache_io)==JPEG_TRANSPORT_OK);
    CHECK(scratch_io.read(scratch_io.context,PROBE_SCRATCH_ADDRESS,actual,4)==0);
    CHECK(cache_io.read(cache_io.context,PROBE_CACHE_ADDRESS,actual,4)!=0);
    CHECK(storage.transport.last_error==JPEG_TRANSPORT_LIMIT && storage.transport.usage.calls==1);
    CHECK(scratch_io.read(scratch_io.context,PROBE_SCRATCH_ADDRESS,actual,4)!=0 && storage.transport.usage.calls==1);
    jpeg_transport_revoke(&storage.transport);
    CHECK(!storage.transport.authorized);
    printf("JPEG_TRANSPORT_PROBE {\"event\":\"complete\",\"passed\":true,\"cold\":%s,\"checks\":%u,\"data_calls\":%llu,\"data_read_bytes\":%llu,\"data_program_bytes\":%llu,\"data_erases\":%llu}\n",
        cold ? "true" : "false",checks,(unsigned long long)data_usage.calls,(unsigned long long)data_usage.read_bytes,
        (unsigned long long)data_usage.program_bytes,(unsigned long long)data_usage.erase_calls);
}
