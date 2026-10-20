#include "color_convert.h"

#ifdef _WIN32
#define TEST_EXPORT __declspec(dllexport)
#else
#define TEST_EXPORT
#endif

TEST_EXPORT bool color_test_row(const void *source, size_t source_bytes, size_t pixels,
                                unsigned precision, int format, uint16_t *output, size_t capacity)
{
    /* Export the production converter unchanged for the independent host oracle. */
    return color_convert_row_rgb565(source, source_bytes, pixels, precision,
                                    (color_sample_format_t)format, output, capacity);
}

TEST_EXPORT uint16_t color_test_pack(uint32_t rgb)
{
    /* Check the production helper still implements the factory web-color ABI. */
    return rgb565_from_rgb888(rgb);
}

TEST_EXPORT uint32_t color_test_expand(uint16_t rgb)
{
    /* Expose the actual migrated helper, including the factory high-bit repeat. */
    return rgb888_from_rgb565(rgb);
}
