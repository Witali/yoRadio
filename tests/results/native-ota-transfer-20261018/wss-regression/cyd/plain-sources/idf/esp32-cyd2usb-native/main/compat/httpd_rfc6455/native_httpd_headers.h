/* SPDX-License-Identifier: Apache-2.0
 * Project RFC6455 checks against the matching ESP-IDF HTTPD private headers.
 * Included only in SHA-guarded generated HTTPD translation units. */
#pragma once
#include <stdbool.h>
#include <string.h>
#include <strings.h>
#include <stdio.h>
#include "http_parser.h"
#include "mbedtls/base64.h"

typedef struct {
    const char *cursor;
    size_t left;
    unsigned count;
} native_httpd_headers_t;
typedef struct {
    const char *name, *value, *end;
    size_t name_length;
} native_httpd_header_t;

static inline bool native_httpd_token_char(unsigned char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
        (c >= '0' && c <= '9') ||
        (c && strchr("!#$%&'*+-.^_`|~", c) != NULL);
}

static inline native_httpd_headers_t native_httpd_headers(httpd_req_t *req) {
    const struct httpd_req_aux *aux = req->aux;
    return (native_httpd_headers_t){aux->scratch, aux->scratch_cur_size,
                                   aux->req_hdrs_count};
}

/* 1 header, 0 end, -1 invalid storage. Header strings have been terminated by
 * the matching SDK parser, and all scans remain within its allocation. */
static inline int native_httpd_next_header(native_httpd_headers_t *headers,
                                           native_httpd_header_t *item) {
    if (!headers->count) return 0;
    if (!headers->cursor) return -1;
    while (headers->left && !*headers->cursor) {
        ++headers->cursor; --headers->left;
    }
    const char *start = headers->cursor;
    const char *end = memchr(start, 0, headers->left);
    if (!end) return -1;
    const char *colon = memchr(start, ':', (size_t)(end - start));
    if (!colon || colon == start) return -1;
    for (const char *p = start; p < colon; ++p)
        if (!native_httpd_token_char((unsigned char)*p)) return -1;
    *item = (native_httpd_header_t){start, colon + 1, end,
                                   (size_t)(colon - start)};
    size_t consumed = (size_t)(end - start) + 1;
    headers->cursor += consumed; headers->left -= consumed; --headers->count;
    return 1;
}

static inline bool native_httpd_header_is(const native_httpd_header_t *item,
                                         const char *field) {
    return item->name_length == strlen(field) &&
        !strncasecmp(item->name, field, item->name_length);
}

/* RFC2616 implied LWS also permits a CRLF followed by SP/HTAB. The SDK retains
 * folds inside a field value. A bare CR/LF is never consumed as whitespace. */
static inline void native_httpd_lws(const char **cursor, const char *end) {
    const char *p = *cursor;
    for (;;) {
        while (p < end && (*p == ' ' || *p == '\t')) ++p;
        if (end - p >= 3 && p[0] == '\r' && p[1] == '\n' &&
            (p[2] == ' ' || p[2] == '\t')) { p += 2; continue; }
        break;
    }
    *cursor = p;
}

static inline bool native_httpd_read_token(const char **cursor, const char *end) {
    const char *start = *cursor;
    while (*cursor < end && native_httpd_token_char((unsigned char)**cursor)) ++*cursor;
    return *cursor != start;
}

/* The SDK stores complete field:value strings separated by NULs. Use its real
 * req_hdrs_count and allocation bound; never reconstruct private ABI offsets. */
static inline bool native_httpd_header(httpd_req_t *req, const char *name,
                                       char *out, size_t capacity) {
    native_httpd_headers_t headers = native_httpd_headers(req);
    native_httpd_header_t item;
    unsigned matches = 0;
    if (!out || !capacity) return false;
    out[0] = 0;
    int result;
    while ((result = native_httpd_next_header(&headers, &item)) == 1) {
        if (native_httpd_header_is(&item, name)) {
            if (++matches != 1) return false;
            const char *p = item.value;
            size_t used = 0;
            bool space = false;
            while (p < item.end) {
                const char *before = p;
                native_httpd_lws(&p, item.end);
                space |= before != p;
                if (p == item.end) break;
                unsigned char c = (unsigned char)*p++;
                if (c < 33 || c > 126) return false;
                if (space && used) {
                    if (used + 1 >= capacity) return false;
                    out[used++] = ' ';
                }
                space = false;
                if (used + 1 >= capacity) return false;
                out[used++] = (char)c;
            }
            if (!used) return false;
            out[used] = 0;
        }
    }
    return result == 0 && matches == 1;
}

static inline bool native_httpd_header_token(httpd_req_t *req,
                                             const char *field, const char *token) {
    native_httpd_headers_t headers = native_httpd_headers(req);
    native_httpd_header_t item;
    bool found = false;
    unsigned count = 0;
    int result;
    while ((result = native_httpd_next_header(&headers, &item)) == 1) {
        if (native_httpd_header_is(&item, field)) {
            const char *p = item.value;
            while (p < item.end) {
                native_httpd_lws(&p, item.end);
                if (p == item.end) break;
                if (*p == ',') { ++p; continue; } /* RFC2616 #rule null item. */
                const char *start = p;
                if (!native_httpd_read_token(&p, item.end)) return false;
                const char *finish = p;
                ++count;
                bool candidate = (size_t)(finish - start) == strlen(token) &&
                    !strncasecmp(start, token, (size_t)(finish - start));
                /* Upgrade is a product list. Other protocol/version offers are
                 * valid, but websocket/version does not name bare websocket. */
                if (!strcasecmp(field, "Upgrade") && p < item.end && *p == '/') {
                    candidate = false;
                    ++p;
                    if (!native_httpd_read_token(&p, item.end)) return false;
                }
                found |= candidate;
                native_httpd_lws(&p, item.end);
                if (p < item.end && *p != ',') return false;
            }
        }
    }
    return result == 0 && count && found;
}

/* Compare each protocol token against earlier offers, including other header
 * lines. Values are case-sensitive. No request-sized token table is allocated. */
static inline bool native_httpd_protocol_unique(httpd_req_t *req,
                                                const char *value, size_t length) {
    native_httpd_headers_t headers = native_httpd_headers(req);
    native_httpd_header_t item;
    int result;
    while ((result = native_httpd_next_header(&headers, &item)) == 1) {
        if (!native_httpd_header_is(&item, "Sec-WebSocket-Protocol")) continue;
        const char *p = item.value;
        while (p < item.end) {
            native_httpd_lws(&p, item.end);
            if (p == item.end) break;
            if (*p == ',') { ++p; continue; }
            const char *start = p;
            if (!native_httpd_read_token(&p, item.end)) return false;
            if (start == value) return true;
            if ((size_t)(p - start) == length && !memcmp(start, value, length)) return false;
            native_httpd_lws(&p, item.end);
            if (p < item.end && *p != ',') return false;
        }
    }
    return false;
}

static inline bool native_httpd_optional_offers(httpd_req_t *req, bool extensions) {
    native_httpd_headers_t headers = native_httpd_headers(req);
    native_httpd_header_t item;
    bool present = false;
    unsigned count = 0;
    int result;
    while ((result = native_httpd_next_header(&headers, &item)) == 1) {
        if (!native_httpd_header_is(&item, extensions ? "Sec-WebSocket-Extensions" : "Sec-WebSocket-Protocol")) continue;
        present = true;
        const char *p = item.value;
        while (p < item.end) {
            native_httpd_lws(&p, item.end);
            if (p == item.end) break;
            if (*p == ',') { ++p; continue; }
            const char *start = p;
            if (!native_httpd_read_token(&p, item.end)) return false;
            ++count;
            if (!extensions && !native_httpd_protocol_unique(req, start, (size_t)(p - start))) return false;
            native_httpd_lws(&p, item.end);
            while (extensions && p < item.end && *p == ';') {
                ++p; native_httpd_lws(&p, item.end);
                if (!native_httpd_read_token(&p, item.end)) return false;
                native_httpd_lws(&p, item.end);
                if (p < item.end && *p == '=') {
                    ++p; native_httpd_lws(&p, item.end);
                    if (p < item.end && *p == '"') {
                        ++p; bool any = false;
                        while (p < item.end && *p != '"') {
                            unsigned char c = (unsigned char)*p++;
                            if (c == '\\') {
                                if (p == item.end) return false;
                                c = (unsigned char)*p++;
                            }
                            /* §9.1 requires the unescaped value itself to be
                             * token, even though quoted-string allows more. */
                            if (!native_httpd_token_char(c)) return false;
                            any = true;
                        }
                        if (!any || p == item.end || *p++ != '"') return false;
                    } else if (!native_httpd_read_token(&p, item.end)) return false;
                    native_httpd_lws(&p, item.end);
                }
            }
            if (p < item.end && *p != ',') return false;
        }
    }
    return result == 0 && (!present || count);
}

static inline bool native_httpd_authority(const char *host) {
    char url[264];
    int length = snprintf(url, sizeof(url), "http://%s/", host);
    if (length < 0 || (size_t)length >= sizeof(url)) return false;
    struct http_parser_url parsed;
    http_parser_url_init(&parsed);
    if (http_parser_parse_url(url, (size_t)length, 0, &parsed)) return false;
    unsigned allowed = (1U << UF_SCHEMA) | (1U << UF_HOST) | (1U << UF_PORT) | (1U << UF_PATH);
    return !(parsed.field_set & ~allowed) && parsed.field_data[UF_HOST].len &&
        parsed.field_data[UF_PATH].off == length - 1 && parsed.field_data[UF_PATH].len == 1;
}

static inline bool native_httpd_version(const char *version) {
    if (!*version || (version[0] == '0' && version[1])) return false;
    unsigned value = 0;
    for (const char *p = version; *p; ++p) {
        if (*p < '0' || *p > '9') return false;
        value = value * 10U + (unsigned)(*p - '0');
        if (value > 255) return false;
    }
    return true;
}

static inline esp_err_t native_httpd_handshake_error(httpd_req_t *req,
                                                    const char *status,
                                                    bool version) {
    if (version && httpd_resp_set_hdr(req, "Sec-WebSocket-Version", "13") != ESP_OK)
        return ESP_FAIL;
    (void)httpd_resp_send_custom_err(req, status, "Invalid WebSocket handshake");
    return ESP_FAIL;
}

static inline esp_err_t native_httpd_handshake_validate(httpd_req_t *req) {
    char host[256], version[4], key[25];
    uint8_t nonce[16]; size_t length = 0;
    if (!native_httpd_header(req, "Host", host, sizeof(host)) ||
        !native_httpd_header(req, "Sec-WebSocket-Version", version, sizeof(version)) ||
        !native_httpd_header(req, "Sec-WebSocket-Key", key, sizeof(key)) ||
        !native_httpd_header_token(req, "Connection", "upgrade") ||
        !native_httpd_header_token(req, "Upgrade", "websocket") ||
        !native_httpd_authority(host) || !native_httpd_version(version) ||
        !native_httpd_optional_offers(req, false) ||
        !native_httpd_optional_offers(req, true))
        return native_httpd_handshake_error(req, "400 Bad Request", false);
    if (strcmp(version, "13"))
        return native_httpd_handshake_error(req, "426 Upgrade Required", true);
    if (strlen(key) != 24 ||
        mbedtls_base64_decode(nonce, sizeof(nonce), &length,
                              (const unsigned char *)key, strlen(key)) != 0 ||
        length != sizeof(nonce))
        return native_httpd_handshake_error(req, "400 Bad Request", false);
    return ESP_OK;
}
