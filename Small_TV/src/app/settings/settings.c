#include "settings.h"
#include <string.h>
#include "asset_defaults.h"
#include "factory_settings.h"
#include "esp_flash.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "nvs.h"

static tv_settings_t current_settings;
static SemaphoreHandle_t settings_mutex;
static nvs_handle_t settings_store;
static uint32_t generation;
static bool dirty;
static int64_t last_change_us;

uint16_t rgb565_from_rgb888(uint32_t rgb)
{
    /* Convert an RGB888 color to the panel RGB565 representation. */

    return ((rgb >> 8) & 0xf800) | ((rgb >> 5) & 0x07e0) | ((rgb >> 3) & 0x001f);
}

uint32_t rgb888_from_rgb565(uint16_t rgb)
{
    /* Expand RGB565 components for the original web color API (0x42008a34/0x42008a6a). */

    unsigned r = (rgb >> 11) & 31, g = (rgb >> 5) & 63, b = rgb & 31;
    /* The original shift/OR sequence repeats high bits, giving white 0xffffff
     * rather than the darker 0xf8fcf8 produced by zero-filling low bits. */
    return (((r << 3) | (r >> 2)) << 16) | (((g << 2) | (g >> 4)) << 8) | (b << 3) | (b >> 2);
}

bool settings_valid(const tv_settings_t *s)
{
    /* Validate all settings and photo lengths before accepting or persisting them. */

    if (s->version != 1 || !memchr(s->ssid, 0, sizeof(s->ssid)) ||
        !memchr(s->password, 0, sizeof(s->password)) || !memchr(s->city, 0, sizeof(s->city)) ||
        !memchr(s->ntp, 0, sizeof(s->ntp)) || !memchr(s->weather_key, 0, sizeof(s->weather_key)) ||
        s->country[2] || s->theme > 3 || s->animation > 4 || s->date_format > 2 ||
        s->night_start < 18 || s->night_start > 23 || s->night_stop < 5 || s->night_stop > 12 ||
        s->photo_seconds < 3 || s->photo_seconds > 60 || s->day_level > 1000 ||
        s->night_level > 1000 || s->fahrenheit > 1 || s->hour12 > 1 || s->miles > 1 ||
        s->browser_time > 1 || s->night_mode > 1 || s->click_count > 10 || s->photo_mask > 31 ||
        s->wifi_mode > 2)
        return false;
    for (unsigned i = 0; i < PHOTO_COUNT; ++i)
        if (s->photo_size[i] > PHOTO_SLOT_BYTES)
            return false;
    return true;
}

static void defaults(tv_settings_t *s)
{
    /* Populate the factory defaults and lengths of the packaged sanitized photos. */

    memset(s, 0, sizeof(*s));
    s->version = 1;
    s->wifi_mode = 2;
    strcpy(s->city, "Shenzhen");
    strcpy(s->country, "CN");
    strcpy(s->ntp, "pool.ntp.org");
    s->night_level = 500;
    s->colors[0] = 0xf800;
    s->colors[1] = 0xffe0;
    s->colors[2] = 0xffff;
    s->date_format = 2;
    s->night_start = 22;
    s->night_stop = 9;
    s->photo_seconds = 5;
    s->photo_mask = 31;
    const uint32_t photo_sizes[PHOTO_COUNT] = DEFAULT_PHOTO_SIZES;
    memcpy(s->photo_size, photo_sizes, sizeof(photo_sizes));
}

esp_err_t settings_flush(void)
{
    /* Persist pending settings to NVS and the original raw sector under the mutex. */

    xSemaphoreTake(settings_mutex, portMAX_DELAY);
    esp_err_t result = ESP_OK;
    if (dirty)
    {
        uint8_t raw[FACTORY_SETTINGS_BYTES];
        factory_settings_encode(&current_settings, raw);
        result = nvs_set_blob(settings_store, "configuration", &current_settings,
                              sizeof(current_settings));
        if (result == ESP_OK)
            result = nvs_commit(settings_store);
        if (result == ESP_OK)
            result = esp_flash_erase_region(NULL, FACTORY_SETTINGS_OFFSET, 4096);
        if (result == ESP_OK)
            result = esp_flash_write(NULL, raw, FACTORY_SETTINGS_OFFSET, sizeof(raw));
        if (result == ESP_OK)
            dirty = false;
    }
    xSemaphoreGive(settings_mutex);
    return result;
}

static void persistence_task(void *unused)
{
    /* Coalesce changes and flush them after the debounce interval. */

    (void)unused;
    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(1000));
        xSemaphoreTake(settings_mutex, portMAX_DELAY);
        bool ready = dirty && esp_timer_get_time() - last_change_us >= 1000000;
        xSemaphoreGive(settings_mutex);
        if (ready)
            settings_flush();
    }
}

esp_err_t settings_init(void)
{
    /* Load settings, preferring the original sector over the older native NVS blob. */

    settings_mutex = xSemaphoreCreateMutex();
    if (!settings_mutex)
        return ESP_ERR_NO_MEM;
    esp_err_t result = nvs_open("small_tv", NVS_READWRITE, &settings_store);
    if (result != ESP_OK)
        return result;
    size_t length = sizeof(current_settings);
    result = nvs_get_blob(settings_store, "configuration", &current_settings, &length);
    /* Older native blobs left this padding byte zero and inferred station mode
     * from SSID. Normalize only NVS, before importing the explicit factory flag. */
    if (result == ESP_OK && length == sizeof(current_settings) && !current_settings.wifi_mode)
        current_settings.wifi_mode = current_settings.ssid[0] ? 1 : 2;
    if (result != ESP_OK || length != sizeof(current_settings) ||
        !settings_valid(&current_settings))
    {
        defaults(&current_settings);
        dirty = true;
    }
    uint8_t raw[FACTORY_SETTINGS_BYTES];
    if (esp_flash_read(NULL, raw, FACTORY_SETTINGS_OFFSET, sizeof(raw)) == ESP_OK)
    {
        tv_settings_t restored;
        defaults(&restored);
        if (factory_settings_decode(raw, &restored))
        {
            current_settings = restored;
            dirty = false;
        }
    }
    generation = 1;
    return xTaskCreate(persistence_task, "settings", 2048, NULL, 1, NULL) == pdPASS
               ? ESP_OK
               : ESP_ERR_NO_MEM;
}

void settings_snapshot(tv_settings_t *out)
{
    /* Copy a consistent settings snapshot while holding the mutex. */

    xSemaphoreTake(settings_mutex, portMAX_DELAY);
    *out = current_settings;
    xSemaphoreGive(settings_mutex);
}

esp_err_t settings_replace(const tv_settings_t *s)
{
    /* Validate and publish changed settings, recording their generation and deadline. */

    if (!settings_valid(s))
        return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(settings_mutex, portMAX_DELAY);
    if (memcmp(s, &current_settings, sizeof(*s)))
    {
        current_settings = *s;
        ++generation;
        dirty = true;
        last_change_us = esp_timer_get_time();
    }
    xSemaphoreGive(settings_mutex);
    return ESP_OK;
}

esp_err_t settings_photo_size(unsigned slot, uint32_t bytes)
{
    /* Persist a photo slot length or invalidation before flash content is changed. */

    if (slot >= PHOTO_COUNT || bytes > PHOTO_SLOT_BYTES)
        return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(settings_mutex, portMAX_DELAY);
    current_settings.photo_size[slot] = bytes;
    ++generation;
    dirty = true;
    last_change_us = esp_timer_get_time();
    xSemaphoreGive(settings_mutex);
    return settings_flush(); /* Record invalidation before erasing a slot. */
}

uint32_t settings_generation(void)
{
    /* Return the generation used to detect settings changes in the renderer. */

    xSemaphoreTake(settings_mutex, portMAX_DELAY);
    uint32_t value = generation;
    xSemaphoreGive(settings_mutex);
    return value;
}
