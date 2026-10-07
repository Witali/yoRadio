// Execute the production framing allocator with deterministic fault injection.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
static bool fail_alloc;
static unsigned live, allocations, opens, closes, frames;
static void *test_calloc(size_t n, size_t s) {
    if (fail_alloc) return NULL;
    void *p = calloc(n, s);
    if (p) { ++live; ++allocations; }
    return p;
}
static void *test_realloc(void *p, size_t n) {
    if (fail_alloc) return NULL;
    bool had_pointer = p != NULL;
    void *q = realloc(p, n);
    if (q) { ++allocations; if (!had_pointer) ++live; }
    return q;
}
static void test_free(void *p) { if (p) { assert(live); --live; } free(p); }
#define calloc test_calloc
#define realloc test_realloc
#define free test_free
#include "native_aac_decoder.c"
#undef calloc
#undef realloc
#undef free

static uint8_t expected[8191];
static size_t expected_size;
static bool retry, fail_open;
esp_audio_err_t esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg, void **p) {
    (void)cfg;
    if (fail_open) return ESP_AUDIO_ERR_MEM_LACK;
    *p = (void *)1; ++opens; return ESP_AUDIO_ERR_OK;
}
void esp_audio_simple_dec_close(void *p) { assert(p); ++closes; }
esp_audio_err_t esp_audio_simple_dec_process(void *p,
    esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *out) {
    assert(p && raw->len == expected_size);
    assert(memcmp(raw->buffer, expected, expected_size) == 0);
    if (retry) { retry = false; out->needed_size = 16384; return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH; }
    ++frames; raw->consumed = raw->len; out->decoded_size = 4096;
    return ESP_AUDIO_ERR_OK;
}
esp_audio_err_t esp_audio_simple_dec_get_info(void *p, esp_audio_simple_dec_info_t *info) {
    (void)p; (void)info; return ESP_AUDIO_ERR_OK;
}
static void frame(size_t size, bool crc) {
    expected_size = size;
    memset(expected, 0x39, size);
    uint8_t header[] = {0xff, crc ? 0xf0 : 0xf1, 0x50, 0x80, 0, 0x1f, 0xfc};
    memcpy(expected, header, 7);
    expected[3] |= (size >> 11) & 3;
    expected[4] = (size >> 3) & 255;
    expected[5] |= (size & 7) << 5;
}
static void feed(native_aac_decoder_t *d, size_t chunk) {
    uint8_t pcm[16384];
    unsigned before = frames;
    for (size_t pos = 0; pos < expected_size;) {
        size_t n = expected_size - pos;
        if (n > chunk) n = chunk;
        esp_audio_simple_dec_raw_t raw = {.buffer=expected+pos, .len=n};
        esp_audio_simple_dec_out_t out = {.buffer=pcm, .len=sizeof(pcm)};
        esp_audio_err_t result = native_aac_decoder_process(d, &raw, &out);
        assert(raw.consumed == n);
        pos += n;
        if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
            assert(pos == expected_size && d->used == expected_size);
            raw.buffer += n; raw.len = 0;
            assert(native_aac_decoder_process(d, &raw, &out) == ESP_AUDIO_ERR_OK);
            assert(raw.consumed == 0 && out.decoded_size == 4096);
        } else assert(result == ESP_AUDIO_ERR_OK);
    }
    assert(frames == before + 1 && d->used == 0);
}
int main(void) {
    fail_alloc = true;
    assert(!native_aac_decoder_create() && live == 0);
    fail_alloc = false;
    const size_t chunks[] = {1, 7, 23, 2048, 8191};
    for (unsigned c=0; c<sizeof(chunks)/sizeof(chunks[0]); ++c) {
        native_aac_decoder_t *d = native_aac_decoder_create();
        assert(d && live == 1 && d->capacity == 7);
        frame(12, false); feed(d, chunks[c]);
        assert(d->capacity == 128 && live == 2);
        unsigned count = allocations;
        frame(120, false); feed(d, chunks[c]);
        assert(allocations == count); // No repeated allocations within capacity.
        frame(8191, false); retry = true; feed(d, chunks[c]);
        assert(d->capacity == 8191);
        frame(8190, true); feed(d, chunks[c]);
        frame(9, true); feed(d, chunks[c]);
        native_aac_decoder_destroy(d);
        assert(live == 0 && opens == closes);
    }
    // Failed initial frame allocation retains the complete header and only
    // consumes its bytes. A later retry can finish the same frame losslessly.
    native_aac_decoder_t *d = native_aac_decoder_create();
    frame(8191, true);
    uint8_t pcm[8192];
    esp_audio_simple_dec_raw_t raw = {.buffer=expected, .len=expected_size};
    esp_audio_simple_dec_out_t out = {.buffer=pcm, .len=sizeof(pcm)};
    fail_alloc = true;
    assert(native_aac_decoder_process(d, &raw, &out) == ESP_AUDIO_ERR_MEM_LACK);
    assert(raw.consumed == 7 && d->used == 7 && d->data == d->header);
    fail_alloc = false; raw.buffer += 7; raw.len -= 7;
    assert(native_aac_decoder_process(d, &raw, &out) == ESP_AUDIO_ERR_OK);
    assert(raw.consumed == expected_size - 7);
    native_aac_decoder_destroy(d);
    // A failed realloc must preserve the earlier allocation/header too.
    d = native_aac_decoder_create(); frame(12, false); feed(d, 1);
    uint8_t *old = d->data; size_t old_capacity = d->capacity;
    frame(8191, false); raw.buffer = expected; raw.len = expected_size;
    fail_alloc = true;
    assert(native_aac_decoder_process(d, &raw, &out) == ESP_AUDIO_ERR_MEM_LACK);
    assert(raw.consumed == 7 && d->data == old && d->capacity == old_capacity);
    assert(memcmp(d->data, expected, 7) == 0);
    fail_alloc = false; native_aac_decoder_destroy(d);
    // SDK-open OOM and a truncated frame are both fully released at close.
    d = native_aac_decoder_create(); frame(120, false); raw.buffer = expected; raw.len = 120;
    fail_open = true;
    assert(native_aac_decoder_process(d, &raw, &out) == ESP_AUDIO_ERR_MEM_LACK);
    native_aac_decoder_destroy(d); fail_open = false;
    d = native_aac_decoder_create(); raw.buffer = expected; raw.len = 17;
    assert(native_aac_decoder_process(d, &raw, &out) == ESP_AUDIO_ERR_OK);
    assert(d->used == 17); native_aac_decoder_destroy(d);
    assert(live == 0 && opens == closes);
    puts("PASS: adaptive ADTS 7..8191 bytes, CRC, fragmented input, no-growth reuse, pending frame retry, create/grow/open OOM and truncated cleanup");
}
