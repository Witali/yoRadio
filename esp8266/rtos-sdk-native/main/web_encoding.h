#pragma once
#include <stddef.h>
#include <string.h>
#include <strings.h>

/* RFC 9110 12.5.3. Integer qvalues; no floating point or allocations. */
static inline int web_encoding_quality(const char *header, const char *wanted) {
    if (!header) return 1000;
    int wildcard = -1, explicit_quality = -1;
    size_t wanted_length = strlen(wanted);
    const char *p = header;
    while (*p) {
        while (*p == ' ' || *p == '\t' || *p == ',') ++p;
        const char *start = p;
        while (*p && *p != ',' && *p != ';' && *p != ' ' && *p != '\t') ++p;
        size_t length = p - start;
        int quality = 1000;
        while (*p == ' ' || *p == '\t') ++p;
        if (*p == ';') {
            ++p;
            while (*p == ' ' || *p == '\t') ++p;
            if (*p == 'q' || *p == 'Q') {
                ++p;
                while (*p == ' ' || *p == '\t') ++p;
                if (*p++ == '=') {
                    while (*p == ' ' || *p == '\t') ++p;
                    unsigned whole = (unsigned)(*p - '0');
                    quality = 0;
                    if (whole <= 1U) {
                        ++p; quality = (int)whole * 1000;
                        unsigned digits = 0, fraction = 0;
                        if (*p == '.') {
                            ++p;
                            while (*p >= '0' && *p <= '9') {
                                if (++digits <= 3U) fraction = fraction * 10U + (unsigned)(*p - '0');
                                ++p;
                            }
                        }
                        if (digits > 3U || (whole && fraction)) quality = 0;
                        else {
                            while (digits++ < 3U) fraction *= 10U;
                            quality += (int)fraction;
                        }
                    }
                } else { --p; quality = 0; }
            } else quality = 0;
            while (*p == ' ' || *p == '\t') ++p;
            if (*p && *p != ',') quality = 0;
        }
        if (length == wanted_length && !strncasecmp(start, wanted, length))
            explicit_quality = quality;
        if (length == 1U && *start == '*') wildcard = quality;
        while (*p && *p != ',') ++p;
    }
    if (explicit_quality >= 0) return explicit_quality;
    if (!strcmp(wanted, "identity")) return wildcard == 0 ? 0 : 1000;
    return wildcard >= 0 ? wildcard : 0;
}
