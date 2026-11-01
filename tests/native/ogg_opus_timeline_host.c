/* Container metadata tests only: no decoder, PCM synthesis or vendor state. */
#include "ogg_opus_timeline.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

/* Public libopus ABI, linked from the installed reference library. These
 * packet helpers do not synthesize audio or inspect private decoder layouts.
 */
extern int opus_packet_get_nb_samples(const unsigned char *packet,
                                     int32_t length, int32_t rate);
extern const char *opus_get_version_string(void);

_Static_assert(sizeof(ogg_opus_timeline) <= 768, "observer must stay bounded");

typedef struct { uint8_t *p; size_t n, capacity; } buffer;
typedef struct {
    uint64_t digest, events, pages, provisional, links, heads, tags;
    size_t consumed;
    oopt_event last;
    oopt_status status;
} result;

static unsigned cases, fixture_runs, reset_positions, semantic_negatives;
static unsigned reference_durations;

static buffer new_buffer(size_t capacity)
{
    buffer b = {calloc(capacity, 1), 0, capacity};
    assert(b.p);
    return b;
}

static void append(buffer *b, const void *bytes, size_t n)
{
    assert(n <= b->capacity - b->n);
    if (n) memcpy(b->p + b->n, bytes, n);
    b->n += n;
}

static void le32(uint8_t *p, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i) p[i] = (uint8_t)(value >> (8u * i));
}

static void le64(uint8_t *p, uint64_t value)
{
    for (unsigned i = 0; i < 8; ++i) p[i] = (uint8_t)(value >> (8u * i));
}

/* Independent bit-at-a-time page construction (not the helper under test). */
static uint32_t page_crc(const uint8_t *p, size_t n)
{
    uint32_t crc = 0;
    for (size_t i = 0; i < n; ++i) {
        unsigned byte = i >= 22 && i < 26 ? 0 : p[i];
        for (unsigned bit = 0; bit < 8; ++bit) {
            bool top = (crc >> 31) != 0;
            bool incoming = (byte & (0x80u >> bit)) != 0;
            crc <<= 1;
            if (top != incoming) crc ^= UINT32_C(0x04c11db7);
        }
    }
    return crc;
}

static size_t page(buffer *out, uint32_t serial, uint32_t sequence,
                   unsigned flags, uint64_t gp, const uint8_t *laces,
                   size_t segments, const uint8_t *payload, size_t bytes)
{
    assert(segments <= 255);
    size_t sum = 0, at = out->n;
    for (size_t i = 0; i < segments; ++i) sum += laces[i];
    assert(sum == bytes);
    uint8_t h[27] = {'O', 'g', 'g', 'S', 0};
    h[5] = (uint8_t)flags;
    le64(h + 6, gp);
    le32(h + 14, serial);
    le32(h + 18, sequence);
    h[26] = (uint8_t)segments;
    append(out, h, sizeof(h));
    append(out, laces, segments);
    append(out, payload, bytes);
    le32(out->p + at + 22, page_crc(out->p + at, out->n - at));
    return at;
}

static size_t packet_page(buffer *out, uint32_t serial, uint32_t sequence,
                          unsigned flags, uint64_t gp,
                          const uint8_t *payload, size_t bytes)
{
    assert(bytes / 255u < 255);
    uint8_t laces[255];
    size_t count = bytes / 255u;
    memset(laces, 255, count);
    laces[count++] = (uint8_t)(bytes % 255u);
    return page(out, serial, sequence, flags, gp, laces, count, payload, bytes);
}

static size_t headers(buffer *out, uint32_t serial, unsigned skip,
                      unsigned family, unsigned channels, unsigned version)
{
    uint8_t head[600] = "OpusHead";
    head[8] = (uint8_t)version;
    head[9] = (uint8_t)channels;
    head[10] = (uint8_t)skip;
    head[11] = (uint8_t)(skip >> 8);
    le32(head + 12, 48000);
    head[18] = (uint8_t)family;
    size_t n = 19;
    if (family) {
        head[19] = 1;
        head[20] = 0;
        if (family == 3) {
            n = 21u + 2u * channels;
            assert(n <= sizeof(head));
            /* A silent matrix is permitted; metadata never mixes samples. */
        } else {
            n = 21u + channels;
            assert(n <= sizeof(head));
            for (unsigned c = 0; c < channels; ++c) head[21 + c] = 0;
        }
    }
    packet_page(out, serial, 0, 2, 0, head, n);
    uint8_t tags[16] = "OpusTags";
    packet_page(out, serial, 1, 0, 0, tags, sizeof(tags));
    return out->n;
}

static buffer stream(unsigned skip, uint64_t gp, const uint8_t *packet,
                     size_t packet_size)
{
    buffer b = new_buffer(4096);
    headers(&b, 77, skip, 0, 2, 1);
    packet_page(&b, 77, 2, 4, gp, packet, packet_size);
    return b;
}

static void hash_number(uint64_t *h, uint64_t n)
{
    for (unsigned i = 0; i < 8; ++i) {
        *h ^= (n >> (8u * i)) & 255u;
        *h *= UINT64_C(1099511628211);
    }
}

static void record(result *r, const oopt_event *e)
{
    ++r->events;
    if (e->flags & OOPT_PAGE) {
        assert(e->crc_verified);
        ++r->pages;
    }
    if (e->flags & OOPT_PROVISIONAL_END) {
        assert(!e->crc_verified && e->raw_end_known);
        assert(!(e->flags & (OOPT_PAGE | OOPT_LINK_END)));
        ++r->provisional;
    }
    if (e->flags & OOPT_LINK_END) ++r->links;
    if (e->flags & OOPT_HEAD) ++r->heads;
    if (e->flags & OOPT_TAGS) ++r->tags;
    hash_number(&r->digest, e->generation);
    hash_number(&r->digest, e->token);
    hash_number(&r->digest, e->link);
    hash_number(&r->digest, e->serial);
    hash_number(&r->digest, e->sequence);
    hash_number(&r->digest, e->flags);
    hash_number(&r->digest, e->crc_verified);
    hash_number(&r->digest, e->opus);
    hash_number(&r->digest, e->pre_skip_known);
    hash_number(&r->digest, e->pre_skip);
    hash_number(&r->digest, e->mapping);
    hash_number(&r->digest, e->channels);
    hash_number(&r->digest, e->streams);
    hash_number(&r->digest, e->coupled);
    hash_number(&r->digest, e->granule_known);
    hash_number(&r->digest, e->granule);
    hash_number(&r->digest, e->page_frames);
    hash_number(&r->digest, e->raw_completed);
    hash_number(&r->digest, e->initial_offset_known);
    hash_number(&r->digest, e->initial_offset);
    hash_number(&r->digest, e->raw_end_known);
    hash_number(&r->digest, e->raw_end);
    r->last = *e;
}

static void release_event(ogg_opus_timeline *s, oopt_event *e, result *r)
{
    record(r, e);
    assert(!oopt_ack(s, e->generation + 1u, e->token));
    assert(!oopt_ack(s, e->generation, e->token + 1u));
    size_t used = 99;
    oopt_event repeat;
    /* Pending backpressure must not touch an invalid borrowed input pointer. */
    assert(oopt_feed(s, NULL, 19, &used, &repeat) == OOPT_EVENT && !used);
    assert(repeat.token == e->token && repeat.flags == e->flags);
    assert(oopt_ack(s, e->generation, e->token));
    assert(!oopt_ack(s, e->generation, e->token));
}

static result observe_state(ogg_opus_timeline *s, const uint8_t *bytes,
                            size_t size, size_t chunk, bool poison)
{
    result r;
    memset(&r, 0, sizeof(r));
    r.digest = UINT64_C(1469598103934665603);
    uint8_t *copy = malloc(size ? size : 1);
    assert(copy);
    if (size) memcpy(copy, bytes, size);
    uint32_t random = UINT32_C(0xc3c3a55a);
    while (r.consumed < size) {
        size_t n = chunk ? chunk : size;
        if (chunk == SIZE_MAX) {
            random = random * UINT32_C(1664525) + UINT32_C(1013904223);
            n = 1u + random % 8192u;
        }
        if (n > size - r.consumed) n = size - r.consumed;
        size_t used = 99;
        oopt_event event;
        r.status = oopt_feed(s, copy + r.consumed, n, &used, &event);
        assert(used <= n);
        if (poison) memset(copy + r.consumed, 0xa5, used);
        r.consumed += used;
        if (r.status == OOPT_EVENT) release_event(s, &event, &r);
        else if (r.status < 0) break;
        else assert(r.status == OOPT_MORE && used == n);
    }
    if (r.status >= 0) {
        for (;;) {
            oopt_event event;
            r.status = oopt_finish(s, &event);
            if (r.status != OOPT_EVENT) break;
            release_event(s, &event, &r);
        }
    }
    free(copy);
    return r;
}

static result observe(const uint8_t *bytes, size_t size, size_t chunk)
{
    ogg_opus_timeline s = {0};
    oopt_reset(&s, 42);
    return observe_state(&s, bytes, size, chunk, true);
}

static result check(buffer *b, oopt_status expected)
{
    result r = observe(b->p, b->n, 1);
    if (r.status != expected)
        fprintf(stderr, "case %u: expected %d got %d after %zu/%zu bytes\n",
                cases, expected, r.status, r.consumed, b->n);
    assert(r.status == expected);
    ++cases;
    if (expected < 0) ++semantic_negatives;
    return r;
}

static void durations(void)
{
    static const unsigned silk[] = {480, 960, 1920, 2880};
    static const unsigned counts[] = {0, 1, 2, 3, 6, 48, 49, 63};
    for (unsigned config = 0; config < 32; ++config) {
        unsigned duration = config < 12 ? silk[config % 4u] :
                            config < 16 ? 480u << (config % 2u) :
                            120u << (config % 4u);
        for (unsigned code = 0; code < 4; ++code) {
            unsigned iterations = code == 3 ? sizeof(counts) / sizeof(counts[0]) : 1;
            for (unsigned c = 0; c < iterations; ++c) {
                unsigned count = code == 3 ? counts[c] : code ? 2u : 1u;
                uint8_t p[2] = {(uint8_t)((config << 3) | code),
                                (uint8_t)(code == 3 ? count : 0)};
                size_t n = code >= 2 ? 2 : 1;
                bool valid = count && count <= 48 && duration * count <= 5760;
                buffer b = stream(0, (uint64_t)duration * count, p, n);
                result r = check(&b, valid ? OOPT_FINISHED : OOPT_INVALID);
                if (valid) {
                    assert(opus_packet_get_nb_samples(p, (int32_t)n, 48000) ==
                           (int)(duration * count));
                    ++reference_durations;
                    assert(r.last.raw_completed == duration * count);
                    assert(r.last.raw_end == duration * count);
                }
                free(b.p);
            }
        }
    }
    uint8_t p = 0xfb;
    buffer b = stream(0, 960, &p, 1); /* Code 3 lacks its count byte. */
    check(&b, OOPT_INVALID);
    free(b.p);
    b = stream(0, 0, NULL, 0); /* An empty audio packet is not a PLC request. */
    check(&b, OOPT_INVALID);
    free(b.p);
    p = 0xfa;
    b = stream(0, 1920, &p, 1); /* Code 2 lacks a frame length. */
    check(&b, OOPT_INVALID);
    free(b.p);
}

static void granules(void)
{
    const uint8_t p = 0xf8; /* CELT 20 ms, code 0, zero coded bytes = PLC. */
    const uint64_t big = UINT64_C(0x20000000001234);
    const unsigned skips[] = {0, 1, 312, 65535};
    for (unsigned i = 0; i < sizeof(skips) / sizeof(skips[0]); ++i) {
        buffer b = stream(skips[i], big + 960, &p, 1);
        result r = check(&b, OOPT_FINISHED);
        assert(r.last.pre_skip == skips[i] && r.last.initial_offset == big);
        assert(r.last.raw_end == 960 && r.last.raw_completed == 960);
        free(b.p);
    }
    buffer b = stream(312, 500, &p, 1);
    result r = check(&b, OOPT_FINISHED);
    assert(r.last.raw_end == 500 && r.last.initial_offset == 0);
    free(b.p);
    b = stream(312, 312, &p, 1);
    r = check(&b, OOPT_FINISHED);
    assert(r.last.raw_end == r.last.pre_skip); /* Empty playable interval. */
    free(b.p);
    b = stream(312, 311, &p, 1);
    check(&b, OOPT_INVALID);
    free(b.p);

    /* Positive initial offset followed by EOS: raw_end is Rprev + delta GP. */
    b = new_buffer(4096);
    headers(&b, 77, 312, 0, 2, 1);
    packet_page(&b, 77, 2, 0, big + 960, &p, 1);
    packet_page(&b, 77, 3, 4, big + 960 + 480, &p, 1);
    r = check(&b, OOPT_FINISHED);
    assert(r.last.raw_completed == 1920 && r.last.raw_end == 1440);
    assert(r.last.initial_offset == big && r.provisional == 1);
    free(b.p);

    /* End trim can cover more than one packet (RFC 7845's limit is SHOULD). */
    b = new_buffer(4096);
    headers(&b, 77, 312, 0, 2, 1);
    packet_page(&b, 77, 2, 0, 960, &p, 1);
    uint8_t laces[] = {1, 1, 1}, packets[] = {0xf8, 0xf8, 0xf8};
    page(&b, 77, 3, 4, 1000, laces, 3, packets, 3);
    r = check(&b, OOPT_FINISHED);
    assert(r.last.raw_end == 1000 && r.last.raw_completed == 3840);
    free(b.p);

    /* A full packet duration can be skipped even when pre_skip is 65535. */
    b = new_buffer(4096);
    headers(&b, 77, 65535, 0, 2, 1);
    uint8_t long_packets[34], long_laces[17];
    for (unsigned i = 0; i < 17; ++i) {
        long_packets[2 * i] = 0xfb;
        long_packets[2 * i + 1] = 6;
        long_laces[i] = 2;
    }
    page(&b, 77, 2, 4, 97920, long_laces, 17, long_packets, 34);
    r = check(&b, OOPT_FINISHED);
    assert(r.last.raw_end == 97920 && r.last.pre_skip == 65535);
    free(b.p);

    const uint64_t invalid_gp[] = {959, UINT64_MAX};
    for (unsigned i = 0; i < 2; ++i) {
        b = new_buffer(4096);
        headers(&b, 77, 0, 0, 2, 1);
        packet_page(&b, 77, 2, 0, invalid_gp[i], &p, 1);
        check(&b, i ? OOPT_UNALIGNED : OOPT_INVALID);
        free(b.p);
    }
    for (unsigned kind = 0; kind < 3; ++kind) {
        b = new_buffer(4096);
        headers(&b, 77, 0, 0, 2, 1);
        packet_page(&b, 77, 2, 0, 960, &p, 1);
        packet_page(&b, 77, 3, kind ? 4 : 0,
                    kind == 0 ? 1919 : kind == 1 ? 959 : 1921, &p, 1);
        check(&b, OOPT_INVALID);
        free(b.p);
    }
}

static buffer continued_stream(void)
{
    buffer b = new_buffer(80000);
    uint8_t head[19] = "OpusHead";
    head[8] = 1; head[9] = 2;
    packet_page(&b, 77, 0, 2, 0, head, 19);
    /* A large OpusTags packet is streamed without retaining its body. */
    uint8_t *tags = calloc(70000, 1);
    assert(tags);
    memcpy(tags, "OpusTags", 8);
    uint8_t laces[255];
    memset(laces, 255, sizeof(laces));
    page(&b, 77, 1, 0, UINT64_MAX, laces, 255, tags, 65025);
    uint8_t rest[20];
    memset(rest, 255, 19); rest[19] = 130;
    page(&b, 77, 2, 1, 0, rest, 20, tags + 65025, 4975);
    free(tags);
    /* Exact-255-byte audio packets need the terminating zero lace. */
    uint8_t audio[510] = {0xf8};
    audio[255] = 0xf8;
    uint8_t one = 255;
    page(&b, 77, 3, 0, UINT64_MAX, &one, 1, audio, 255);
    uint8_t two[] = {0, 255};
    page(&b, 77, 4, 1, 960, two, 2, audio + 255, 255);
    uint8_t zero = 0;
    page(&b, 77, 5, 5, 1920, &zero, 1, NULL, 0);
    return b;
}

static void boundaries(void)
{
    buffer b = continued_stream();
    result baseline = observe(b.p, b.n, 0);
    assert(baseline.status == OOPT_FINISHED && baseline.last.raw_end == 1920);
    const size_t splits[] = {1, 2, 257, 4096, SIZE_MAX};
    for (unsigned i = 0; i < sizeof(splits) / sizeof(splits[0]); ++i) {
        result r = observe(b.p, b.n, splits[i]);
        assert(r.status == OOPT_FINISHED && r.digest == baseline.digest);
        ++cases;
    }
    free(b.p);
    /* Split a code-3 TOC/count across pages while retaining just two bytes. */
    b = new_buffer(4096);
    headers(&b, 77, 0, 0, 2, 1);
    uint8_t p[255] = {0xfb, 6}, lace = 255;
    page(&b, 77, 2, 0, UINT64_MAX, &lace, 1, p, 255);
    uint8_t tail[] = {0};
    page(&b, 77, 3, 5, 5760, tail, 1, NULL, 0);
    result r = check(&b, OOPT_FINISHED);
    assert(r.last.raw_completed == 5760);
    free(b.p);

    /* Nil pages carry no packet completion, and do not invent audio duration. */
    const uint8_t plc = 0xf8;
    b = new_buffer(4096);
    headers(&b, 77, 0, 0, 2, 1);
    packet_page(&b, 77, 2, 0, 960, &plc, 1);
    page(&b, 77, 3, 0, UINT64_MAX, NULL, 0, NULL, 0);
    page(&b, 77, 4, 4, 960, NULL, 0, NULL, 0);
    r = check(&b, OOPT_FINISHED);
    assert(r.last.raw_completed == 960 && r.last.raw_end == 960);
    free(b.p);

    /* All split prefixes in a compact continued packet exercise reset states. */
    b = new_buffer(4096);
    headers(&b, 77, 0, 0, 2, 1);
    page(&b, 77, 2, 0, UINT64_MAX, &lace, 1, p, 255);
    page(&b, 77, 3, 5, 5760, tail, 1, NULL, 0);
    buffer fresh = stream(0, 960, &plc, 1);
    for (size_t cut = 0; cut <= b.n; ++cut) {
        ogg_opus_timeline s = {0};
        oopt_reset(&s, 9);
        result partial = observe_state(&s, b.p, cut, 1, true);
        (void)partial;
        uint64_t old_token = s.token_sequence;
        oopt_reset(&s, 9); /* Same generation must still invalidate old tokens. */
        assert(!oopt_ack(&s, 9, old_token));
        result full = observe_state(&s, fresh.p, fresh.n, 1, true);
        assert(full.status == OOPT_FINISHED && full.last.raw_completed == 960);
        ++reset_positions;
    }
    free(fresh.p);
    free(b.p);
}

static void mappings_and_links(void)
{
    const uint8_t p[] = {0xf8, 0};
    const unsigned families[] = {0, 1, 2, 3, 255};
    const unsigned channels[] = {2, 8, 4, 3, 255};
    for (unsigned i = 0; i < 5; ++i) {
        buffer b = new_buffer(4096);
        headers(&b, 77, 0, families[i], channels[i], 15);
        packet_page(&b, 77, 2, 4, 960, p, families[i] ? 2 : 1);
        result r = check(&b, OOPT_FINISHED);
        assert(r.last.mapping == families[i] && r.last.channels == channels[i]);
        free(b.p);
    }
    /* A real self-delimited first stream: TOC, length 0, then last stream TOC. */
    buffer b = new_buffer(4096);
    uint8_t h[23] = "OpusHead";
    h[8] = 1; h[9] = 2; h[18] = 1; h[19] = 2;
    h[21] = 0; h[22] = 1;
    packet_page(&b, 77, 0, 2, 0, h, 23);
    uint8_t tags[16] = "OpusTags";
    packet_page(&b, 77, 1, 0, 0, tags, 16);
    uint8_t multi[] = {0xf8, 0, 0xf8};
    packet_page(&b, 77, 2, 4, 960, multi, 3);
    result r = check(&b, OOPT_FINISHED);
    assert(r.last.streams == 2 && r.last.raw_completed == 960);
    free(b.p);

    b = new_buffer(4096);
    headers(&b, 77, 312, 0, 2, 1);
    packet_page(&b, 77, 2, 4, 960, p, 1);
    const uint8_t vorbis[] = {1, 'v', 'o', 'r', 'b', 'i', 's'};
    packet_page(&b, 78, 0, 2, 0, vorbis, sizeof(vorbis));
    packet_page(&b, 78, 1, 4, 12345, p, 1);
    headers(&b, 79, 1, 0, 1, 1);
    packet_page(&b, 79, 2, 4, 960, p, 1);
    result baseline = observe(b.p, b.n, 0);
    r = check(&b, OOPT_FINISHED);
    assert(r.digest == baseline.digest && r.links == 3 && r.heads == 2);
    assert(r.last.link == 3 && r.last.pre_skip == 1 && r.last.channels == 1);
    free(b.p);

    /* Explicit pending reset and stale tokens while a NEW event is pending. */
    b = stream(0, 960, p, 1);
    ogg_opus_timeline s = {0};
    oopt_reset(&s, 3);
    size_t used;
    oopt_event old, newer;
    assert(oopt_feed(&s, b.p, b.n, &used, &old) == OOPT_EVENT);
    oopt_reset(&s, 3);
    assert(oopt_feed(&s, b.p, b.n, &used, &newer) == OOPT_EVENT);
    assert(newer.token > old.token && !oopt_ack(&s, 3, old.token));
    assert(s.pending && oopt_ack(&s, 3, newer.token));
    ++cases;
    free(b.p);
}

static void negatives(void)
{
    const uint8_t plc = 0xf8;
    /* Every semantic mutation below has a freshly computed valid page CRC. */
    for (unsigned kind = 0; kind < 9; ++kind) {
        buffer b = new_buffer(4096);
        headers(&b, 77, 0, 0, 2, 1);
        if (kind == 0) packet_page(&b, 77, 3, 4, 960, &plc, 1); /* gap */
        if (kind == 1) packet_page(&b, 78, 2, 4, 960, &plc, 1); /* multiplex */
        if (kind == 2) packet_page(&b, 78, 0, 2, 0, &plc, 1); /* overlapping BOS */
        if (kind == 3) packet_page(&b, 77, 2, 5, 960, &plc, 1); /* orphan prefix */
        if (kind == 4) {
            uint8_t body[255] = {0xf8}, lace = 255;
            page(&b, 77, 2, 0, UINT64_MAX, &lace, 1, body, 255);
            packet_page(&b, 77, 3, 4, 960, &plc, 1); /* dropped continuation */
        }
        if (kind == 5) page(&b, 77, 2, 4, UINT64_MAX, NULL, 0, NULL, 0);
        if (kind == 6) {
            uint8_t body[255] = {0xf8}, lace = 255;
            page(&b, 77, 2, 4, UINT64_MAX, &lace, 1, body, 255);
        }
        if (kind == 7) {
            packet_page(&b, 77, 2, 0, 960, &plc, 1);
            page(&b, 77, 3, 4, 959, NULL, 0, NULL, 0);
        }
        if (kind == 8) {
            uint8_t body[255] = {0xf8}, lace = 255;
            page(&b, 77, 2, 0, 0, &lace, 1, body, 255);
        }
        oopt_status expected = (kind == 1 || kind == 2) ? OOPT_UNSUPPORTED :
                               kind == 6 ? OOPT_TRUNCATED :
                               kind == 8 ? OOPT_INVALID : OOPT_UNALIGNED;
        check(&b, expected);
        free(b.p);
    }
    for (unsigned kind = 0; kind < 7; ++kind) {
        buffer b = new_buffer(4096);
        uint8_t h[23] = "OpusHead";
        h[8] = kind == 0 ? 16 : 1;
        h[9] = kind == 1 ? 0 : 2;
        h[18] = kind == 2 ? 42 : kind >= 3 ? 1 : 0;
        h[19] = kind == 3 ? 0 : 1;
        h[20] = kind == 4 ? 2 : 0;
        h[21] = kind == 5 ? 1 : 0;
        size_t size = kind >= 3 && kind != 6 ? 23 : 19;
        packet_page(&b, 77, 0, 2, 0, h, size);
        check(&b, kind == 0 || kind == 2 ? OOPT_UNSUPPORTED : OOPT_INVALID);
        free(b.p);
    }
    /* Distinguish a provisional EOS bound from a corrupted, unverified page. */
    buffer b = stream(0, 960, &plc, 1);
    b.p[b.n - 1] ^= 4;
    result r = check(&b, OOPT_INVALID);
    assert(r.provisional == 1 && r.pages == 2 && r.links == 0);
    free(b.p);
    /* Every truncation of a complete stream must stay non-finished. */
    b = stream(0, 960, &plc, 1);
    for (size_t cut = 0; cut < b.n; ++cut) {
        r = observe(b.p, cut, 1);
        assert(r.status == OOPT_TRUNCATED);
        ++cases;
    }
    free(b.p);

    /* Checked 64-bit limits and token exhaustion using owned observer state. */
    b = new_buffer(4096);
    size_t at = headers(&b, 77, 0, 0, 2, 1);
    packet_page(&b, 77, 2, 4, UINT64_MAX - 1u, &plc, 1);
    ogg_opus_timeline s = {0};
    oopt_reset(&s, 42);
    r = observe_state(&s, b.p, at, 1, true);
    assert(r.status == OOPT_TRUNCATED);
    s.raw_completed = UINT64_MAX - 100u;
    s.previous_gp = UINT64_MAX - 100u;
    s.previous_gp_known = s.first_audio = s.offset_known = true;
    r = observe_state(&s, b.p + at, b.n - at, 1, true);
    assert(r.status == OOPT_LIMIT);
    oopt_reset(&s, 42);
    s.token_sequence = UINT64_MAX;
    r = observe_state(&s, b.p, at, 1, true);
    assert(r.status == OOPT_LIMIT);
    oopt_reset(&s, 42);
    assert(s.fault == OOPT_LIMIT);
    free(b.p);
    cases += 3;
}

static buffer load(const char *path)
{
    FILE *f = fopen(path, "rb");
    assert(f && !fseek(f, 0, SEEK_END));
    long n = ftell(f);
    assert(n > 0 && !fseek(f, 0, SEEK_SET));
    buffer b = new_buffer((size_t)n);
    b.n = fread(b.p, 1, b.capacity, f);
    assert(b.n == b.capacity && !fclose(f));
    return b;
}

static void fixture(const char *name, const char *path, uint64_t raw)
{
    buffer b = load(path);
    const size_t chunks[] = {0, 4096, 257, 1, SIZE_MAX};
    result baseline;
    memset(&baseline, 0, sizeof(baseline));
    for (unsigned i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i) {
        result r = observe(b.p, b.n, chunks[i]);
        if (r.status != OOPT_FINISHED)
            fprintf(stderr, "%s: chunk %zu status %d at %zu/%zu\n",
                    name, chunks[i], r.status, r.consumed, b.n);
        assert(r.status == OOPT_FINISHED && r.consumed == b.n);
        assert(r.last.raw_completed == raw && r.last.raw_end == 528312);
        assert(r.last.pre_skip == 312 && r.last.initial_offset_known);
        assert(r.last.initial_offset == 0 && r.links == 1 && r.provisional == 1);
        if (!i) baseline = r;
        else assert(r.digest == baseline.digest && r.pages == baseline.pages);
        printf("{\"fixture\":\"%s\",\"split\":\"%s\",\"bytes\":%zu,"
               "\"pages\":%" PRIu64 ",\"raw_frames\":%" PRIu64 ","
               "\"raw_end\":%" PRIu64 ",\"pre_skip\":%u,"
               "\"digest\":\"%016" PRIx64 "\",\"passed\":true}\n",
               name, i == 0 ? "whole" : i == 1 ? "4096" : i == 2 ? "257" :
               i == 3 ? "1" : "seeded", b.n, r.pages, r.last.raw_completed,
               r.last.raw_end, r.last.pre_skip, r.digest);
        ++fixture_runs;
    }
    free(b.p);
}

int main(int argc, char **argv)
{
    assert(argc == 3);
    durations();
    granules();
    boundaries();
    mappings_and_links();
    negatives();
    fixture("20ms", argv[1], 528960);
    fixture("120ms", argv[2], 529920);
    printf("{\"reference\":\"libopus\",\"version\":\"%s\","
           "\"duration_comparisons\":%u,\"passed\":true}\n",
           opus_get_version_string(), reference_durations);
    printf("{\"suite\":\"ogg-opus-timeline-host\",\"passed\":true,"
           "\"cases\":%u,\"semantic_negatives\":%u,\"reset_positions\":%u,"
           "\"fixture_runs\":%u,\"state_bytes\":%zu,\"physical_hardware\":false,"
           "\"playback_trim_implemented\":false}\n", cases, semantic_negatives,
           reset_positions, fixture_runs, sizeof(ogg_opus_timeline));
    return 0;
}
