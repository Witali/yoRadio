// Private ABI: esp_audio_codec ESP32-C3 archive SHA-256
// 311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909.
// See docs/ESP32C3_AAC_PACKED_HISTORY_20261001.md before changing these offsets.
#include "qemu_aac_packed_history.h"
#include "packed_complex14.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <string.h>

_Static_assert(sizeof(void *) == 4 && sizeof(int32_t) == 4, "Pinned decoder ABI is RV32 only");

static const char *TAG = "aac_packed";
static unsigned selected, repetition;
static struct {
    uint32_t sbr_frames, ps_frames, lc_skips, pairs, changed, max_shift;
    uint32_t exponents[16], saturated, nonzero_to_zero, zero_to_nonzero;
    uint32_t near_zero, near_zero_changed, ratios[6];
    int64_t bias_real, bias_imag;
} stats;

void packed_history_reset(unsigned run) {
    memset(&stats, 0, sizeof(stats));
    repetition = run;
    selected = 0;
}

void packed_history_select(unsigned variant) { assert(variant <= 7); selected = variant; }

typedef struct { int32_t *real, *imag; unsigned count; } span_t;
typedef struct { span_t spans[100]; unsigned count; uintptr_t low, high; } spans_t;

static void in_bounds(const spans_t *s, const void *ptr, unsigned bytes) {
    uintptr_t p = (uintptr_t)ptr;
    assert(!(p & 3u) && p >= s->low && p <= s->high && bytes <= s->high - p);
}

static void add_span(spans_t *s, int32_t *real, int32_t *imag, unsigned n) {
    assert(n && s->count < 100);
    in_bounds(s, real, n * 4); in_bounds(s, imag, n * 4);
    // Check all typed sample ranges are disjoint, including Re versus Im.
    // Run 1 audits the ABI. Runs 2/3 omit the quadratic overlap audit for timing.
    if (repetition == 1) {
        uintptr_t p[2] = {(uintptr_t)real, (uintptr_t)imag};
        assert(p[0] + n * 4 <= p[1] || p[1] + n * 4 <= p[0]);
        for (unsigned i = 0; i < s->count; ++i) {
            uintptr_t q[2] = {(uintptr_t)s->spans[i].real, (uintptr_t)s->spans[i].imag};
            for (unsigned a = 0; a < 2; ++a) for (unsigned b = 0; b < 2; ++b)
                assert(p[a] + n * 4 <= q[b] || q[b] + s->spans[i].count * 4 <= p[a]);
        }
    }
    s->spans[s->count++] = (span_t){real, imag, n};
}

static void *pointer_at(const void *base, unsigned offset) {
    void *p; memcpy(&p, (const uint8_t *)base + offset, sizeof(p)); return p;
}

static void add_table(spans_t *s, int32_t **real, int32_t **imag,
                      unsigned rows, unsigned columns) {
    in_bounds(s, real, rows * 4); in_bounds(s, imag, rows * 4);
    for (unsigned i = 0; i < rows; ++i) add_span(s, real[i], imag[i], columns);
}

static void ps_spans(spans_t *s, uint8_t *owner, uint8_t *ps) {
    assert(ps == owner + 0xc988 && pointer_at(owner, 0xc984) == ps);
    s->low = (uintptr_t)(owner + 0x7678); s->high = (uintptr_t)(owner + 0x93b4);
    int32_t **real = pointer_at(ps, 0x1d0), **imag = pointer_at(ps, 0x1d4);
    in_bounds(s, real, 61 * 4); in_bounds(s, imag, 61 * 4);
    for (unsigned band = 0; band < 61; ++band)
        add_span(s, real[band], imag[band], band < 20 ? 2 : band < 32 ? 14 : 1);
    add_table(s, pointer_at(ps, 0x1d8), pointer_at(ps, 0x1dc), 10, 2);
    // The linked constant is checked too, rather than trusting the reference tree.
    extern const int32_t aRevLinkDelaySer[3];
    for (unsigned link = 0; link < 3; ++link) {
        assert(aRevLinkDelaySer[link] == link + 3);
        add_table(s, pointer_at(ps, 0x1a0 + link * 4), pointer_at(ps, 0x1ac + link * 4), link + 3, 20);
        add_table(s, pointer_at(ps, 0x1b8 + link * 4), pointer_at(ps, 0x1c4 + link * 4), link + 3, 10);
    }
    int32_t *hybrid = pointer_at(ps, 0x1fc);
    in_bounds(s, hybrid, 28);
    assert(hybrid[0] == 3 && hybrid[2] == 12);
    add_table(s, pointer_at(hybrid, 12), pointer_at(hybrid, 16), 3, 12);
}

static uint32_t magnitude(int32_t x) { return x < 0 ? 0u - (uint32_t)x : (uint32_t)x; }

static void quantize(const span_t *span, pc14_mode_t mode) {
    for (unsigned i = 0; i < span->count; ++i) {
        int32_t r = span->real[i], q = span->imag[i], rr, qq;
        ++stats.pairs;
        if (selected == 7) continue; // Exact, same traversal and pointer checks.
        unsigned saturated;
        uint32_t packed = pc14_pack(r, q, mode, &saturated);
        pc14_unpack(packed, mode, &rr, &qq);
        unsigned exponent = packed >> 28;
        if (exponent + 3 > stats.max_shift) stats.max_shift = exponent + 3;
        stats.changed += (r != rr) + (q != qq);
        if (repetition == 1) {
            ++stats.exponents[exponent]; stats.saturated += saturated;
            stats.nonzero_to_zero += (r && !rr) + (q && !qq);
            stats.zero_to_nonzero += (!r && rr) + (!q && qq);
            stats.near_zero += (magnitude(r) < 8) + (magnitude(q) < 8);
            stats.near_zero_changed += (magnitude(r) < 8 && r != rr) + (magnitude(q) < 8 && q != qq);
            stats.bias_real += (int64_t)rr - r; stats.bias_imag += (int64_t)qq - q;
            uint32_t a = magnitude(r), b = magnitude(q), lo = a < b ? a : b, hi = a > b ? a : b;
            // Both zero; only one zero; max/min <2, <16, <256, >=256.
            unsigned bucket = !hi ? 0 : !lo ? 1 : (uint64_t)hi < (uint64_t)lo * 2 ? 2 :
                              (uint64_t)hi < (uint64_t)lo * 16 ? 3 : (uint64_t)hi < (uint64_t)lo * 256 ? 4 : 5;
            ++stats.ratios[bucket];
        }
        span->real[i] = rr; span->imag[i] = qq;
    }
}

void __real_sbr_dec(int16_t *, void *, void *, int32_t, int32_t *, void *, void *, void *);
void __wrap_sbr_dec(int16_t *input, void *output, void *frame, int32_t apply,
                    int32_t *control, void *other_output, void *ps, void *core) {
    __real_sbr_dec(input, output, frame, apply, control, other_output, ps, core);
    if (!selected) return;
    assert(control[4] == 32 && control[6] == 8 && (control[1] == 0 || control[1] == 1));
    unsigned scope = selected == 7 ? 3 : (selected - 1) % 3 + 1;
    pc14_mode_t mode = selected >= 4 ? PC14_MIDPOINT : PC14_NEAREST;
    uint8_t *f = frame;
    spans_t spans = {.low = (uintptr_t)frame, .high = (uintptr_t)frame + 0x64b8};
    if ((scope & 1) && !control[1]) {
        add_span(&spans, (int32_t *)(f + 0x11b0), (int32_t *)(f + 0x25b0), 8 * 32);
        add_span(&spans, (int32_t *)(f + 0x3e38), (int32_t *)(f + 0x39b4), 6 * 48);
        ++stats.sbr_frames;
    } else if ((scope & 1) && control[1]) ++stats.lc_skips;
    if ((scope & 2) && ps) { ps_spans(&spans, f - 8, ps); ++stats.ps_frames; }
    for (unsigned i = 0; i < spans.count; ++i) quantize(spans.spans + i, mode);
}

void packed_history_report(const char *name, unsigned variant, unsigned run,
                           uint32_t *rows, uint32_t *changed, unsigned *shift) {
    *rows = stats.sbr_frames + stats.ps_frames; *changed = stats.changed; *shift = stats.max_shift;
    assert(stats.pairs == stats.sbr_frames * 544u + stats.ps_frames * 653u);
    ESP_LOGI(TAG, "PCX14_HISTORY case=%s variant=%u run=%u sbr_frames=%" PRIu32
             " ps_frames=%" PRIu32 " lc_skips=%" PRIu32 " pairs=%" PRIu32,
             name, variant, run, stats.sbr_frames, stats.ps_frames, stats.lc_skips, stats.pairs);
    if (run != 1 || !variant || variant == 7) return;
    ESP_LOGI(TAG, "PCX14_QUANT case=%s variant=%u run=%u pairs=%" PRIu32
             " saturated=%" PRIu32 " nonzero_to_zero=%" PRIu32 " zero_to_nonzero=%" PRIu32
             " near_zero=%" PRIu32 " near_zero_changed=%" PRIu32
             " bias_real=%" PRId64 " bias_imag=%" PRId64,
             name, variant, run, stats.pairs, stats.saturated, stats.nonzero_to_zero,
             stats.zero_to_nonzero, stats.near_zero, stats.near_zero_changed, stats.bias_real, stats.bias_imag);
    for (unsigned i = 0; i < 16; ++i)
        ESP_LOGI(TAG, "PCX14_EXP case=%s variant=%u run=%u exponent=%u count=%" PRIu32,
                 name, variant, run, i, stats.exponents[i]);
    for (unsigned i = 0; i < 6; ++i)
        ESP_LOGI(TAG, "PCX14_RATIO case=%s variant=%u run=%u bucket=%u count=%" PRIu32,
                 name, variant, run, i, stats.ratios[i]);
}

// Independent int64 division oracle for the portable representation.
static int64_t oracle_m(int32_t x, unsigned shift, pc14_mode_t mode) {
    int64_t scale = (int64_t)1 << shift;
    if (mode == PC14_NEAREST) return x < 0 ? -((-(int64_t)x + scale / 2) / scale) : ((int64_t)x + scale / 2) / scale;
    return x < 0 ? -((-(int64_t)x + scale - 1) / scale) : (int64_t)x / scale;
}

static void check_pair(int32_t r, int32_t i, pc14_mode_t mode) {
    unsigned shift = 3;
    for (; shift < 18; ++shift) {
        int64_t a = oracle_m(r, shift, mode), b = oracle_m(i, shift, mode);
        if (a >= -8192 && a <= 8191 && b >= -8192 && b <= 8191) break;
    }
    unsigned clipped; uint32_t word = pc14_pack(r, i, mode, &clipped);
    assert((word >> 28) + 3 == shift);
    int64_t a = oracle_m(r, shift, mode), b = oracle_m(i, shift, mode);
    assert(clipped == (a > 8191) + (b > 8191));
    if (a > 8191) a = 8191;
    if (b > 8191) b = 8191;
    assert(pc14_sign_extend(word & 0x3fff) == a);
    assert(pc14_sign_extend((word >> 14) & 0x3fff) == b);
    if (mode == PC14_MIDPOINT) {
        a = a * ((int64_t)1 << shift) + (a ? (int64_t)1 << (shift - 1) : 0);
        b = b * ((int64_t)1 << shift) + (b ? (int64_t)1 << (shift - 1) : 0);
    } else { a *= (int64_t)1 << shift; b *= (int64_t)1 << shift; }
    int32_t rr, ii; pc14_unpack(word, mode, &rr, &ii);
    assert(rr == a && ii == b);
    if (!r) assert(!rr);
    if (!i) assert(!ii);
}

void packed_history_arithmetic_tests(void) {
    for (unsigned m = 0; m < 2; ++m) {
        for (unsigned e = 0; e < 16; ++e) {
            for (int32_t mantissa = -8192; mantissa < 8192; ++mantissa) {
                uint32_t word = (e << 28) | ((uint32_t)mantissa & 0x3fff);
                int32_t r, i; pc14_unpack(word, m, &r, &i);
                int64_t expected = (int64_t)mantissa * ((int64_t)1 << (e + 3));
                if (m && mantissa) expected += (int64_t)1 << (e + 2);
                assert(r == expected && i == 0);
            }
            vTaskDelay(1);
        }
        int32_t edges[] = {INT32_MIN, INT32_MIN + 1, INT32_MAX, INT32_MAX - 1,
                           -65540, -65539, -65537, -65536, -65535, -8, -7, -4, -1,
                           0, 1, 4, 7, 8, 65531, 65532, 65535};
        for (unsigned a = 0; a < sizeof(edges) / sizeof(edges[0]); ++a)
            for (unsigned b = 0; b < sizeof(edges) / sizeof(edges[0]); ++b) check_pair(edges[a], edges[b], m);
        for (unsigned shift = 3; shift <= 18; ++shift) {
            int64_t scale = (int64_t)1 << shift;
            for (int sign = -1; sign <= 1; sign += 2) {
                for (int delta = -1; delta <= 1; ++delta) {
                    int64_t x = sign * (8192 * scale - scale / 2 + delta);
                    if (x >= INT32_MIN && x <= INT32_MAX) check_pair((int32_t)x, 0, m);
                }
            }
        }
        uint32_t rng = 0x14324143;
        for (unsigned k = 0; k < 8192; ++k) {
            int32_t pair[2];
            for (unsigned j = 0; j < 2; ++j) { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; memcpy(pair + j, &rng, 4); }
            check_pair(pair[0], pair[1], m);
            if (!(k % 256)) vTaskDelay(1);
        }
    }
    assert(pc14_pack(8, -8, PC14_NEAREST, NULL) == 0x0fffc001u);
    ESP_LOGI(TAG, "PCX14_ARITHMETIC_PASS mantissas=16384 exponents=16 modes=2 edges random-pairs=16384");
}
