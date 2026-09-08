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
