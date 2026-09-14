/* Host-only path-count observer. Never linked into ESP8266 firmware.
 * Calls the unmodified decoder first, then derives cwrsi search lengths from
 * its exact signed pulse vector. No second entropy decode or state mutation.
 * Counts are workload evidence, NOT Xtensa timing or predicted acceleration.
 */
#include "config.h"
#include "cwrs.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

static struct {
    uint64_t calls, dimensions, many_pulses, many_dimensions_zero;
    uint64_t dimension_searches, dimension_probes, dimension_extra_probes;
    uint64_t column_searches, column_probes, row_searches, row_probes;
    uint64_t dimension_probe_histogram[33];
} counts;

static void check(int ok) {
    if (!ok) { fputs("PVQ path observer invariant failed\n", stderr); abort(); }
}

static void save_counts(void) {
    const char *name = getenv("YORADIO_PVQ_COUNTS");
    check(name != NULL);
    FILE *out = fopen(name, "wb");
    check(out != NULL);
    fprintf(out, "{\"calls\":%" PRIu64 ",\"dimensions\":%" PRIu64
        ",\"many_pulses\":%" PRIu64 ",\"many_dimensions_zero\":%" PRIu64
        ",\"dimension_searches\":%" PRIu64 ",\"dimension_probes\":%" PRIu64
        ",\"dimension_extra_probes\":%" PRIu64
        ",\"column_searches\":%" PRIu64 ",\"column_probes\":%" PRIu64
        ",\"row_searches\":%" PRIu64 ",\"row_probes\":%" PRIu64
        ",\"dimension_probe_histogram\":[",
        counts.calls, counts.dimensions, counts.many_pulses,
        counts.many_dimensions_zero, counts.dimension_searches,
        counts.dimension_probes, counts.dimension_extra_probes,
        counts.column_searches, counts.column_probes, counts.row_searches,
        counts.row_probes);
    for (unsigned i = 0; i < 33; ++i)
        fprintf(out, "%s%" PRIu64, i ? "," : "", counts.dimension_probe_histogram[i]);
    /* Histogram bucket32 is >=32; it does not limit decoding. */
    fputs("]}\n", out);
    check(fclose(out) == 0);
}

__attribute__((constructor)) static void init_counts(void) {
    check(atexit(save_counts) == 0);
}

opus_val32 __real_decode_pulses(int *y, int n, int k, ec_dec *dec);
opus_val32 __wrap_decode_pulses(int *y, int n, int k, ec_dec *dec) {
    opus_val32 energy = __real_decode_pulses(y, n, k, dec);
    check(n > 1 && k > 0);
    counts.calls++;
    uint64_t sum = 0, squares = 0;
    int64_t remaining = k;
    for (int j = 0; j < n; ++j) {
        const int64_t pulse = y[j];
        const uint64_t magnitude = pulse < 0 ? (uint64_t)-pulse : (uint64_t)pulse;
        sum += magnitude;
        squares += (uint64_t)(pulse * pulse);
        check(magnitude <= (uint64_t)remaining);
        if (n - j > 2) {
            counts.dimensions++;
            if (remaining >= n - j) {
                counts.many_pulses++;
                if (remaining - (int64_t)magnitude < n - j) {
                    counts.column_searches++;
                    counts.column_probes += n - j - (remaining - (int64_t)magnitude);
                } else {
                    counts.row_searches++;
                    counts.row_probes += magnitude + 1;
                }
            } else if (magnitude == 0) {
                counts.many_dimensions_zero++;
            } else {
                counts.dimension_searches++;
                counts.dimension_probes += magnitude;
                counts.dimension_extra_probes += magnitude - 1;
                counts.dimension_probe_histogram[magnitude < 32 ? magnitude : 32]++;
            }
        }
        remaining -= magnitude;
    }
    check(remaining == 0 && sum == (uint64_t)k);
    check((uint32_t)squares == (uint32_t)energy);
    return energy;
}
