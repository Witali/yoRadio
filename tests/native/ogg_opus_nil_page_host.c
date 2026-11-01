/* Differential container tests through public libogg APIs; no audio decoder. */
#include "ogg_opus_timeline.h"
#include <ogg/ogg.h>
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct { unsigned char bytes[4096]; size_t size; } stream_bytes;
typedef struct { unsigned pages, packets, holes, sync_errors; bool eos; } reference;
typedef struct { oopt_status status; uint64_t frames, end; unsigned pages; } observation;

static void put32(unsigned char *p, uint32_t n)
{
    for (unsigned i = 0; i < 4; ++i) p[i] = (unsigned char)(n >> (8u * i));
}

static void put64(unsigned char *p, uint64_t n)
{
    for (unsigned i = 0; i < 8; ++i) p[i] = (unsigned char)(n >> (8u * i));
}

/* Deliberately independent from the observer's byte-at-a-time CRC helper. */
static uint32_t checksum(const unsigned char *p, size_t n)
{
    uint32_t crc = 0;
    for (size_t i = 0; i < n; ++i) {
        unsigned byte = i >= 22 && i < 26 ? 0 : p[i];
        for (unsigned bit = 0; bit < 8; ++bit) {
            bool top = (crc >> 31) != 0;
            bool input = (byte & (0x80u >> bit)) != 0;
            crc <<= 1;
            if (top != input) crc ^= UINT32_C(0x04c11db7);
        }
    }
    return crc;
}

static size_t page(stream_bytes *b, uint32_t sequence, unsigned flags,
                   uint64_t gp, const unsigned char *laces, size_t segments,
                   const unsigned char *payload, size_t size)
{
    size_t start = b->size, sum = 0;
    assert(segments <= 255 && 27 + segments + size <= sizeof(b->bytes) - start);
    for (size_t i = 0; i < segments; ++i) sum += laces[i];
    assert(sum == size);
    unsigned char *h = b->bytes + start;
    memset(h, 0, 27);
    memcpy(h, "OggS", 4);
    h[5] = (unsigned char)flags;
    put64(h + 6, gp);
    put32(h + 14, 77);
    put32(h + 18, sequence);
    h[26] = (unsigned char)segments;
    if (segments) memcpy(h + 27, laces, segments);
    if (size) memcpy(h + 27 + segments, payload, size);
    b->size += 27 + segments + size;
    put32(h + 22, checksum(h, b->size - start));
    return start;
}

static void headers(stream_bytes *b)
{
    unsigned char head[19] = "OpusHead", tags[16] = "OpusTags";
    head[8] = 1;
    head[9] = 2;
    put32(head + 12, 48000);
    unsigned char lace = sizeof(head);
    page(b, 0, 2, 0, &lace, 1, head, sizeof(head));
    lace = sizeof(tags);
    page(b, 1, 0, 0, &lace, 1, tags, sizeof(tags));
}

static void payload(unsigned char *p, size_t size)
{
    assert(size >= 255);
    for (size_t i = 0; i < size; ++i) p[i] = (unsigned char)(i * 17u + 3u);
    p[0] = 0xf8; /* A 20 ms TOC; compressed-frame validity is not tested. */
}

/* Placement: 0 before the open packet, 1 inside it, 2 after completion.
 * Negative: 1 a missing nil-page sequence; 2 a corrupted nil-page CRC.
 */
static stream_bytes make_stream(unsigned placement, unsigned continued,
                                unsigned nil_count, unsigned tail,
                                unsigned negative)
{
    stream_bytes b = {{0}, 0};
    headers(&b);
    unsigned char body[262], lace = 255;
    payload(body, sizeof(body));
    uint32_t sequence = 2;
    for (unsigned step = 0; step < 3; ++step) {
        if (step == placement) {
            for (unsigned i = 0; i < nil_count; ++i) {
                if (negative == 1 && !i) ++sequence;
                bool end = placement == 2 && i + 1 == nil_count;
                size_t at = page(&b, sequence++, continued | (end ? 4u : 0u),
                                 end ? 960 : UINT64_MAX, NULL, 0, NULL, 0);
                if (negative == 2 && !i) b.bytes[at + 6] ^= 1;
            }
        }
        if (step == 0) page(&b, sequence++, 0, UINT64_MAX, &lace, 1, body, 255);
        if (step == 1) {
            unsigned char final_lace = (unsigned char)tail;
            page(&b, sequence++, placement == 2 ? 1u : 5u, 960,
                 &final_lace, 1, body + 255, tail);
        }
    }
    return b;
}

static reference libogg_read(const stream_bytes *b, unsigned expected_tail,
                             unsigned expected_packets)
{
    ogg_sync_state sync;
    ogg_stream_state stream;
    assert(ogg_sync_init(&sync) == 0 && ogg_stream_init(&stream, 77) == 0);
    char *input = ogg_sync_buffer(&sync, (long)b->size);
    assert(input);
    memcpy(input, b->bytes, b->size);
    assert(ogg_sync_wrote(&sync, (long)b->size) == 0);
    reference r = {0};
    unsigned headers_seen = 0;
    for (;;) {
        ogg_page current;
        int status = ogg_sync_pageout(&sync, &current);
        if (status < 0) { ++r.sync_errors; continue; }
        if (!status) break;
        ++r.pages;
        assert(ogg_stream_pagein(&stream, &current) == 0);
        for (;;) {
            ogg_packet packet;
            status = ogg_stream_packetout(&stream, &packet);
            if (status < 0) { ++r.holes; continue; }
            if (!status) break;
            if (headers_seen < 2) {
                assert(packet.bytes == (headers_seen ? 16 : 19));
                assert(!memcmp(packet.packet, headers_seen ? "OpusTags" : "OpusHead", 8));
                ++headers_seen;
            } else {
                unsigned char expected[262];
                payload(expected, sizeof(expected));
                assert(packet.bytes == (long)(255u + expected_tail));
                assert(!memcmp(packet.packet, expected, (size_t)packet.bytes));
                ++r.packets;
            }
        }
    }
    r.eos = ogg_stream_eos(&stream) != 0;
    assert(headers_seen == 2 && r.packets == expected_packets && r.eos);
    assert(ogg_stream_clear(&stream) == 0 && ogg_sync_clear(&sync) == 0);
    return r;
}

static observation observe(const stream_bytes *b, size_t chunk)
{
    unsigned char *copy = malloc(b->size);
    assert(copy);
    memcpy(copy, b->bytes, b->size);
    ogg_opus_timeline s = {0};
    oopt_reset(&s, 9);
    observation r = {0};
    size_t position = 0;
    uint32_t random = 1234;
    for (;;) {
        oopt_event event;
        if (position < b->size) {
            size_t n = chunk ? chunk : b->size;
            if (chunk == SIZE_MAX) {
                random = random * UINT32_C(1664525) + UINT32_C(1013904223);
                n = 1 + random % 97;
            }
            if (n > b->size - position) n = b->size - position;
            size_t used;
            r.status = oopt_feed(&s, copy + position, n, &used, &event);
            assert(used <= n);
            memset(copy + position, 0xa5, used); /* No borrowed pointer survives. */
            position += used;
        } else {
            r.status = oopt_finish(&s, &event);
        }
        if (r.status == OOPT_EVENT) {
            if (event.flags & OOPT_PAGE) ++r.pages;
            if (event.flags & OOPT_LINK_END) {
                assert(event.crc_verified && event.raw_end_known);
                r.frames = event.raw_completed;
                r.end = event.raw_end;
            }
            assert(oopt_ack(&s, event.generation, event.token));
        } else if (r.status != OOPT_MORE) break;
    }
    free(copy);
    return r;
}

int main(void)
{
    unsigned cases = 0, schedules = 0, mismatches = 0;
    const size_t chunks[] = {0, 1, 27, 257, SIZE_MAX};
    for (unsigned placement = 0; placement < 3; ++placement)
    for (unsigned continued = 0; continued < 2; ++continued)
    for (unsigned nil_count = 1; nil_count <= 2; ++nil_count)
    for (unsigned tail = 0; tail <= 7; tail += 7) {
        stream_bytes b = make_stream(placement, continued, nil_count, tail, 0);
        reference ref = libogg_read(&b, tail, 1);
        assert(!ref.holes && !ref.sync_errors && ref.pages == 4 + nil_count);
        unsigned bad = 0;
        for (unsigned i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i) {
            observation got = observe(&b, chunks[i]);
            bool pass = got.status == OOPT_FINISHED && got.frames == 960 &&
                        got.end == 960 && got.pages == ref.pages;
            bad += !pass;
            ++schedules;
            printf("{\"case\":%u,\"placement\":%u,\"nil_continued\":%u,"
                   "\"nil_count\":%u,\"tail\":%u,\"schedule\":%u,"
                   "\"libogg_packets\":%u,\"libogg_pages\":%u,"
                   "\"observer_status\":%d,\"expected_status\":%d,\"passed\":%s}\n",
                   cases, placement, continued, nil_count, tail, i, ref.packets,
                   ref.pages, (int)got.status, (int)OOPT_FINISHED, pass ? "true" : "false");
        }
        mismatches += bad;
        ++cases;
    }
    unsigned negative_cases = 0;
    for (unsigned negative = 1; negative <= 2; ++negative)
    for (unsigned continued = 0; continued < 2; ++continued) {
        stream_bytes b = make_stream(1, continued, 1, 0, negative);
        reference ref = libogg_read(&b, 0, 0);
        assert(ref.holes == 1 && ref.sync_errors == (negative == 2));
        for (unsigned i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i) {
            observation got = observe(&b, chunks[i]);
            oopt_status expected = negative == 1 ? OOPT_UNALIGNED : OOPT_INVALID;
            bool pass = got.status == expected;
            mismatches += !pass;
            ++schedules;
            printf("{\"negative\":%u,\"nil_continued\":%u,\"schedule\":%u,"
                   "\"libogg_packets\":%u,\"libogg_holes\":%u,\"libogg_sync_errors\":%u,"
                   "\"observer_status\":%d,\"expected_status\":%d,\"passed\":%s}\n",
                   negative, continued, i, ref.packets, ref.holes, ref.sync_errors,
                   (int)got.status, (int)expected, pass ? "true" : "false");
        }
        ++negative_cases;
    }
    printf("{\"suite\":\"ogg-opus-nil-page-host\",\"cases\":%u,\"negative_cases\":%u,"
           "\"schedules\":%u,\"mismatches\":%u,\"state_bytes\":%zu,\"passed\":%s}\n",
           cases, negative_cases, schedules, mismatches, sizeof(ogg_opus_timeline),
           mismatches ? "false" : "true");
    return mismatches ? EXIT_FAILURE : EXIT_SUCCESS;
}
