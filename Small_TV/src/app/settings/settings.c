#include "settings.h"
#include <stddef.h>
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
static uint32_t theme_selection_generation;
static bool dirty;
static int64_t last_change_us;
static portMUX_TYPE jpeg_limit_lock=portMUX_INITIALIZER_UNLOCKED;
static uint32_t jpeg_write_limit_kib=TV_JPEG_WRITE_LIMIT_DEFAULT_KIB;

/* Read the old native ABI explicitly; the unchanged raw-sector ABI is separate. */
typedef struct
{
    uint32_t version;
    char ssid[33], password[65], city[65], country[3], ntp[65], weather_key[65];
    uint16_t day_level, night_level, colors[3];
    uint8_t theme, animation, date_format, night_start, night_stop, photo_seconds;
    uint8_t fahrenheit, hour12, miles, browser_time, night_mode, click_count, photo_mask;
    uint8_t wifi_mode;
    uint32_t photo_size[PHOTO_COUNT];
} tv_settings_v1_t;
_Static_assert(sizeof(tv_settings_v1_t) == 344 && offsetof(tv_settings_v1_t, wifi_mode) == 323 &&
               offsetof(tv_settings_v1_t, photo_size) == 324, "Unexpected legacy settings ABI");
_Static_assert(sizeof(tv_settings_t) == 364 && offsetof(tv_settings_t, photo_size) == 344,
               "Unexpected version 2 settings ABI");

bool settings_country_valid(const char country[TV_COUNTRY_BYTES])
{
    /* Bound a country/region key and keep it safe as an unescaped URI component.
     * Unknown, well-formed keys retain the factory GB timezone fallback. */
    if (!country)
        return false;
    size_t length = 0;
    while (length < TV_COUNTRY_BYTES && country[length])
        ++length;
    if (length < 2 || length == TV_COUNTRY_BYTES)
        return false;
    if (length > 2 && (length == 3 || country[2] != '-'))
        return false;
    for (size_t i = 0; i < length; ++i)
    {
        if (i == 2)
            continue;
        unsigned char c = country[i];
        bool letter = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
        if (!letter && !(i > 2 && c >= '0' && c <= '9'))
            return false;
    }
    return true;
}

bool settings_valid(const tv_settings_t *s)
{
    /* Validate all settings and photo lengths before accepting or persisting them.
     * FIXED_RECONSTRUCTION: validate the entire regional key, not country[2]. */

    if (s->version != TV_SETTINGS_VERSION || !memchr(s->ssid, 0, sizeof(s->ssid)) ||
        !memchr(s->password, 0, sizeof(s->password)) || !memchr(s->city, 0, sizeof(s->city)) ||
        !memchr(s->ntp, 0, sizeof(s->ntp)) || !memchr(s->weather_key, 0, sizeof(s->weather_key)) ||
        !settings_country_valid(s->country) || s->theme > 3 || s->animation > 4 || s->date_format > 2 ||
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
    s->version = TV_SETTINGS_VERSION;
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

static bool load_nvs(tv_settings_t *s, bool *migrated)
{
    /* Load version 2 or migrate every field of the released 344-byte version 1.
     * FIXED_RECONSTRUCTION: expanding country must not reinterpret old NTP,
     * brightness or photo bytes at their new offsets or discard saved settings. */
    union { tv_settings_t latest; tv_settings_v1_t legacy; } saved;
    size_t length = sizeof(saved);
    *migrated = false;
    if (nvs_get_blob(settings_store, "configuration", &saved, &length) != ESP_OK)
        return false;
    if (length == sizeof(saved.latest) && saved.latest.version == TV_SETTINGS_VERSION)
        *s = saved.latest;
    else if (length == sizeof(saved.legacy) && saved.legacy.version == 1 &&
             memchr(saved.legacy.country, 0, sizeof(saved.legacy.country)))
    {
        const tv_settings_v1_t *old = &saved.legacy;
        memset(s, 0, sizeof(*s));
        s->version = TV_SETTINGS_VERSION;
        memcpy(s->ssid, old->ssid, sizeof(s->ssid));
        memcpy(s->password, old->password, sizeof(s->password));
        memcpy(s->city, old->city, sizeof(s->city));
        memcpy(s->country, old->country, sizeof(old->country));
        memcpy(s->ntp, old->ntp, sizeof(s->ntp));
        memcpy(s->weather_key, old->weather_key, sizeof(s->weather_key));
        s->day_level = old->day_level;
        s->night_level = old->night_level;
        memcpy(s->colors, old->colors, sizeof(s->colors));
        s->theme = old->theme;
        s->animation = old->animation;
        s->date_format = old->date_format;
        s->night_start = old->night_start;
        s->night_stop = old->night_stop;
        s->photo_seconds = old->photo_seconds;
        s->fahrenheit = old->fahrenheit;
        s->hour12 = old->hour12;
        s->miles = old->miles;
        s->browser_time = old->browser_time;
        s->night_mode = old->night_mode;
        s->click_count = old->click_count;
        s->photo_mask = old->photo_mask;
        /* Earliest version 1 blobs left the mode byte as zero-filled padding. */
        s->wifi_mode = old->wifi_mode ? old->wifi_mode : old->ssid[0] ? 1 : 2;
        memcpy(s->photo_size, old->photo_size, sizeof(s->photo_size));
        *migrated = true;
    }
    else
        return false;
    return settings_valid(s);
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
    /* Load settings, preferring the original sector over the native NVS fallback.
     * FIXED_RECONSTRUCTION: migrate version 1 NVS while preserving raw-sector
     * precedence and explicit version 2 setup mode, including wifi_mode == 0. */

    settings_mutex = xSemaphoreCreateMutex();
    if (!settings_mutex)
        return ESP_ERR_NO_MEM;
    esp_err_t result = nvs_open("small_tv", NVS_READWRITE, &settings_store);
    if (result != ESP_OK)
        return result;
    /* REQUESTED_CHANGE: keep the new preference outside both legacy layouts.
     * Reading an absent key uses the default without a startup flash write. */
    uint32_t jpeg_limit=TV_JPEG_WRITE_LIMIT_DEFAULT_KIB;
    result=nvs_get_u32(settings_store,"jpeg_write_kib",&jpeg_limit);
    if(result!=ESP_OK && result!=ESP_ERR_NVS_NOT_FOUND)return result;
    portENTER_CRITICAL(&jpeg_limit_lock);jpeg_write_limit_kib=jpeg_limit;portEXIT_CRITICAL(&jpeg_limit_lock);
    bool migrated;
    dirty = false;
    if (!load_nvs(&current_settings, &migrated))
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
            dirty = migrated;
        }
    }
    dirty = dirty || migrated;
    last_change_us = esp_timer_get_time();
    generation = 1;
    theme_selection_generation = 0;
    return xTaskCreate(persistence_task, "settings", 2048, NULL, 1, NULL) == pdPASS
               ? ESP_OK
               : ESP_ERR_NO_MEM;
}

void settings_snapshot(tv_settings_t *out)
{
    /* Copy a consistent settings snapshot while holding the mutex. */

    settings_snapshot_with_revisions(out, NULL, NULL);
}

void settings_snapshot_with_revisions(tv_settings_t *out, uint32_t *configuration_revision,
                                      uint32_t *theme_selection_revision)
{
    /* Copy display values and command revisions under one lock.
     * FIXED_RECONSTRUCTION: a same-value theme selection is an explicit reset
     * command at 0x4200d7f0; /updateCity clears the same latch at 0x4200f3cc.
     * Keep the revision coherent with the theme and location so a concurrent
     * HTTP command cannot reset an older or already-seen snapshot. */

    xSemaphoreTake(settings_mutex, portMAX_DELAY);
    *out = current_settings;
    if (configuration_revision)
        *configuration_revision = generation;
    if (theme_selection_revision)
        *theme_selection_revision = theme_selection_generation;
    xSemaphoreGive(settings_mutex);
}

static void mark_settings_changed_locked(void)
{
    /* Schedule one debounced write for changed bytes; the caller holds the mutex. */
    ++generation;
    dirty = true;
    last_change_us = esp_timer_get_time();
}

esp_err_t settings_select_theme(unsigned theme)
{
    /* Publish every valid theme command, including unchanged selections.
     * FIXED_RECONSTRUCTION: 0x4200d7f0 clears the theme-init latch unconditionally.
     * The transient command counter is not persisted; unchanged configuration
     * bytes do not need another flash write. Repeated commands may coalesce. */

    if (theme > 3)
        return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(settings_mutex, portMAX_DELAY);
    if (current_settings.theme != theme)
    {
        current_settings.theme = (uint8_t)theme;
        mark_settings_changed_locked();
    }
    ++theme_selection_generation;
    xSemaphoreGive(settings_mutex);
    return ESP_OK;
}

esp_err_t settings_update_city(const char *city, const char *country)
{
    /* Apply only the location and always request a coherent theme reinitialization.
     * FIXED_RECONSTRUCTION: 0x4200f2c0 clears the theme latch even for the same
     * city. Publish both under one mutex; do not replay an HTTP snapshot's older
     * theme, brightness or photo lengths over concurrent changes. Identical city
     * commands advance only the transient revision and never schedule flash I/O. */
    if (!city || !city[0] || strlen(city) >= sizeof(current_settings.city) ||
        !settings_country_valid(country))
        return ESP_ERR_INVALID_ARG;
    xSemaphoreTake(settings_mutex, portMAX_DELAY);
    if (strcmp(current_settings.city, city) || strcmp(current_settings.country, country))
    {
        strcpy(current_settings.city, city);
        strcpy(current_settings.country, country);
        mark_settings_changed_locked();
    }
    ++theme_selection_generation;
    xSemaphoreGive(settings_mutex);
    return ESP_OK;
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
        mark_settings_changed_locked();
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
    mark_settings_changed_locked();
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

uint32_t settings_jpeg_write_limit_kib(void)
{
    /* A short atomic snapshot is cheap enough for every decoder checkpoint. */
    portENTER_CRITICAL(&jpeg_limit_lock);uint32_t value=jpeg_write_limit_kib;portEXIT_CRITICAL(&jpeg_limit_lock);
    return value;
}

esp_err_t settings_set_jpeg_write_limit_kib(uint32_t kib)
{
    /* Persist before publishing; serialize with ordinary settings NVS commits.
     * A repeated value causes no flash write or unrelated theme reinitialization. */
    xSemaphoreTake(settings_mutex,portMAX_DELAY);
    esp_err_t result=ESP_OK;
    if(kib!=settings_jpeg_write_limit_kib()) {
        result=nvs_set_u32(settings_store,"jpeg_write_kib",kib);
        if(result==ESP_OK)result=nvs_commit(settings_store);
        if(result==ESP_OK) {
            portENTER_CRITICAL(&jpeg_limit_lock);jpeg_write_limit_kib=kib;portEXIT_CRITICAL(&jpeg_limit_lock);
        }
    }
    xSemaphoreGive(settings_mutex);return result;
}
