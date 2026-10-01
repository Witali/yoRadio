// Private ABI: esp_audio_codec ESP32-C3 archive SHA-256
// 311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909.
// See docs/ESP32C3_AAC_PACKED_HISTORY_20261001.md before changing this layout.
#include "qemu_aac_packed_history.h"
#include "aac_sbr_abi.h"
#include "packed_complex14.h"
#include "packed_complex16.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <string.h>

_Static_assert(sizeof(void *) == 4 && sizeof(int32_t) == 4, "Pinned decoder ABI is RV32 only");

#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_HISTORY_TEST
#define PACKED_LABEL "PCX16"
#else
#define PACKED_LABEL "PCX14"
#endif

static const char *TAG = "aac_packed";
static unsigned selected, repetition;
static struct {
    uint32_t sbr_frames, ps_frames, lc_skips, pairs, changed, max_shift;
    uint32_t exponents[16], saturated, nonzero_to_zero, zero_to_nonzero;
    uint32_t near_zero, near_zero_changed, ratios[6];
    uint32_t blocks8, tail_pairs, scalar_pairs;
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

static void add_table(spans_t *s, int32_t **real, int32_t **imag,
                      unsigned rows, unsigned columns) {
    in_bounds(s, real, rows * 4); in_bounds(s, imag, rows * 4);
    for (unsigned i = 0; i < rows; ++i) add_span(s, real[i], imag[i], columns);
}

static void ps_spans(spans_t *s, aac_sbr_owner_abi_t *owner, aac_ps_abi_t *ps) {
    assert(ps == &owner->embedded_ps && owner->ps == ps);
    aac_sbr_ps_overlay_abi_t *workspace = &owner->channel[1].ps_overlay;
    s->low = (uintptr_t)workspace->peak; s->high = (uintptr_t)&workspace->relocated_ps;
    int32_t **real = ps->delay_real, **imag = ps->delay_imag;
    in_bounds(s, real, 61 * 4); in_bounds(s, imag, 61 * 4);
    for (unsigned band = 0; band < 61; ++band)
        add_span(s, real[band], imag[band], band < 20 ? 2 : band < 32 ? 14 : 1);
    add_table(s, ps->sub_delay_real, ps->sub_delay_imag, 10, 2);
    // The linked constant is checked too, rather than trusting the reference tree.
    extern const int32_t aRevLinkDelaySer[3];
    for (unsigned link = 0; link < 3; ++link) {
        assert(aRevLinkDelaySer[link] == link + 3);
        add_table(s, ps->serial_real[link], ps->serial_imag[link], link + 3, 20);
        add_table(s, ps->sub_serial_real[link], ps->sub_serial_imag[link], link + 3, 10);
    }
    aac_hybrid_abi_t *hybrid = ps->hybrid;
    in_bounds(s, hybrid, sizeof(*hybrid));
    assert(hybrid->bands == 3 && hybrid->history_length == 12);
    add_table(s, hybrid->real_history, hybrid->imag_history, 3, 12);
}

static uint32_t magnitude(int32_t x) { return x < 0 ? 0u - (uint32_t)x : (uint32_t)x; }

#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_HISTORY_TEST
static void quantize(const span_t *span, pc14_mode_t unused) {
    (void)unused;
    stats.pairs += span->count;
    if (selected == 7) return;
    for (unsigned base = 0; base < span->count; base += 8) {
        unsigned n = span->count - base;
        if (n > 8) n = 8;
        // Original values are retained only for diagnostics. This roundtrip is
        // an accuracy probe, not an allocation reduction or optimized hot path.
        int32_t r[8], q[8]; uint32_t words[8], exponents = 0;
        memcpy(r, span->real + base, n * sizeof(int32_t));
        memcpy(q, span->imag + base, n * sizeof(int32_t));
        unsigned clipped = 0;
        if (selected <= 3 && n == 8) {
            exponents = pc16_pack8(r, q, words, &clipped);
            pc16_unpack8(words, exponents, span->real + base, span->imag + base);
            ++stats.blocks8;
        } else {
            for (unsigned i = 0; i < n; ++i) {
                unsigned pair_clipped;
                pc16_store(words, &exponents, i, r[i], q[i], &pair_clipped);
                clipped += pair_clipped;
                pc16_load(words, &exponents, i, span->real + base + i, span->imag + base + i);
            }
            if (selected <= 3) stats.tail_pairs += n;
            else stats.scalar_pairs += n;
        }
        if (repetition == 1) stats.saturated += clipped;
        for (unsigned i = 0; i < n; ++i) {
            int32_t rr = span->real[base + i], qq = span->imag[base + i];
            unsigned e = (exponents >> (4 * i)) & 15u;
            if (e + 1 > stats.max_shift) stats.max_shift = e + 1;
            stats.changed += (r[i] != rr) + (q[i] != qq);
            if (repetition != 1) continue;
            ++stats.exponents[e];
            stats.nonzero_to_zero += (r[i] && !rr) + (q[i] && !qq);
            stats.zero_to_nonzero += (!r[i] && rr) + (!q[i] && qq);
            stats.near_zero += (magnitude(r[i]) < 2) + (magnitude(q[i]) < 2);
            stats.near_zero_changed += (magnitude(r[i]) < 2 && r[i] != rr) + (magnitude(q[i]) < 2 && q[i] != qq);
            stats.bias_real += (int64_t)rr - r[i]; stats.bias_imag += (int64_t)qq - q[i];
            uint32_t a = magnitude(r[i]), b = magnitude(q[i]), lo = a < b ? a : b, hi = a > b ? a : b;
            unsigned bucket = !hi ? 0 : !lo ? 1 : (uint64_t)hi < (uint64_t)lo * 2 ? 2 :
                              (uint64_t)hi < (uint64_t)lo * 16 ? 3 : (uint64_t)hi < (uint64_t)lo * 256 ? 4 : 5;
            ++stats.ratios[bucket];
        }
    }
}
#else
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
#endif

void __real_sbr_dec(int16_t *, void *, void *, int32_t, int32_t *, void *, void *, void *);
void __wrap_sbr_dec(int16_t *input, void *output, void *frame, int32_t apply,
                    int32_t *control, void *other_output, void *ps, void *core) {
    __real_sbr_dec(input, output, frame, apply, control, other_output, ps, core);
    if (!selected) return;
    aac_sbr_control_abi_t *config = (void *)control;
    assert(config->columns == 32 && config->write_offset == 8 &&
           (config->low_complexity == 0 || config->low_complexity == 1));
    unsigned scope = selected == 7 ? 3 : (selected - 1) % 3 + 1;
    pc14_mode_t mode = selected >= 4 ? PC14_MIDPOINT : PC14_NEAREST;
    aac_sbr_frame_abi_t *f = frame;
    spans_t spans = {.low = (uintptr_t)frame, .high = (uintptr_t)frame +
        sizeof(aac_sbr_channel_abi_t) - offsetof(aac_sbr_channel_abi_t, frame)};
    if ((scope & 1) && !config->low_complexity) {
        add_span(&spans, &f->low_real[0][0], &f->low_imag[0][0], 8 * 32);
        add_span(&spans, &f->high_real_history[0][0], &f->high_imag_history[0][0], 6 * 48);
        ++stats.sbr_frames;
    } else if ((scope & 1) && config->low_complexity) ++stats.lc_skips;
    if ((scope & 2) && ps) {
        // PS is passed only for the left channel; recover its containing owner.
        aac_sbr_owner_abi_t *owner = (void *)((uint8_t *)frame -
            offsetof(aac_sbr_owner_abi_t, channel[0].frame));
        ps_spans(&spans, owner, ps); ++stats.ps_frames;
    }
    for (unsigned i = 0; i < spans.count; ++i) quantize(spans.spans + i, mode);
}

void packed_history_report(const char *name, unsigned variant, unsigned run,
                           uint32_t *rows, uint32_t *changed, unsigned *shift) {
    *rows = stats.sbr_frames + stats.ps_frames; *changed = stats.changed; *shift = stats.max_shift;
    assert(stats.pairs == stats.sbr_frames * 544u + stats.ps_frames * 653u);
    ESP_LOGI(TAG, PACKED_LABEL "_HISTORY case=%s variant=%u run=%u sbr_frames=%" PRIu32
             " ps_frames=%" PRIu32 " lc_skips=%" PRIu32 " pairs=%" PRIu32,
             name, variant, run, stats.sbr_frames, stats.ps_frames, stats.lc_skips, stats.pairs);
#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_HISTORY_TEST
    ESP_LOGI(TAG, "PCX16_BLOCKS case=%s variant=%u run=%u blocks8=%" PRIu32
             " tail_pairs=%" PRIu32 " scalar_pairs=%" PRIu32,
             name, variant, run, stats.blocks8, stats.tail_pairs, stats.scalar_pairs);
#endif
    if (run != 1 || !variant || variant == 7) return;
    ESP_LOGI(TAG, PACKED_LABEL "_QUANT case=%s variant=%u run=%u pairs=%" PRIu32
             " saturated=%" PRIu32 " nonzero_to_zero=%" PRIu32 " zero_to_nonzero=%" PRIu32
             " near_zero=%" PRIu32 " near_zero_changed=%" PRIu32
             " bias_real=%" PRId64 " bias_imag=%" PRId64,
             name, variant, run, stats.pairs, stats.saturated, stats.nonzero_to_zero,
             stats.zero_to_nonzero, stats.near_zero, stats.near_zero_changed, stats.bias_real, stats.bias_imag);
    for (unsigned i = 0; i < 16; ++i)
        ESP_LOGI(TAG, PACKED_LABEL "_EXP case=%s variant=%u run=%u exponent=%u count=%" PRIu32,
                 name, variant, run, i, stats.exponents[i]);
    for (unsigned i = 0; i < 6; ++i)
        ESP_LOGI(TAG, PACKED_LABEL "_RATIO case=%s variant=%u run=%u bucket=%u count=%" PRIu32,
                 name, variant, run, i, stats.ratios[i]);
}

// Independent int64 division oracle for the portable representation.
static int64_t oracle_m(int32_t x, unsigned shift, pc14_mode_t mode) {
    int64_t scale = (int64_t)1 << shift;
    if (mode == PC14_NEAREST) return x < 0 ? -((-(int64_t)x + scale / 2) / scale) : ((int64_t)x + scale / 2) / scale;
    return x < 0 ? -((-(int64_t)x + scale - 1) / scale) : (int64_t)x / scale;
}

#ifndef CONFIG_YORADIO_QEMU_AAC_PC16_HISTORY_TEST
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
#else
void packed_history_arithmetic_tests(void) {
    for (unsigned e = 0; e < 16; ++e) {
        for (int32_t m = INT16_MIN; m <= INT16_MAX; ++m) {
            int32_t r, i;
            uint32_t bits = (uint32_t)m & 0xffffu;
            pc16_unpack(bits | (bits << 16), e, &r, &i);
            assert(r == (int64_t)m * ((int64_t)1 << (e + 1)) && r == i);
        }
        vTaskDelay(1);
    }
    uint32_t rng = 0x16160401u;
    for (unsigned block = 0; block < 4096; ++block) {
        int32_t real[8], imag[8], rr[8], ii[8]; uint32_t words[8];
        for (unsigned n = 0; n < 8; ++n) {
            rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; memcpy(real + n, &rng, 4);
            rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; memcpy(imag + n, &rng, 4);
            if (!block) { real[n] = INT32_MIN; imag[n] = INT32_MAX; }
        }
        unsigned clipped;
        uint32_t exponents = pc16_pack8(real, imag, words, &clipped);
        pc16_unpack8(words, exponents, rr, ii);
        unsigned expected_clips = 0;
        for (unsigned n = 0; n < 8; ++n) {
            unsigned shift = 1;
            int64_t r, i;
            for (;;) {
                r = oracle_m(real[n], shift, PC14_NEAREST); i = oracle_m(imag[n], shift, PC14_NEAREST);
                if (shift == 16 || (r >= INT16_MIN && r <= INT16_MAX && i >= INT16_MIN && i <= INT16_MAX)) break;
                ++shift;
            }
            expected_clips += (r > INT16_MAX) + (i > INT16_MAX);
            if (r > INT16_MAX) r = INT16_MAX;
            if (i > INT16_MAX) i = INT16_MAX;
            assert(((exponents >> (n * 4)) & 15u) + 1 == shift);
            assert(rr[n] == r * ((int64_t)1 << shift) && ii[n] == i * ((int64_t)1 << shift));
        }
        assert(clipped == expected_clips);
        if (!(block % 128)) vTaskDelay(1);
    }
    ESP_LOGI(TAG, "PCX16_ARITHMETIC_PASS mantissas=65536 exponents=16 block8=4096 shift=1..16");
}
#endif
