#include "factory_ui.h"
#include "factory_bitmaps.h"
#include <string.h>

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
        return false;
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

static void draw_text(int x, int y, int left, int right, bool complete_glyphs, const char *text,
                      unsigned height, uint16_t color, uint16_t background, bool transparent)
{
    /* Share factory decoding/spacing between panel-clipped and bounded labels. */

    const unsigned char *cursor = (const unsigned char *)text;
    while (*cursor && x < right)
    {
        unsigned advance = height / 2;
        tv_bitmap_t glyph;
        bool found;
        if (cursor[0] >= 0x81 && cursor[1])
        {
            /* These are the original two-byte Celsius/Fahrenheit codes,
             * not UTF-8 degree signs. Their bitmap advances a full 24 pixels. */
            unsigned symbol =
                cursor[0] == 0xa8 && cursor[1] == 0x48 ? TV_SYMBOL_FAHRENHEIT : TV_SYMBOL_CELSIUS;
            found = factory_symbol(symbol, &glyph);
            cursor += 2;
            advance = height;
        }
        else
        {
            found = factory_glyph(*cursor++, height, &glyph);
        }
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
    /* Measure opaque factory text, including full-width two-byte unit symbols. */

    unsigned width = 0;
    const unsigned char *cursor = (const unsigned char *)text;
    while (*cursor)
    {
        bool pair = cursor[0] >= 0x81 && cursor[1];
        width += pair ? height : height / 2;
        cursor += pair ? 2 : 1;
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
