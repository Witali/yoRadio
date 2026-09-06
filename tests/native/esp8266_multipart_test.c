#include <assert.h>
#include <stdio.h>
#include "web_multipart.h"
static char result[2048];
static size_t length;
static unsigned starts, ends;
static bool receive(mp_event_t event, const uint8_t *data, size_t size, void *ctx) {
    (void)ctx;
    if (event == MP_BEGIN) {
        char name[32];
        assert(mp_parameter((const char *)data, "name", name, sizeof(name)));
        assert(!strcmp(name, "plfile"));
        ++starts;
    } else if (event == MP_DATA) {
        assert(length + size < sizeof(result));
        memcpy(result + length, data, size);
        length += size;
    } else ++ends;
    return true;
}
int main(void) {
    const char *body = "--abcdef\r\nContent-Disposition: form-data; name=\"plfile\"; filename=\"x.csv\"\r\n\r\n"
        "station\thttp://radio/\t0\n\r\n--abcdefXnot-a-boundary\r\n--abcdef--\r\n";
    const char *expected = "station\thttp://radio/\t0\n\r\n--abcdefXnot-a-boundary";
    for (size_t step = 1; step <= strlen(body); ++step) {
        web_multipart_t p;
        assert(mp_init(&p, "abcdef", receive, NULL));
        starts = ends = 0; length = 0;
        for (size_t off = 0; off < strlen(body); off += step) {
            size_t n = strlen(body) - off;
            if (n > step) n = step;
            assert(mp_feed(&p, (const uint8_t *)body + off, n));
        }
        assert(mp_complete(&p));
        assert(starts == 1 && ends == 1);
        assert(length == strlen(expected) && !memcmp(result, expected, length));
    }
    for (size_t cut = 0; cut < strlen(body) - 4; ++cut) {
        web_multipart_t p;
        assert(mp_init(&p, "abcdef", receive, NULL));
        starts = ends = 0; length = 0;
        bool ok = mp_feed(&p, (const uint8_t *)body, cut);
        assert(!ok || !mp_complete(&p));
    }
    char value[32];
    assert(!mp_parameter("filename=\"wrong\"", "name", value, sizeof(value)));
    puts("Streaming multipart tests passed");
    return 0;
}
