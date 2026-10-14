#include "factory_ui.h"
#include "factory_bitmaps.h"
#include "unicode_bitmaps.h"
#include "text.h"
#include <string.h>

static bool unicode_glyph(unsigned character, unsigned height, tv_bitmap_t *out)
{
    /* Find a bundled Spleen Unicode glyph with the factory text-cell dimensions.
     * FIXED_FACTORY: non-ASCII text must render its scalar instead of triggering
     * the unrelated Celsius fallback in 0x4200aae0. ASCII uses the original data. */
    unsigned first = 0, end = UNICODE_GLYPH_COUNT;
    while (first < end)
    {
        unsigned middle = first + (end - first) / 2;
        if (unicode_codepoints[middle] < character)
            first = middle + 1;
        else
            end = middle;
    }
    if (first == UNICODE_GLYPH_COUNT || unicode_codepoints[first] != character)
        return false;
    const uint8_t *pixels;
    if (height == 16)
        pixels = unicode_font16[first];
    else if (height == 24)
        pixels = unicode_font24[first];
    else if (height == 32)
        pixels = unicode_font32[first];
    else
        return false;
    unsigned width = height / 2;
    *out = (tv_bitmap_t){pixels, width, height, (width + 7) / 8};
    return true;
}

bool factory_glyph(unsigned character, unsigned height, tv_bitmap_t *out)
{
    /* Find a bounded glyph in the extracted factory bitmap tables. */

    const factory_font_table_t *table = NULL;
    for (unsigned i = 0; i < FACTORY_FONT_COUNT; ++i)
    {
        if (factory_fonts[i].height == height)
        {
            table = &factory_fonts[i];
            break;
        }
    }
    if (!table || character < table->first || character >= table->first + table->count)
        return character >= 128 && unicode_glyph(character, height, out);
    *out = (tv_bitmap_t){table->data + (character - table->first) * table->stride * height,
                         table->width, height, table->stride};
    return true;
}

bool factory_symbol(unsigned symbol, tv_bitmap_t *out)
{
    /* Find a temperature-unit or decorative bitmap by its logical ID. */

    if (symbol >= FACTORY_SYMBOL_COUNT)
        return false;
    const factory_symbol_table_t *table = &factory_symbols[symbol];
    *out = (tv_bitmap_t){table->data, table->width, table->height, table->stride};
    return true;
}

static unsigned text_token(const char *text, size_t available, size_t *consumed)
{
    /* Decode one UTF-8 scalar or one of the two explicit factory unit tokens.
     * FIXED_FACTORY: an arbitrary high-byte pair is not a Celsius symbol.
     * Recognize Unicode Celsius/Fahrenheit and degree+C/F spellings consistently. */
    const unsigned char *bytes = (const unsigned char *)text;
    if (available >= 2 && ((bytes[0] == 0xa1 && bytes[1] == 0xe6) ||
                          (bytes[0] == 0xa8 && bytes[1] == 0x48)))
    {
        *consumed = 2;
        return bytes[0] == 0xa1 ? 0x2103 : 0x2109;
    }
    unsigned scalar = text_utf8_decode(text, available, consumed);
    if (scalar == 0xb0 && available > *consumed &&
        (bytes[*consumed] == 'C' || bytes[*consumed] == 'F'))
    {
        scalar = bytes[*consumed] == 'C' ? 0x2103 : 0x2109;
        ++*consumed;
    }
    return scalar;
}

static void draw_text(int x, int y, int left, int right, bool complete_glyphs, const char *text,
                      unsigned height, uint16_t color, uint16_t background, bool transparent)
{
    /* Share scalar decoding/spacing between panel-clipped and bounded labels.
     * FIXED_FACTORY: preserve the two unit bitmaps, decode complete UTF-8 and
     * render unsupported scalars as '?' rather than inventing Celsius symbols. */

    if (!text)
        return;
    const char *cursor = text;
    size_t remaining = strlen(text);
    while (remaining && x < right)
    {
        unsigned advance = height / 2;
        tv_bitmap_t glyph;
        bool found;
        size_t consumed;
        unsigned scalar = text_token(cursor, remaining, &consumed);
        if (scalar == 0x2103 || scalar == 0x2109)
        {
            /* Keep the original 24x24 Celsius/Fahrenheit bitmaps and their
             * height-based advance, independent of the source spelling. */
            unsigned symbol = scalar == 0x2109 ? TV_SYMBOL_FAHRENHEIT : TV_SYMBOL_CELSIUS;
            found = factory_symbol(symbol, &glyph);
            advance = height;
        }
        else
        {
            found = factory_glyph(scalar, height, &glyph);
            if (!found && scalar >= 128)
                found = factory_glyph('?', height, &glyph);
        }
        cursor += consumed;
        remaining -= consumed;
        unsigned spacing = transparent && height == 16 && advance == 8 ? 5 : advance;
        /* A transparent glyph can be wider than its advance. Require both to
         * fit, and never draw half of a legacy two-byte temperature symbol. */
        unsigned extent = found && glyph.width > spacing ? glyph.width : spacing;
        if (complete_glyphs && extent > (unsigned)(right - x))
            break;
        if (found)
        {
            if (left >= 0)
                display_bitmap_region(x, y, &glyph, left, y, right, y + height,
                                       color, background, transparent);
            else
                display_bitmap(x, y, &glyph, color, background, transparent);
        }
        else if (!transparent)
        {
            /* The factory uses a space with black ink to erase large digits. */
            extern void display_fill(int, int, int, int, uint16_t);
            int start = left >= 0 && x < left ? left : x;
            int end = x + (int)advance;
            if (end > right) end = right;
            display_fill(start, y, end - start, height, background);
        }
        /* 0x4200aad0 subtracts three from the normal eight-pixel advance. */
        x += spacing;
    }
}

void display_factory_text(int x, int y, const char *text, unsigned height, uint16_t color,
                          uint16_t background, bool transparent)
{
    /* Preserve the recovered text API, including partial glyphs at the panel edge. */

    draw_text(x, y, -1, 240, false, text, height, color, background, transparent);
}

void display_factory_text_bounded(int x, int y, int width, const char *text, unsigned height,
                                  uint16_t color, uint16_t background, bool transparent)
{
    /* Draw complete glyphs within one field, stopping before its right edge.
     * FIXED_FACTORY: 0x4200abee bounds text by the panel rather than the field;
     * long city/weather labels can overwrite adjacent content. */

    if (x < 0 || x >= 240 || width <= 0)
        return;
    if (width > 240 - x)
        width = 240 - x;
    draw_text(x, y, x, x + width, true, text, height, color, background, transparent);
}

unsigned display_factory_text_width(const char *text, unsigned height)
{
    /* Measure exactly the scalar/unit cells used by the opaque text renderer.
     * FIXED_FACTORY: UTF-8 byte length is not glyph width; share decoding with draw_text. */

    unsigned width = 0;
    if (!text)
        return 0;
    const char *cursor = text;
    size_t remaining = strlen(text);
    while (remaining)
    {
        size_t consumed;
        unsigned scalar = text_token(cursor, remaining, &consumed);
        width += scalar == 0x2103 || scalar == 0x2109 ? height : height / 2;
        cursor += consumed;
        remaining -= consumed;
    }
    return width;
}

void display_factory_text_window(int x, int y, int width, unsigned offset, const char *text,
                                 unsigned height, uint16_t color, uint16_t background)
{
    /* Draw a moving text prefix through a fixed, opaque field window.
     * REQUESTED_CHANGE: retain partial glyphs at both edges during scrolling. */

    if (x < 0 || x >= 240 || width <= 0)
        return;
    if (width > 240 - x) width = 240 - x;
    unsigned length = display_factory_text_width(text, height);
    unsigned limit = length > (unsigned)width ? length - width : 0;
    if (offset > limit) offset = limit;
    draw_text(x - (int)offset, y, x, x + width, false, text, height, color, background, false);
}

void display_factory_symbol(int x, int y, unsigned symbol, uint16_t color, uint16_t background)
{
    /* Draw one extracted decorative bitmap with foreground/background colors. */

    tv_bitmap_t bitmap;
    if (factory_symbol(symbol, &bitmap))
        display_bitmap(x, y, &bitmap, color, background, false);
}
