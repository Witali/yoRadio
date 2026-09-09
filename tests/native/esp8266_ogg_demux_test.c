#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ogg_opus_demux.h"

#define WIRE_CAPACITY (OGG_OPUS_TAG_MAX_BYTES + 131072u)
#define RECORD_CAPACITY 4096u

static uint8_t wire[WIRE_CAPACITY], saved[WIRE_CAPACITY];
static uint8_t reference_packet[OGG_OPUS_TAG_MAX_BYTES + 1u];
static size_t wire_size;
static const uint8_t head[19] = {
    'O','p','u','s','H','e','a','d', 1, 1, 0x38, 1, 0x80, 0xbb, 0, 0, 0, 0, 0
};
static const uint8_t tags[16] = {'O','p','u','s','T','a','g','s',0,0,0,0,0,0,0,0};

typedef struct {
    size_t size, stored;
    uint64_t granule;
    uint32_t index, serial, hash;
    bool last, eos, start;
} record_t;

typedef struct {
    record_t records[RECORD_CAPACITY];
    size_t count;
    size_t cancel_at;
} capture_t;

static capture_t actual, expected;

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void put32(uint8_t *p, uint32_t value) {
    for (unsigned i = 0; i < 4; ++i) p[i] = (uint8_t)(value >> (8u * i));
}

/* Independent bitwise implementation, deliberately not the production table. */
static uint32_t page_crc(const uint8_t *p, size_t size) {
    uint32_t crc = 0;
    for (size_t i = 0; i < size; ++i) {
        crc ^= (uint32_t)(i >= 22 && i < 26 ? 0 : p[i]) << 24;
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc << 1) ^ ((crc >> 31) ? 0x04c11db7u : 0);
    }
    return crc;
}

static size_t page_length(size_t at) {
    const size_t count = wire[at + 26];
    size_t result = 27 + count;
    for (size_t i = 0; i < count; ++i) result += wire[at + 27 + i];
    return result;
}

static void refresh_crc(size_t at) {
    put32(wire + at + 22, page_crc(wire + at, page_length(at)));
}

static size_t page(uint8_t flags, uint32_t serial, uint32_t sequence,
                   uint64_t granule, const uint8_t *laces, size_t count,
                   const uint8_t *body) {
    assert(count <= 255);
    size_t body_size = 0;
    for (size_t i = 0; i < count; ++i) body_size += laces[i];
    const size_t at = wire_size;
    assert(at + 27 + count + body_size <= sizeof(wire));
    uint8_t *p = wire + at;
    memset(p, 0, 27);
    memcpy(p, "OggS", 4);
    p[5] = flags;
    put32(p + 6, (uint32_t)granule);
    put32(p + 10, (uint32_t)(granule >> 32));
    put32(p + 14, serial);
    put32(p + 18, sequence);
    p[26] = (uint8_t)count;
    if (count) memcpy(p + 27, laces, count);
    if (body_size) memcpy(p + 27 + count, body, body_size);
    wire_size += 27 + count + body_size;
    refresh_crc(at);
    return at;
}

static size_t one_packet(uint8_t flags, uint32_t serial, uint32_t sequence,
                         uint64_t granule, const uint8_t *body, size_t size) {
    uint8_t laces[255];
    const size_t count = size / 255 + 1;
    assert(count <= sizeof(laces));
    memset(laces, 255, count);
    laces[count - 1] = (uint8_t)(size % 255);
    return page(flags, serial, sequence, granule, laces, count, body);
}

static void headers(uint32_t serial) {
    one_packet(2, serial, 0, 0, head, sizeof(head));
    one_packet(0, serial, 1, 0, tags, sizeof(tags));
}

static uint32_t hash_bytes(const uint8_t *p, size_t size) {
    uint32_t hash = 2166136261u;
    for (size_t i = 0; i < size; ++i) hash = (hash ^ p[i]) * 16777619u;
    return hash;
}

static int capture(void *context, const ogg_opus_packet_t *p) {
    capture_t *c = context;
    assert(c->count < RECORD_CAPACITY);
    assert(p->stored_size <= OGG_OPUS_PACKET_BYTES);
    assert(p->stored_size <= p->size);
    if (p->packet_index == 1) assert(p->stored_size == 16);
    else assert(p->stored_size == p->size);
    record_t *r = &c->records[c->count++];
    memset(r, 0, sizeof(*r));
    r->size = p->size; r->stored = p->stored_size;
    r->index = p->packet_index; r->serial = p->serial;
    r->granule = p->page_granule; r->last = p->page_last_packet;
    r->eos = p->page_eos; r->start = p->stream_start;
    r->hash = hash_bytes(p->data, p->stored_size);
    return c->cancel_at && c->count == c->cancel_at ? -77 : 0;
}

/* A whole-buffer reference parser for the test only: independently reconstruct
 * every packet and page event, then compare with the incremental implementation. */
static void reference(const uint8_t *bytes, size_t length) {
    memset(&expected, 0, sizeof(expected));
    size_t at = 0, packet_size = 0;
    uint32_t index = 0;
    while (at < length) {
        assert(length - at >= 27);
        const uint8_t *p = bytes + at;
        const size_t count = p[26];
        assert(length - at >= 27 + count);
        size_t body_size = 0, last = SIZE_MAX;
        for (size_t i = 0; i < count; ++i) {
            body_size += p[27 + i];
            if (p[27 + i] != 255) last = i;
        }
        assert(length - at >= 27 + count + body_size);
        assert(page_crc(p, 27 + count + body_size) == get32(p + 22));
        if (p[5] & 2) index = 0;
        const uint8_t *data = p + 27 + count;
        for (size_t i = 0; i < count; ++i) {
            const size_t lace = p[27 + i];
            assert(packet_size + lace <= sizeof(reference_packet));
            memcpy(reference_packet + packet_size, data, lace);
            data += lace;
            packet_size += lace;
            if (lace == 255) continue;
            const ogg_opus_packet_t packet = {
                .data = reference_packet, .size = packet_size,
                .stored_size = index == 1 && packet_size > 16 ? 16 : packet_size,
                .packet_index = index, .serial = get32(p + 14),
                .page_granule = (uint64_t)get32(p + 6) |
                    ((uint64_t)get32(p + 10) << 32),
                .page_last_packet = i == last, .page_eos = !!(p[5] & 4),
                .stream_start = index == 0
            };
            assert(capture(&expected, &packet) == 0);
            packet_size = 0;
            ++index;
        }
        at += 27 + count + body_size;
    }
    assert(!packet_size);
}

static int feed_block(ogg_opus_demux_t *d, const uint8_t *bytes, size_t size) {
    size_t at = 0;
    for (;;) {
        size_t consumed = SIZE_MAX;
        const size_t before = actual.count;
        const int result = ogg_opus_demux_feed(d, bytes ? bytes + at : NULL,
            size - at, &consumed, capture, &actual);
        assert(consumed <= size - at);
        at += consumed;
        if (result == OGG_OPUS_DEMUX_PACKET) {
            assert(actual.count == before + 1);
            continue;
        }
        if (result == OGG_OPUS_DEMUX_NEED_INPUT) {
            assert(actual.count == before);
            assert(at == size);
        }
        return result;
    }
}

static void reset(ogg_opus_demux_t *d) {
    ogg_opus_demux_init(d);
    memset(&actual, 0, sizeof(actual));
}

static void compare(void) {
    assert(actual.count == expected.count);
    assert(memcmp(actual.records, expected.records,
                  actual.count * sizeof(record_t)) == 0);
}

static void valid_chunks_mode(const uint8_t *bytes, size_t size, size_t chunk,
                              bool live_join, bool finite) {
    ogg_opus_demux_t d;
    reset(&d);
    ogg_opus_demux_init_ex(&d, live_join);
    for (size_t at = 0; at < size;) {
        const size_t take = size - at < chunk ? size - at : chunk;
        assert(feed_block(&d, bytes + at, take) == OGG_OPUS_DEMUX_NEED_INPUT);
        at += take;
    }
    assert(ogg_opus_demux_finish(&d) ==
           (finite ? 0 : OGG_OPUS_DEMUX_ERR_TRUNCATED));
    compare();
}

static void valid_chunks(const uint8_t *bytes, size_t size, size_t chunk) {
    valid_chunks_mode(bytes, size, chunk, false, true);
}

static void expect_error(int error) {
    ogg_opus_demux_t d;
    reset(&d);
    assert(feed_block(&d, wire, wire_size) == error);
    assert(ogg_opus_demux_finish(&d) == error);
    size_t consumed = SIZE_MAX;
    assert(ogg_opus_demux_feed(&d, wire, wire_size, &consumed,
                             capture, &actual) == error);
    assert(consumed == 0);
}

static void build_cross_pages(void) {
    uint8_t body[600];
    for (size_t i = 0; i < sizeof(body); ++i) body[i] = (uint8_t)(i * 13u + 5u);
    wire_size = 0;
    headers(1234);
    const uint8_t first[] = {1, 255};
    page(0, 1234, 2, 960, first, sizeof(first), body);
    /* An empty page does not lose the carried packet, regardless of its
     * continued flag: it contains no packet data to continue. */
    page(0, 1234, 3, UINT64_MAX, NULL, 0, NULL);
    const uint8_t second[] = {52, 255, 0, 1};
    page(5, 1234, 4, 3740, second, sizeof(second), body + 256);
}

static void test_fragmentation_and_timing(void) {
    build_cross_pages();
    reference(wire, wire_size);
    assert(expected.count == 6);
    assert(expected.records[2].last && expected.records[2].granule == 960);
    assert(expected.records[3].size == 307 && !expected.records[3].last);
    assert(expected.records[4].size == 255 && !expected.records[4].last);
    assert(expected.records[5].last && expected.records[5].eos);
    assert(expected.records[5].granule == 3740); /* Pass through EOS trim GP. */
    for (size_t split = 0; split <= wire_size; ++split) {
        ogg_opus_demux_t d;
        reset(&d);
        assert(feed_block(&d, wire, split) == OGG_OPUS_DEMUX_NEED_INPUT);
        assert(feed_block(&d, wire + split, wire_size - split) ==
               OGG_OPUS_DEMUX_NEED_INPUT);
        assert(ogg_opus_demux_finish(&d) == 0);
        compare();
    }
    for (size_t chunk = 1; chunk <= 301; chunk += 7)
        valid_chunks(wire, wire_size, chunk);
    ogg_opus_demux_t d;
    reset(&d);
    size_t used = 0;
    assert(ogg_opus_demux_feed(&d, wire, wire_size, &used, capture, &actual) == 0);
    assert(used == 47 && actual.count == 1); /* Exactly one packet per call. */
    for (size_t end = 0; end < wire_size; ++end) {
        reset(&d);
        assert(feed_block(&d, wire, end) == OGG_OPUS_DEMUX_NEED_INPUT);
        assert(ogg_opus_demux_finish(&d) == OGG_OPUS_DEMUX_ERR_TRUNCATED);
    }
    puts("fragmentation, continuation, zero laces and EOS metadata passed");
}

static void test_chains_and_empty_pages(void) {
    wire_size = 0;
    const uint8_t audio = 0xf8;
    headers(11);
    page(0, 11, 2, UINT64_MAX, NULL, 0, NULL);
    one_packet(4, 11, 3, 700, &audio, 1);
    headers(22);
    one_packet(0, 22, 2, 960, &audio, 1);
    page(4, 22, 3, UINT64_MAX, NULL, 0, NULL);
    reference(wire, wire_size);
    valid_chunks(wire, wire_size, 1);
    assert(actual.count == 6 && actual.records[3].start);
    assert(actual.records[3].index == 0 && actual.records[3].serial == 22);
    /* Exercise the wire counter's specified rollover without billions of pages. */
    ogg_opus_demux_t d;
    reset(&d);
    wire_size = 0;
    headers(33);
    assert(feed_block(&d, wire, wire_size) == OGG_OPUS_DEMUX_NEED_INPUT);
    d.next_sequence = UINT32_MAX;
    wire_size = 0;
    one_packet(0, 33, UINT32_MAX, 960, &audio, 1);
    one_packet(4, 33, 0, 1900, &audio, 1);
    assert(feed_block(&d, wire, wire_size) == OGG_OPUS_DEMUX_NEED_INPUT);
    assert(ogg_opus_demux_finish(&d) == 0 && d.next_sequence == 1);
    puts("chains, empty pages and sequence wrap passed");
}

static void build_long_tags(size_t size) {
    wire_size = 0;
    one_packet(2, 51, 0, 0, head, sizeof(head));
    memset(reference_packet, 0, size);
    memcpy(reference_packet, tags, sizeof(tags));
    size_t offset = 0;
    uint32_t seq = 1;
    bool done = false;
    while (!done) {
        uint8_t laces[255];
        size_t count = 0, body_size = 0;
        while (count < sizeof(laces)) {
            const size_t remaining = size - offset - body_size;
            const uint8_t lace = remaining < 255 ? (uint8_t)remaining : 255;
            laces[count++] = lace;
            body_size += lace;
            if (lace < 255) { done = true; break; }
        }
        page(offset ? 1 : 0, 51, seq++, done ? 0 : UINT64_MAX,
             laces, count, reference_packet + offset);
        offset += body_size;
    }
    const uint8_t audio = 0xf8;
    one_packet(4, 51, seq, 960, &audio, 1);
}

static void test_limits_and_many_packets(void) {
    build_long_tags(OGG_OPUS_TAG_MAX_BYTES);
    reference(wire, wire_size);
    valid_chunks(wire, wire_size, 73);
    assert(actual.records[1].size == OGG_OPUS_TAG_MAX_BYTES);
    assert(actual.records[1].stored == 16);
    build_long_tags(OGG_OPUS_TAG_MAX_BYTES + 1u);
    expect_error(OGG_OPUS_DEMUX_ERR_PACKET_TOO_LARGE);
    uint8_t data[OGG_OPUS_PACKET_BYTES + 1u];
    memset(data, 0xa5, sizeof(data));
    wire_size = 0;
    headers(1);
    one_packet(4, 1, 2, 960, data, OGG_OPUS_PACKET_BYTES);
    reference(wire, wire_size);
    valid_chunks(wire, wire_size, 17);
    wire_size = 0;
    headers(1);
    one_packet(4, 1, 2, 960, data, sizeof(data));
    expect_error(OGG_OPUS_DEMUX_ERR_PACKET_TOO_LARGE);
    wire_size = 0;
    memcpy(data, head, sizeof(head));
    one_packet(2, 1, 0, 0, data, sizeof(data));
    expect_error(OGG_OPUS_DEMUX_ERR_PACKET_TOO_LARGE);
    wire_size = 0;
    headers(1);
    uint8_t laces[255];
    memset(laces, 1, sizeof(laces));
    page(4, 1, 2, 255u * 960u, laces, sizeof(laces), data);
    reference(wire, wire_size);
    valid_chunks(wire, wire_size, 1);
    assert(actual.count == 257);
    puts("packet bounds, 1 MiB tags and 255 packet pages passed");
}

static void test_crc_delivery_contract(void) {
    const uint8_t data[] = {0xf8, 0xf9};
    const uint8_t laces[] = {1, 1};
    wire_size = 0;
    headers(1);
    const size_t at = page(4, 1, 2, 1900, laces, 2, data);
    wire[wire_size - 1] ^= 1;
    expect_error(OGG_OPUS_DEMUX_ERR_CRC);
    assert(actual.count == 3); /* Earlier packet emitted; final withheld. */
    assert(actual.records[2].index == 2 && !actual.records[2].last);
    wire[wire_size - 1] ^= 1;
    wire[at + 22] ^= 1; /* Corrupt checksum field rather than packet bytes. */
    expect_error(OGG_OPUS_DEMUX_ERR_CRC);
    assert(actual.count == 3);
    build_cross_pages();
    const size_t audio_page = 47 + 44;
    wire[audio_page + page_length(audio_page) - 1] ^= 1;
    expect_error(OGG_OPUS_DEMUX_ERR_CRC);
    assert(actual.count == 3 && actual.records[2].last);
    ogg_opus_demux_t d;
    reset(&d);
    size_t offset = 0, used;
    const size_t packet_bytes[] = {47, 44, 30};
    for (size_t i = 0; i < sizeof(packet_bytes) / sizeof(packet_bytes[0]); ++i) {
        assert(ogg_opus_demux_feed(&d, wire + offset, wire_size - offset,
                                  &used, capture, &actual) == 0);
        assert(used == packet_bytes[i]);
        offset += used;
    }
    assert(ogg_opus_demux_feed(&d, wire + offset, wire_size - offset,
                              &used, capture, &actual) == OGG_OPUS_DEMUX_ERR_CRC);
    assert(used == 255); /* Stop at bad page end; leave subsequent input alone. */
    /* Last COMPLETE packet precedes an unfinished tail: it cannot be held
     * with only one packet buffer. The API explicitly documents this case. */
    wire_size = 0;
    one_packet(2, 1, 0, 0, head, sizeof(head));
    wire[wire_size - 1] ^= 1;
    expect_error(OGG_OPUS_DEMUX_ERR_CRC);
    assert(actual.count == 0);
    puts("CRC failure withholding and streaming delivery contract passed");
}

static void test_invalid_framing(void) {
    const uint8_t audio = 0xf8;
    wire_size = 0;
    headers(1);
    const size_t at = one_packet(4, 1, 2, 960, &audio, 1);
    const size_t total = wire_size;
    memcpy(saved, wire, total);
    struct mutation { size_t offset; uint8_t value; int error; } mutations[] = {
        {0, 'X', OGG_OPUS_DEMUX_ERR_FORMAT},
        {4, 1, OGG_OPUS_DEMUX_ERR_FORMAT},
        {5, 0x82, OGG_OPUS_DEMUX_ERR_FORMAT},
        {5, 0, OGG_OPUS_DEMUX_ERR_FORMAT},
        {18, 1, OGG_OPUS_DEMUX_ERR_SEQUENCE},
        {at + 18, 3, OGG_OPUS_DEMUX_ERR_SEQUENCE},
        {at + 14, 2, OGG_OPUS_DEMUX_ERR_SERIAL},
        {at + 5, 6, OGG_OPUS_DEMUX_ERR_FORMAT},
        {at + 5, 5, OGG_OPUS_DEMUX_ERR_CONTINUATION},
        {6, 1, OGG_OPUS_DEMUX_ERR_FORMAT},
        {47 + 6, 1, OGG_OPUS_DEMUX_ERR_FORMAT},
    };
    for (size_t i = 0; i < sizeof(mutations) / sizeof(mutations[0]); ++i) {
        memcpy(wire, saved, total);
        wire[mutations[i].offset] = mutations[i].value;
        expect_error(mutations[i].error);
    }
    memcpy(wire, saved, total);
    wire[at + 5] = 0; refresh_crc(at); /* Clean boundary without EOS. */
    ogg_opus_demux_t d;
    reset(&d);
    assert(feed_block(&d, wire, wire_size) == OGG_OPUS_DEMUX_NEED_INPUT);
    assert(ogg_opus_demux_finish(&d) == OGG_OPUS_DEMUX_ERR_TRUNCATED);
    build_cross_pages();
    const size_t last = 47 + 44 + (27 + 2 + 256) + 27;
    wire[last + 5] = 4;
    expect_error(OGG_OPUS_DEMUX_ERR_CONTINUATION);
    build_cross_pages();
    wire[47 + 44 + 5] = 4; /* EOS cannot have a partial packet tail. */
    expect_error(OGG_OPUS_DEMUX_ERR_CONTINUATION);
    wire_size = 0;
    page(2, 1, 0, UINT64_MAX, NULL, 0, NULL);
    expect_error(OGG_OPUS_DEMUX_ERR_FORMAT);
    wire_size = 0;
    headers(1);
    one_packet(4, 1, 2, 960, NULL, 0);
    expect_error(OGG_OPUS_DEMUX_ERR_FORMAT);
    wire_size = 0;
    headers(1);
    one_packet(4, 1, 2, 960, &audio, 1);
    headers(1); /* Adjacent chains must have distinct stream serials. */
    expect_error(OGG_OPUS_DEMUX_ERR_SERIAL);
    wire_size = 0;
    headers(1);
    one_packet(4, 1, 2, UINT64_MAX, &audio, 1);
    expect_error(OGG_OPUS_DEMUX_ERR_FORMAT);
    puts("invalid capture, version, flags, sequence, serial and continuation passed");
}

static void test_header_bounds_and_cancellation(void) {
    uint8_t bytes[300];
    memset(bytes, 0, sizeof(bytes));
    memcpy(bytes, head, sizeof(head));
    wire_size = 0;
    one_packet(2, 1, 0, 0, bytes, 18);
    expect_error(OGG_OPUS_DEMUX_ERR_FORMAT);
    bytes[0] = 'X';
    wire_size = 0;
    one_packet(2, 1, 0, 0, bytes, 19);
    expect_error(OGG_OPUS_DEMUX_ERR_FORMAT);
    for (unsigned invalid = 0; invalid < 3; ++invalid) {
        wire_size = 0;
        one_packet(2, 1, 0, 0, head, sizeof(head));
        memcpy(bytes, tags, sizeof(tags));
        if (invalid == 0) bytes[0] = 'X';
        if (invalid == 1) bytes[8] = 1; /* Vendor field exceeds packet bounds. */
        one_packet(0, 1, 1, 0, bytes, invalid == 2 ? 15 : 16);
        expect_error(OGG_OPUS_DEMUX_ERR_FORMAT);
    }
    wire_size = 0;
    memcpy(bytes, head, sizeof(head));
    const uint8_t two[] = {19, 1};
    page(2, 1, 0, 0, two, 2, bytes);
    expect_error(OGG_OPUS_DEMUX_ERR_FORMAT);
    wire_size = 0;
    one_packet(2, 1, 0, 0, head, sizeof(head));
    memcpy(bytes, tags, sizeof(tags));
    const uint8_t tag_audio[] = {16, 1};
    page(0, 1, 1, 0, tag_audio, 2, bytes);
    expect_error(OGG_OPUS_DEMUX_ERR_FORMAT);
    build_cross_pages();
    ogg_opus_demux_t d;
    reset(&d);
    actual.cancel_at = 3;
    assert(feed_block(&d, wire, wire_size) == -77);
    assert(actual.count == 3 && ogg_opus_demux_finish(&d) == -77);
    size_t used = 123;
    assert(ogg_opus_demux_feed(&d, wire, wire_size, &used, capture, &actual) == -77);
    assert(used == 0 && actual.count == 3);
    reset(&d);
    assert(ogg_opus_demux_feed(NULL, wire, 1, &used, capture, &actual) == -1);
    assert(used == 0);
    assert(ogg_opus_demux_feed(&d, NULL, 1, &used, capture, &actual) == -1);
    assert(ogg_opus_demux_feed(&d, wire, 1, NULL, capture, &actual) == -1);
    assert(ogg_opus_demux_feed(&d, wire, 1, &used, NULL, &actual) == -1);
    assert(ogg_opus_demux_feed(&d, NULL, 0, &used, capture, &actual) == 1);
    assert(ogg_opus_demux_finish(NULL) == -1);
    puts("header bounds, cancellation and argument contracts passed");
}

static uint32_t random_state = 0x65b18ec4u;

static uint32_t random_u32(void) {
    random_state ^= random_state << 13;
    random_state ^= random_state >> 17;
    random_state ^= random_state << 5;
    return random_state;
}

static void test_generated_page_boundaries(void) {
    for (unsigned trial = 0; trial < 24; ++trial) {
        uint8_t laces[64u * 7u];
        size_t lace_count = 0, bytes = 0;
        for (unsigned packet = 0; packet < 64; ++packet) {
            size_t size = random_u32() % OGG_OPUS_PACKET_BYTES + 1u;
            if (packet % 8 == 0) size = 255;
            if (packet % 8 == 1) size = 510;
            if (packet % 8 == 2) size = 1530;
            if (packet % 8 == 3) size = 1536;
            for (size_t i = 0; i < size; ++i)
                reference_packet[bytes++] = (uint8_t)random_u32();
            while (size >= 255) { laces[lace_count++] = 255; size -= 255; }
            laces[lace_count++] = (uint8_t)size;
        }
        wire_size = 0;
        headers(987);
        size_t at = 0, body_at = 0;
        uint32_t seq = 2, complete = 0;
        while (at < lace_count) {
            size_t count = random_u32() % 15u + 1u;
            if (count > lace_count - at) count = lace_count - at;
            const uint8_t continued = at && laces[at - 1] == 255 ? 1 : 0;
            if ((random_u32() & 3u) == 0)
                page((uint8_t)(random_u32() & 1u), 987, seq++, UINT64_MAX,
                     NULL, 0, NULL);
            const uint32_t previous_complete = complete;
            size_t body_size = 0;
            for (size_t i = 0; i < count; ++i) {
                body_size += laces[at + i];
                if (laces[at + i] < 255) ++complete;
            }
            const bool eos = at + count == lace_count;
            const uint64_t gp = complete == previous_complete ? UINT64_MAX :
                                complete * 960u - (eos ? 123u : 0u);
            page(continued | (eos ? 4 : 0), 987, seq++, gp,
                 laces + at, count, reference_packet + body_at);
            at += count; body_at += body_size;
        }
        assert(body_at == bytes && complete == 64);
        reference(wire, wire_size);
        valid_chunks(wire, wire_size, random_u32() % 257u + 1u);
    }
    /* Deterministic corruption corpus runs through the same bounded parser
     * under ASan/UBSan; malformed input must terminate or request more bytes. */
    build_cross_pages();
    const size_t size = wire_size;
    memcpy(saved, wire, size);
    for (unsigned trial = 0; trial < 2000; ++trial) {
        memcpy(wire, saved, size);
        for (unsigned flip = 0; flip <= trial % 3; ++flip)
            wire[random_u32() % size] ^= (uint8_t)(1u << (random_u32() % 8u));
        ogg_opus_demux_t d;
        reset(&d);
        for (size_t at = 0; at < size;) {
            size_t take = random_u32() % 79u + 1u;
            if (take > size - at) take = size - at;
            if (feed_block(&d, wire + at, take) < 0) break;
            at += take;
        }
    }
    puts("generated page boundaries and 2000 malformed streams passed");
}

static size_t build_live_join(void) {
    /* Reproduce IntenseRadio's cached header pages and live sequence jump:
     * 47-byte Head, 105-byte Tags, then seq2534 with five 140-byte packets.
     * These are synthetic packet bytes; the optional capture test below
     * also verifies every packet in the unmodified recorded radio stream. */
    uint8_t metadata[77] = {0}, audio[700];
    const uint8_t laces[] = {140, 140, 140, 140, 140};
    memcpy(metadata, tags, sizeof(tags));
    memset(audio, 0xfc, sizeof(audio));
    wire_size = 0;
    one_packet(2, 0x800004aau, 0, 0, head, sizeof(head));
    one_packet(0, 0x800004aau, 1, 0, metadata, sizeof(metadata));
    const size_t at = page(0, 0x800004aau, 2534, UINT64_C(10522378560),
                           laces, sizeof(laces), audio);
    page(4, 0x800004aau, 2535, UINT64_C(10522383360),
         laces, sizeof(laces), audio);
    return at;
}

static void live_error(int error) {
    ogg_opus_demux_t d;
    reset(&d);
    ogg_opus_demux_init_ex(&d, true);
    assert(feed_block(&d, wire, wire_size) == error);
    assert(ogg_opus_demux_finish(&d) == error);
}

static void test_live_join(void) {
    const size_t first = build_live_join();
    assert(first == 152);
    expect_error(OGG_OPUS_DEMUX_ERR_SEQUENCE);
    assert(actual.count == 2); /* Old failure: headers delivered, no audio. */
    reference(wire, wire_size);
    const size_t chunks[] = {1, 2, 7, 27, 140, 255, 1024, 1536, WIRE_CAPACITY};
    for (size_t i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i)
        valid_chunks_mode(wire, wire_size, chunks[i], true, true);
    assert(actual.count == 12 && actual.records[6].last);
    assert(actual.records[6].granule == UINT64_C(10522378560));
    const size_t next = first + page_length(first);
    put32(wire + next + 18, 2537); refresh_crc(next);
    live_error(OGG_OPUS_DEMUX_ERR_SEQUENCE); /* No holes after baseline. */
    assert(actual.count == 7);
    build_live_join(); wire[first + 5] = 1; refresh_crc(first);
    live_error(OGG_OPUS_DEMUX_ERR_SEQUENCE); /* No partial first packet. */
    build_live_join(); wire[first + 14] ^= 1; refresh_crc(first);
    live_error(OGG_OPUS_DEMUX_ERR_SERIAL);
    build_live_join(); wire[first + 22] ^= 1;
    live_error(OGG_OPUS_DEMUX_ERR_CRC);
    assert(actual.count == 6); /* Last packet still waits for CRC. */
    build_live_join(); put32(wire + first + 18, 1); refresh_crc(first);
    live_error(OGG_OPUS_DEMUX_ERR_SEQUENCE);
    build_live_join(); put32(wire + 47 + 18, 5); refresh_crc(47);
    live_error(OGG_OPUS_DEMUX_ERR_SEQUENCE); /* Headers remain strict. */
    uint8_t body[256] = {0};
    const uint8_t tail[] = {1, 255};
    wire_size = 0; headers(1);
    page(0, 1, 2534, 960, tail, 2, body);
    live_error(OGG_OPUS_DEMUX_ERR_SEQUENCE); /* Unsupported partial tail. */
    assert(actual.count == 2);
    wire_size = 0; headers(1);
    page(0, 1, 2, UINT64_MAX, NULL, 0, NULL);
    one_packet(4, 1, 2534, 960, body, 1);
    live_error(OGG_OPUS_DEMUX_ERR_SEQUENCE); /* Empty page used the chance. */
    wire_size = 0; headers(1);
    page(0, 1, 2, 960, tail, 2, body);
    const uint8_t final_laces[] = {1};
    page(5, 1, 2534, 1920, final_laces, 1, body);
    live_error(OGG_OPUS_DEMUX_ERR_SEQUENCE); /* No resync inside a packet. */
    wire_size = 0; headers(1);
    one_packet(4, 1, UINT32_MAX, 960, body, 1);
    headers(2);
    one_packet(0, 2, UINT32_MAX, 960, body, 1);
    one_packet(4, 2, 0, 1920, body, 1);
    reference(wire, wire_size);
    valid_chunks_mode(wire, wire_size, 1024, true, true); /* Chain and wrap. */
    puts("live join opt-in, strict rejection, 1024-byte input and later holes passed");
}

static void test_live_capture(const char *filename) {
    FILE *file = fopen(filename, "rb");
    assert(file);
    wire_size = fread(wire, 1, sizeof(wire), file);
    assert(!ferror(file) && wire_size < sizeof(wire));
    assert(fclose(file) == 0);
    reference(wire, wire_size);
    expect_error(OGG_OPUS_DEMUX_ERR_SEQUENCE);
    assert(actual.count == 2);
    const size_t chunks[] = {1, 7, 255, 1024, 1536, WIRE_CAPACITY};
    for (size_t i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i)
        valid_chunks_mode(wire, wire_size, chunks[i], true, false);
    printf("live capture packets identical: %s (%zu bytes, %zu packets)\n",
           filename, wire_size, actual.count);
}

static void test_fixture(const char *filename) {
    FILE *file = fopen(filename, "rb");
    assert(file);
    wire_size = fread(wire, 1, sizeof(wire), file);
    assert(!ferror(file) && wire_size < sizeof(wire));
    assert(fclose(file) == 0);
    reference(wire, wire_size);
    assert(expected.count > 2);
    const size_t chunks[] = {1, 2, 7, 27, 255, 1024, 1536, 4096, WIRE_CAPACITY};
    for (size_t i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i)
        valid_chunks(wire, wire_size, chunks[i]);
    printf("fixture packets identical: %s (%zu packets)\n", filename, actual.count);
}

int main(int argc, char **argv) {
    assert(sizeof(ogg_opus_demux_t) < 1900);
    test_fragmentation_and_timing();
    test_chains_and_empty_pages();
    test_limits_and_many_packets();
    test_crc_delivery_contract();
    test_invalid_framing();
    test_header_bounds_and_cancellation();
    test_generated_page_boundaries();
    test_live_join();
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--live-capture") == 0) {
            assert(i + 1 < argc);
            test_live_capture(argv[++i]);
        } else test_fixture(argv[i]);
    }
    printf("Ogg Opus demux tests passed; state bytes: %zu\n", sizeof(ogg_opus_demux_t));
    return 0;
}
