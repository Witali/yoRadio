#include "media.h"
#include "media_internal.h"
#include "settings.h"
#include "board.h"
#include "esp_timer.h"
#include "photo_worker.h"
#include <string.h>

static struct
{
    bool active, preparing, finishing;
    unsigned slot, chunks, next;
    uint32_t length, received;
    uint64_t cache_program_bytes;
    int64_t last_activity;
} upload;

bool photo_upload_active_unlocked(void)
{
    /* Expire an abandoned upload and report the current upload state.
     * FIXED_FACTORY: abandoned factory uploads have no inactivity recovery.
     * Release our upload state after 120 seconds so drawing/uploads can resume. */

    if (upload.active && !upload.preparing && !upload.finishing && esp_timer_get_time() - upload.last_activity > 120000000)
        upload.active = false;
    return upload.active;
}

bool photo_upload_overlaps_unlocked(uint32_t offset,size_t bytes)
{
    /* Immutable animation/weather reads do not share the mutable photo slot. */
    if(!photo_upload_active_unlocked() || !bytes)return false;
    uint32_t source=ASSETS_BASE+upload.slot*PHOTO_SLOT_BYTES;
    return offset>=source ? offset-source<PHOTO_SLOT_BYTES:bytes>source-offset;
}

esp_err_t photo_upload_start_detailed(unsigned slot, uint32_t length, unsigned chunks,
                                      photo_diagnostic_t *diagnostic)
{
    /* REQUESTED_CHANGE: claim upload ownership before waiting for background
     * cancellation; durable cache invalidation precedes source erase/write. */
    photo_diagnostic_t local;
    if(!diagnostic)diagnostic=&local;
    memset(diagnostic,0,sizeof(*diagnostic));
    if (slot >= PHOTO_COUNT || length < 4 || length > PHOTO_SLOT_BYTES ||
        chunks != (length + PHOTO_CHUNK_BYTES - 1) / PHOTO_CHUNK_BYTES)
    {
        if (diagnostic) diagnostic->status = PHOTO_ARGUMENT;
        return ESP_ERR_INVALID_ARG;
    }
    xSemaphoreTake(media_mutex, portMAX_DELAY);
    if (photo_upload_active_unlocked())
    {
        xSemaphoreGive(media_mutex);
        if (diagnostic) diagnostic->status = PHOTO_BUSY;
        return ESP_ERR_INVALID_STATE;
    }
    memset(&upload, 0, sizeof(upload));
    upload.active = upload.preparing = true;
    upload.slot = slot; upload.length = length; upload.chunks = chunks;
    upload.last_activity = esp_timer_get_time();
    photo_worker_forget(slot);
    xSemaphoreGive(media_mutex);
    esp_err_t result = photo_worker_invalidate(slot, diagnostic);
    /* REQUESTED_CHANGE: retain cache invalidation traffic across source upload.
     * The finish step gets the remaining budget, never a second full allowance. */
    upload.cache_program_bytes=diagnostic->program_bytes;
    if (result == ESP_OK)
    {
        result = settings_photo_size(slot, 0);
        if (result != ESP_OK && diagnostic) diagnostic->status = PHOTO_SETTINGS;
    }
    if (result == ESP_OK)
        result = esp_partition_erase_range(media_partition, slot * PHOTO_SLOT_BYTES, PHOTO_SLOT_BYTES);
    if (result != ESP_OK && diagnostic && diagnostic->status == PHOTO_OK)
        diagnostic->status = PHOTO_STORAGE;
    xSemaphoreTake(media_mutex, portMAX_DELAY);
    upload.preparing = false;
    upload.active = result == ESP_OK;
    upload.last_activity = esp_timer_get_time();
    xSemaphoreGive(media_mutex);
    return result;
}

esp_err_t photo_upload_start(unsigned slot, uint32_t length, unsigned chunks)
{
    /* Synchronous C API shares the exact worker operation used by HTTP. */
    return photo_upload_start_detailed(slot, length, chunks, NULL);
}

esp_err_t photo_upload_chunk(unsigned slot, unsigned index, unsigned total, const uint8_t *data,
                             size_t length)
{
    /* Accept an ordered upload block or an exact retry of its last block.
     * FIXED_FACTORY: 0x4200dc58 receives a caller-sized body into a shared buffer
     * and does not enforce chunk ordering. Bound writes to the declared slot,
     * enforce the next index, and accept a last-block retry only if bytes match. */

    if (!data || !length) return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(media_mutex, portMAX_DELAY);
    esp_err_t result = ESP_ERR_INVALID_ARG;
    if (photo_upload_active_unlocked() && !upload.preparing && !upload.finishing &&
        slot == upload.slot && total == upload.chunks &&
        index < total)
    {
        uint32_t start = index * PHOTO_CHUNK_BYTES;
        size_t expected = upload.length - start;
        if (expected > PHOTO_CHUNK_BYTES)
            expected = PHOTO_CHUNK_BYTES;
        if (length == expected && index == upload.next)
        {
            result =
                esp_partition_write(media_partition, slot * PHOTO_SLOT_BYTES + start, data, length);
            if (result == ESP_OK)
            {
                ++upload.next;
                upload.received += (uint32_t)length;
                upload.last_activity = esp_timer_get_time();
            }
        }
        else if (length == expected && upload.next > 0 && index == upload.next - 1)
        {
            /* A lost HTTP reply may cause the browser to repeat the last block. */
            uint8_t saved[64];
            result = ESP_OK;
            for (size_t p = 0; p < length; p += sizeof(saved))
            {
                size_t block = length - p < sizeof(saved) ? length - p : sizeof(saved);
                if (media_read_unlocked(ASSETS_BASE + slot * PHOTO_SLOT_BYTES + start + (uint32_t)p,
                                        saved, block) != ESP_OK ||
                    memcmp(saved, data + p, block))
                {
                    result = ESP_ERR_INVALID_ARG;
                    break;
                }
            }
            if (result == ESP_OK)
                upload.last_activity = esp_timer_get_time();
        }
    }
    xSemaphoreGive(media_mutex);
    return result;
}

esp_err_t photo_upload_finish_detailed(unsigned slot, photo_diagnostic_t *diagnostic)
{
    /* FIXED_FACTORY: publish only complete ordered uploads after successful
     * privacy, ONE decode/cache preparation and whole physical-frame verify.
     * REQUESTED_CHANGE: slow processing never holds the shared media mutex. */
    if (diagnostic) memset(diagnostic, 0, sizeof(*diagnostic));
    xSemaphoreTake(media_mutex, portMAX_DELAY);
    if (!photo_upload_active_unlocked() || upload.preparing || upload.finishing ||
        slot != upload.slot || upload.next != upload.chunks || upload.received != upload.length)
    {
        xSemaphoreGive(media_mutex);
        if (diagnostic) diagnostic->status = PHOTO_BUSY;
        return ESP_ERR_INVALID_STATE;
    }
    upload.finishing = true;
    uint32_t length = upload.length;
    uint64_t prior_program_bytes=upload.cache_program_bytes;
    xSemaphoreGive(media_mutex);
    esp_err_t result = photo_worker_prepare(slot, length, prior_program_bytes, diagnostic);
    if (result == ESP_OK)
    {
        result = settings_photo_size(slot, length);
        if (result != ESP_OK && diagnostic) diagnostic->status = PHOTO_SETTINGS;
    }
    xSemaphoreTake(media_mutex, portMAX_DELAY);
    upload.active = upload.finishing = false;
    xSemaphoreGive(media_mutex);
    if (result == ESP_OK) photo_worker_publish(slot, length);
    return result;
}

esp_err_t photo_upload_finish(unsigned slot)
{
    /* Synchronous users invoke the same real codec/cache operation as HTTP. */
    return photo_upload_finish_detailed(slot, NULL);
}
