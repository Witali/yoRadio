/* REQUESTED_CHANGE: one verified producer and durable cache for actual photos. */
#include "photo_codec.h"
#include "photo_storage.h"
#include "jpeg_baseline.h"
#include "jpeg_backing.h"
#include "jpeg_cache_layout.h"
#include "board.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static struct {
    jpeg_transport_t *transport;
    jpeg_guard_sha256_t hash;
    jpeg_transport_port_t ports[4];
    jpeg_cache_t cache;
    jpeg_nor_t scratch;
    jpeg_backing_t backing;
    uint8_t fresh[(JPEG_CACHE_SCRATCH_BYTES/4096u+8u)/8u];
    size_t allocation_required,allocation_available;
    bool allocation_refused,service_refused,decoding;
    bool initialized,background;
} codec;

static jpeg_decode_check_t request_check(void *context)
{
    /* Every source/cache/scratch/decoder callback shares one stop cause. */
    (void)context;
    if(codec.background && photo_codec_cancelled())return JPEG_CHECK_CANCELLED;
    jpeg_transport_result_t result=jpeg_transport_check(codec.transport);
    if(result==JPEG_TRANSPORT_STATE && codec.transport->last_error!=JPEG_TRANSPORT_OK)
        result=codec.transport->last_error;
    if(result==JPEG_TRANSPORT_TIME)return JPEG_CHECK_TIME;
    if(result==JPEG_TRANSPORT_LIMIT)return JPEG_CHECK_IO_LIMIT;
    size_t required,available;
    if(codec.service_refused)return JPEG_CHECK_CANCELLED;
    if(codec.decoding && !photo_storage_service_memory(&required,&available)) {
        /* FIXED_RECONSTRUCTION: allocation-time headroom alone is insufficient;
         * Wi-Fi/HTTP can allocate later. Abort cooperatively before starving
         * the other tasks, unwind codec pools and report the exact reserve. */
        codec.service_refused=true;codec.allocation_required=required;
        codec.allocation_available=available;return JPEG_CHECK_CANCELLED;
    }
    return result==JPEG_TRANSPORT_OK || result==JPEG_TRANSPORT_IO ? JPEG_CHECK_OK:JPEG_CHECK_CANCELLED;
}

static int checkpoint(void *context)
{
    /* The cache also checks buffered RAM work, not only physical callbacks. */
    return request_check(context)!=JPEG_CHECK_OK;
}

static void end_job(void)
{
    /* Discard every borrower BEFORE reusing port memory; cleanup never flushes. */
    jpeg_cache_abort(&codec.cache);jpeg_backing_abort(&codec.backing);
    jpeg_nor_abort(&codec.scratch);jpeg_transport_end(codec.transport);
}

static esp_err_t begin_job(unsigned slot,bool writing,bool background,photo_diagnostic_t *diagnostic)
{
    /* Capability maps are compiled constants, never flash offsets from HTTP. */
    memset(diagnostic,0,sizeof(*diagnostic));
    if(!codec.initialized || slot>=PHOTO_COUNT){diagnostic->status=PHOTO_STORAGE;return ESP_ERR_INVALID_STATE;}
    end_job();codec.background=background;codec.allocation_refused=false;
    codec.service_refused=codec.decoding=false;
    const jpeg_transport_limits_t limits={writing ? 200000:5000,writing ? 64000000:2000000,
                                         writing ? 16000000:0,writing ? 4096:0,
                                         writing ? 180000000:2000000};
    if(jpeg_transport_begin(codec.transport,&limits)!=JPEG_TRANSPORT_OK)goto failed;
    jpeg_cache_devices_t devices;
    const jpeg_nor_extent_t sources={ASSETS_BASE,PHOTO_COUNT*PHOTO_SLOT_BYTES};
    const jpeg_nor_extent_t metadata[]={
        {jpeg_cache_layout.journal.banks[0],4096},{jpeg_cache_layout.journal.banks[1],4096}};
    if(jpeg_transport_port(codec.transport,&codec.ports[0],&sources,1,false,&devices.source) ||
       jpeg_transport_port(codec.transport,&codec.ports[1],jpeg_cache_layout.frames[slot].extents,
            jpeg_cache_layout.frames[slot].count,writing,&devices.frames) ||
       jpeg_transport_port(codec.transport,&codec.ports[2],metadata,2,writing,&devices.metadata))goto failed;
    diagnostic->cache=jpeg_cache_open(&codec.cache,&jpeg_cache_layout,&devices,&codec.hash,checkpoint,NULL);
    if(diagnostic->cache!=JPEG_CACHE_OK)goto failed;
    return ESP_OK;
failed:
    diagnostic->status=PHOTO_STORAGE;return ESP_FAIL;
}

static esp_err_t finish_job(esp_err_t result,photo_diagnostic_t *diagnostic)
{
    /* Preserve low-level causes before cleanup resets reusable handles. */
    diagnostic->transport=codec.transport ? codec.transport->last_error:JPEG_TRANSPORT_STATE;
    diagnostic->io=codec.transport ? codec.transport->last_io_error:0;
    if(result!=ESP_OK && codec.service_refused) {
        diagnostic->status=PHOTO_MEMORY;diagnostic->service_memory=true;
        diagnostic->required=codec.allocation_required;diagnostic->available=codec.allocation_available;
        diagnostic->available_known=true;
    }
    if(result!=ESP_OK && diagnostic->status==PHOTO_DECODE &&
       diagnostic->decode.status==JPEG_DECODE_ALLOCATION && codec.allocation_refused) {
        diagnostic->status=PHOTO_MEMORY;diagnostic->required=codec.allocation_required;
        diagnostic->available=codec.allocation_available;diagnostic->available_known=true;
    }
    if(codec.cache.failed)diagnostic->cache=codec.cache.last_error;
    if(codec.cache.last_error==JPEG_CACHE_SOURCE_LIMIT) {
        diagnostic->required=codec.cache.required;diagnostic->available=codec.cache.available;
        diagnostic->available_known=true;
    }
    if(result!=ESP_OK && diagnostic->status==PHOTO_OK)diagnostic->status=PHOTO_STORAGE;
    end_job();return result;
}

static int input(void *context,uint32_t offset,void *data,size_t bytes)
{
    /* Includes fresh physical readback, not only before/after source hashes. */
    (void)context;return jpeg_cache_read_source(&codec.cache,offset,data,bytes);
}

static int output(void *context,uint32_t row,const uint16_t *data,uint32_t count)
{
    /* Producer rows remain provisional until physical verification and journal. */
    (void)context;return jpeg_cache_write_row(&codec.cache,row,data,count);
}

static void *allocate(void *context,size_t bytes)
{
    /* All producers preserve platform service headroom, including the factory
     * strip producer. This is a resource refusal, never a damaged-JPEG error.
     * Libjpeg may retry a smaller allocation; only its final fatal is reported. */
    (void)context;size_t available=photo_storage_allocation_available();
    codec.allocation_refused=bytes>available;
    if(codec.allocation_refused) {
        codec.allocation_required=bytes;codec.allocation_available=available;return NULL;
    }
    return malloc(bytes);
}

static void release(void *context,void *data,size_t bytes)
{
    /* Both the factory strip producer and libjpeg release on every failure path. */
    (void)context;(void)bytes;free(data);
}

static bool decode(uint32_t length,photo_diagnostic_t *diagnostic)
{
    /* Metadata is inspected first. Each complete decode writes ordered rows once;
     * prepare-only TJpgd refusal can fall back before emitting a single row. */
    jpeg_privacy_source_t source={NULL,length,input,checkpoint};
    if(jpeg_privacy_check(&source,&diagnostic->privacy)!=JPEG_PRIVACY_OK) {
        diagnostic->status=PHOTO_PRIVACY;return false;
    }
    jpeg_decode_request_t request={NULL,length,LCD_WIDTH,LCD_HEIGHT,input,output,request_check};
    jpeg_decode_allocator_t allocator={NULL,allocate,release};
    if(diagnostic->privacy.process==0xc0 && diagnostic->privacy.precision==8 &&
       diagnostic->privacy.components<=3 &&
       !(diagnostic->privacy.components==3 && diagnostic->privacy.adobe_transform==1)) {
        diagnostic->baseline=true;
        jpeg_decode_status_t status=jpeg_baseline_decode(&request,&allocator,&diagnostic->decode);
        if(status==JPEG_DECODE_OK)return true;
        if(status!=JPEG_DECODE_UNSUPPORTED || diagnostic->decode.rows) {
            diagnostic->status=PHOTO_DECODE;return false;
        }
    }
    diagnostic->baseline=false;
    jpeg_nor_device_t device;
    if(jpeg_transport_port(codec.transport,&codec.ports[3],jpeg_cache_scratch_extents,
        JPEG_CACHE_SCRATCH_EXTENTS,true,&device)!=JPEG_TRANSPORT_OK ||
       jpeg_nor_open(&codec.scratch,&device,jpeg_cache_scratch_extents,JPEG_CACHE_SCRATCH_EXTENTS,
           JPEG_CACHE_SCRATCH_BYTES,jpeg_layout.allowed,jpeg_layout.allowed_count)!=JPEG_NOR_OK ||
       jpeg_backing_begin(&codec.backing,&codec.scratch,checkpoint,NULL,codec.fresh,sizeof(codec.fresh))!=JPEG_SCRATCH_OK) {
        diagnostic->status=PHOTO_STORAGE;return false;
    }
    jpeg_decoder_config_t config={allocator,jpeg_backing_callbacks(&codec.backing),65536,LCD_WIDTH,LCD_HEIGHT};
    jpeg_decoder_t *decoder=jpeg_decoder_create(&config,&diagnostic->decode);
    if(!decoder){diagnostic->status=PHOTO_DECODE;return false;}
    jpeg_decode_status_t status=jpeg_decoder_decode(decoder,&request,&diagnostic->decode);
    jpeg_decoder_destroy(decoder);
    if(status!=JPEG_DECODE_OK){diagnostic->status=PHOTO_DECODE;return false;}
    return true;
}

esp_err_t photo_codec_init(void)
{
    /* No cache state is trusted before the full platform/resource/stamp guard. */
    if(codec.initialized)return ESP_ERR_INVALID_STATE;
    esp_err_t error=photo_storage_authorize(&jpeg_layout,&codec.transport,&codec.hash);
    if(error==ESP_OK)codec.initialized=true;
    return error;
}

esp_err_t photo_codec_invalidate(unsigned slot,photo_diagnostic_t *diagnostic)
{
    /* This durable step MUST finish before erasing or overwriting source bytes. */
    photo_diagnostic_t local;if(!diagnostic)diagnostic=&local;
    esp_err_t result=begin_job(slot,true,false,diagnostic);
    if(result==ESP_OK) {
        diagnostic->cache=jpeg_cache_invalidate(&codec.cache,slot);
        if(diagnostic->cache!=JPEG_CACHE_OK)result=ESP_FAIL;
    }
    return finish_job(result,diagnostic);
}

esp_err_t photo_codec_prepare(unsigned slot,uint32_t length,bool background,
                             photo_diagnostic_t *diagnostic)
{
    /* A cold verified hit skips decoding; misses validate AND fill the frame. */
    photo_diagnostic_t local;if(!diagnostic)diagnostic=&local;
    esp_err_t result=begin_job(slot,true,background,diagnostic);
    if(result!=ESP_OK)return finish_job(result,diagnostic);
    diagnostic->cache=jpeg_cache_lookup(&codec.cache,slot,length);
    if(diagnostic->cache==JPEG_CACHE_OK){diagnostic->cached=true;return finish_job(ESP_OK,diagnostic);}
    if(diagnostic->cache!=JPEG_CACHE_MISS && diagnostic->cache!=JPEG_CACHE_VERIFY)
        return finish_job(ESP_FAIL,diagnostic);
    /* A verify mismatch poisons only the cache handle; keep the SAME global job
     * budget and reread journal from physical bytes before rebuilding. */
    jpeg_cache_devices_t devices=codec.cache.devices;
    jpeg_cache_abort(&codec.cache);
    diagnostic->cache=jpeg_cache_open(&codec.cache,&jpeg_cache_layout,&devices,&codec.hash,checkpoint,NULL);
    if(diagnostic->cache==JPEG_CACHE_OK)diagnostic->cache=jpeg_cache_begin(&codec.cache,slot,length);
    if(diagnostic->cache!=JPEG_CACHE_OK)return finish_job(ESP_FAIL,diagnostic);
    codec.decoding=true;bool decoded=decode(length,diagnostic);codec.decoding=false;
    if(!decoded)return finish_job(ESP_FAIL,diagnostic);
    diagnostic->cache=jpeg_cache_commit(&codec.cache);
    if(diagnostic->cache!=JPEG_CACHE_OK){diagnostic->status=PHOTO_VERIFY;result=ESP_FAIL;}
    return finish_job(result,diagnostic);
}

esp_err_t photo_codec_draw(unsigned slot,uint32_t length,
    int (*row)(void *,uint32_t,const uint16_t *,uint32_t),void *context,
    photo_diagnostic_t *diagnostic)
{
    /* Readonly display job: verify source and the entire physical frame first.
     * No library decode or program/erase operation is permitted in this epoch. */
    photo_diagnostic_t local;if(!diagnostic)diagnostic=&local;
    esp_err_t result=begin_job(slot,false,false,diagnostic);
    if(!row){diagnostic->status=PHOTO_ARGUMENT;return finish_job(ESP_ERR_INVALID_ARG,diagnostic);}
    if(result!=ESP_OK)return finish_job(result,diagnostic);
    diagnostic->cache=jpeg_cache_lookup(&codec.cache,slot,length);
    if(diagnostic->cache!=JPEG_CACHE_OK)return finish_job(ESP_ERR_NOT_FOUND,diagnostic);
    uint16_t pixels[LCD_WIDTH];
    for(uint32_t y=0;y<LCD_HEIGHT;++y) {
        diagnostic->cache=jpeg_cache_read_row(&codec.cache,y,pixels,LCD_WIDTH);
        if(diagnostic->cache!=JPEG_CACHE_OK || row(context,y,pixels,LCD_WIDTH)) {
            diagnostic->status=PHOTO_VERIFY;return finish_job(ESP_FAIL,diagnostic);
        }
    }
    diagnostic->cached=true;return finish_job(ESP_OK,diagnostic);
}

void photo_diagnostic_describe(const photo_diagnostic_t *diagnostic,char *text,size_t bytes)
{
    /* Network sees bounded domain reasons; never echo JPEG metadata or a private
     * upstream error buffer. Known limits include exact required/available. */
    if(!text || !bytes)return;
    const char *reason="photo-storage-unavailable";
    if(diagnostic) {
        if(diagnostic->transport==JPEG_TRANSPORT_TIME)reason="time-limit";
        else if(diagnostic->transport==JPEG_TRANSPORT_LIMIT)reason="io-limit";
        else if(diagnostic->status==PHOTO_BUSY)reason="upload-busy-or-incomplete";
        else if(diagnostic->status==PHOTO_ARGUMENT)reason="invalid-upload-arguments";
        else if(diagnostic->status==PHOTO_SETTINGS)reason="settings-write-failed";
        else if(diagnostic->status==PHOTO_PRIVACY)reason=jpeg_privacy_status_name(diagnostic->privacy.status);
        else if(diagnostic->status==PHOTO_DECODE)reason=jpeg_decoder_status_name(diagnostic->decode.status);
        else if(diagnostic->status==PHOTO_VERIFY)reason="cache-verification-failed";
        else if(diagnostic->cache==JPEG_CACHE_SOURCE_CHANGED)reason="source-changed";
        else if(diagnostic->cache==JPEG_CACHE_VERIFY)reason="cache-readback-failed";
        if(diagnostic->status==PHOTO_DECODE && diagnostic->decode.available_known) {
            snprintf(text,bytes,"%s; required=%llu available=%llu",reason,
                (unsigned long long)diagnostic->decode.required,(unsigned long long)diagnostic->decode.available);return;
        }
        if(diagnostic->available_known) {
            snprintf(text,bytes,"%s; required=%llu available=%llu",
                diagnostic->status==PHOTO_MEMORY ?
                    (diagnostic->service_memory ? "service-heap-reserve":"heap-headroom"):"source-limit",
                (unsigned long long)diagnostic->required,(unsigned long long)diagnostic->available);return;
        }
    }
    snprintf(text,bytes,"%s",reason);
}
