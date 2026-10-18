#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <string.h>

// Common privacy boundary, BEFORE async dispatch, recovery or opening. Existing
// target asset allowlists still apply afterward. GET is the sole static method;
// the only public /data file is the exact canonical playlist download. Encoded
// paths, aliases, dot segments and case variants never reach filesystem helpers.
static inline bool native_wifi_public_static_uri(const char *uri, bool is_get) {
    if (!uri || !is_get || uri[0] != '/') return false;
    size_t length = 0, path = 0;
    bool query = false;
    for (; length < 512U && uri[length]; ++length) {
        unsigned char c = (unsigned char)uri[length];
        if (c <= 0x20 || c >= 0x7f || c == '#' || c == '\\') return false;
        if (!query && c == '?') { path = length; query = true; }
        else if (!query && c == '%') return false;
    }
    if (length == 512U) return false;
    if (!query) path = length;
    if (!path || path >= 160U) return false;
    for (size_t i = 1; i < path; ++i) {
        if (uri[i] == '/' && uri[i - 1U] == '/') return false;
        if (uri[i] == '.' && uri[i - 1U] == '/' &&
            (i + 1U == path || uri[i + 1U] == '/' ||
             (uri[i + 1U] == '.' && (i + 2U == path || uri[i + 2U] == '/')))) return false;
    }
    bool data = path >= 5U;
    static const char lower[] = "data";
    for (size_t i = 0; data && i < 4U; ++i) {
        unsigned char c = (unsigned char)uri[i + 1U];
        if (c >= 'A' && c <= 'Z') c = (unsigned char)(c + ('a' - 'A'));
        if (c != (unsigned char)lower[i]) data = false;
    }
    data = data && (path == 5U || uri[5] == '/');
    static const char playlist[] = "/data/playlist.csv";
    return !data || (path == sizeof(playlist) - 1U && !memcmp(uri, playlist, sizeof(playlist) - 1U));
}
