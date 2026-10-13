#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "web_file_form.h"

static uint8_t saved[100000];
static size_t saved_size;
static unsigned opens, closes;
static bool fail_begin, fail_write, fail_end;
static bool begin(unsigned slot, void *context) {
    (void)slot; (void)context; ++opens; return !fail_begin;
}
static bool write_data(const uint8_t *data, size_t size, void *context) {
    (void)context;
    if (fail_write) return false;
    assert(saved_size + size <= sizeof(saved));
    memcpy(saved + saved_size, data, size); saved_size += size; return true;
}
static bool end(void *context) { (void)context; ++closes; return !fail_end; }
static web_file_form_t form;
static bool parse(const uint8_t *body, size_t size, size_t step, web_form_mode_t mode) {
    memset(&form, 0, sizeof(form));
    form.mode = mode;
    form.sink = (web_form_sink_t){begin, write_data, end, NULL};
    opens = closes = 0; saved_size = 0;
    web_multipart_t p;
    assert(mp_init(&p, "boundary", web_file_form_part, &form));
    for (size_t offset = 0; offset < size; offset += step) {
        size_t n = size - offset;
        if (n > step) n = step;
        if (!mp_feed(&p, body + offset, n)) return false;
    }
    return mp_complete(&p);
}
#define PART(name, file) "--boundary\r\nContent-Disposition: form-data; name=\"" name "\"; filename=\"" file "\"\r\n\r\n"
#define LAST "\r\n--boundary--\r\n"
static void rejected(const char *body, web_form_mode_t mode) {
    for (size_t step = 1; step < 64; ++step)
        assert(!parse((const uint8_t *)body, strlen(body), step, mode));
}
int main(void) {
    const char *body = PART("plfile", "playlist.csv")
        "fixture\thttp://example.invalid/audio\t0\n\r\n--boundaryXnot-a-boundary" LAST;
    const char *expected = "fixture\thttp://example.invalid/audio\t0\n\r\n--boundaryXnot-a-boundary";
    size_t size = strlen(body);
    for (size_t step = 1; step <= size; ++step) {
        assert(parse((const uint8_t *)body, size, step, WEB_FORM_UPLOAD));
        assert(opens == 1 && closes == 1 && form.files == 1 && form.playlist[0]);
        assert(!strcmp(form.names[0], "playlist.csv"));
        assert(saved_size == strlen(expected) && !memcmp(saved, expected, saved_size));
    }
    for (size_t cut = 0; cut < size - 4; ++cut)
        assert(!parse((const uint8_t *)body, cut, 17, WEB_FORM_UPLOAD));
    fail_begin = true; assert(!parse((const uint8_t *)body, size, 7, WEB_FORM_UPLOAD)); fail_begin = false;
    fail_write = true; assert(!parse((const uint8_t *)body, size, 7, WEB_FORM_UPLOAD)); fail_write = false;
    fail_end = true; assert(!parse((const uint8_t *)body, size, 7, WEB_FORM_UPLOAD)); fail_end = false;

    const char *many = PART("www", "C:\\fakepath\\style.css.gz") "\x1f\x8b" "binary"
        "\r\n" PART("data", "playlist.csv") "fixture\thttp://example.invalid\t0\n" LAST;
    for (size_t step = 1; step <= strlen(many); ++step) {
        assert(parse((const uint8_t *)many, strlen(many), step, WEB_FORM_BOARD));
        assert(form.files == 2 && !form.playlist[0] && form.playlist[1]);
        assert(!strcmp(form.names[0], "style.css.gz"));
    }
    rejected(PART("www", "bad..css.gz") "x" LAST, WEB_FORM_BOARD);
    rejected(PART("www", "style.css") "x" LAST, WEB_FORM_BOARD);
    rejected(PART("data", "unknown.csv") "x" LAST, WEB_FORM_BOARD);
    rejected(PART("www", "a.gz") "x\r\n" PART("www", "a.gz") "y" LAST, WEB_FORM_BOARD);
    rejected(PART("plfile", "x") LAST, WEB_FORM_UPLOAD);
    rejected(PART("plfile", "x") "x\r\n" PART("plfile", "x") "x" LAST, WEB_FORM_UPLOAD);
    rejected(PART("ssid", "") "one\r\n" PART("ssid", "") "two" LAST, WEB_FORM_CREDENTIALS);
    rejected(PART("pass", "") "line\nbreak" LAST, WEB_FORM_CREDENTIALS);
    const char *credentials = PART("ssid", "") "fixture\r\n" PART("pass", "") LAST;
    assert(parse((const uint8_t *)credentials, strlen(credentials), 1, WEB_FORM_CREDENTIALS));
    assert(form.ssid_seen && form.password_seen && !strcmp(form.ssid, "fixture") && !form.password[0]);

    // Binary 90 KiB transfer, including NULs and arbitrary byte values. Storage
    // retains the payload; the production parser/form have fixed sizes.
    const char *prefix = PART("www", "style.css.gz");
    const size_t bytes = 90 * 1024;
    uint8_t *large = malloc(strlen(prefix) + bytes + strlen(LAST));
    assert(large);
    memcpy(large, prefix, strlen(prefix));
    for (size_t i = 0; i < bytes; ++i) large[strlen(prefix) + i] = (uint8_t)i;
    memcpy(large + strlen(prefix) + bytes, LAST, strlen(LAST));
    for (size_t step = 1; step <= 8192; step *= 2) {
        assert(parse(large, strlen(prefix) + bytes + strlen(LAST), step, WEB_FORM_BOARD));
        assert(saved_size == bytes && !memcmp(saved, large + strlen(prefix), bytes));
    }
    free(large);
    char over[1200];
    size_t n = (size_t)sprintf(over, "%s", PART("wifile", "wifi.csv"));
    memset(over + n, 'x', 800); n += 800;
    strcpy(over + n, LAST);
    rejected(over, WEB_FORM_UPLOAD);
    // 16 staged file slots are bounded; a 17th must never call the sink.
    char slots[4096]; n = 0;
    for (unsigned i = 0; i < 17; ++i)
        n += (size_t)sprintf(slots + n, "%s--boundary\r\nContent-Disposition: form-data; name=\"www\"; filename=\"%u.gz\"\r\n\r\nx", i ? "\r\n" : "", i);
    strcpy(slots + n, LAST);
    rejected(slots, WEB_FORM_BOARD);
    printf("Web file form passed: form=%zu parser=%zu bytes; arbitrary splits, binary 90 KiB, bounds, truncation, sink failures\n", sizeof(form), sizeof(web_multipart_t));
    return 0;
}
