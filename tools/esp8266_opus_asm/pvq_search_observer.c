/* Host-only observer: log exact cwrsi row-search bounds after unchanged decode.
 * No ESP8266 code or decoder state changes. The JSONL contains only synthetic
 * test-vector coordinates, not network data. Remaining L1 norm identifies the
 * largest j with U(n,j) <= i on the strictly increasing n>=3, j>=n row.
 */
#include "config.h"
#include "cwrs.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static FILE *trace;
static void check(int ok) { if (!ok) abort(); }
static void close_trace(void) { check(trace && fclose(trace) == 0); }
__attribute__((constructor)) static void open_trace(void) {
    const char *name = getenv("YORADIO_PVQ_SEARCH_TRACE");
    check(name != NULL); trace = fopen(name, "wb"); check(trace != NULL);
    check(atexit(close_trace) == 0);
}
opus_val32 __real_decode_pulses(int *, int, int, ec_dec *);
opus_val32 __wrap_decode_pulses(int *y, int n, int k, ec_dec *dec) {
    opus_val32 energy = __real_decode_pulses(y, n, k, dec);
    int64_t remaining = k;
    uint64_t squares = 0;
    check(n > 1 && k > 0);
    for (int j = 0; j < n; ++j) {
        int64_t v = y[j], magnitude = v < 0 ? -v : v;
        check(magnitude <= remaining);
        if (n-j > 2 && remaining >= n-j && remaining-magnitude >= n-j)
            check(fprintf(trace, "[%d,%d,%d]\n", n-j, (int)remaining,
                (int)(remaining-magnitude)) > 0);
        remaining -= magnitude; squares += (uint64_t)(v*v);
    }
    check(remaining == 0 && (uint32_t)squares == (uint32_t)energy);
    return energy;
}
