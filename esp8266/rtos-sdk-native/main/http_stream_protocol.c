#include "http_stream_protocol.h"

#include <ctype.h>
#include <stdlib.h>
#include <string.h>

bool http_stream_idle_expired(uint32_t now, uint32_t last, uint32_t timeout) {
    return (uint32_t)(now - last) >= timeout;
}

#ifdef _MSC_VER
#define strcasecmp _stricmp
#define strncasecmp _strnicmp
#else
#include <strings.h>
#endif

enum {
    RESPONSE_STATUS = 1, RESPONSE_DONE = 2, RESPONSE_CR = 4,
    RESPONSE_LINE = 8, RESPONSE_TRANSFER = 16, RESPONSE_CHUNKED = 32,
    RESPONSE_UNSUPPORTED = 64, RESPONSE_ERROR = 128,
};

void http_response_header_init(http_response_header_t *parser) {
    memset(parser, 0, sizeof(*parser));
}

static bool response_u32(const char *value, uint32_t *result) {
    if (!*value) return false;
    uint32_t parsed = 0;
    for (; *value; ++value) {
        if (*value < '0' || *value > '9') return false;
        unsigned digit = (unsigned)(*value - '0');
        if (parsed > (UINT32_MAX - digit) / 10U) return false;
        parsed = parsed * 10U + digit;
    }
    *result = parsed;
    return true;
}

static bool response_status(http_response_header_t *parser, const char *line) {
    size_t length = parser->line_bytes, start;
    if (length >= 7U && memcmp(line, "ICY ", 4) == 0) start = 4;
    else if (length >= 12U && memcmp(line, "HTTP/1.", 7) == 0 &&
             line[7] >= '0' && line[7] <= '9' && line[8] == ' ') start = 9;
    else return false;
    if (line[start] < '1' || line[start] > '5' ||
        line[start + 1] < '0' || line[start + 1] > '9' ||
        line[start + 2] < '0' || line[start + 2] > '9' ||
        (length > start + 3U && line[start + 3] != ' ')) return false;
    parser->status = (uint16_t)((line[start] - '0') * 100 +
        (line[start + 1] - '0') * 10 + line[start + 2] - '0');
    parser->flags |= RESPONSE_STATUS;
    return true;
}

static bool response_field(http_response_header_t *parser, char *line,
                            char *redirect, size_t redirect_capacity) {
    char *colon = strchr(line, ':');
    if (!colon || colon == line) return false;
    for (char *cursor = line; cursor < colon; ++cursor) {
        unsigned char c = (unsigned char)*cursor;
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || strchr("!#$%&'*+-.^_`|~", c)))
            return false;
    }
    *colon++ = '\0';
    while (*colon == ' ' || *colon == '\t') ++colon;
    char *end = colon + strlen(colon);
    while (end > colon && (end[-1] == ' ' || end[-1] == '\t')) --end;
    *end = '\0';
    if (strcasecmp(line, "icy-metaint") == 0)
        return response_u32(colon, &parser->metadata_interval);
    if (strcasecmp(line, "icy-br") == 0)
        return response_u32(colon, &parser->bitrate);
    if (strcasecmp(line, "location") == 0) {
        size_t size = (size_t)(end - colon);
        if (size >= redirect_capacity) return false;
        memcpy(redirect, colon, size + 1U);
    } else if (strcasecmp(line, "transfer-encoding") == 0) {
        /* Only one chunked coding is implemented, not gzip or stacked codings. */
        if ((parser->flags & RESPONSE_TRANSFER) ||
            !http_stream_header_has_token(colon, "chunked") ||
            strcasecmp(colon, "chunked") != 0)
            parser->flags |= RESPONSE_UNSUPPORTED;
        else parser->flags |= RESPONSE_CHUNKED;
        parser->flags |= RESPONSE_TRANSFER;
    }
    return true;
}

int http_response_header_feed(http_response_header_t *parser,
    uint8_t *line, size_t line_capacity, const uint8_t *input, size_t length,
    size_t *consumed, char *redirect, size_t redirect_capacity) {
    if (consumed) *consumed = 0;
    if (!parser || !line || line_capacity < 2U || (!input && length) ||
        !consumed || !redirect || !redirect_capacity || parser->line_bytes >= line_capacity)
        return HTTP_RESPONSE_HEADER_ERROR;
    if (parser->flags & RESPONSE_ERROR) return HTTP_RESPONSE_HEADER_ERROR;
    if (parser->flags & RESPONSE_DONE) return HTTP_RESPONSE_HEADER_DONE;
    for (size_t index = 0; index < length; ++index) {
        unsigned char c = input[index];
        *consumed = index + 1U;
        if (parser->total_bytes >= HTTP_RESPONSE_HEADER_MAX_BYTES) goto invalid;
        ++parser->total_bytes;
        if (parser->flags & RESPONSE_CR) {
            if (c != '\n') goto invalid;
            parser->flags &= (uint8_t)~RESPONSE_CR;
        } else if (c == '\r') {
            parser->flags |= RESPONSE_CR;
            continue;
        }
        if (c == '\n') {
            line[parser->line_bytes] = '\0';
            if (!(parser->flags & RESPONSE_STATUS)) {
                if (!response_status(parser, (const char *)line)) goto invalid;
                parser->line_bytes = 0;
            } else if (!parser->line_bytes || (parser->flags & RESPONSE_LINE)) {
                if (parser->line_bytes &&
                    !response_field(parser, (char *)line, redirect, redirect_capacity)) goto invalid;
                parser->line_bytes = 0;
                parser->flags |= RESPONSE_DONE;
                return HTTP_RESPONSE_HEADER_DONE;
            } else parser->flags |= RESPONSE_LINE;
            continue;
        }
        if (!c || c == 127U || (c < 32U && c != '\t')) goto invalid;
        if (parser->flags & RESPONSE_LINE) {
            parser->flags &= (uint8_t)~RESPONSE_LINE;
            if (c == ' ' || c == '\t') {
                /* RFC 9112 5.2: unfold before field interpretation. */
                c = ' ';
            } else {
                /* A following recv may have overwritten the prior terminator
                 * at line_bytes. c is already saved before restoring it. */
                line[parser->line_bytes] = '\0';
                if (!response_field(parser, (char *)line, redirect, redirect_capacity)) goto invalid;
                parser->line_bytes = 0;
            }
        }
        if (parser->line_bytes >= HTTP_RESPONSE_HEADER_MAX_LINE ||
            parser->line_bytes >= line_capacity - 1U) goto invalid;
        line[parser->line_bytes++] = c;
    }
    return HTTP_RESPONSE_HEADER_MORE;
invalid:
    parser->flags |= RESPONSE_ERROR;
    return HTTP_RESPONSE_HEADER_ERROR;
}

bool http_response_header_finished(const http_response_header_t *parser) {
    return parser && (parser->flags & (RESPONSE_DONE | RESPONSE_ERROR)) == RESPONSE_DONE;
}
bool http_response_header_chunked(const http_response_header_t *parser) {
    return (parser->flags & RESPONSE_CHUNKED) != 0;
}
bool http_response_header_unsupported_transfer(const http_response_header_t *parser) {
    return (parser->flags & RESPONSE_UNSUPPORTED) != 0;
}

static bool append_bytes(char *output, size_t output_size, size_t *used,
                         const char *data, size_t length) {
    if (!output || !used || !data || *used >= output_size ||
        length >= output_size - *used)
        return false;
    memcpy(output + *used, data, length);
    *used += length;
    output[*used] = '\0';
    return true;
}

bool http_stream_parse_url(const char *url, http_stream_url_t *parts,
                           char *host, size_t host_size) {
    if (!url || !parts || !host || host_size < 2U ||
        strncmp(url, "http://", 7) != 0)
        return false;
    const char *authority = url + 7;
    const char *authority_end = authority + strcspn(authority, "/?#");
    if (authority_end == authority) return false;

    const char *colon = NULL;
    for (const char *cursor = authority; cursor < authority_end; ++cursor) {
        if (*cursor == '@' || *cursor == '[' || *cursor == ']') return false;
        if (*cursor == ':') colon = cursor;
    }
    const char *host_end = colon ? colon : authority_end;
    size_t host_length = (size_t)(host_end - authority);
    if (!host_length || host_length >= host_size) return false;
    memcpy(host, authority, host_length);
    host[host_length] = '\0';

    unsigned long port = 80;
    if (colon) {
        char *tail = NULL;
        port = strtoul(colon + 1, &tail, 10);
        if (tail != authority_end || !port || port > 65535UL) return false;
    }

    const char *fragment = strchr(authority_end, '#');
    const char *url_end = url + strlen(url);
    const char *target_end = fragment ? fragment : url_end;
    const char *target = authority_end;
    if (target == target_end || *target == '#') target = "/";

    parts->authority = authority;
    parts->authority_length = (size_t)(authority_end - authority);
    parts->target = target;
    parts->query_only = target == authority_end && *target == '?';
    parts->target_length = target == authority_end
                               ? (size_t)(target_end - target)
                               : 1U;
    parts->port = (uint16_t)port;
    return true;
}

bool http_stream_resolve_redirect(const char *base_url,
                                  const char *location, char *output,
                                  size_t output_size) {
    if (!base_url || !location || !output || !output_size) return false;
    while (*location == ' ' || *location == '\t') ++location;
    size_t location_length = strlen(location);
    while (location_length &&
           (location[location_length - 1] == ' ' ||
            location[location_length - 1] == '\t'))
        --location_length;
    if (!location_length || memchr(location, '\r', location_length) ||
        memchr(location, '\n', location_length))
        return false;

    size_t used = 0;
    output[0] = '\0';
    if (location_length >= 7U &&
        strncasecmp(location, "http://", 7U) == 0)
        return append_bytes(output, output_size, &used, location,
                            location_length);
    if (location_length >= 8U &&
        strncasecmp(location, "https://", 8U) == 0)
        return false;
    if (location_length >= 2U && location[0] == '/' && location[1] == '/') {
        return append_bytes(output, output_size, &used, "http:", 5U) &&
               append_bytes(output, output_size, &used, location,
                            location_length);
    }

    http_stream_url_t base;
    char host[96];
    if (!http_stream_parse_url(base_url, &base, host, sizeof(host)))
        return false;
    if (!append_bytes(output, output_size, &used, "http://", 7U) ||
        !append_bytes(output, output_size, &used, base.authority,
                      base.authority_length))
        return false;
    if (location[0] == '/')
        return append_bytes(output, output_size, &used, location,
                            location_length);

    const char *base_target = base.target;
    size_t base_path_length = base.target_length;
    const char *query = memchr(base_target, '?', base_path_length);
    if (query) base_path_length = (size_t)(query - base_target);
    if (location[0] == '?') {
        return append_bytes(output, output_size, &used, base_target,
                            base_path_length) &&
               append_bytes(output, output_size, &used, location,
                            location_length);
    }
    const char *last_slash = NULL;
    for (size_t index = 0; index < base_path_length; ++index)
        if (base_target[index] == '/') last_slash = base_target + index;
    size_t directory_length = last_slash
                                  ? (size_t)(last_slash - base_target) + 1U
                                  : 1U;
    return append_bytes(output, output_size, &used, base_target,
                        directory_length) &&
           append_bytes(output, output_size, &used, location,
                        location_length);
}

bool http_stream_header_has_token(const char *value, const char *token) {
    if (!value || !token || !token[0]) return false;
    size_t token_length = strlen(token);
    const char *cursor = value;
    while (*cursor) {
        while (*cursor == ' ' || *cursor == '\t' || *cursor == ',') ++cursor;
        const char *end = cursor;
        while (*end && *end != ',') ++end;
        const char *trimmed = end;
        while (trimmed > cursor &&
               (trimmed[-1] == ' ' || trimmed[-1] == '\t'))
            --trimmed;
        if ((size_t)(trimmed - cursor) == token_length &&
            strncasecmp(cursor, token, token_length) == 0)
            return true;
        cursor = end;
    }
    return false;
}

void http_chunk_decoder_init(http_chunk_decoder_t *decoder) {
    memset(decoder, 0, sizeof(*decoder));
    decoder->state = HTTP_CHUNK_SIZE;
}

static bool finish_chunk_size(http_chunk_decoder_t *decoder) {
    decoder->line[decoder->line_length] = '\0';
    char *extension = strchr(decoder->line, ';');
    if (extension) *extension = '\0';
    if (!decoder->line[0]) return false;
    for (const char *cursor = decoder->line; *cursor; ++cursor)
        if (!isxdigit((unsigned char)*cursor)) return false;
    char *tail = NULL;
    unsigned long size = strtoul(decoder->line, &tail, 16);
    if (!tail || *tail || size > UINT32_MAX) return false;
    decoder->line_length = 0;
    decoder->remaining = (uint32_t)size;
    decoder->state = size ? HTTP_CHUNK_DATA : HTTP_CHUNK_TRAILERS;
    decoder->trailer_has_data = false;
    return true;
}

bool http_chunk_decode(http_chunk_decoder_t *decoder, uint8_t *buffer,
                       size_t input_size, size_t *output_size) {
    if (!decoder || (!buffer && input_size) || !output_size) return false;
    size_t input = 0;
    size_t output = 0;
    while (input < input_size && decoder->state != HTTP_CHUNK_DONE &&
           decoder->state != HTTP_CHUNK_ERROR) {
        switch (decoder->state) {
            case HTTP_CHUNK_SIZE: {
                uint8_t byte = buffer[input++];
                if (byte == '\n') {
                    if (!finish_chunk_size(decoder))
                        decoder->state = HTTP_CHUNK_ERROR;
                } else if (byte != '\r') {
                    if (decoder->line_length + 1U >= sizeof(decoder->line))
                        decoder->state = HTTP_CHUNK_ERROR;
                    else
                        decoder->line[decoder->line_length++] = (char)byte;
                }
                break;
            }
            case HTTP_CHUNK_DATA: {
                size_t count = input_size - input;
                if (count > decoder->remaining) count = decoder->remaining;
                memmove(buffer + output, buffer + input, count);
                output += count;
                input += count;
                decoder->remaining -= (uint32_t)count;
                if (!decoder->remaining) decoder->state = HTTP_CHUNK_DATA_CR;
                break;
            }
            case HTTP_CHUNK_DATA_CR:
                decoder->state = buffer[input++] == '\r'
                                     ? HTTP_CHUNK_DATA_LF
                                     : HTTP_CHUNK_ERROR;
                break;
            case HTTP_CHUNK_DATA_LF:
                decoder->state = buffer[input++] == '\n'
                                     ? HTTP_CHUNK_SIZE
                                     : HTTP_CHUNK_ERROR;
                break;
            case HTTP_CHUNK_TRAILERS: {
                uint8_t byte = buffer[input++];
                if (byte == '\n') {
                    if (!decoder->trailer_has_data)
                        decoder->state = HTTP_CHUNK_DONE;
                    decoder->trailer_has_data = false;
                } else if (byte != '\r') {
                    decoder->trailer_has_data = true;
                }
                break;
            }
            default:
                decoder->state = HTTP_CHUNK_ERROR;
                break;
        }
    }
    *output_size = output;
    return decoder->state != HTTP_CHUNK_ERROR;
}

bool http_chunk_decoder_finished(const http_chunk_decoder_t *decoder) {
    return decoder && decoder->state == HTTP_CHUNK_DONE;
}
