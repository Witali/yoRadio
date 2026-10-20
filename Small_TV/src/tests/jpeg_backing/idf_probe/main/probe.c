/* Target-only decoder/NOR gate; real SDK flash and PSA, no Wi-Fi/LCD or upload. */
#include "jpeg_backing.h"
#include "jpeg_espidf.h"
#include "jpeg_layout.h"
#include "probe_fixture.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static jpeg_espidf_t storage;
static jpeg_nor_t nor;
static jpeg_transport_port_t port;
static jpeg_backing_t backing;
static uint8_t bitmap[(SCRATCH_LOGICAL_BYTES/4096u+8u)/8u];
static size_t requested,peak;
static unsigned checks,passes,checkpoint_calls;
static const probe_fixture_t *fixture;
static uint32_t next_row;
static psa_hash_operation_t rows_hash=PSA_HASH_OPERATION_INIT;
#define CHECK(v) do {++checks;if(!(v)){printf("JPEG_DECODER_PROBE {\"event\":\"failure\",\"line\":%d,\"transport_error\":%u}\n",__LINE__,storage.transport.last_error);return false;}} while(0)

static void *allocate(void *context,size_t bytes)
{
    /* Count actual requested context/pools separately from SDK heap overhead. */
    (void)context;void *data=malloc(bytes);
    if(data){requested+=bytes;if(requested>peak)peak=requested;}return data;
}

static void release(void *context,void *data,size_t bytes)
{
    /* Production allocator API provides the exact released request size. */
    (void)context;configASSERT(bytes<=requested);requested-=bytes;free(data);
}

static int storage_check(void *context)
{
    /* This check also covers buffered NOR work without physical callbacks. */
    (void)context;return jpeg_transport_check(&storage.transport);
}

static jpeg_decode_check_t request_check(void *context)
{
    /* Preserve the transport's precise global stop reason on callback failure.
     * Yield only in this standalone probe so the watchdog/idle task can run. */
    (void)context;if(++checkpoint_calls%64u==0)vTaskDelay(1);
    jpeg_transport_result_t result=jpeg_transport_check(&storage.transport);
    /* Inactive handles return STATE; the owner retains the original cause. */
    if(result==JPEG_TRANSPORT_STATE && storage.transport.last_error!=JPEG_TRANSPORT_OK)result=storage.transport.last_error;
    if(result==JPEG_TRANSPORT_OK || result==JPEG_TRANSPORT_IO)return JPEG_CHECK_OK;
    if(result==JPEG_TRANSPORT_LIMIT)return JPEG_CHECK_IO_LIMIT;
    if(result==JPEG_TRANSPORT_TIME)return JPEG_CHECK_TIME;
    return JPEG_CHECK_CANCELLED;
}

static int read_input(void *context,uint32_t offset,void *data,size_t bytes)
{
    /* Const fixture source is bounded; only backing uses actual esp_flash I/O. */
    (void)context;if(offset>fixture->bytes || bytes>fixture->bytes-offset)return -1;
    memcpy(data,fixture->data+offset,bytes);return 0;
}

static int output_row(void *context,uint32_t row,const uint16_t *pixels,uint32_t count)
{
    /* Hash actual little-endian RGB565 output without allocating a full frame. */
    (void)context;if(row!=next_row || !count || count>240)return -1;
    if(psa_hash_update(&rows_hash,(const uint8_t *)pixels,count*sizeof(*pixels))!=PSA_SUCCESS)return -2;
    ++next_row;return 0;
}

static bool begin_job(uint64_t calls)
{
    /* Drop old disposable cache BEFORE reusing its borrowed transport port. */
    jpeg_backing_abort(&backing);
    jpeg_transport_limits_t limits={calls,32u*1024u*1024u,4u*1024u*1024u,256,180000000};
    CHECK(jpeg_transport_begin(&storage.transport,&limits)==JPEG_TRANSPORT_OK);
    jpeg_nor_device_t device;
    CHECK(jpeg_transport_port(&storage.transport,&port,scratch_extents,SCRATCH_EXTENT_COUNT,true,&device)==JPEG_TRANSPORT_OK);
    CHECK(jpeg_nor_open(&nor,&device,scratch_extents,SCRATCH_EXTENT_COUNT,SCRATCH_LOGICAL_BYTES,jpeg_layout.allowed,jpeg_layout.allowed_count)==JPEG_NOR_OK);
    CHECK(jpeg_backing_begin(&backing,&nor,storage_check,NULL,bitmap,sizeof(bitmap))==JPEG_SCRATCH_OK);
    return true;
}

static bool decode_case(jpeg_decoder_t *decoder,const char *name,unsigned image,jpeg_decode_status_t expected)
{
    /* Rows remain provisional until OK and the independent digest match. */
    fixture=&fixtures[image];next_row=0;checkpoint_calls=0;
    CHECK(psa_hash_setup(&rows_hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
    printf("JPEG_DECODER_PROBE {\"event\":\"start\",\"case\":\"%s\"}\n",name);
    jpeg_decode_request_t request={NULL,fixture->bytes,0,0,read_input,output_row,request_check};
    jpeg_decode_diagnostic_t d={0};int64_t start=esp_timer_get_time();
    jpeg_decode_status_t result=jpeg_decoder_decode(decoder,&request,&d);
    int64_t elapsed=esp_timer_get_time()-start;uint8_t digest[32];size_t bytes=0;
    CHECK(psa_hash_finish(&rows_hash,digest,sizeof(digest),&bytes)==PSA_SUCCESS && bytes==32);
    CHECK(psa_hash_abort(&rows_hash)==PSA_SUCCESS);
    CHECK(result==expected && d.stores_opened==d.stores_closed && !backing.scratch.active_files);
    if(expected==JPEG_DECODE_OK)CHECK(next_row==d.height && !memcmp(digest,fixture->expected,32));
    else CHECK(!d.rows);
    if(expected==JPEG_DECODE_BACKING_LIMIT)CHECK(d.required==460800 && d.available==460799 && !storage.transport.usage.calls);
    if(expected==JPEG_DECODE_IO_LIMIT)CHECK(storage.transport.usage.calls==17 && d.callback_error);
    jpeg_transport_usage_t usage=storage.transport.usage;
    uint64_t before=usage.calls;jpeg_backing_abort(&backing);CHECK(storage.transport.usage.calls==before);
    ++passes;
    printf("JPEG_DECODER_PROBE {\"event\":\"case\",\"case\":\"%s\",\"status\":\"%s\",\"passed\":true,\"elapsed_us\":%lld,\"pool_peak\":%llu,\"context_bytes\":%u,\"requested_peak\":%u,\"required\":%llu,\"available\":%llu,\"reused\":%s,\"calls\":%llu,\"read_bytes\":%llu,\"program_bytes\":%llu,\"erases\":%llu,\"stack_free_bytes\":%u}\n",
        name,jpeg_decoder_status_name(result),(long long)elapsed,(unsigned long long)d.pool_peak,(unsigned)d.context_bytes,(unsigned)peak,
        (unsigned long long)d.required,(unsigned long long)d.available,d.reused_object ? "true":"false",
        (unsigned long long)usage.calls,(unsigned long long)usage.read_bytes,(unsigned long long)usage.program_bytes,
        (unsigned long long)usage.erase_calls,(unsigned)uxTaskGetStackHighWaterMark(NULL));
    return true;
}

static bool run_probe(void)
{
    /* Full linked target pipeline, reuse after quota failure and capacity refusal. */
    CHECK(jpeg_espidf_init(&storage)==ESP_OK);
    jpeg_transport_limits_t startup={8192,1048576,0,0,60000000};
    jpeg_transport_result_t authorization=jpeg_espidf_authorize(&storage,&jpeg_layout,&startup);
    printf("JPEG_DECODER_PROBE {\"event\":\"authorization\",\"authorized\":%s,\"result\":%u}\n",authorization==JPEG_TRANSPORT_OK ? "true":"false",authorization);
    CHECK(authorization==JPEG_TRANSPORT_OK && begin_job(100000));
    jpeg_decoder_config_t config={{NULL,allocate,release},jpeg_backing_callbacks(&backing),65536,240,240};
    jpeg_decode_diagnostic_t d={0};jpeg_decoder_t *decoder=jpeg_decoder_create(&config,&d);CHECK(decoder);
    CHECK(decode_case(decoder,"small-cmyk12",0,JPEG_DECODE_OK));
    CHECK(begin_job(17) && decode_case(decoder,"quota",0,JPEG_DECODE_IO_LIMIT));
    CHECK(begin_job(100000) && decode_case(decoder,"recover",0,JPEG_DECODE_OK));
    CHECK(begin_job(100000) && decode_case(decoder,"full-cmyk12",1,JPEG_DECODE_OK));
    CHECK(begin_job(100000) && decode_case(decoder,"lossless16",2,JPEG_DECODE_OK));
    CHECK(begin_job(100000) && decode_case(decoder,"gray",3,JPEG_DECODE_OK));
    jpeg_decoder_destroy(decoder);CHECK(!requested && begin_job(100000));
    config.backing.capacity=460799;decoder=jpeg_decoder_create(&config,&d);CHECK(decoder);
    CHECK(decode_case(decoder,"capacity",1,JPEG_DECODE_BACKING_LIMIT));
    jpeg_decoder_destroy(decoder);CHECK(!requested);
    jpeg_transport_revoke(&storage.transport);
    printf("JPEG_DECODER_PROBE {\"event\":\"complete\",\"passed\":true,\"checks\":%u,\"cases\":%u,\"heap_final_requested\":%u,\"heap_peak_requested\":%u,\"heap_minimum_free\":%u,\"adapter_bytes\":%u,\"nor_bytes\":%u,\"stack_free_bytes\":%u}\n",
        checks,passes,(unsigned)requested,(unsigned)peak,(unsigned)heap_caps_get_minimum_free_size(MALLOC_CAP_8BIT),(unsigned)sizeof(backing),(unsigned)sizeof(nor),(unsigned)uxTaskGetStackHighWaterMark(NULL));
    return true;
}

void app_main(void)
{
    /* Only this owned standalone firmware executes the destructive scratch test. */
    (void)run_probe();
}
