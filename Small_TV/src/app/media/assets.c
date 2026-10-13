#include "media.h"
#include "media_internal.h"
#include "board.h"
#include "display.h"
#include "settings.h"
#include "tjpgd.h"
#include <stdlib.h>
#include <string.h>

const esp_partition_t *media_partition;
SemaphoreHandle_t media_mutex;

esp_err_t media_init(void)
{
    /* Locate the fixed media partition and initialize its access mutex. */

    media_partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, 0x40, "assets");
    media_mutex = xSemaphoreCreateMutex();
    if (!media_mutex)
        return ESP_ERR_NO_MEM;
    if (!media_partition || media_partition->address != ASSETS_BASE ||
        media_partition->size != 0x1e7000)
        return ESP_ERR_NOT_FOUND;
    return ESP_OK;
}

esp_err_t media_read_unlocked(uint32_t offset, void *data, size_t length)
{
    /* Read a bounded absolute asset offset while the media mutex is held. */

    if (!media_partition || offset < ASSETS_BASE || length > media_partition->size ||
        offset - ASSETS_BASE > media_partition->size - length)
        return ESP_ERR_INVALID_SIZE;
    return esp_partition_read(media_partition, offset - ASSETS_BASE, data, length);
}

esp_err_t media_read(uint32_t offset, void *data, size_t length)
{
    /* Read an asset safely unless an upload currently owns the partition. */

    xSemaphoreTake(media_mutex, portMAX_DELAY);
    esp_err_t result = photo_upload_active_unlocked() ? ESP_ERR_INVALID_STATE
                                                      : media_read_unlocked(offset, data, length);
    xSemaphoreGive(media_mutex);
    return result;
}

bool media_upload_active(void)
{
    /* Check the upload state while holding the media mutex. */

    xSemaphoreTake(media_mutex, portMAX_DELAY);
    bool active = photo_upload_active_unlocked();
    xSemaphoreGive(media_mutex);
    return active;
}

typedef struct
{
    uint32_t offset;
    size_t length, position;
    int x, y;
    bool discard, read_error;
} jpeg_stream_t;

static size_t jpeg_stream_read(JDEC *decoder, uint8_t *buffer, size_t length)
{
    /* Feed or skip bounded flash bytes for the streaming JPEG decoder. */

    jpeg_stream_t *stream = decoder->device;
    if (length > stream->length - stream->position)
        length = stream->length - stream->position;
    if (buffer &&
        media_read_unlocked(stream->offset + (uint32_t)stream->position, buffer, length) != ESP_OK)
    {
        stream->read_error = true;
        return 0;
    }
    stream->position += length;
    return length;
}

static int jpeg_output_block(JDEC *decoder, void *pixels, JRECT *rect)
{
    /* Draw one decoded JPEG block or discard it during validation. */

    jpeg_stream_t *stream = decoder->device;
    if (!stream->discard)
        display_blit(stream->x + rect->left, stream->y + rect->top, rect->right - rect->left + 1,
                     rect->bottom - rect->top + 1, pixels);
    return 1;
}

static esp_err_t jpeg_decode_unlocked(jpeg_stream_t *stream, unsigned width, unsigned height)
{
    /* Decode a bounded baseline JPEG using a temporary work pool.
     * FIXED_RECONSTRUCTION: select byte-clipped IDCT in tjpgdcnf.h, matching
     * the original 0x42011624..0x420116c6 before color conversion.
     * FIXED_FACTORY: 0x4200c33e ignores flash errors; a failed streaming decode
     * can leave old/new stripes mixed. Erase only the known image rectangle
     * after decompression fails; validation and preparation never paint. */

    void *workspace = malloc(8192);
    if (!workspace)
        return ESP_ERR_NO_MEM;
    JDEC decoder;
    JRESULT result = jd_prepare(&decoder, jpeg_stream_read, workspace, 8192, stream);
    bool dimensions_valid = result == JDR_OK && decoder.width <= LCD_WIDTH &&
                            decoder.height <= LCD_HEIGHT &&
                            (!width || decoder.width == width) &&
                            (!height || decoder.height == height);
    if (dimensions_valid)
        result = jd_decomp(&decoder, jpeg_output_block, 0);
    else if (result == JDR_OK)
        result = JDR_FMT1;
    free(workspace);
    if (result != JDR_OK || stream->read_error)
    {
        if (dimensions_valid && !stream->discard)
            display_fill(stream->x, stream->y, decoder.width, decoder.height, 0);
        return ESP_ERR_INVALID_ARG;
    }
    return ESP_OK;
}

esp_err_t media_validate_jpeg_unlocked(uint32_t offset, size_t length, unsigned width,
                                       unsigned height)
{
    /* Fully decode a photo without drawing to verify dimensions and content. */

    jpeg_stream_t stream = {.offset = offset, .length = length, .discard = true};
    return jpeg_decode_unlocked(&stream, width, height);
}

static esp_err_t draw_jpeg_unlocked(uint32_t offset, size_t length, int x, int y)
{
    /* Stream a JPEG from flash to the requested display position. */

    jpeg_stream_t stream = {.offset = offset, .length = length, .x = x, .y = y};
    return jpeg_decode_unlocked(&stream, 0, 0);
}

esp_err_t media_draw_jpeg(uint32_t offset, size_t length, int x, int y)
{
    /* Draw an asset JPEG while excluding concurrent flash uploads. */

    xSemaphoreTake(media_mutex, portMAX_DELAY);
    esp_err_t result = photo_upload_active_unlocked() ? ESP_ERR_INVALID_STATE
                                                      : draw_jpeg_unlocked(offset, length, x, y);
    xSemaphoreGive(media_mutex);
    return result;
}

esp_err_t media_draw_photo(unsigned slot)
{
    /* Draw an enabled photo slot using its persisted byte length. */

    xSemaphoreTake(media_mutex, portMAX_DELAY);
    tv_settings_t settings;
    settings_snapshot(&settings);
    esp_err_t result = ESP_ERR_NOT_FOUND;
    if (slot < PHOTO_COUNT && settings.photo_size[slot])
        result = photo_upload_active_unlocked()
                     ? ESP_ERR_INVALID_STATE
                     : draw_jpeg_unlocked(ASSETS_BASE + slot * PHOTO_SLOT_BYTES,
                                          settings.photo_size[slot], 0, 0);
    xSemaphoreGive(media_mutex);
    return result;
}

static uint16_t little16(const uint8_t *data)
{
    /* Read a little-endian 16-bit asset-header field. */
    return data[0] | (data[1] << 8);
}
static uint32_t little32(const uint8_t *data)
{
    /* Read a little-endian 32-bit asset-header field. */
    return little16(data) | ((uint32_t)little16(data + 2) << 16);
}

static esp_err_t animation_entry(unsigned animation, unsigned frame, uint32_t *offset,
                                 uint32_t *length)
{
    /* Validate and locate one frame in the original GIF/JPEG container. */

    if (animation > 4 || frame >= 126)
        return ESP_ERR_INVALID_ARG;
    uint8_t header[11], entry[8];
    uint32_t base = ANIMATION_BASE + animation * ANIMATION_SLOT_BYTES;
    if (media_read_unlocked(base, header, sizeof(header)) != ESP_OK || memcmp(header, "GIF", 3) ||
        little16(header + 7) != 74 || little16(header + 9) != 74 ||
        little32(header + 3) > ANIMATION_SLOT_BYTES ||
        media_read_unlocked(base + 11 + frame * 8, entry, 8) != ESP_OK)
        return ESP_ERR_INVALID_ARG;
    *length = little32(entry);
    uint32_t relative = little32(entry + 4);
    if (!*length || relative < 1024 || relative > little32(header + 3) ||
        *length > little32(header + 3) - relative)
        return ESP_ERR_NOT_FOUND;
    *offset = base + relative;
    return ESP_OK;
}

unsigned media_animation_frames(unsigned animation)
{
    /* Count valid frames in the selected animation container. */

    xSemaphoreTake(media_mutex, portMAX_DELAY);
    unsigned count = 0;
    uint32_t offset, length;
    if (!photo_upload_active_unlocked())
        while (count < 126 && animation_entry(animation, count, &offset, &length) == ESP_OK)
            ++count;
    xSemaphoreGive(media_mutex);
    return count;
}

esp_err_t media_draw_animation(unsigned animation, unsigned frame, int x, int y)
{
    /* Decode and draw the selected animation frame under the media mutex. */

    xSemaphoreTake(media_mutex, portMAX_DELAY);
    uint32_t offset, length;
    esp_err_t result = photo_upload_active_unlocked()
                           ? ESP_ERR_INVALID_STATE
                           : animation_entry(animation, frame, &offset, &length);
    if (result == ESP_OK)
        result = draw_jpeg_unlocked(offset, length, x, y);
    xSemaphoreGive(media_mutex);
    return result;
}

esp_err_t media_draw_weather(const char *code, int x, int y)
{
    /* Validate and render the selected 60x60 factory weather BMP. */

    static const char *const codes[] = {"01d", "01n", "02d", "02n", "03d", "03n",
                                        "04d", "04n", "09d", "09n", "10d", "10n",
                                        "11d", "11n", "13d", "13n", "50d", "50n"};
    unsigned index = 0;
    while (index < 18 && strcmp(code, codes[index]))
        ++index;
    if (index == 18)
        return ESP_ERR_NOT_FOUND;
    xSemaphoreTake(media_mutex, portMAX_DELAY);
    esp_err_t result = ESP_ERR_INVALID_STATE;
    if (!photo_upload_active_unlocked())
    {
        uint32_t base = WEATHER_BASE + index * WEATHER_SLOT_BYTES;
        uint8_t header[54], row[180];
        uint16_t pixels[60];
        result = media_read_unlocked(base, header, sizeof(header));
        if (result == ESP_OK && (!memcmp(header, "BM", 2)) && little32(header + 18) == 60 &&
            little32(header + 22) == 60 && little16(header + 28) == 24 &&
            little32(header + 30) == 0 && little32(header + 10) <= WEATHER_SLOT_BYTES - 10800)
        {
            for (int line = 0; line < 60; ++line)
            {
                result = media_read_unlocked(base + little32(header + 10) + (59 - line) * 180, row,
                                             sizeof(row));
                if (result != ESP_OK)
                    break;
                for (unsigned c = 0; c < 60; ++c)
                    pixels[c] = rgb565_from_rgb888((row[c * 3 + 2] << 16) | (row[c * 3 + 1] << 8) |
                                                   row[c * 3]);
                display_blit(x, y + line, 60, 1, pixels);
            }
        }
        else
            result = ESP_ERR_INVALID_ARG;
    }
    xSemaphoreGive(media_mutex);
    return result;
}
