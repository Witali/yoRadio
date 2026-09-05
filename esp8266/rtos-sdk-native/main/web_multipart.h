#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* A streaming form-data parser. At most 512 bytes are retained, including
 * incomplete headers or a boundary split at an arbitrary TCP read. */
typedef enum { MP_BEGIN, MP_DATA, MP_END } mp_event_t;
typedef bool (*mp_handler_t)(mp_event_t event, const uint8_t *data,
                             size_t length, void *context);
typedef struct {
    uint8_t buffer[512];
    size_t used;
    char marker[76];
    size_t marker_length;
    unsigned state; /* first boundary, headers, data, suffix, done */
    mp_handler_t handler;
    void *context;
} web_multipart_t;

static inline bool mp_init(web_multipart_t *p, const char *boundary,
                            mp_handler_t handler, void *context) {
    size_t n = strlen(boundary);
    if (!n || n > 70 || strpbrk(boundary, "\r\n")) return false;
    memset(p, 0, sizeof(*p));
    memcpy(p->marker, "\r\n--", 4);
    memcpy(p->marker + 4, boundary, n);
    p->marker_length = n + 4;
    p->handler = handler;
    p->context = context;
    return true;
}

static inline void mp_consume(web_multipart_t *p, size_t n) {
    p->used -= n;
    memmove(p->buffer, p->buffer + n, p->used);
}

static inline bool mp_process(web_multipart_t *p) {
    for (;;) {
        if (p->state == 0) {
            size_t n = p->marker_length - 2;
            if (p->used < n + 2) return true;
            if (memcmp(p->buffer, p->marker + 2, n) ||
                memcmp(p->buffer + n, "\r\n", 2)) return false;
            mp_consume(p, n + 2);
            p->state = 1;
        } else if (p->state == 1) {
            size_t n = 0;
            while (n + 4 <= p->used &&
                   memcmp(p->buffer + n, "\r\n\r\n", 4)) ++n;
            if (n + 4 > p->used) return p->used < sizeof(p->buffer);
            if (memchr(p->buffer, 0, n)) return false;
            p->buffer[n] = 0;
            if (!p->handler(MP_BEGIN, p->buffer, n, p->context)) return false;
            mp_consume(p, n + 4);
            p->state = 2;
        } else if (p->state == 2) {
            size_t n = 0, m = p->marker_length;
            while (n + m + 2 <= p->used) {
                if (!memcmp(p->buffer + n, p->marker, m) &&
                    (!memcmp(p->buffer + n + m, "--", 2) ||
                     !memcmp(p->buffer + n + m, "\r\n", 2))) break;
                ++n;
            }
            if (n + m + 2 <= p->used) {
                if (n && !p->handler(MP_DATA, p->buffer, n, p->context))
                    return false;
                if (!p->handler(MP_END, NULL, 0, p->context)) return false;
                mp_consume(p, n + m);
                p->state = 3;
            } else {
                /* Keep marker + its two-byte suffix until the next read. */
                n = p->used > m + 1 ? p->used - m - 1 : 0;
                if (!n) return true;
                if (!p->handler(MP_DATA, p->buffer, n, p->context)) return false;
                mp_consume(p, n);
            }
        } else if (p->state == 3) {
            if (p->used < 2) return true;
            bool last = !memcmp(p->buffer, "--", 2);
            if (!last && memcmp(p->buffer, "\r\n", 2)) return false;
            mp_consume(p, 2);
            p->state = last ? 4 : 1;
        } else {
            /* Only an optional CRLF epilogue is accepted by this endpoint. */
            if (p->used > 2 || (p->used && p->buffer[0] != '\r') ||
                (p->used == 2 && p->buffer[1] != '\n')) return false;
            return true;
        }
    }
}

static inline bool mp_feed(web_multipart_t *p, const uint8_t *data, size_t n) {
    while (n) {
        size_t count = sizeof(p->buffer) - p->used;
        if (count > n) count = n;
        if (!count) return false;
        memcpy(p->buffer + p->used, data, count);
        p->used += count; data += count; n -= count;
        if (!mp_process(p)) return false;
    }
    return true;
}

static inline bool mp_complete(const web_multipart_t *p) {
    return p->state == 4 && (p->used == 0 || p->used == 2);
}

static inline bool mp_parameter(const char *headers, const char *name,
                                char *out, size_t capacity) {
    size_t n = strlen(name);
    for (const char *s = headers; (s = strstr(s, name)) != NULL; ++s) {
        if (s != headers && s[-1] != ' ' && s[-1] != ';') continue;
        if (s[n] != '=' || s[n+1] != '"') continue;
        const char *value = s + n + 2, *end = strchr(value, '"');
        if (!end || (size_t)(end - value) >= capacity) return false;
        memcpy(out, value, (size_t)(end - value));
        out[end-value] = 0;
        return true;
    }
    return false;
}
