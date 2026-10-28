/* REQUESTED_CHANGE: real ESP-IDF flash/PSA/time binding for the guarded JPEG
 * transport. Bootstrap discovery is readonly; ordinary I/O uses revocable ports. */
#include "jpeg_espidf.h"
#include "esp_flash.h"
#include "esp_flash_partitions.h"
#include "esp_partition.h"
#include "esp_timer.h"
#include <stdlib.h>
#include <string.h>

static uint64_t clock_us(void *context)
{
    /* ESP-IDF monotonic boot time, no busy waits or software delays. */
    (void)context;return (uint64_t)esp_timer_get_time();
}

static int flash_read(void *context,uint32_t address,void *data,size_t bytes)
{
    /* Transport already preflighted physical bounds and byte/count/time limits. */
    (void)context;return esp_flash_read(NULL,data,address,(uint32_t)bytes);
}

static int flash_program(void *context,uint32_t address,const void *data,size_t bytes)
{
    /* SDK splits this bounded logical page using the selected chip driver.
     * 256 is a transport unit, not a claim about the identified chip page size. */
    (void)context;return esp_flash_write(NULL,data,address,(uint32_t)bytes);
}

static int flash_erase(void *context,uint32_t address)
{
    /* Exactly one already authorized4KiB sector; no erase-chip recovery. */
    (void)context;return esp_flash_erase_region(NULL,address,JPEG_NOR_SECTOR_BYTES);
}

static int hash_begin(void *context)
{
    /* Existing pinned PSA SHA-256, not a new implementation or private API. */
    jpeg_espidf_t *s=context;return (int)psa_hash_setup(&s->hash,PSA_ALG_SHA_256);
}

static int hash_update(void *context,const void *data,size_t bytes)
{
    /* Feed bounded immutable chunks under the guard's startup deadline. */
    jpeg_espidf_t *s=context;return (int)psa_hash_update(&s->hash,data,bytes);
}

static int hash_finish(void *context,uint8_t digest[32])
{
    /* A provider reporting the wrong digest length is not successful verification. */
    jpeg_espidf_t *s=context;size_t bytes=0;
    psa_status_t result=psa_hash_finish(&s->hash,digest,32,&bytes);
    return result==PSA_SUCCESS && bytes==32 ? 0 : (result==PSA_SUCCESS ? -1 : (int)result);
}

static void hash_reset(void *context)
{
    /* PSA abort is valid after success or partial setup/update/finish failure. */
    jpeg_espidf_t *s=context;(void)psa_hash_abort(&s->hash);
}

jpeg_guard_sha256_t jpeg_espidf_hash_provider(jpeg_espidf_t *storage)
{
    /* Reuse the already-qualified platform SHA implementation for cache jobs. */
    return (jpeg_guard_sha256_t){storage,hash_begin,hash_update,hash_finish,hash_reset};
}

static esp_err_t sdk_matches(const jpeg_guard_partition_t *parts,unsigned count)
{
    /* Do not trust a selected assets-only iterator or discard unexpected entries. */
    esp_partition_iterator_t iterator=NULL;
    esp_err_t error=esp_partition_find_err(ESP_PARTITION_TYPE_ANY,ESP_PARTITION_SUBTYPE_ANY,NULL,&iterator);
    if(error!=ESP_OK)return error;
    unsigned seen=0;uint32_t matched=0;
    while(iterator) {
        const esp_partition_t *part=esp_partition_get(iterator);bool found=false;
        if(part && part->flash_chip==esp_flash_default_chip && part->erase_size==JPEG_NOR_SECTOR_BYTES)
            for(unsigned i=0;i<count;++i) {
                const jpeg_guard_partition_t *raw=&parts[i];
                if(part->type==raw->type && part->subtype==raw->subtype && part->address==raw->offset &&
                    part->size==raw->bytes && !memcmp(part->label,raw->label,16) &&
                    part->encrypted==((raw->flags&PART_FLAG_ENCRYPTED)!=0) &&
                    part->readonly==((raw->flags&PART_FLAG_READONLY)!=0) && !(matched&(1u<<i))) {
                    found=true;matched|=1u<<i;break;
                }
            }
        if(!found){esp_partition_iterator_release(iterator);return ESP_ERR_INVALID_STATE;}
        ++seen;iterator=esp_partition_next(iterator);
    }
    return seen==count ? ESP_OK : ESP_ERR_INVALID_STATE;
}

static esp_err_t discover(jpeg_guard_partition_t *out,unsigned *count)
{
    /* Temporary3KiB heap is freed before codec/NOR caches exist. Verify complete
     * raw records/MD5/tail; SDK descriptors alone lose unknown raw flag bits. */
    esp_partition_info_t *table=malloc(ESP_PARTITION_TABLE_MAX_LEN);
    if(!table)return ESP_ERR_NO_MEM;
    esp_err_t error=esp_flash_read(NULL,table,ESP_PARTITION_TABLE_OFFSET,ESP_PARTITION_TABLE_MAX_LEN);
    int total=0;
    if(error==ESP_OK)error=esp_partition_table_verify(table,false,&total);
    if(error==ESP_OK && (total<=0 || total>(int)JPEG_GUARD_MAX_PARTITIONS))error=ESP_ERR_INVALID_SIZE;
    if(error==ESP_OK) {
        for(int i=0;i<total;++i) {
            if(table[i].magic!=ESP_PARTITION_MAGIC){error=ESP_ERR_INVALID_STATE;break;}
            out[i]=(jpeg_guard_partition_t){.offset=table[i].pos.offset,.bytes=table[i].pos.size,
                .flags=table[i].flags,.type=table[i].type,.subtype=table[i].subtype};
            memcpy(out[i].label,table[i].label,16);
        }
        if(error==ESP_OK && table[total].magic!=ESP_PARTITION_MAGIC_MD5)error=ESP_ERR_INVALID_STATE;
        const uint8_t *bytes=(const uint8_t *)table;
        for(size_t i=(size_t)(total+1)*sizeof(*table);error==ESP_OK && i<ESP_PARTITION_TABLE_MAX_LEN;++i)
            if(bytes[i]!=0xff)error=ESP_ERR_INVALID_STATE;
    }
    free(table);
    if(error!=ESP_OK)return error;
    error=sdk_matches(out,(unsigned)total);if(error!=ESP_OK)return error;
    /* Canonical ordering for the guard, independent of partition table ordering. */
    for(unsigned i=1;i<(unsigned)total;++i) {
        jpeg_guard_partition_t part=out[i];unsigned j=i;
        while(j && out[j-1].offset>part.offset){out[j]=out[j-1];--j;}
        out[j]=part;
    }
    *count=(unsigned)total;return ESP_OK;
}

esp_err_t jpeg_espidf_init(jpeg_espidf_t *s)
{
    /* Physical capacity and image-configured capacity must both match at guard. */
    if(!s)return ESP_ERR_INVALID_ARG;
    if(s->transport.initialized)return ESP_ERR_INVALID_STATE;
    esp_err_t error=esp_flash_get_physical_size(NULL,&s->physical_bytes);
    if(error==ESP_OK)error=esp_flash_get_size(NULL,&s->configured_bytes);
    if(error!=ESP_OK)return error;
    if(psa_crypto_init()!=PSA_SUCCESS)return ESP_FAIL;
    psa_hash_operation_t blank=PSA_HASH_OPERATION_INIT;s->hash=blank;
    jpeg_nor_device_t raw={s,s->physical_bytes,256,flash_read,flash_program,flash_erase};
    return jpeg_transport_init(&s->transport,&raw,clock_us,NULL)==JPEG_TRANSPORT_OK ? ESP_OK : ESP_ERR_INVALID_STATE;
}

static jpeg_transport_result_t authorize(jpeg_espidf_t *s,const jpeg_guard_layout_t *layout,
    const jpeg_provision_stamp_t *stamp,jpeg_provision_diagnostic_t *diagnostic,
    const jpeg_transport_limits_t *limits)
{
    /* Any discovery failure leaves every old port revoked, including retries. */
    if(!s || !s->transport.initialized)return JPEG_TRANSPORT_STATE;
    jpeg_transport_revoke(&s->transport);s->discovery_error=0;s->discovery_us=0;
    if(!layout || !limits || limits->read_bytes<ESP_PARTITION_TABLE_MAX_LEN || !limits->calls ||
        !limits->duration_us)return JPEG_TRANSPORT_ARGUMENT;
    if(s->configured_bytes!=layout->flash_bytes || s->physical_bytes!=layout->flash_bytes)return JPEG_TRANSPORT_GUARD;
    uint64_t started=clock_us(NULL);jpeg_guard_partition_t parts[JPEG_GUARD_MAX_PARTITIONS];unsigned count=0;
    s->discovery_error=discover(parts,&count);
    uint64_t now=clock_us(NULL);
    if(now<started)return JPEG_TRANSPORT_CLOCK;
    s->discovery_us=now-started;
    if(s->discovery_error)return JPEG_TRANSPORT_GUARD;
    if(s->discovery_us>=limits->duration_us)return JPEG_TRANSPORT_TIME;
    jpeg_transport_limits_t remaining=*limits;
    --remaining.calls;remaining.read_bytes-=ESP_PARTITION_TABLE_MAX_LEN;remaining.duration_us-=s->discovery_us;
    jpeg_guard_sha256_t hash={s,hash_begin,hash_update,hash_finish,hash_reset};
    return stamp ? jpeg_transport_provision(&s->transport,layout,parts,count,&hash,stamp,diagnostic,&remaining):
                   jpeg_transport_authorize(&s->transport,layout,parts,count,&hash,&remaining);
}

jpeg_transport_result_t jpeg_espidf_authorize(jpeg_espidf_t *s,const jpeg_guard_layout_t *layout,
                                             const jpeg_transport_limits_t *limits)
{
    /* Ordinary callers retain strictly read-only startup authorization. */
    return authorize(s,layout,NULL,NULL,limits);
}

jpeg_transport_result_t jpeg_espidf_provision(jpeg_espidf_t *s,const jpeg_guard_layout_t *layout,
    const jpeg_provision_stamp_t *stamp,jpeg_provision_diagnostic_t *diagnostic,
    const jpeg_transport_limits_t *limits)
{
    /* Fail/revoke even for an absent provision descriptor; never fall through
     * to an ordinary authorization path that could retain stale capabilities. */
    if(diagnostic){memset(diagnostic,0,sizeof(*diagnostic));diagnostic->status=JPEG_PROVISION_GUARD;}
    if(!stamp){if(s)jpeg_transport_revoke(&s->transport);return JPEG_TRANSPORT_ARGUMENT;}
    return authorize(s,layout,stamp,diagnostic,limits);
}
