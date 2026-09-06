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

void http_chunk_decoder_init(http_chunk_decoder_t *decoder);
bool http_chunk_decode(http_chunk_decoder_t *decoder, uint8_t *buffer,
                       size_t input_size, size_t *output_size);
bool http_chunk_decoder_finished(const http_chunk_decoder_t *decoder);
