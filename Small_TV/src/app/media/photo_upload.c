#include "media.h"
#include "media_internal.h"
#include "settings.h"
#include "board.h"
#include "esp_timer.h"
#include <string.h>

static struct {
    bool active;
    unsigned slot, chunks, next;
    uint32_t length, received;
    int64_t last_activity;
} upload;

bool photo_upload_active_unlocked(void)
{
    if (upload.active && esp_timer_get_time()-upload.last_activity>120000000) upload.active=false;
    return upload.active;
}

esp_err_t photo_upload_start(unsigned slot,uint32_t length,unsigned chunks)
{
    if (slot>=PHOTO_COUNT || length<4 || length>PHOTO_SLOT_BYTES || chunks!=(length+PHOTO_CHUNK_BYTES-1)/PHOTO_CHUNK_BYTES) return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(media_mutex,portMAX_DELAY);
    esp_err_t result=ESP_ERR_INVALID_STATE;
    if (!photo_upload_active_unlocked()) {
        result=settings_photo_size(slot,0);
        if (result==ESP_OK) result=esp_partition_erase_range(media_partition,slot*PHOTO_SLOT_BYTES,PHOTO_SLOT_BYTES);
        if (result==ESP_OK) {
            memset(&upload,0,sizeof(upload)); upload.active=true; upload.slot=slot; upload.length=length; upload.chunks=chunks; upload.last_activity=esp_timer_get_time();
        }
    }
    xSemaphoreGive(media_mutex); return result;
}

esp_err_t photo_upload_chunk(unsigned slot,unsigned index,unsigned total,const uint8_t *data,size_t length)
{
    xSemaphoreTake(media_mutex,portMAX_DELAY);
    esp_err_t result=ESP_ERR_INVALID_ARG;
    if (photo_upload_active_unlocked() && slot==upload.slot && total==upload.chunks && index<total) {
        uint32_t start=index*PHOTO_CHUNK_BYTES;
        size_t expected=upload.length-start; if (expected>PHOTO_CHUNK_BYTES) expected=PHOTO_CHUNK_BYTES;
        if (length==expected && index==upload.next) {
            result=esp_partition_write(media_partition,slot*PHOTO_SLOT_BYTES+start,data,length);
            if (result==ESP_OK) {++upload.next; upload.received+=(uint32_t)length; upload.last_activity=esp_timer_get_time();}
        } else if (length==expected && upload.next>0 && index==upload.next-1) {
            /* A lost HTTP reply may cause the browser to repeat the last block. */
            uint8_t saved[64]; result=ESP_OK;
            for (size_t p=0; p<length; p+=sizeof(saved)) {
                size_t block=length-p<sizeof(saved)?length-p:sizeof(saved);
                if (media_read_unlocked(ASSETS_BASE+slot*PHOTO_SLOT_BYTES+start+(uint32_t)p,saved,block)!=ESP_OK || memcmp(saved,data+p,block)) {result=ESP_ERR_INVALID_ARG; break;}
            }
            if (result==ESP_OK) upload.last_activity=esp_timer_get_time();
        }
    }
    xSemaphoreGive(media_mutex); return result;
}

static bool photo_headers_safe(uint32_t base,uint32_t length)
{
    uint8_t bytes[16]; bool dimensions=false;
    if (media_read_unlocked(base,bytes,2)!=ESP_OK || bytes[0]!=255 || bytes[1]!=0xd8) return false;
    uint32_t pos=2;
    while (pos+4<=length) {
        if (media_read_unlocked(base+pos,bytes,4)!=ESP_OK || bytes[0]!=255 || bytes[1]==255) return false;
        unsigned marker=bytes[1], segment=(bytes[2]<<8)|bytes[3];
        if (segment<2 || segment>length-pos-2) return false;
        if (marker==0xfe || (marker>=0xe1 && marker<=0xef) || marker==0xc2) return false;
        if (marker==0xe0) {
            if (segment<16 || media_read_unlocked(base+pos+4,bytes,5)!=ESP_OK || memcmp(bytes,"JFIF\0",5)) return false;
            /* Only the fixed JFIF header; embedded thumbnails may contain metadata. */
            if (segment!=16 || media_read_unlocked(base+pos+16,bytes,2)!=ESP_OK || bytes[0] || bytes[1]) return false;
        }
        if (marker==0xc0) {
            if (segment<8 || media_read_unlocked(base+pos+4,bytes,5)!=ESP_OK || bytes[0]!=8 ||
                ((bytes[1]<<8)|bytes[2])!=240 || ((bytes[3]<<8)|bytes[4])!=240) return false;
            dimensions=true;
        }
        if (marker==0xda) {
            if (!dimensions) return false;
            /* Single baseline scan, with its EOI exactly at the declared end.
             * Reject APP/COM segments after SOS and data appended after EOI. */
            pos+=segment+2;
            bool escaped=false;
            uint8_t entropy[64];
            while (pos<length) {
                size_t block=length-pos<sizeof(entropy)?length-pos:sizeof(entropy);
                if (media_read_unlocked(base+pos,entropy,block)!=ESP_OK) return false;
                for (size_t i=0;i<block;++i) {
                    unsigned byte=entropy[i];
                    if (!escaped) {escaped=byte==255; continue;}
                    if (byte==255) continue;
                    if (byte==0 || (byte>=0xd0 && byte<=0xd7)) {escaped=false; continue;}
                    return byte==0xd9 && pos+i+1==length;
                }
                pos+=(uint32_t)block;
            }
            return false;
        }
        pos+=segment+2;
    }
    return false;
}

esp_err_t photo_upload_finish(unsigned slot)
{
    xSemaphoreTake(media_mutex,portMAX_DELAY);
    esp_err_t result=ESP_ERR_INVALID_STATE;
    if (photo_upload_active_unlocked() && slot==upload.slot && upload.next==upload.chunks && upload.received==upload.length) {
        uint32_t base=ASSETS_BASE+slot*PHOTO_SLOT_BYTES;
        result=photo_headers_safe(base,upload.length)?media_validate_jpeg_unlocked(base,upload.length,240,240):ESP_ERR_INVALID_ARG;
        if (result==ESP_OK) result=settings_photo_size(slot,upload.length);
        upload.active=false;
    }
    xSemaphoreGive(media_mutex); return result;
}
