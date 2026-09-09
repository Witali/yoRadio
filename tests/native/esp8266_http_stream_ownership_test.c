/* Real opener/header/chunk/URL parsers; only transport/time are mocked.
 * A closed fd is immediately reused by a simulated WebUI client. */
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef _WIN32
#include <strings.h>
#else
#define strcasecmp _stricmp
#endif
#include "http_stream_protocol.h"
#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "line %d: %s\n", __LINE__, #expr); return 1; \
} } while (0)
#define AUDIO_URL_BYTES 512U
#define HTTP_MAX_REDIRECTS 3U
#define HTTP_HEADER_TIMEOUT_MS 10000U
#define YORADIO_ESP8266_AUDIO_PROFILE 0
#define ESP_LOGI(...) ((void)0)
#define pdMS_TO_TICKS(value) (value)
typedef uint32_t TickType_t;
/* STREAM_TYPE */
static uint8_t s_work[1024];
static char s_host[96];
enum { FREE_FD, AUDIO_FD, WEB_FD };
static int owners[16], closes, connects, closed_web, last_fd;
static bool reuse_closed, fail_send;
static unsigned fail_connect;
static int64_t clock_us;
static const char *replies[4];
static size_t read_offset, read_step;
static unsigned read_cost_us;
static const char *reply;
static TickType_t xTaskGetTickCount(void) { return (TickType_t)(clock_us / 1000); }
static int64_t esp_timer_get_time(void) { return clock_us; }
static void vTaskDelay(unsigned ticks) { clock_us += (int64_t)ticks * 1000; }
static bool parse_http_url(const char *url, http_stream_url_t *parts) {
    return http_stream_parse_url(url, parts, s_host, sizeof(s_host));
}
static int connect_http(uint16_t port) {
    (void)port;
    ++connects;
    if ((unsigned)connects == fail_connect) { errno = ECONNREFUSED; return -1; }
    reply = replies[(connects - 1) % 4]; read_offset = 0;
    for (int fd = 3; fd < 16; ++fd) {
        if (owners[fd] == FREE_FD) { owners[fd] = AUDIO_FD; last_fd = fd; return fd; }
    }
    errno = EMFILE; return -1;
}
static int mock_close(int fd) {
    if (fd < 0 || fd >= 16 || owners[fd] == FREE_FD) { errno = EBADF; return -1; }
    ++closes;
    if (owners[fd] == WEB_FD) ++closed_web;
    owners[fd] = reuse_closed ? WEB_FD : FREE_FD;
    /* close may alter errno; protocol errors must still return EPROTO. */
    errno = EIO; return 0;
}
static int mock_recv(int fd, void *destination, size_t capacity, int flags) {
    (void)flags;
    if (fd < 0 || fd >= 16 || owners[fd] != AUDIO_FD) { errno = EBADF; return -1; }
    if (!reply) { errno = EAGAIN; return -1; }
    size_t remaining = strlen(reply) - read_offset;
    size_t size = remaining < capacity ? remaining : capacity;
    if (read_step && size > read_step) size = read_step;
    memcpy(destination, reply + read_offset, size); read_offset += size;
    clock_us += read_cost_us;
    return (int)size;
}
static bool send_all(int fd, const char *text) {
    (void)fd; (void)text;
    if (fail_send) errno = ENOMEM;
    return !fail_send;
}
static bool send_all_bytes(int fd, const char *text, size_t size) {
    (void)size; return send_all(fd, text);
}
#define close mock_close
#define recv mock_recv
/* PARSER_IMPLEMENTATION */
/* OPEN_IMPLEMENTATION */
static void caller_cleanup(http_stream_t stream) {
    /* CALLER_CLEANUP */
}
static void reset(void) {
    memset(owners, 0, sizeof(owners));
    for (size_t i = 0; i < sizeof(replies)/sizeof(replies[0]); ++i) replies[i] = NULL;
    closes = connects = closed_web = 0; last_fd = -1;
    fail_connect = 0; fail_send = false; reuse_closed = true;
    clock_us = 0; read_step = 0; read_cost_us = 0; errno = 0;
}
static http_stream_t empty_stream(void) {
    http_stream_t stream;
    memset(&stream, 0, sizeof(stream)); stream.socket = -1; return stream;
}
static int invalid_chunk(bool retry) {
    reset();
    replies[0] = "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\nZ\r\nbad\r\n";
    char url[AUDIO_URL_BYTES] = "http://radio.invalid/live";
    http_stream_t stream = empty_stream();
    CHECK(open_http_stream(url, &stream) == -9);
    CHECK(errno == EPROTO && closes == 1 && owners[last_fd] == WEB_FD);
    if (retry) {
        fail_connect = 2; CHECK(open_http_stream(url, &stream) == -2);
    }
    /* Same cleanup used after failed retries or cancellation. */
    caller_cleanup(stream);
    CHECK(closed_web == 0 && closes == 1);
    CHECK(stream.socket == -1); return 0;
}
static int successful_retry(void) {
    reset();
    replies[0] = "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\nZ\r\n";
    replies[1] = "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nIcy-Br: 128\r\n\r\n3\r\nabc\r\n0\r\n\r\n";
    char url[AUDIO_URL_BYTES] = "http://radio.invalid/live";
    http_stream_t stream = empty_stream();
    CHECK(open_http_stream(url, &stream) == -9);
    int web_fd = last_fd;
    CHECK(open_http_stream(url, &stream) == 0);
    CHECK(stream.socket != web_fd && owners[stream.socket] == AUDIO_FD);
    CHECK(stream.body_size == 3 && memcmp(s_work, "abc", 3) == 0);
    CHECK(stream.advertised_bitrate == 128 && http_chunk_decoder_finished(&stream.chunk_decoder));
    caller_cleanup(stream);
    CHECK(closes == 2 && closed_web == 0 && owners[web_fd] == WEB_FD);
    return 0;
}
static int open_cases(void) {
    static const struct { const char *reply; int result; } cases[] = {
        {"HTTP/1.1 200 OK\r\nTransfer-Encoding: gzip\r\n\r\n", -9},
        {"HTTP/1.1 404 Not Found\r\n\r\n", -6},
        {"HTTP/1.1 200 OK\r\n", -4},
        {NULL, -4}, /* Header timeout. */
        {"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n3\r\nabcX", -9},
        {"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n3", 0}, /* Incomplete, not invalid. */
        {"HTTP/1.1 200 OK\r\n\r\nabc", 0},
    };
    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        reset(); replies[0] = cases[i].reply;
        char url[AUDIO_URL_BYTES] = "http://radio.invalid/live";
        http_stream_t stream = empty_stream();
        CHECK(open_http_stream(url, &stream) == cases[i].result);
        if (cases[i].result == -4)
            CHECK(errno == (cases[i].reply ? ECONNRESET : ETIMEDOUT));
        CHECK(stream.socket == (cases[i].result == 0 ? last_fd : -1));
        caller_cleanup(stream);
        CHECK(closes == 1 && closed_web == 0);
    }
    reset(); fail_send = true;
    char url[AUDIO_URL_BYTES] = "http://radio.invalid/live";
    http_stream_t stream = empty_stream();
    CHECK(open_http_stream(url, &stream) == -3 && stream.socket == -1);
    CHECK(errno == ENOMEM); /* close() must not hide the allocation failure. */
    caller_cleanup(stream); CHECK(closes == 1 && closed_web == 0);

    reset(); read_step = 1;
    replies[0] = "HTTP/1.1 302 Found\r\nLocation: /next\r\n\r\n";
    replies[1] = "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n";
    stream = empty_stream();
    CHECK(open_http_stream(url, &stream) == 0 && connects == 2 && closes == 1);
    CHECK(strcmp(url, "http://radio.invalid/next") == 0);
    CHECK(stream.socket == last_fd && stream.chunked && stream.body_size == 0);
    caller_cleanup(stream); CHECK(closes == 2 && closed_web == 0);
    return 0;
}
static int wide_headers(void) {
    char wire[8192];
    size_t used = (size_t)snprintf(wire, sizeof(wire), "HTTP/1.1 200 OK\r\n");
    for (unsigned n = 0; n < 60; ++n)
        used += (size_t)snprintf(wire + used, sizeof(wire) - used,
            "X-Icy-Description-%u: harmless aggregate padding for a long station response\r\n", n);
    used += (size_t)snprintf(wire + used, sizeof(wire) - used,
        "Icy-Br: 56\r\nIcy-Metaint: 4096\r\n\r\nOggSbody");
    CHECK(used > sizeof(s_work) && used < sizeof(wire));
    reset(); replies[0] = wire;
    char url[AUDIO_URL_BYTES] = "http://radio.invalid/opus.opus";
    http_stream_t stream = empty_stream();
    CHECK(open_http_stream(url, &stream) == 0);
    CHECK(stream.advertised_bitrate == 56 && stream.metadata_interval == 4096);
    CHECK(stream.body_size == 8 && !memcmp(s_work, "OggSbody", 8));
    caller_cleanup(stream); CHECK(closes == 1 && !closed_web);
    /* A sender cannot defeat the overall deadline by staying readable. */
    reset(); replies[0] = wire; read_step = 1; read_cost_us = 1000000;
    stream = empty_stream();
    CHECK(open_http_stream(url, &stream) == -4 && errno == ETIMEDOUT);
    caller_cleanup(stream); CHECK(closes == 1 && !closed_web);
    return 0;
}
int main(void) {
    if (invalid_chunk(true) || invalid_chunk(false) || successful_retry() || open_cases() || wide_headers()) return 1;
    puts("HTTP stream ownership tests passed"); return 0;
}
