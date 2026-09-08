#pragma once
#include <stddef.h>
#include <string.h>

/* One JSON string unit, never a partial UTF-8 code point or escape. ICY text
 * has no reliable charset here. Keep valid UTF-8 unchanged and render each
 * invalid byte as '?' instead of breaking the browser's whole WebSocket.
 * This keeps the existing 2x escaping bound; no extra message buffer/heap.
 * ASCII controls retain the existing omitted-from-display policy. */
static inline size_t json_text_unit(const char **source, char encoded[5]) {
    const unsigned char *s = (const unsigned char *)*source;
    unsigned char c = *s;
    size_t count = 1;
    encoded[0] = '\0';
    if (!c) return 0;
    *source += 1;
    if (c < 0x20U) return 0;
    if (c == '"' || c == '\\') {
        encoded[0] = '\\'; encoded[1] = (char)c; encoded[2] = '\0';
        return 2;
    }
    if (c >= 0x80U) {
        if (c >= 0xc2U && c <= 0xdfU) count = 2;
        else if (c >= 0xe0U && c <= 0xefU) count = 3;
        else if (c >= 0xf0U && c <= 0xf4U) count = 4;
        else goto invalid;
        for (size_t i = 1; i < count; ++i) {
            /* Stop at the first NUL; never look past the input string. */
            if (s[i] < 0x80U || s[i] > 0xbfU) goto invalid;
        }
        if ((c == 0xe0U && s[1] < 0xa0U) ||
            (c == 0xedU && s[1] > 0x9fU) ||
            (c == 0xf0U && s[1] < 0x90U) ||
            (c == 0xf4U && s[1] > 0x8fU)) goto invalid;
    }
    memcpy(encoded, s, count);
    encoded[count] = '\0';
    *source += count - 1U;
    return count;
invalid:
    encoded[0] = '?'; encoded[1] = '\0';
    return 1;
}
