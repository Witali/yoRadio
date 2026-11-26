#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define json_buffer_t original_json_buffer_t
#define json_buffer_init original_json_buffer_init
#define json_buffer_bytes original_json_buffer_bytes
#define json_buffer_raw original_json_buffer_raw
#define json_buffer_string original_json_buffer_string
#define json_utf8_sequence original_json_utf8_sequence
#include "original_json_buffer.h"
#undef json_buffer_t
#undef json_buffer_init
#undef json_buffer_bytes
#undef json_buffer_raw
#undef json_buffer_string
#undef json_utf8_sequence

#include "json_buffer.h"
#include "json_sink.h"

#define CHECK(value, label) do { if (!(value)) { fprintf(stderr, "FAIL %s at %s:%d\n", label, __FILE__, __LINE__); exit(42); } } while (0)
#define LIMIT 8192U
#define GUARD 16U

_Static_assert(sizeof(json_buffer_t) == sizeof(original_json_buffer_t), "Buffer layout size changed");
_Static_assert(_Alignof(json_buffer_t) == _Alignof(original_json_buffer_t), "Buffer alignment changed");
#define SAME_OFFSET(field) _Static_assert(offsetof(json_buffer_t, field) == offsetof(original_json_buffer_t, field), "Buffer field moved")
SAME_OFFSET(data); SAME_OFFSET(capacity); SAME_OFFSET(length); SAME_OFFSET(failed);

static size_t differential_cases;
static size_t groups;

typedef struct {
    char output[LIMIT];
    char stage[256];
    size_t used, staged, chunk, calls, fail_at;
    bool partial_failure;
} collector_t;

static void collector_flush(collector_t *out) {
    CHECK(out->staged <= out->chunk && out->chunk <= sizeof(out->stage), "bounded staging");
    CHECK(out->used <= LIMIT && out->staged <= LIMIT - out->used, "collector extent");
    memcpy(out->output + out->used, out->stage, out->staged);
    out->used += out->staged;
    out->staged = 0;
}

static bool collect(void *context, const char *data, size_t size) {
    collector_t *out = context;
    CHECK(size != 0, "zero-sized callback omitted");
    size_t call = out->calls++;
    if (call == out->fail_at) {
        if (out->partial_failure) {
            CHECK(out->staged < out->chunk, "partial stage extent");
            out->stage[out->staged++] = data[0];
            if (out->staged == out->chunk) collector_flush(out);
        }
        return false;
    }
    while (size) {
        size_t count = out->chunk - out->staged;
        if (count > size) count = size;
        memcpy(out->stage + out->staged, data, count);
        out->staged += count; data += count; size -= count;
        if (out->staged == out->chunk) collector_flush(out);
    }
    return true;
}

static collector_t fresh_collector(size_t chunk) {
    collector_t result;
    result.used = result.staged = result.calls = 0;
    result.chunk = chunk; result.fail_at = SIZE_MAX; result.partial_failure = false;
    return result;
}

static void original_message(original_json_buffer_t *out, const char *text) {
    const char binary[] = {'x', '\0', 'y'};
    original_json_buffer_raw(out, "{\"name\":");
    original_json_buffer_string(out, text);
    original_json_buffer_raw(out, ",\"number\":4294967295,\"raw\":");
    original_json_buffer_bytes(out, binary, sizeof(binary));
    original_json_buffer_raw(out, "}");
}

static void buffer_message(json_buffer_t *out, const char *text) {
    const char binary[] = {'x', '\0', 'y'};
    json_buffer_raw(out, "{\"name\":");
    json_buffer_string(out, text);
    json_buffer_raw(out, ",\"number\":4294967295,\"raw\":");
    json_buffer_bytes(out, binary, sizeof(binary));
    json_buffer_raw(out, "}");
}

static void sink_message(json_sink_t *out, const char *text) {
    const char binary[] = {'x', '\0', 'y'};
    json_sink_raw(out, "{\"name\":");
    json_sink_string(out, text);
    json_sink_raw(out, ",\"number\":4294967295,\"raw\":");
    json_sink_bytes(out, binary, sizeof(binary));
    json_sink_raw(out, "}");
}

static void differential(const char *text, size_t capacity, size_t chunk, bool message) {
    CHECK(capacity <= LIMIT && chunk && chunk <= 256, "test bounds");
    unsigned char old_data[LIMIT + 2 * GUARD], new_data[LIMIT + 2 * GUARD];
    memset(old_data, 0xa5, capacity + 2 * GUARD);
    memset(new_data, 0xa5, capacity + 2 * GUARD);
    original_json_buffer_t original;
    json_buffer_t candidate;
    json_sink_t sink, counter;
    collector_t out = fresh_collector(chunk);
    original_json_buffer_init(&original, (char *)old_data + GUARD, capacity);
    json_buffer_init(&candidate, (char *)new_data + GUARD, capacity);
    json_sink_init(&sink, capacity, collect, &out);
    json_sink_init(&counter, capacity, NULL, (void *)(uintptr_t)1);
    if (message) {
        original_message(&original, text); buffer_message(&candidate, text);
        sink_message(&sink, text); sink_message(&counter, text);
    } else {
        original_json_buffer_string(&original, text); json_buffer_string(&candidate, text);
        json_sink_string(&sink, text); json_sink_string(&counter, text);
    }
    collector_flush(&out);
    CHECK(original.capacity == candidate.capacity && original.length == candidate.length && original.failed == candidate.failed, "buffer state equivalence");
    CHECK(!memcmp(old_data, new_data, capacity + 2 * GUARD), "buffer bytes equivalence");
    for (size_t i = 0; i < GUARD; ++i) {
        CHECK(new_data[i] == 0xa5 && new_data[GUARD + capacity + i] == 0xa5, "buffer guards");
    }
    CHECK(sink.failed == original.failed && sink.length == original.length, "sink state equivalence");
    CHECK(counter.failed == original.failed && counter.length == original.length, "count state equivalence");
    CHECK(out.used == sink.length && !memcmp(out.output, old_data + GUARD, out.used), "sink bytes equivalence");
    if (!original.failed) CHECK(sink.length == counter.length && old_data[GUARD + original.length] == '\0', "count emitted bytes");
    ++differential_cases;
}

static void spans_and_layout(void) {
    struct vector { const char *input, *expected; size_t length, consumed; bool scratch; } vectors[] = {
        {"A", "A", 1, 1, false}, {"\"", "\\\"", 2, 1, true}, {"\\", "\\\\", 2, 1, true},
        {"\x01", "\\u0001", 6, 1, true}, {"\x1f", "\\u001f", 6, 1, true},
        {"\x7f", "\x7f", 1, 1, false}, {"\xc2\x80", "\xc2\x80", 2, 2, false},
        {"\xe2\x82\xac", "\xe2\x82\xac", 3, 3, false},
        {"\xf4\x8f\xbf\xbf", "\xf4\x8f\xbf\xbf", 4, 4, false},
        {"\x80", "\\ufffd", 6, 1, true}, {"\xc0\xaf", "\\ufffd", 6, 1, true},
        {"\xed\xa0\x80", "\\ufffd", 6, 1, true}, {"\xf4\x90\x80\x80", "\\ufffd", 6, 1, true},
    };
    for (size_t i = 0; i < sizeof(vectors) / sizeof(vectors[0]); ++i) {
        struct { char before[8], scratch[6], after[8]; } memory;
        memset(&memory, 0xa5, sizeof(memory));
        const uint8_t *cursor = (const uint8_t *)vectors[i].input;
        const char *span = NULL; size_t size = 0;
        CHECK(json_string_next_span(&cursor, memory.scratch, &span, &size), "span exists");
        CHECK(size == vectors[i].length && (size_t)(cursor - (const uint8_t *)vectors[i].input) == vectors[i].consumed, "span extent");
        CHECK(!memcmp(span, vectors[i].expected, size), "span encoding");
        CHECK(span == (vectors[i].scratch ? memory.scratch : vectors[i].input), "caller-owned span");
        for (size_t j = 0; j < sizeof(memory.before); ++j)
            CHECK((unsigned char)memory.before[j] == 0xa5 && (unsigned char)memory.after[j] == 0xa5, "six-byte scratch guards");
    }
    const uint8_t *end = (const uint8_t *)"";
    const uint8_t *saved = end; const char *span = (const char *)(uintptr_t)1; size_t size = 1; char scratch[6];
    CHECK(!json_string_next_span(&end, scratch, &span, &size) && end == saved && span == NULL && size == 0, "empty span");
    ++groups;
}

static void corpus_and_capacities(void) {
    const char *texts[] = {"", "plain ASCII", "quotes:\" and slash:\\", "\x01\x08\x09\x0a\x0d\x1f\x7f",
        "\xc2\x80\xdf\xbf\xe0\xa0\x80\xed\x9f\xbf\xf0\x90\x80\x80\xf4\x8f\xbf\xbf",
        "\xc0\xaf\xc1\x80\x80\xbf\xfe\xff", "\xe0\x80\x80\xed\xa0\x80\xf4\x90\x80\x80",
        "\xc2", "\xe2\x82", "\xf0\x90\x80", "\xf0Z\x80\xbf", "\xef\xbf\xbd"};
    for (size_t i = 0; i < sizeof(texts) / sizeof(texts[0]); ++i) {
        for (size_t capacity = 0; capacity <= 192; ++capacity)
            differential(texts[i], capacity, 1 + capacity % 7, false);
    }
    char controls[32]; for (size_t i = 1; i < sizeof(controls); ++i) controls[i - 1] = (char)i; controls[31] = 0;
    for (size_t cap = 0; cap <= 192; ++cap) differential(controls, cap, 5, false);
    char large[801]; memset(large, 1, sizeof(large) - 1); large[800] = 0;
    for (size_t cap = 0; cap <= 4804; ++cap) differential(large, cap, 256, false);
    char full[4913]; memset(full, 'x', sizeof(full) - 1); full[4912] = 0;
    for (size_t cap = 4908; cap <= 4917; ++cap) differential(full, cap, 31, false);
    ++groups;
}

static void exhaustive_and_truncation(void) {
    char text[3] = {1, 1, 0};
    for (unsigned a = 1; a <= 255; ++a) for (unsigned b = 1; b <= 255; ++b) {
        text[0] = (char)a; text[1] = (char)b; differential(text, 17, 1 + a % 7, false);
    }
    const uint8_t leads[] = {0xe0, 0xe1, 0xec, 0xed, 0xee, 0xef, 0xf0, 0xf1, 0xf3, 0xf4};
    const uint8_t seconds[] = {0x80, 0x8f, 0x90, 0x9f, 0xa0, 0xbf};
    for (size_t i = 0; i < sizeof(leads); ++i) for (size_t j = 0; j < sizeof(seconds); ++j) {
        uint8_t bytes[4] = {leads[i], seconds[j], 0x80, 0xbf};
        size_t maximum = leads[i] < 0xf0 ? 3 : 4;
        for (size_t length = 0; length <= maximum; ++length) {
            char *bounded = malloc(length + 1); CHECK(bounded != NULL, "test allocation");
            memcpy(bounded, bytes, length); bounded[length] = 0;
            for (size_t cap = 0; cap < 28; ++cap) differential(bounded, cap, 3, false);
            free(bounded);
        }
    }
    ++groups;
}

static void split_messages(void) {
    const char *text = "a\x01\"\\\xe2\x82\xac\xf0\x90\x80\x80\xff";
    const size_t chunks[] = {1, 2, 3, 4, 5, 6, 7, 15, 31, 255, 256};
    for (size_t i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i)
        for (size_t cap = 0; cap < 160; ++cap) differential(text, cap, chunks[i], true);
    ++groups;
}

static void failures_are_sticky(void) {
    const char *text = "x\x01\"\\\xe2\x82\xac\xff";
    collector_t good = fresh_collector(3); json_sink_t output;
    json_sink_init(&output, LIMIT, collect, &good); json_sink_string(&output, text);
    CHECK(!output.failed && good.calls > 3, "failure reference");
    for (size_t failure = 0; failure < good.calls; ++failure) {
        collector_t out = fresh_collector(3); out.fail_at = failure;
        json_sink_init(&output, LIMIT, collect, &out); json_sink_string(&output, text);
        CHECK(output.failed && out.calls == failure + 1, "writer failure propagated");
        collector_flush(&out); CHECK(out.used == output.length, "only completed spans counted");
        size_t length = output.length, calls = out.calls;
        json_sink_bytes(&output, "later", 5); json_sink_raw(&output, "later"); json_sink_string(&output, "later");
        CHECK(output.failed && output.length == length && out.calls == calls, "no output after failure");
    }
    collector_t partial = fresh_collector(16); partial.fail_at = 1; partial.partial_failure = true;
    json_sink_init(&output, LIMIT, collect, &partial); json_sink_string(&output, "\x01"); collector_flush(&partial);
    CHECK(output.failed && output.length == 1 && partial.used == 2, "partial external failure retained");
    ++groups;
}

static void zero_and_overflow(void) {
    collector_t out = fresh_collector(1); json_sink_t sink;
    json_sink_init(&sink, 0, collect, &out); CHECK(!sink.failed, "zero-capacity init unchanged");
    json_sink_bytes(&sink, NULL, 0); CHECK(sink.failed && sink.length == 0 && !out.calls, "zero capacity rejects even zero append");
    json_sink_init(&sink, 1, collect, &out); json_sink_bytes(&sink, NULL, 0);
    CHECK(!sink.failed && !sink.length && !out.calls, "zero append needs no callback");
    json_sink_bytes(&sink, "x", 1); CHECK(sink.failed && !out.calls, "reserved NUL boundary");
    json_sink_init(&sink, 2, collect, &out); json_sink_bytes(&sink, "x", 1); json_sink_bytes(&sink, NULL, 0);
    CHECK(!sink.failed && sink.length == 1 && out.calls == 1, "last available payload byte");
    json_sink_bytes(&sink, "x", 1); CHECK(sink.failed && sink.length == 1 && out.calls == 1, "capacity failure sticky");
    json_sink_init(&sink, SIZE_MAX, NULL, (void *)(uintptr_t)1); json_sink_bytes(&sink, NULL, SIZE_MAX - 1);
    CHECK(!sink.failed && sink.length == SIZE_MAX - 1, "count-only does not dereference span");
    json_sink_bytes(&sink, NULL, 2); CHECK(sink.failed && sink.length == SIZE_MAX - 1, "checked overflow rejected");
    json_sink_init(&sink, SIZE_MAX, NULL, NULL); sink.length = SIZE_MAX; json_sink_bytes(&sink, NULL, 0);
    CHECK(sink.failed && sink.length == SIZE_MAX, "invalid length rejected before subtraction");
    ++groups;
}

int main(void) {
    spans_and_layout(); corpus_and_capacities(); exhaustive_and_truncation();
    split_messages(); failures_are_sticky(); zero_and_overflow();
    CHECK(groups == 6, "group count");
    printf("PASS %zu JSON sink groups; differential_cases=%zu; buffer_layout=%zu\n", groups, differential_cases, sizeof(json_buffer_t));
    return 0;
}
