#pragma once
#include <stdbool.h>
#include "esp_http_client.h"

// One instance per opened stream connection; never reuse after a failure.
typedef struct {
    bool failed;
} stream_http_reader_t;

// Close on a fatal error, preserve valid partial bytes, then report the failure
// on the next call without entering TLS again. Receive timeouts stay retryable.
int stream_http_read(stream_http_reader_t *reader, esp_http_client_handle_t client,
                     char *buffer, int length);
