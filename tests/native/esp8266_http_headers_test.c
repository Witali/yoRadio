#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "http_stream_protocol.h"

_Static_assert(sizeof(http_response_header_t) == 16, "Header state must stay compact");
typedef struct {
    http_response_header_t parser;
    char redirect[512];
    int result;
} parsed_t;

/* Emulate production recv's exact aliasing: append to the current logical
 * line, then reuse the same 1-KiB buffer for every following field and body. */
static parsed_t parse(const uint8_t *wire, size_t length, size_t step, size_t split) {
    struct { uint32_t before; uint8_t bytes[1024]; uint32_t after; } scratch;
    scratch.before = scratch.after = 0x5a3917ceU;
    memset(scratch.bytes, 0xcc, sizeof(scratch.bytes));
    parsed_t parsed;
    memset(&parsed, 0, sizeof(parsed));
    http_response_header_init(&parsed.parser);
    size_t offset = 0;
    while (offset < length && parsed.result == HTTP_RESPONSE_HEADER_MORE) {
        size_t start = parsed.parser.line_bytes;
        size_t received = length - offset;
        if (received > sizeof(scratch.bytes) - start) received = sizeof(scratch.bytes) - start;
        if (step && received > step) received = step;
        if (offset < split && received > split - offset) received = split - offset;
        assert(received > 0);
        memcpy(scratch.bytes + start, wire + offset, received);
        size_t consumed = SIZE_MAX;
        parsed.result = http_response_header_feed(&parsed.parser, scratch.bytes,
            sizeof(scratch.bytes), scratch.bytes + start, received, &consumed,
            parsed.redirect, sizeof(parsed.redirect));
        assert(consumed <= received);
        if (parsed.result == HTTP_RESPONSE_HEADER_DONE) {
            assert(parsed.parser.total_bytes == offset + consumed);
            assert(!memcmp(scratch.bytes + start + consumed, wire + offset + consumed,
                           received - consumed));
            memmove(scratch.bytes, scratch.bytes + start + consumed, received - consumed);
            assert(!memcmp(scratch.bytes, wire + offset + consumed, received - consumed));
        } else if (parsed.result == HTTP_RESPONSE_HEADER_MORE) assert(consumed == received);
        offset += consumed;
        assert(scratch.before == 0x5a3917ceU && scratch.after == 0x5a3917ceU);
    }
    assert(http_response_header_finished(&parsed.parser) == (parsed.result == HTTP_RESPONSE_HEADER_DONE));
    if (parsed.result != HTTP_RESPONSE_HEADER_MORE) {
        size_t consumed = SIZE_MAX;
        assert(http_response_header_feed(&parsed.parser, scratch.bytes, sizeof(scratch.bytes),
            (const uint8_t *)"x", 1, &consumed, parsed.redirect, sizeof(parsed.redirect)) == parsed.result);
        assert(consumed == 0); // terminal states do not consume body/error recovery data
    }
    return parsed;
}

static void valid_splits(void) {
    static const uint8_t wire[] = "HTTP/1.1 200 OK\r\nServer: test\r\n"
        "iCy-MeTaInT: 4096 \t\r\nICY-BR: 56\r\nicy-br: 56\r\n"
        "Location: /opus.opus?quality=high\r\nTransfer-Encoding:\r\n\tchunked\r\n"
        "X-Description: first\r\n second\r\n\tthird\r\n\r\nOggS\0\xff\r\n";
    for (size_t split = 0; split < sizeof(wire); ++split) {
        parsed_t p = parse(wire, sizeof(wire) - 1, 0, split);
        assert(p.result == HTTP_RESPONSE_HEADER_DONE && p.parser.status == 200);
        assert(p.parser.metadata_interval == 4096 && p.parser.bitrate == 56);
        assert(!strcmp(p.redirect, "/opus.opus?quality=high"));
        assert(http_response_header_chunked(&p.parser));
        assert(!http_response_header_unsupported_transfer(&p.parser));
    }
    for (size_t step = 1; step <= sizeof(wire); ++step)
        assert(parse(wire, sizeof(wire) - 1, step, 0).result == HTTP_RESPONSE_HEADER_DONE);
    static const uint8_t icy[] = "ICY 200 OK\nicy-br:\n\t24\n\n\0\xff";
    parsed_t p = parse(icy, sizeof(icy) - 1, 1, 0);
    assert(p.result == HTTP_RESPONSE_HEADER_DONE && p.parser.status == 200 && p.parser.bitrate == 24);
    assert(!http_response_header_chunked(&p.parser));
    const char *redirect = "HTTP/1.0 302 Found\r\nLocation: ../new\r\n\r\n";
    p = parse((const uint8_t *)redirect, strlen(redirect), 1, 0);
    assert(p.result == HTTP_RESPONSE_HEADER_DONE && p.parser.status == 302 && !strcmp(p.redirect, "../new"));
    // Every incomplete prefix, including the terminal CR, is incomplete at EOF.
    const char *minimal = "HTTP/1.1 200 OK\r\nIcy-Br: 24\r\n\r\n";
    for (size_t size = 0; size < strlen(minimal); ++size)
        assert(parse((const uint8_t *)minimal, size, 1, 0).result == HTTP_RESPONSE_HEADER_MORE);
}

static void invalid_cases(void) {
    const char *invalid[] = {
        "garbage 200 OK\r\n\r\n", "HTTP/1.1 2000 bad\r\n\r\n", "ICY 99\n\n",
        "HTTP/1.1 200 OK\rX", "HTTP/1.1 200 OK\nBad Header: x\n\n",
        "HTTP/1.1 200 OK\n: x\n\n", "HTTP/1.1 200 OK\nMissing-Colon\n\n",
        "HTTP/1.1 200 OK\n orphan continuation\n\n",
        "HTTP/1.1 200 OK\nIcy-Metaint: -1\n\n", "HTTP/1.1 200 OK\nIcy-Br: 56x\n\n",
        "HTTP/1.1 200 OK\nIcy-Br: 4294967296\n\n", "HTTP/1.1 200 OK\nIcy-Br:\n\n",
        "HTTP/1.1 200 OK\nX: bad\x01value\n\n",
    };
    for (size_t i = 0; i < sizeof(invalid) / sizeof(invalid[0]); ++i)
        for (size_t step = 1; step <= 1024; step *= 2)
            assert(parse((const uint8_t *)invalid[i], strlen(invalid[i]), step, 0).result == HTTP_RESPONSE_HEADER_ERROR);
    static const uint8_t embedded_nul[] = "HTTP/1.1 200 OK\nX: before\0after\n\n";
    assert(parse(embedded_nul, sizeof(embedded_nul) - 1, 1, 0).result == HTTP_RESPONSE_HEADER_ERROR);
    const char *unsupported[] = {
        "HTTP/1.1 200 OK\nTransfer-Encoding: gzip\n\n",
        "HTTP/1.1 200 OK\nTransfer-Encoding: gzip, chunked\n\n",
        "HTTP/1.1 200 OK\nTransfer-Encoding: chunked\nTransfer-Encoding: chunked\n\n",
    };
    for (size_t i = 0; i < sizeof(unsupported) / sizeof(unsupported[0]); ++i) {
        parsed_t p = parse((const uint8_t *)unsupported[i], strlen(unsupported[i]), 1, 0);
        assert(p.result == HTTP_RESPONSE_HEADER_DONE && http_response_header_unsupported_transfer(&p.parser));
    }
}

static size_t aggregate(uint8_t *wire, size_t target) {
    const char *status = "HTTP/1.1 200 OK\r\n";
    size_t used = strlen(status);
    memcpy(wire, status, used);
    while (used + 2 < target) {
        size_t remaining = target - used - 2;
        size_t field = remaining > 1025 ? 1025 : remaining;
        if (remaining > field && remaining - field < 4) field -= 4 - (remaining - field);
        assert(field >= 4);
        wire[used++] = 'X'; wire[used++] = ':';
        memset(wire + used, 'a', field - 4); used += field - 4;
        wire[used++] = '\r'; wire[used++] = '\n';
    }
    wire[used++] = '\r'; wire[used++] = '\n';
    assert(used == target);
    return used;
}

static void bounds(void) {
    uint8_t wire[17000];
    size_t size = aggregate(wire, HTTP_RESPONSE_HEADER_MAX_BYTES);
    wire[size] = 0; wire[size + 1] = 255; // body is not charged to the header cap
    for (size_t step = 1; step <= 1024; step *= 2) {
        parsed_t p = parse(wire, size + 2, step, 0);
        assert(p.result == HTTP_RESPONSE_HEADER_DONE && p.parser.total_bytes == size);
    }
    size = aggregate(wire, HTTP_RESPONSE_HEADER_MAX_BYTES + 1);
    assert(parse(wire, size, 7, 0).result == HTTP_RESPONSE_HEADER_ERROR);
    const char *status = "HTTP/1.1 200 OK\r\n";
    size_t prefix = strlen(status);
    memcpy(wire, status, prefix);
    wire[prefix] = 'X'; wire[prefix + 1] = ':';
    memset(wire + prefix + 2, 'a', 1021);
    memcpy(wire + prefix + 1023, "\r\n\r\n", 4);
    assert(parse(wire, prefix + 1027, 1024, 0).result == HTTP_RESPONSE_HEADER_DONE);
    memset(wire + prefix + 2, 'a', 1022);
    memcpy(wire + prefix + 1024, "\r\n\r\n", 4);
    assert(parse(wire, prefix + 1028, 1024, 0).result == HTTP_RESPONSE_HEADER_ERROR);
    memcpy(wire + prefix, "Location: ", 10);
    memset(wire + prefix + 10, 'a', 512);
    memcpy(wire + prefix + 522, "\r\n\r\n", 4);
    assert(parse(wire, prefix + 526, 17, 0).result == HTTP_RESPONSE_HEADER_ERROR);
    // Folding must not bypass the logical line bound.
    memcpy(wire + prefix, "X: ", 3);
    memset(wire + prefix + 3, 'a', 1000);
    memcpy(wire + prefix + 1003, "\r\n\tmore-than-twenty-bytes\r\n\r\n", 30);
    assert(parse(wire, prefix + 1033, 13, 0).result == HTTP_RESPONSE_HEADER_ERROR);
}

int main(int argc, char **argv) {
    valid_splits(); invalid_cases(); bounds();
    if (argc == 2) {
        FILE *file = fopen(argv[1], "rb"); assert(file);
        uint8_t captured[17000];
        size_t size = fread(captured, 1, sizeof(captured), file);
        assert(!ferror(file) && fclose(file) == 0 && size > 1023);
        parsed_t p = parse(captured, size, 13, 0);
        assert(p.result == HTTP_RESPONSE_HEADER_DONE && p.parser.status == 200 && p.parser.bitrate == 56);
        printf("Captured IntenseRadio header: %zu bytes, HTTP 200 / ICY 56 PASS\n", size);
    }
    puts("Incremental HTTP header tests PASS: 16-byte state, 1024-byte scratch, splits/alias/body/EOF/bounds");
    return 0;
}
