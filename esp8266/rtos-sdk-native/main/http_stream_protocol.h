#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    const char *authority;
    size_t authority_length;
    const char *target;
    size_t target_length;
    bool query_only;
    uint16_t port;
} http_stream_url_t;

typedef enum {
    HTTP_CHUNK_SIZE = 0,
    HTTP_CHUNK_DATA,
    HTTP_CHUNK_DATA_CR,
    HTTP_CHUNK_DATA_LF,
    HTTP_CHUNK_TRAILERS,
    HTTP_CHUNK_DONE,
    HTTP_CHUNK_ERROR,
} http_chunk_state_t;

typedef struct {
    http_chunk_state_t state;
    uint32_t remaining;
    uint8_t line_length;
    bool trailer_has_data;
    char line[24];
} http_chunk_decoder_t;

bool http_stream_parse_url(const char *url, http_stream_url_t *parts,
                           char *host, size_t host_size);
bool http_stream_resolve_redirect(const char *base_url,
                                  const char *location, char *output,
                                  size_t output_size);
bool http_stream_header_has_token(const char *value, const char *token);

#define HTTP_RESPONSE_HEADER_MAX_BYTES 16384U
#define HTTP_RESPONSE_HEADER_MAX_LINE 1023U
enum { HTTP_RESPONSE_HEADER_ERROR = -1, HTTP_RESPONSE_HEADER_MORE = 0,
       HTTP_RESPONSE_HEADER_DONE = 1 };
/* No embedded buffer/allocation: the audio owner lends its existing scratch. */
typedef struct {
    uint32_t metadata_interval, bitrate;
    uint16_t total_bytes, line_bytes, status;
    uint8_t flags;
} http_response_header_t;

void http_response_header_init(http_response_header_t *parser);
/* Input may start at line + parser->line_bytes, so recv appends directly into
 * the SAME scratch. feed compacts/unfolds behind its read cursor. DONE consumes
 * exactly the final LF; following body bytes are untouched. The caller sets
 * redirect[0] to NUL initially and retains it across calls. Logical field lines
 * (including unfolded continuations) have a 1023-octet cap excluding CR/LF;
 * aggregate wire headers, including status/delimiters, have a 16-KiB cap. */
int http_response_header_feed(http_response_header_t *parser,
    uint8_t *line, size_t line_capacity, const uint8_t *input, size_t length,
    size_t *consumed, char *redirect, size_t redirect_capacity);
bool http_response_header_finished(const http_response_header_t *parser);
bool http_response_header_chunked(const http_response_header_t *parser);
bool http_response_header_unsupported_transfer(const http_response_header_t *parser);

void http_chunk_decoder_init(http_chunk_decoder_t *decoder);
bool http_chunk_decode(http_chunk_decoder_t *decoder, uint8_t *buffer,
                       size_t input_size, size_t *output_size);
bool http_chunk_decoder_finished(const http_chunk_decoder_t *decoder);

/* Monotonic 32-bit ticks, including a single counter wrap. All arguments
 * use the same tick unit; callers convert milliseconds with their OS. */
bool http_stream_idle_expired(uint32_t now, uint32_t last, uint32_t timeout);
