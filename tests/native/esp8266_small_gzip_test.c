#include "small_gzip.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
static small_gzip_t state;
static size_t written, failure_after;
static bool output(void *context, const unsigned char *data, size_t size) {
    assert(size > 0 && size <= 512);
    if (failure_after && written + size > failure_after) return false;
    written += size;
    return fwrite(data, 1, size, context) == size;
}
int main(int argc, char **argv) {
    assert(argc >= 4 && sizeof(state) <= 2700);
    FILE *in = fopen(argv[1], "rb"), *out = fopen(argv[2], "wb");
    assert(in && out);
    size_t chunk = strtoul(argv[3], NULL, 10);
    if (argc > 4) failure_after = strtoul(argv[4], NULL, 10);
    unsigned char input[4096];
    assert(chunk && chunk <= sizeof(input));
    small_gzip_init(&state, output, out);
    bool ok = true;
    size_t n;
    while ((n = fread(input, 1, chunk, in)) && ok) ok = small_gzip_feed(&state, input, n);
    ok = ok && small_gzip_finish(&state);
    assert(!small_gzip_feed(&state, input, 1));
    assert(!small_gzip_finish(&state));
    fclose(in); fclose(out);
    return ok ? 0 : 2;
}
