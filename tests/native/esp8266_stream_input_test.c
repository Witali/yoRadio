#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include "stream_input_buffer.h"

typedef struct { int unused; } http_stream_t;
typedef struct { uint8_t data[6144]; size_t size; } helix_codec_t;
typedef struct { uint32_t generation; uint64_t measured_bytes; } output_context_t;
static uint8_t s_work[1024], wire[20000];
static size_t wire_size, wire_pos, readable, receive_limit;
static unsigned receive_calls, cancel_after, metadata_calls;
static size_t last_metadata_size;
static uint32_t generation;
static int receive_error;
static int64_t now, clock_step;
static bool generation_current(uint32_t value) { return value == generation; }
static int64_t esp_timer_get_time(void) { now += clock_step; return now; }
static uint8_t *helix_codec_write_pointer(helix_codec_t *codec, size_t *capacity) {
    *capacity = sizeof(codec->data) - codec->size;
    return codec->data + codec->size;
}
static int helix_codec_buffer_commit(helix_codec_t *codec, size_t size) {
    assert(size <= sizeof(codec->data) - codec->size);
    codec->size += size;
    return 0;
}
static void parse_icy_title(size_t size) {
    ++metadata_calls; last_metadata_size = size;
}
static int stream_receive(http_stream_t *stream, uint8_t *destination, size_t size) {
    (void)stream;
    ++receive_calls;
    if (cancel_after && receive_calls == cancel_after) ++generation;
    if (wire_pos == wire_size) return 0;
    if (wire_pos == readable) { errno = receive_error; return -1; }
    if (size > readable - wire_pos) size = readable - wire_pos;
    if (size > receive_limit) size = receive_limit;
    memcpy(destination, wire + wire_pos, size);
    wire_pos += size;
    return (int)size;
}
#include "stream_input_refill.inc"

static void reset(size_t size) {
    wire_size = readable = size;
    wire_pos = 0; receive_limit = 1024;
    receive_calls = cancel_after = metadata_calls = 0;
    last_metadata_size = 0; generation = 1;
    now = clock_step = 0; receive_error = EAGAIN;
    for (size_t i = 0; i < size; ++i) wire[i] = (uint8_t)i;
}

static void test_fill_and_refill(void) {
    reset(10000);
    http_stream_t stream = {0};
    helix_codec_t codec = {0};
    output_context_t output = {1, 0};
    stream_icy_t icy = {0};
    assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_FULL);
    assert(codec.size == 6144 && wire_pos == 6144 && output.measured_bytes == 6144);
    assert(memcmp(codec.data, wire, 6144) == 0);
    /* A decoded frame frees space; refill exactly that space before the next. */
    memmove(codec.data, codec.data + 417, codec.size - 417); codec.size -= 417;
    assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_FULL);
    assert(codec.size == 6144 && memcmp(codec.data, wire + 417, 6144) == 0);
}

static void test_partial_network(void) {
    reset(10000); readable = 900; receive_limit = 73;
    http_stream_t stream = {0}; helix_codec_t codec = {0};
    output_context_t output = {1, 0}; stream_icy_t icy = {0};
    assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_AGAIN);
    assert(codec.size == 900);
    assert(!stream_prefill_ready(codec.size, 6144, false, 999999, 1000));
    assert(stream_prefill_ready(codec.size, 6144, false, 1000000, 1000));
    assert(stream_prefill_ready(codec.size, 6144, false, 0, 0));
    assert(stream_prefill_ready(6144, 6144, false, 0, 1000));
    assert(stream_prefill_ready(codec.size, 6144, true, 0, 1000));
    receive_error = ETIMEDOUT;
    assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_TIMEOUT);
    assert(codec.size == 900); /* Timeout must not destroy queued audio. */
    receive_error = EIO;
    assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_ERROR);
    wire_size = readable;
    assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_EOF);
    assert(codec.size == 900);
}

static void test_cancel_and_budget(void) {
    reset(10000); cancel_after = 2;
    http_stream_t stream = {0}; helix_codec_t codec = {0};
    output_context_t output = {1, 0}; stream_icy_t icy = {0};
    assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_CANCELLED);
    assert(codec.size == 1024); /* No stale commit after cancellation. */
    reset(10000); codec.size = 0; clock_step = 700;
    assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_YIELD);
    assert(codec.size == 2048 && receive_calls == 2);
}

static void test_icy_split_everywhere(void) {
    /* Includes zero-length metadata, truncated-to-scratch 4080-byte metadata,
     * and multiple boundaries per recv(). The audio queue must be identical. */
    for (size_t chunk = 1; chunk <= 1024; chunk += 17) {
        reset(0);
        size_t at = 0;
        memcpy(wire + at, "ABCDE", 5); at += 5;
        wire[at++] = 1; memset(wire + at, 'M', 16); at += 16;
        memcpy(wire + at, "FGHIJ", 5); at += 5;
        wire[at++] = 0;
        memcpy(wire + at, "KLMNO", 5); at += 5;
        wire[at++] = 255; memset(wire + at, 'X', 4080); at += 4080;
        memcpy(wire + at, "PQRST", 5); at += 5;
        wire_size = at; readable = 10; receive_limit = chunk;
        http_stream_t stream = {0}; helix_codec_t codec = {0};
        output_context_t output = {1, 0};
        stream_icy_t icy = {5, 5, 0, 0};
        assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_AGAIN);
        assert(codec.size == 5 && metadata_calls == 0);
        readable = wire_size;
        assert(stream_input_refill(&stream, &codec, &icy, &output) == STREAM_FILL_EOF);
        assert(codec.size == 20 && memcmp(codec.data, "ABCDEFGHIJKLMNOPQRST", 20) == 0);
        assert(metadata_calls == 2 && last_metadata_size == 1023);
        assert(output.measured_bytes == 20);
    }
}

int main(void) {
    test_fill_and_refill(); test_partial_network();
    test_cancel_and_budget(); test_icy_split_everywhere();
    puts("Stream input tests passed");
    return 0;
}
