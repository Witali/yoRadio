#include "factory_settings.h"
#include <string.h>

static uint32_t read32(const uint8_t *data)
{
    /* Read an unaligned little-endian 32-bit field from the factory sector. */

    return data[0] | (uint32_t)data[1] << 8 | (uint32_t)data[2] << 16 | (uint32_t)data[3] << 24;
}

static void write32(uint8_t *data, uint32_t value)
{
    /* Write a 32-bit value in the original little-endian sector format. */

    for (unsigned i = 0; i < 4; ++i)
        data[i] = (uint8_t)(value >> (8 * i));
}

static void read_string(char *out, size_t capacity, const uint8_t *data, size_t width)
{
    /* Import a bounded factory string while recognizing erased flash bytes. */

    if (data[0] == 0xff)
        return;
    size_t length = 0;
    while (length < width && data[length] && data[length] != 0xff)
        ++length;
    if (length >= capacity)
        length = capacity - 1;
    memcpy(out, data, length);
    out[length] = 0;
}

static unsigned bounded(const uint8_t *raw, unsigned offset, unsigned low, unsigned high,
                        unsigned fallback)
{
    /* Read a factory integer or retain its documented default if out of range. */

    unsigned value = read32(raw + offset);
    return value >= low && value <= high ? value : fallback;
}

bool factory_settings_decode(const uint8_t raw[FACTORY_SETTINGS_BYTES], tv_settings_t *s)
{
    /* Import the original raw settings layout into validated native fields. */

    bool present = false;
    for (unsigned i = 0; i < FACTORY_SETTINGS_BYTES; ++i)
        if (raw[i] != 0xff)
        {
            present = true;
            break;
        }
    if (!present)
        return false;
    read_string(s->ssid, sizeof(s->ssid), raw + 4, 65);
    /* The original sector uses fixed 65-byte strings and 32-bit flags.
     * The compact native struct uses different widths and must not be memcpy'd. */
    read_string(s->password, sizeof(s->password), raw + 0x45, 65);
    read_string(s->ntp, sizeof(s->ntp), raw + 0x86, 65);
    read_string(s->country, sizeof(s->country), raw + 0xc7, 20);
    read_string(s->city, sizeof(s->city), raw + 0xdb, 65);
    read_string(s->weather_key, sizeof(s->weather_key), raw + 0x11c, 65);
    s->wifi_mode = bounded(raw, 0x160, 0, 2, s->ssid[0] ? 1 : 2);
    s->animation = bounded(raw, 0x164, 0, 4, 0);
    s->theme = bounded(raw, 0x168, 0, 3, 0);
    s->fahrenheit = bounded(raw, 0x16c, 0, 1, 0);
    s->hour12 = bounded(raw, 0x170, 0, 1, 0);
    s->miles = bounded(raw, 0x174, 0, 1, 0);
    s->browser_time = bounded(raw, 0x178, 0, 1, 0);
    s->date_format = bounded(raw, 0x17c, 0, 2, 2);
    s->day_level = bounded(raw, 0x180, 0, 1000, 0);
    s->colors[0] = bounded(raw, 0x184, 0, 65535, 0xf800);
    s->colors[1] = bounded(raw, 0x188, 0, 65535, 0xffe0);
    s->colors[2] = bounded(raw, 0x18c, 0, 65535, 0xffff);
    s->night_mode = bounded(raw, 0x190, 0, 1, 0);
    s->night_start = bounded(raw, 0x194, 18, 23, 22);
    s->night_stop = bounded(raw, 0x198, 5, 12, 9);
    s->night_level = bounded(raw, 0x19c, 0, 1000, 500);
    s->photo_seconds = bounded(raw, 0x1a0, 3, 60, 5);
    s->photo_mask = bounded(raw, 0x1a4, 0, 31, 31);
    for (unsigned i = 0; i < PHOTO_COUNT; ++i)
        s->photo_size[i] = bounded(raw, 0x1a8 + i * 4, 0, PHOTO_SLOT_BYTES, s->photo_size[i]);
    return settings_valid(s);
}

void factory_settings_encode(const tv_settings_t *s, uint8_t raw[FACTORY_SETTINGS_BYTES])
{
    /* Serialize native preferences into the factory-compatible raw sector. */

    memset(raw, 0, FACTORY_SETTINGS_BYTES);
    write32(raw, s->photo_mask);
    memcpy(raw + 4, s->ssid, strlen(s->ssid));
    memcpy(raw + 0x45, s->password, strlen(s->password));
    memcpy(raw + 0x86, s->ntp, strlen(s->ntp));
    memcpy(raw + 0xc7, s->country, 2);
    memcpy(raw + 0xdb, s->city, strlen(s->city));
    memcpy(raw + 0x11c, s->weather_key, strlen(s->weather_key));
    write32(raw + 0x160, s->wifi_mode);
    /* Preserve both factory photo-mask fields; the second drives the slideshow.
     * Five file lengths follow it, starting at byte 0x1a8. */
    unsigned values[] = {s->animation,   s->theme,        s->fahrenheit,  s->hour12,
                         s->miles,       s->browser_time, s->date_format, s->day_level,
                         s->colors[0],   s->colors[1],    s->colors[2],   s->night_mode,
                         s->night_start, s->night_stop,   s->night_level, s->photo_seconds,
                         s->photo_mask};
    for (unsigned i = 0; i < sizeof(values) / sizeof(values[0]); ++i)
        write32(raw + 0x164 + i * 4, values[i]);
    for (unsigned i = 0; i < PHOTO_COUNT; ++i)
        write32(raw + 0x1a8 + i * 4, s->photo_size[i]);
}
