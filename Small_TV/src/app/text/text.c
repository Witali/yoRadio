#include "text.h"
#include <string.h>

uint32_t text_utf8_decode(const char *text, size_t available, size_t *consumed)
{
    /* Decode one Unicode scalar without reading beyond the supplied byte range.
     * FIXED_FACTORY: 0x4200abee groups every high byte with its successor and
     * 0x4200aae0 turns unknown pairs into Celsius. Invalid UTF-8 consumes only
     * one byte, keeping any following ASCII/valid sequence available to decode. */
    if (consumed)
        *consumed = 0;
    if (!text || !available || !consumed || !text[0])
        return 0;
    const unsigned char *bytes = (const unsigned char *)text;
    *consumed = 1;
    if (bytes[0] < 0x80)
        return bytes[0];
    unsigned length;
    uint32_t scalar, minimum;
    if (bytes[0] >= 0xc2 && bytes[0] <= 0xdf)
        length = 2, scalar = bytes[0] & 0x1f, minimum = 0x80;
    else if (bytes[0] >= 0xe0 && bytes[0] <= 0xef)
        length = 3, scalar = bytes[0] & 0x0f, minimum = 0x800;
    else if (bytes[0] >= 0xf0 && bytes[0] <= 0xf4)
        length = 4, scalar = bytes[0] & 0x07, minimum = 0x10000;
    else
        return 0xfffd;
    if (length > available)
        return 0xfffd;
    for (unsigned i = 1; i < length; ++i)
    {
        if ((bytes[i] & 0xc0) != 0x80)
            return 0xfffd;
        scalar = (scalar << 6) | (bytes[i] & 0x3f);
    }
    if (scalar < minimum || scalar > 0x10ffff || (scalar >= 0xd800 && scalar <= 0xdfff))
        return 0xfffd;
    *consumed = length;
    return scalar;
}

size_t text_utf8_copy(char *out, size_t capacity, const char *text, size_t source_limit)
{
    /* Preserve a complete UTF-8 prefix within the original source-byte budget.
     * FIXED_FACTORY: 0x4200fccc truncates labels at 15 raw bytes and can leave
     * half a character. Repair malformed bytes as '?' without swallowing ASCII.
     * This helper is for UTF-8 fields, not the separate legacy unit tokens. */
    if (!out || !capacity)
        return 0;
    if (!text)
    {
        out[0] = 0;
        return 0;
    }
    size_t length = strlen(text), position = 0, written = 0;
    while (position < length && position < source_limit)
    {
        size_t consumed;
        uint32_t scalar = text_utf8_decode(text + position, length - position, &consumed);
        if (!consumed || consumed > source_limit - position)
            break;
        bool malformed = scalar == 0xfffd && consumed == 1;
        size_t bytes = malformed ? 1 : consumed;
        if (bytes >= capacity - written)
            break;
        if (malformed)
            out[written] = '?';
        else
            memmove(out + written, text + position, bytes);
        written += bytes;
        position += consumed;
    }
    out[written] = 0;
    return written;
}
