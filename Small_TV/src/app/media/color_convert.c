#include "color_convert.h"
#include <string.h>

uint16_t rgb565_from_rgb888(uint32_t rgb)
{
    /* Convert RGB888 with the unchanged factory 0x42008a96 truncation. */
    return ((rgb >> 8) & 0xf800) | ((rgb >> 5) & 0x07e0) | ((rgb >> 3) & 0x001f);
}

uint32_t rgb888_from_rgb565(uint16_t rgb)
{
    /* Expand RGB565 using the factory 0x42008a6a high-bit replication. */
    unsigned r = (rgb >> 11) & 31, g = (rgb >> 5) & 63, b = rgb & 31;
    return (((r << 3) | (r >> 2)) << 16) | (((g << 2) | (g >> 4)) << 8) | (b << 3) | (b >> 2);
}

static unsigned sample_channels(color_sample_format_t format)
{
    /* Keep the sample layout independent of JPEG's color-space enum values. */
    switch (format)
    {
    case COLOR_SAMPLES_GRAY: return 1;
    case COLOR_SAMPLES_RGB: return 3;
    case COLOR_SAMPLES_CMYK:
    case COLOR_SAMPLES_CMYK_ADOBE: return 4;
    default: return 0;
    }
}

static uint32_t read_sample(const uint8_t *source, size_t sample, unsigned bytes)
{
    /* memcpy permits an unaligned 16-bit input row without aliasing violations. */
    if (bytes == 1)
        return source[sample];
    uint16_t value;
    memcpy(&value, source + sample * 2, sizeof(value));
    return value;
}

static uint32_t sample_to_byte(uint32_t value, uint32_t maximum)
{
    /* Normalize the full sample range before the unchanged RGB565 truncation. */
    if (maximum == 255)
        return value;
    return (value * 255u + maximum / 2u) / maximum;
}

bool color_convert_row_rgb565(const void *source, size_t source_bytes, size_t pixels,
                              unsigned precision, color_sample_format_t format,
                              uint16_t *destination, size_t destination_pixels)
{
    /* REQUESTED_CHANGE: convert grayscale/RGB/CMYK rows at all JPEG sample depths
     * in a format module.  Existing eight-bit RGB and web-color results stay
     * exact; new depths use full-range rounding, with no floating point or heap.
     * Validate the entire row before painting so corrupt samples cannot expose
     * a partially converted row to the caller. */
    unsigned channels = sample_channels(format);
    unsigned bytes = precision > 8 ? 2 : 1;
    if (!source || !destination || !pixels || !channels || precision < 2 || precision > 16 ||
        pixels > SIZE_MAX / channels / bytes || pixels > SIZE_MAX / sizeof(*destination) ||
        destination_pixels < pixels)
        return false;
    size_t input_bytes = pixels * channels * bytes;
    size_t output_bytes = pixels * sizeof(*destination);
    uintptr_t input_start = (uintptr_t)source, output_start = (uintptr_t)destination;
    if (source_bytes < input_bytes || input_start > UINTPTR_MAX - input_bytes ||
        output_start > UINTPTR_MAX - output_bytes ||
        (input_start < output_start + output_bytes && output_start < input_start + input_bytes))
        return false;
    const uint8_t *samples = source;
    uint32_t maximum = (1u << precision) - 1u;
    if (precision != 8 && precision != 16)
        for (size_t i = 0; i < pixels * channels; ++i)
            if (read_sample(samples, i, bytes) > maximum)
                return false;
    for (size_t pixel = 0; pixel < pixels; ++pixel)
    {
        size_t start = pixel * channels;
        if (channels == 1)
        {
            uint32_t gray = sample_to_byte(read_sample(samples, start, bytes), maximum);
            destination[pixel] = rgb565_from_rgb888(gray * 0x010101u);
            continue;
        }
        uint32_t black = channels == 4 ? read_sample(samples, start + 3, bytes) : 0;
        if (format == COLOR_SAMPLES_CMYK)
            black = maximum - black;
        uint32_t rgb[3];
        for (unsigned component = 0; component < 3; ++component)
        {
            uint32_t value = read_sample(samples, start + component, bytes);
            if (channels == 4)
            {
                if (format == COLOR_SAMPLES_CMYK)
                    value = maximum - value;
                /* 65535^2 + 32767 fits uint32_t, including 16-bit lossless.
                 * Keep full precision until the CMYK multiply is complete. */
                value = (value * black + maximum / 2u) / maximum;
            }
            rgb[component] = sample_to_byte(value, maximum);
        }
        destination[pixel] = rgb565_from_rgb888((rgb[0] << 16) | (rgb[1] << 8) | rgb[2]);
    }
    return true;
}
