#pragma once
/* Portable bounded native web form contract. No target SDK dependencies. */
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
    if (!p || !boundary || !handler) return false;
    size_t n = 0;
    while (n <= 70 && boundary[n]) ++n;
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

/* Header parsing shares the body's fixed bound. Callers pass terminated HTTP
 * header values, or the terminated MP_BEGIN header block (at most 508 bytes).
 * Every parameter, including unknown extensions, is validated before use. */
#define MP_HEADER_BYTES 512U

typedef struct {
    const char *name, *value, *value_end;
    size_t name_length;
    bool quoted;
} mp_header_parameter_t;

static inline unsigned char mp_lower(unsigned char c) {
    return c >= 'A' && c <= 'Z' ? (unsigned char)(c + ('a' - 'A')) : c;
}

static inline bool mp_equal(const char *a, size_t n, const char *b, size_t m) {
    if (n != m) return false;
    for (size_t i = 0; i < n; ++i)
        if (mp_lower((unsigned char)a[i]) != mp_lower((unsigned char)b[i]))
            return false;
    return true;
}

static inline bool mp_token(unsigned char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
        (c >= '0' && c <= '9') ||
        (c && strchr("!#$%&'*+-.^_`|~", c) != NULL);
}

static inline void mp_skip_space(const char **p, const char *end) {
    while (*p < end && (**p == ' ' || **p == '\t')) ++*p;
}

static inline bool mp_bounded_end(const char *text, const char **end) {
    if (!text) return false;
    size_t n = 0;
    while (n < MP_HEADER_BYTES && text[n]) ++n;
    if (n == MP_HEADER_BYTES) return false;
    *end = text + n;
    return true;
}

/* Cursor begins after a media/disposition token. 1 = parameter, 0 = end,
 * -1 = malformed input. Only HTTP token or quoted-string values are accepted. */
static inline int mp_next_parameter(const char **cursor, const char *end,
                                    mp_header_parameter_t *parameter) {
    const char *p = *cursor;
    mp_skip_space(&p, end);
    if (p == end) return 0;
    if (*p++ != ';') return -1;
    mp_skip_space(&p, end);
    parameter->name = p;
    while (p < end && mp_token((unsigned char)*p)) ++p;
    parameter->name_length = (size_t)(p - parameter->name);
    if (!parameter->name_length) return -1;
    mp_skip_space(&p, end);
    if (p == end || *p++ != '=') return -1;
    mp_skip_space(&p, end);
    if (p == end) return -1;
    parameter->quoted = *p == '"';
    if (parameter->quoted) {
        parameter->value = ++p;
        while (p < end && *p != '"') {
            unsigned char c = (unsigned char)*p++;
            if (c == '\\') {
                if (p == end) return -1;
                c = (unsigned char)*p++;
            }
            if ((c < 32 && c != '\t') || c == 127) return -1;
        }
        if (p == end) return -1;
        parameter->value_end = p++;
    } else {
        parameter->value = p;
        while (p < end && mp_token((unsigned char)*p)) ++p;
        parameter->value_end = p;
        if (p == parameter->value) return -1;
    }
    mp_skip_space(&p, end);
    if (p != end && *p != ';') return -1;
    *cursor = p;
    return 1;
}

/* Compare each new key to earlier keys rather than retaining a request-sized
 * table. With the 512-byte input bound, both work and stack use are bounded. */
static inline bool mp_parameters_valid(const char *start, const char *end) {
    const char *cursor = start;
    mp_header_parameter_t current;
    int result;
    while ((result = mp_next_parameter(&cursor, end, &current)) == 1) {
        const char *previous = start;
        mp_header_parameter_t seen;
        while (mp_next_parameter(&previous, end, &seen) == 1 &&
               seen.name != current.name) {
            if (mp_equal(current.name, current.name_length,
                         seen.name, seen.name_length)) return false;
        }
    }
    return result == 0;
}

static inline bool mp_copy_parameter(const mp_header_parameter_t *parameter,
                                     char *out, size_t capacity,
                                     bool filename) {
    if (!out || !capacity) return false;
    size_t used = 0;
    out[0] = 0;
    for (const char *p = parameter->value; p < parameter->value_end; ++p) {
        char c = *p;
        if (parameter->quoted && c == '\\') {
            char next = *++p; /* Validated by mp_next_parameter. */
            /* Browser Windows file paths historically contain raw backslashes.
             * Retain those separators before basename validation. Standard
             * escaped quote/backslash still decodes normally. */
            if (filename && next != '\\' && next != '"') {
                if (used + 1 >= capacity) { out[0] = 0; return false; }
                out[used++] = '\\';
            }
            c = next;
        }
        if (used + 1 >= capacity) { out[0] = 0; return false; }
        out[used++] = c;
    }
    out[used] = 0;
    return true;
}

static inline bool mp_find_parameter(const char *start, const char *end,
                                     const char *name,
                                     mp_header_parameter_t *found) {
    const char *cursor = start;
    mp_header_parameter_t parameter;
    size_t length = strlen(name);
    while (mp_next_parameter(&cursor, end, &parameter) == 1) {
        if (mp_equal(parameter.name, parameter.name_length, name, length)) {
            *found = parameter;
            return true;
        }
    }
    return false;
}

/* HTTP media type names and parameter keys are case-insensitive. A boundary
 * must be an exact parameter, unique, 1..70 MIME bchars, with no trailing space.
 * MIME separators such as ':' require a quoted HTTP parameter value. */
static inline bool mp_form_data_boundary(const char *type, char *out,
                                         size_t capacity) {
    const char *end;
    if (!out || !capacity) return false;
    out[0] = 0;
    if (!mp_bounded_end(type, &end)) return false;
    const char *p = type;
    mp_skip_space(&p, end);
    const char *token = p;
    while (p < end && mp_token((unsigned char)*p)) ++p;
    if (!mp_equal(token, (size_t)(p - token), "multipart", 9) ||
        p == end || *p++ != '/') return false;
    token = p;
    while (p < end && mp_token((unsigned char)*p)) ++p;
    if (!mp_equal(token, (size_t)(p - token), "form-data", 9) ||
        !mp_parameters_valid(p, end)) return false;
    mp_header_parameter_t boundary;
    if (!mp_find_parameter(p, end, "boundary", &boundary) ||
        !mp_copy_parameter(&boundary, out, capacity, false)) return false;
    size_t n = strlen(out);
    bool valid = n > 0 && n <= 70 && out[n - 1] != ' ';
    for (size_t i = 0; valid && i < n; ++i) {
        unsigned char c = (unsigned char)out[i];
        valid = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') || strchr("'()+_,-./:=? ", c) != NULL;
    }
    if (!valid) out[0] = 0;
    return valid;
}

static inline bool mp_disposition_parameters(const char *headers,
                                             const char **start,
                                             const char **finish) {
    const char *end;
    if (!mp_bounded_end(headers, &end)) return false;
    bool found = false;
    for (const char *p = headers; p < end;) {
        const char *name = p;
        while (p < end && mp_token((unsigned char)*p)) ++p;
        size_t length = (size_t)(p - name);
        if (!length || p == end || *p++ != ':') return false;
        const char *value = p;
        while (p < end && *p != '\r' && *p != '\n') {
            unsigned char c = (unsigned char)*p++;
            if ((c < 32 && c != '\t') || c == 127) return false;
        }
        const char *value_end = p;
        if (p < end) {
            if (*p++ != '\r' || p == end || *p++ != '\n') return false;
        }
        if (!mp_equal(name, length, "Content-Disposition", 19)) continue;
        if (found) return false;
        found = true;
        mp_skip_space(&value, value_end);
        const char *token = value;
        while (value < value_end && mp_token((unsigned char)*value)) ++value;
        if (!mp_equal(token, (size_t)(value - token), "form-data", 9) ||
            !mp_parameters_valid(value, value_end)) return false;
        /* RFC 7578 does not use extended filename*. Reject it and name* so
         * consumers cannot disagree between encoded and ordinary names. */
        mp_header_parameter_t extended;
        if (mp_find_parameter(value, value_end, "name*", &extended) ||
            mp_find_parameter(value, value_end, "filename*", &extended)) return false;
        *start = value;
        *finish = value_end;
    }
    return found;
}

/* Compatibility entry point. Parameters are read only from one exact
 * Content-Disposition: form-data header, after validating its complete list. */
static inline bool mp_parameter(const char *headers, const char *name,
                                char *out, size_t capacity) {
    const char *start, *end;
    if (!out || !capacity) return false;
    out[0] = 0;
    if (!mp_disposition_parameters(headers, &start, &end)) return false;
    mp_header_parameter_t parameter;
    return mp_find_parameter(start, end, name, &parameter) &&
        mp_copy_parameter(&parameter, out, capacity,
                          mp_equal(name, strlen(name), "filename", 8));
}

/* File forms need to distinguish a missing filename from a malformed or
 * oversized one. Parse both fields once, rejecting the latter before storage. */
static inline bool mp_disposition(const char *headers, char *name,
                                  size_t name_capacity, char *filename,
                                  size_t filename_capacity, bool *have_filename) {
    const char *start, *end;
    if (!have_filename || !name || !name_capacity ||
        !filename || !filename_capacity) return false;
    name[0] = filename[0] = 0;
    *have_filename = false;
    if (!mp_disposition_parameters(headers, &start, &end)) return false;
    mp_header_parameter_t parameter;
    if (!mp_find_parameter(start, end, "name", &parameter) ||
        !mp_copy_parameter(&parameter, name, name_capacity, false) || !name[0])
        return false;
    if (mp_find_parameter(start, end, "filename", &parameter)) {
        if (!mp_copy_parameter(&parameter, filename, filename_capacity, true))
            return false;
        *have_filename = true;
    }
    return true;
}

