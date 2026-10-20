#include "media.h"
#include "media_internal.h"
#include "settings.h"
#include "board.h"
#include "esp_timer.h"
#include "jpeg_privacy.h"
#include <string.h>

static struct
{
    bool active;
    unsigned slot, chunks, next;
    uint32_t length, received;
    int64_t last_activity;
} upload;

bool photo_upload_active_unlocked(void)
{
    /* Expire an abandoned upload and report the current upload state.
     * FIXED_FACTORY: abandoned factory uploads have no inactivity recovery.
     * Release our upload state after 120 seconds so drawing/uploads can resume. */

    if (upload.active && esp_timer_get_time() - upload.last_activity > 120000000)
        upload.active = false;
    return upload.active;
}

esp_err_t photo_upload_start(unsigned slot, uint32_t length, unsigned chunks)
{
    /* Validate a new upload, invalidate its slot and erase only that photo region.
     * FIXED_FACTORY: 0x4200dda4 checks slot/maximum size but not minimum size
     * or chunk-count consistency. Check both and mark the photo absent before erase so
     * interrupted uploads cannot expose old lengths over partially written data. */

    if (slot >= PHOTO_COUNT || length < 4 || length > PHOTO_SLOT_BYTES ||
        chunks != (length + PHOTO_CHUNK_BYTES - 1) / PHOTO_CHUNK_BYTES)
        return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(media_mutex, portMAX_DELAY);
    esp_err_t result = ESP_ERR_INVALID_STATE;
    if (!photo_upload_active_unlocked())
    {
        result = settings_photo_size(slot, 0);
        if (result == ESP_OK)
            result = esp_partition_erase_range(media_partition, slot * PHOTO_SLOT_BYTES,
                                               PHOTO_SLOT_BYTES);
        if (result == ESP_OK)
        {
            memset(&upload, 0, sizeof(upload));
            upload.active = true;
            upload.slot = slot;
            upload.length = length;
            upload.chunks = chunks;
            upload.last_activity = esp_timer_get_time();
        }
    }
    xSemaphoreGive(media_mutex);
    return result;
}

esp_err_t photo_upload_chunk(unsigned slot, unsigned index, unsigned total, const uint8_t *data,
                             size_t length)
{
    /* Accept an ordered upload block or an exact retry of its last block.
     * FIXED_FACTORY: 0x4200dc58 receives a caller-sized body into a shared buffer
     * and does not enforce chunk ordering. Bound writes to the declared slot,
     * enforce the next index, and accept a last-block retry only if bytes match. */

    xSemaphoreTake(media_mutex, portMAX_DELAY);
    esp_err_t result = ESP_ERR_INVALID_ARG;
    if (photo_upload_active_unlocked() && slot == upload.slot && total == upload.chunks &&
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

static int privacy_read(void *context, uint32_t offset, void *data, size_t bytes)
{
    /* Read only this immutable upload while media_mutex owns its source slot. */
    uint32_t base = *(const uint32_t *)context;
    return media_read_unlocked(base + offset, data, bytes);
}

static int privacy_check(void *context)
{
    /* The synchronous legacy owner holds media_mutex; background owner later
     * supplies its request deadline/cancellation checkpoint to the same gate. */
    (void)context;
    return 0;
}

static bool photo_headers_safe(uint32_t base, uint32_t length)
{
    /* REQUESTED_CHANGE: inspect metadata in every scan rather than conflating
     * privacy with baseline-only decoder support. Entropy validation is separate. */
    jpeg_privacy_source_t source = {&base, length, privacy_read, privacy_check};
    return jpeg_privacy_check(&source, NULL) == JPEG_PRIVACY_OK;
}

esp_err_t photo_upload_finish(unsigned slot)
{
    /* Validate a complete photo, then publish its stored length.
     * FIXED_FACTORY: 0x4200d978 publishes a length without checking complete
     * ordered data or JPEG validity. Publish only after all chunks and decode
     * validation succeed. REQUESTED_CHANGE: enforce metadata-free 240x240 JPEG. */

    xSemaphoreTake(media_mutex, portMAX_DELAY);
    esp_err_t result = ESP_ERR_INVALID_STATE;
    if (photo_upload_active_unlocked() && slot == upload.slot && upload.next == upload.chunks &&
        upload.received == upload.length)
    {
        uint32_t base = ASSETS_BASE + slot * PHOTO_SLOT_BYTES;
        result = photo_headers_safe(base, upload.length)
                     ? media_validate_jpeg_unlocked(base, upload.length, 240, 240)
                     : ESP_ERR_INVALID_ARG;
        if (result == ESP_OK)
            result = settings_photo_size(slot, upload.length);
        upload.active = false;
    }
    xSemaphoreGive(media_mutex);
    return result;
}
