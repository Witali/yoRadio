#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned allocation_calls, fail_allocation, live_allocations;
static size_t maximum_request;
static void *page_allocate(void *old, size_t bytes)
{
    ++allocation_calls;
    if (bytes > maximum_request) maximum_request = bytes;
    if (allocation_calls == fail_allocation) return NULL;
    void *p = realloc(old, bytes);
    if (p && !old) ++live_allocations;
    return p;
}
static void page_free(void *p)
{
    if (p) { assert(live_allocations); --live_allocations; }
    free(p);
}
#define OGG_PAGE_INPUT_REALLOC page_allocate
#define OGG_PAGE_INPUT_FREE page_free
#include "ogg_page_input.h"
#include "opus_pcm_trim.h"

/* Reuse the independently constructed CRC/page fixtures and run the complete
 * original observer suite too; none of its sources or saved captures change.
 */
#define main original_timeline_main
#include "ogg_opus_timeline_host.c"
#undef main

static unsigned page_cases, trim_cases, refused_allocations;

static unsigned scan_pages(const buffer *b, size_t chunk, bool poison,
                           bool recover_oom, ogg_page_input_status expected)
{
    ogg_page_input owner = {0};
    opi_reset(&owner, 99);
    size_t at = 0, page_at = 0;
    unsigned pages = 0;
    ogg_page_input_status status = OPI_MORE;
    while (at < b->n) {
        size_t take = b->n - at;
        if (take > chunk) take = chunk;
        uint8_t *borrow = malloc(take);
        assert(borrow);
        memcpy(borrow, b->p + at, take);
        size_t used = SIZE_MAX;
        status = opi_feed(&owner, borrow, take, &used);
        assert(used <= take);
        if (poison) memset(borrow, 0xa5, take);
        free(borrow);
        at += used;
        if (status == OPI_NO_MEMORY && recover_oom) {
            ++refused_allocations;
            fail_allocation = 0;
            continue;
        }
        if (status < 0) break;
        if (status == OPI_PAGE) {
            assert(owner.ready && owner.event.crc_verified);
            assert(owner.size == at - page_at && owner.size <= OGG_PAGE_INPUT_MAX);
            assert(!memcmp(owner.page, b->p + page_at, owner.size));
            uint64_t token = owner.event.token;
            size_t blocked = SIZE_MAX;
            assert(opi_feed(&owner, b->p + at, b->n - at, &blocked) == OPI_PAGE);
            assert(blocked == 0 && owner.event.token == token);
            assert(!opi_ack(&owner, 98, token) && !opi_ack(&owner, 99, token + 1));
            assert(opi_ack(&owner, 99, token) && !opi_ack(&owner, 99, token));
            ++pages;
            page_at = at;
        } else assert(used);
    }
    if (status >= 0) status = opi_finish(&owner);
    assert(status == expected);
    opi_reset(&owner, 99);
    assert(!owner.page && !owner.capacity && !owner.ready && !live_allocations);
    ++page_cases;
    return pages;
}

static void pages_and_oom(const char *path)
{
    buffer b = load(path);
    const size_t chunks[] = {SIZE_MAX, 4096, 257, 1};
    unsigned baseline_pages = 0;
    for (unsigned i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i) {
        allocation_calls = 0;
        unsigned pages = scan_pages(&b, chunks[i], true, false, OPI_FINISHED);
        if (!i) baseline_pages = pages;
        else assert(pages == baseline_pages);
    }
    unsigned calls = allocation_calls;
    for (unsigned fail = 1; fail <= calls; ++fail) {
        allocation_calls = 0;
        fail_allocation = fail;
        assert(scan_pages(&b, 4096, true, true, OPI_FINISHED) == baseline_pages);
        assert(!fail_allocation);
        allocation_calls = 0;
        fail_allocation = fail;
        scan_pages(&b, 4096, true, false, OPI_NO_MEMORY);
        fail_allocation = 0;
    }
    printf("{\"page_fixture\":true,\"bytes\":%zu,\"pages\":%u,"
           "\"allocation_ordinals\":%u,\"passed\":true}\n", b.n, baseline_pages, calls);
    free(b.p);
}

static void boundaries_and_crc(void)
{
    uint8_t plc = 0xf8;
    buffer b = stream(312, 960, &plc, 1);
    for (size_t cut = 0; cut < b.n; ++cut) {
        buffer prefix = {b.p, cut, cut};
        scan_pages(&prefix, 1, true, false, OPI_TRUNCATED);
    }
    for (size_t cut = 0; cut <= b.n; ++cut) {
        ogg_page_input owner = {0};
        opi_reset(&owner, 7);
        size_t at = 0;
        while (at < cut) {
            size_t used;
            ogg_page_input_status status = opi_feed(&owner, b.p + at, cut - at, &used);
            assert(status >= 0);
            at += used;
            if (status == OPI_PAGE)
                assert(opi_ack(&owner, 7, owner.event.token));
        }
        opi_reset(&owner, 7);
        assert(!live_allocations);
        size_t used;
        assert(opi_feed(&owner, b.p, b.n, &used) == OPI_PAGE);
        uint64_t old = owner.event.token;
        opi_reset(&owner, 7);
        assert(opi_feed(&owner, b.p, b.n, &used) == OPI_PAGE);
        assert(!opi_ack(&owner, 7, old));
        assert(opi_ack(&owner, 7, owner.event.token));
        opi_reset(&owner, 7);
        ++page_cases;
    }
    b.p[b.n - 1] ^= 1;
    assert(scan_pages(&b, 1, false, false, OPI_INVALID) == 2);
    free(b.p);

    /* Multiple logical links in one borrowed input, including a bypass link.
     * Each verified LINK_END remains pending until its own explicit ACK.
     */
    b = stream(312, 960, &plc, 1);
    uint8_t other = 0;
    packet_page(&b, 78, 0, 6, 0, &other, 1);
    headers(&b, 79, 1, 0, 1, 1);
    packet_page(&b, 79, 2, 4, 960, &plc, 1);
    assert(scan_pages(&b, SIZE_MAX, true, false, OPI_FINISHED) == 7);
    free(b.p);

    /* The largest legal page remains bounded even with a continued packet. */
    b = new_buffer(OGG_PAGE_INPUT_MAX + 64);
    uint8_t *payload = calloc(255u * 255u, 1);
    uint8_t laces[255];
    assert(payload);
    memset(laces, 255, sizeof(laces));
    page(&b, 88, 0, 2, UINT64_MAX, laces, 255, payload, 255u * 255u);
    uint8_t zero = 0;
    page(&b, 88, 1, 5, 0, &zero, 1, NULL, 0);
    assert(scan_pages(&b, 257, true, false, OPI_FINISHED) == 2);
    assert(maximum_request == OGG_PAGE_INPUT_MAX);
    free(payload);
    free(b.p);

    ogg_page_input owner = {0};
    opi_reset(&owner, 1);
    size_t used = 3;
    assert(opi_feed(&owner, NULL, 1, &used) == OPI_INVALID && used == 0);
    assert(opi_feed(&owner, NULL, 0, NULL) == OPI_INVALID);
    opi_reset(&owner, 1);
}

static void clipping_model(unsigned channels, unsigned bits, uint64_t total,
                            unsigned skip, uint64_t end)
{
    opus_pcm_trim trim = {0};
    assert(opt_begin(&trim, 55, (uint16_t)skip, (uint8_t)channels) == OPT_OK);
    assert(opt_end(&trim, 55, end, total) == OPT_OK);
    uint64_t at = 0, sent = 0;
    size_t width = channels * (bits / 8u);
    while (at < total) {
        uint64_t frames = 1u + (at * 17u + channels) % 577u;
        if (frames > total - at) frames = total - at;
        size_t bytes = (size_t)frames * width;
        opus_pcm_span span = {SIZE_MAX, SIZE_MAX};
        assert(opt_clip(&trim, 55, 48000, (uint8_t)channels,
                        (uint8_t)bits, bytes, &span) == OPT_OK);
        assert(span.offset <= bytes && span.size <= bytes - span.offset);
        uint64_t first = at < skip ? skip : at;
        uint64_t last = at + frames > end ? end : at + frames;
        uint64_t expected = first < last ? last - first : 0;
        assert(span.size == expected * width);
        if (expected) assert(span.offset == (first - at) * width);
        sent += span.size / width;
        at += frames;
    }
    assert(sent == (end > skip ? end - skip : 0));
    assert(trim.raw_position == total && opt_finish(&trim, 55) == OPT_OK);
    opt_reset(&trim);
    ++trim_cases;
}

static void clipping(void)
{
    const unsigned skips[] = {0, 1, 312, 65535};
    const unsigned channels[] = {1, 2, 8, 255};
    const unsigned bits[] = {8, 16, 24, 32};
    for (unsigned s = 0; s < 4; ++s)
        for (unsigned c = 0; c < 4; ++c)
            for (unsigned b = 0; b < 4; ++b) {
                clipping_model(channels[c], bits[b], 70000, skips[s], 68903);
                clipping_model(channels[c], bits[b], 960, skips[s], 0);
                clipping_model(channels[c], bits[b], 960, skips[s], 501);
            }
    opus_pcm_trim trim = {0}, before;
    opus_pcm_span span = {9, 10}, unchanged = span;
    assert(opt_begin(&trim, 7, 312, 2) == OPT_OK);
    before = trim;
    assert(opt_clip(&trim, 8, 48000, 2, 16, 100, &span) == OPT_INVALID);
    assert(opt_clip(&trim, 7, 24000, 2, 16, 100, &span) == OPT_INVALID);
    assert(opt_clip(&trim, 7, 48000, 1, 16, 100, &span) == OPT_INVALID);
    assert(opt_clip(&trim, 7, 48000, 2, 20, 100, &span) == OPT_INVALID);
    assert(opt_clip(&trim, 7, 48000, 2, 16, 101, &span) == OPT_UNALIGNED);
    assert(!memcmp(&trim, &before, sizeof(trim)) && !memcmp(&span, &unchanged, sizeof(span)));
    assert(opt_clip(&trim, 7, 48000, 2, 16, 4000, &span) == OPT_OK);
    before = trim;
    assert(opt_end(&trim, 7, 900, 1200) == OPT_UNALIGNED);
    assert(!memcmp(&trim, &before, sizeof(trim)));
    assert(opt_end(&trim, 7, 1100, 1200) == OPT_OK);
    assert(opt_clip(&trim, 7, 48000, 2, 16, 800, &span) == OPT_OK);
    assert(span.size == 400 && opt_finish(&trim, 7) == OPT_OK);
    before = trim;
    assert(opt_clip(&trim, 7, 48000, 2, 16, 4, &span) == OPT_UNALIGNED);
    assert(!memcmp(&trim, &before, sizeof(trim)));
    opt_reset(&trim);
    assert(opt_begin(&trim, 1, 0, 2) == OPT_OK);
    trim.raw_position = UINT64_MAX - 10u;
    before = trim;
    assert(opt_clip(&trim, 1, 48000, 2, 16, 44, &span) == OPT_LIMIT);
    assert(!memcmp(&trim, &before, sizeof(trim)));
    trim_cases += 12;
}

int main(int argc, char **argv)
{
    assert(argc == 3);
    assert(original_timeline_main(argc, argv) == 0);
    pages_and_oom(argv[1]);
    pages_and_oom(argv[2]);
    boundaries_and_crc();
    clipping();
    assert(!live_allocations);
    printf("{\"suite\":\"ogg-page-input-host\",\"passed\":true,\"page_cases\":%u,"
           "\"trim_cases\":%u,\"allocation_refusals\":%u,\"max_page_bytes\":%zu,"
           "\"production_integrated\":false}\n", page_cases, trim_cases,
           refused_allocations, maximum_request);
    return 0;
}
