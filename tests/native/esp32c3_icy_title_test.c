// Oracle is the previous whole-block strstr/strchr algorithm, including its
// bare-quote fallback. Check published 191-byte prefixes, not full log strings.
#include "icy_title.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

enum { MAX_METADATA = 255 * 16 };
static unsigned checks;
static uint32_t random_state = 0x917bae4d;
static uint32_t random_value(void) {
    random_state ^= random_state << 13;
    random_state ^= random_state >> 17;
    random_state ^= random_state << 5;
    return random_state;
}

static bool legacy(const uint8_t *data, size_t size, char output[192]) {
    char metadata[MAX_METADATA + 1];
    assert(size <= MAX_METADATA);
    memcpy(metadata, data, size);
    metadata[size] = '\0';
    char *title = strstr(metadata, "StreamTitle='");
    if (!title) return false;
    title += strlen("StreamTitle='");
    char *end = strstr(title, "';");
    if (!end) end = strchr(title, '\'');
    if (!end) return false;
    *end = '\0';
    const size_t length = strlen(title);
    const size_t keep = length < 191 ? length : 191;
    memcpy(output, title, keep);
    output[keep] = '\0';
    return true;
}

static void equal(icy_title_parser_t *parser, const uint8_t *data, size_t size) {
    char expected[192];
    const bool present = legacy(data, size, expected);
    const char *actual = icy_title_finish(parser);
    assert((actual != NULL) == present);
    if (present) {
        assert(strlen(actual) < sizeof(expected));
        assert(strcmp(actual, expected) == 0);
    }
    // Finishing twice or feeding another block without reset cannot change it.
    const uint8_t poison[] = "StreamTitle='unexpected';";
    icy_title_feed(parser, poison, sizeof(poison));
    actual = icy_title_finish(parser);
    assert((actual != NULL) == present);
    if (present) assert(strcmp(actual, expected) == 0);
    ++checks;
}

static void split_case(const uint8_t *data, size_t size) {
    struct {
        uint64_t before;
        icy_title_parser_t parser;
        uint64_t after;
    } guarded = {.before = UINT64_C(0x12345678aabbccdd),
                 .after = UINT64_C(0x9988776655443322)};
    for (size_t split = 0; split <= size; ++split) {
        icy_title_begin(&guarded.parser);
        icy_title_feed(&guarded.parser, data, split);
        icy_title_feed(&guarded.parser, NULL, 0);
        icy_title_feed(&guarded.parser, data + split, size - split);
        equal(&guarded.parser, data, size);
        assert(guarded.before == UINT64_C(0x12345678aabbccdd));
        assert(guarded.after == UINT64_C(0x9988776655443322));
    }
    icy_title_begin(&guarded.parser);
    for (size_t i = 0; i < size; ++i)
        icy_title_feed(&guarded.parser, data + i, 1);
    equal(&guarded.parser, data, size);
}

static void targeted(void) {
    const char *cases[] = {"", "StreamTitle='", "StreamTitle='';",
        "StreamTitle='Don't Stop';StreamUrl='x';",
        "StreamTitle='a'b'c';", "StreamTitle='a'b'c'",
        "StreamTitle='a'b", "StreamTitle='unterminated",
        "StreamTitle='first';StreamTitle='second';", "streamTitle='wrong';",
        "SSSSStreamTitle='overlap';", "StreamTiStreamTitle='overlap';",
        "StreamUrl='link';StreamTitle='title';",
        "StreamTitle='abc'';", "StreamTitle='title';garbage",
        "StreamTitle='\xd1\x91Radio \xe2\x80\x94 \xf0\x9f\x8e\xb5';"};
    for (size_t i = 0; i < sizeof(cases)/sizeof(*cases); ++i)
        split_case((const uint8_t *)cases[i], strlen(cases[i]));
    const uint8_t with_nul[] = "StreamTitle='before'\0;StreamTitle='after';";
    split_case(with_nul, sizeof(with_nul));
    const uint8_t early_nul[] = "padding\0StreamTitle='hidden';";
    split_case(early_nul, sizeof(early_nul));
    uint8_t block[MAX_METADATA];
    // Termination before, at and after published-prefix capacity; valid and
    // malformed full-size blocks. A late ; must override an earlier bare quote.
    for (size_t length = 189; length <= 194; ++length) {
        memset(block, 'x', sizeof(block));
        memcpy(block, "StreamTitle='", 13);
        block[13 + length] = '\'';
        block[14 + length] = ';';
        split_case(block, sizeof(block));
    }
    memset(block, 'x', sizeof(block));
    memcpy(block, "StreamTitle='", 13);
    block[16] = '\'';
    block[MAX_METADATA - 2] = '\'';
    block[MAX_METADATA - 1] = ';';
    split_case(block, sizeof(block));
    block[MAX_METADATA - 1] = 'x';
    split_case(block, sizeof(block));
    memset(block, 'x', sizeof(block));
    memcpy(block + MAX_METADATA - 15, "StreamTitle='';", 15);
    split_case(block, sizeof(block));
}

static void randomized(void) {
    uint8_t block[MAX_METADATA];
    for (unsigned iteration = 0; iteration < 20000; ++iteration) {
        size_t size = random_value() % (MAX_METADATA + 1);
        for (size_t i = 0; i < size; ++i) {
            const char alphabet[] = "StreamTitle='; abc\0\xff";
            block[i] = (uint8_t)alphabet[random_value() % (sizeof(alphabet) - 1)];
        }
        if (size >= 15) {
            size_t at = random_value() % (size - 14);
            memcpy(block + at, "StreamTitle='", 13);
            // Most random blocks should actually reach a title before NUL.
            if (iteration % 3) memset(block, 'x', at);
            if (iteration % 2) {
                size_t end = at + 13 + random_value() % (size - at - 14);
                memset(block + at + 13, 'q', end - at - 13);
                block[end] = '\'';
                block[end + 1] = ';';
            }
        }
        icy_title_parser_t parser;
        icy_title_begin(&parser);
        for (size_t offset = 0; offset < size;) {
            size_t count = 1 + random_value() % 257;
            if (count > size - offset) count = size - offset;
            icy_title_feed(&parser, block + offset, count);
            offset += count;
        }
        equal(&parser, block, size);
    }
}

static void reset_and_independence(void) {
    icy_title_parser_t a, b;
    const uint8_t first[] = "StreamTitle='first';";
    const uint8_t second[] = "StreamTitle='second';";
    icy_title_begin(&a);
    icy_title_feed(&a, first, 16); // Cancel in the middle of a title.
    icy_title_begin(&a);
    icy_title_begin(&b);
    for (size_t i = 0; i < sizeof(second); ++i) {
        icy_title_feed(&a, second + i, 1);
        if (i < sizeof(first)) icy_title_feed(&b, first + i, 1);
    }
    equal(&a, second, sizeof(second));
    equal(&b, first, sizeof(first));
}

int main(void) {
    targeted();
    randomized();
    reset_and_independence();
    printf("ICY title differential PASS: %u cases; parser %zu bytes vs 4081; seed 0x917bae4d\n",
           checks, sizeof(icy_title_parser_t));
    return 0;
}
