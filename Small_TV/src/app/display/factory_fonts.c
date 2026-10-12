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

void display_factory_text(int x, int y, const char *text, unsigned height, uint16_t color,
                          uint16_t background, bool transparent)
{
    /* Draw factory glyphs with the spacing recovered at 0x4200aa1e/0x4200abee. */

    const unsigned char *cursor = (const unsigned char *)text;
    while (*cursor && x < 240)
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
        if (found)
            display_bitmap(x, y, &glyph, color, background, transparent);
        else if (!transparent)
        {
            /* The factory uses a space with black ink to erase large digits. */
            extern void display_fill(int, int, int, int, uint16_t);
            display_fill(x, y, advance, height, background);
        }
        if (transparent && height == 16 && advance == 8)
            /* 0x4200aad0 subtracts three from the normal eight-pixel advance. */
            advance = 5;
        x += advance;
    }
}

void display_factory_symbol(int x, int y, unsigned symbol, uint16_t color, uint16_t background)
{
    /* Draw one extracted decorative bitmap with foreground/background colors. */

    tv_bitmap_t bitmap;
    if (factory_symbol(symbol, &bitmap))
        display_bitmap(x, y, &bitmap, color, background, false);
}
