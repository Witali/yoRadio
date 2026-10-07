// Host-only comparison using the separately downloaded, pinned FAAD2 source.
// No upstream implementation is copied into the production firmware.
#include <math.h>
#include "common.h"
#include "structs.h"
#include "neaacdec.h"
#include "packed_complex14.h"
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#if !defined(SBR_DEC) || !defined(PS_DEC) || defined(SBR_LOW_POWER) || defined(LC_ONLY_DECODER)
#error "Comparison requires full complex SBR and PS"
#endif
_Static_assert(sizeof(real_t) == 4, "Comparison uses float32 or int32, not double");

typedef struct {
    uint64_t pairs, changed, saturated, out_of_range, exponents[16];
    double square_sum, peak;
} trace_t;
static trace_t traces[2];
static double float_scale;
static unsigned scope;

static void pair(real_t *r, real_t *i, unsigned kind) {
    trace_t *t = traces + kind;
    double a = *r, b = *i;
    ++t->pairs; t->square_sum += a*a+b*b;
    if (fabs(a) > t->peak) t->peak = fabs(a);
    if (fabs(b) > t->peak) t->peak = fabs(b);
#ifdef FIXED_POINT
    int32_t ar = *r, bi = *i;
#else
    a *= float_scale; b *= float_scale;
    if (a < INT32_MIN || a > INT32_MAX || b < INT32_MIN || b > INT32_MAX) {
        ++t->out_of_range; return; // Report an unrepresentable trial, never hide it.
    }
    int32_t ar = (int32_t)llround(a), bi = (int32_t)llround(b);
#endif
    unsigned saturated;
    uint32_t word = pc14_pack(ar, bi, PC14_NEAREST, &saturated);
    t->saturated += saturated; ++t->exponents[word >> 28];
    int32_t rr, ii; pc14_unpack(word, PC14_NEAREST, &rr, &ii);
    t->changed += (ar != rr) + (bi != ii);
#ifdef FIXED_POINT
    *r = rr; *i = ii;
#else
    *r = rr / float_scale; *i = ii / float_scale;
#endif
}

static void complex_array(complex_t *p, unsigned count) {
    for (unsigned i = 0; i < count; ++i) pair(&RE(p[i]), &IM(p[i]), 1);
}

static void quantize(NeAACDecHandle handle) {
    NeAACDecStruct *d = handle;
    for (unsigned element = 0; element < MAX_SYNTAX_ELEMENTS; ++element) {
        sbr_info *s = d->sbr[element];
        if (!s) continue;
        if (scope & 1) for (unsigned ch = 0; ch < 2; ++ch)
            for (unsigned row = 0; row < s->tHFGen; ++row)
                for (unsigned band = 0; band < 64; ++band)
                    pair(&QMF_RE(s->Xsbr[ch][row][band]), &QMF_IM(s->Xsbr[ch][row][band]), 0);
        if ((scope & 2) && s->ps && s->ps_used) {
            ps_info *p = s->ps;
            complex_array(&p->delay_Qmf[0][0], 14 * 64);
            complex_array(&p->delay_SubQmf[0][0], 2 * 32);
            complex_array(&p->delay_Qmf_ser[0][0][0], 3 * 5 * 64);
            complex_array(&p->delay_SubQmf_ser[0][0][0], 3 * 5 * 32);
            // Mixing/phase coefficients have a different fixed-point scale.
            // Hybrid buffers live behind a private opaque pointer. Neither is
            // included in this explicitly limited PS-delay comparison.
        }
    }
}

static void scale_test(void) {
    uint32_t rng = 0x14320005u;
    unsigned checked = 0;
    for (unsigned n = 0; n < 32768; ++n) {
        int32_t v[2];
        for (unsigned k = 0; k < 2; ++k) {
            rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
            v[k] = (int32_t)(rng & 0x0fffffffu) - 0x08000000;
        }
        uint32_t p = pc14_pack(v[0], v[1], PC14_NEAREST, NULL);
        int32_t r, i; pc14_unpack(p, PC14_NEAREST, &r, &i);
        if (!(p >> 28)) continue; // Exclude the minimum-shift floor.
        for (unsigned k = 1; k <= 3; ++k) {
            int32_t factor = 1 << k, rr, ii;
            unsigned saturated;
            uint32_t q = pc14_pack(v[0] * factor, v[1] * factor, PC14_NEAREST, &saturated);
            pc14_unpack(q, PC14_NEAREST, &rr, &ii);
            assert(!saturated && rr == (int64_t)r * factor && ii == (int64_t)i * factor);
            assert((q & 0x0fffffffu) == (p & 0x0fffffffu));
            ++checked;
        }
    }
    assert(checked > 98000);
    int32_t r, i;
    pc14_unpack(pc14_pack(1, -1, PC14_NEAREST, NULL), PC14_NEAREST, &r, &i);
    assert(r == 0 && i == 0);
    pc14_unpack(pc14_pack(8, -8, PC14_NEAREST, NULL), PC14_NEAREST, &r, &i);
    assert(r == 8 && i == -8); // An improvement is possible at the minimum floor.
    printf("{\"interior_scale_invariance_cases\":%u,\"minimum_shift_exception_checked\":true}\n", checked);
}

int main(int argc, char **argv) {
    if (argc == 2 && !strcmp(argv[1], "--quantizer-scale-test")) { scale_test(); return 0; }
    assert(argc == 5);
    scope = strtoul(argv[2], NULL, 10); assert(scope <= 3);
    float_scale = strtod(argv[3], NULL); assert(float_scale > 0);
    unsigned repeats = strtoul(argv[4], NULL, 10); assert(repeats == 1 || repeats == 2);
    FILE *f = fopen(argv[1], "rb"); assert(f);
    fseek(f, 0, SEEK_END); long size = ftell(f); rewind(f); assert(size > 0);
    unsigned char *data = calloc(1, size + 1024); assert(data);
    assert(fread(data, 1, size, f) == size); fclose(f);
    NeAACDecHandle dec[2]; long start[2];
    for (unsigned leg = 0; leg < 2; ++leg) {
        dec[leg] = NeAACDecOpen(); assert(dec[leg]);
        NeAACDecConfigurationPtr config = NeAACDecGetCurrentConfiguration(dec[leg]);
        // Upstream defaults to MAIN even in a fixed build that disables MAIN.
        // This is the fallback object type; the ADTS header supplies the real one.
        config->defObjectType = LC;
        config->outputFormat = FAAD_FMT_16BIT;
        assert(NeAACDecSetConfiguration(dec[leg], config));
        unsigned long rate; unsigned char channels;
        start[leg] = NeAACDecInit(dec[leg], data, size, &rate, &channels);
        assert(start[leg] >= 0);
    }
    assert(start[0] == start[1]);
    uint64_t samples = 0, different = 0, over_two = 0, over_five = 0, frames = 0;
    uint64_t square_error = 0, square_signal = 0;
    unsigned maximum = 0, ps_frames = 0, rate = 0, channels = 0;
    for (unsigned repeat = 0; repeat < repeats; ++repeat)
    for (long pos = start[0]; pos + 7 <= size;) {
        assert(data[pos] == 0xff && (data[pos+1] & 0xf6) == 0xf0);
        unsigned length = ((data[pos+3] & 3) << 11) | (data[pos+4] << 3) | (data[pos+5] >> 5);
        assert(length >= 7 && pos + length <= size);
        NeAACDecFrameInfo info[2]; int16_t *pcm[2];
        for (unsigned leg = 0; leg < 2; ++leg) {
            pcm[leg] = NeAACDecDecode(dec[leg], &info[leg], data + pos, length);
            if (info[leg].error) fprintf(stderr, "decode error %u frame %" PRIu64 "\n", info[leg].error, frames);
            assert(!info[leg].error && pcm[leg]);
        }
        assert(info[0].samples == info[1].samples && info[0].channels == info[1].channels &&
               info[0].samplerate == info[1].samplerate && info[0].bytesconsumed == info[1].bytesconsumed);
        assert(info[0].bytesconsumed == length);
        rate = info[0].samplerate; channels = info[0].channels;
        for (unsigned i = 0; i < info[0].samples; ++i) {
            int delta = (int)pcm[1][i] - pcm[0][i]; unsigned error = delta < 0 ? -delta : delta;
            different += error != 0; over_two += error > 2; over_five += error > 5;
            if (error > maximum) maximum = error;
            square_error += (uint64_t)error * error;
            square_signal += (int64_t)pcm[0][i] * pcm[0][i];
        }
        samples += info[0].samples; ++frames;
        ps_frames += ((NeAACDecStruct *)dec[0])->ps_used_global != 0;
        if (scope) quantize(dec[1]);
        pos += length;
    }
    printf("{\"samples\":%" PRIu64 ",\"frames\":%" PRIu64 ",\"rate\":%u,\"channels\":%u,"
           "\"ps_frames\":%u,\"different\":%" PRIu64 ",\"over_two\":%" PRIu64
           ",\"over_five\":%" PRIu64 ",\"maximum\":%u,\"square_error\":%" PRIu64
           ",\"square_signal\":%" PRIu64 ",\"scope\":%u,\"float_scale\":%.0f,\"history\":[",
           samples, frames, rate, channels, ps_frames, different, over_two, over_five, maximum,
           square_error, square_signal, scope, float_scale);
    for (unsigned k = 0; k < 2; ++k) {
        trace_t *t = traces + k;
        printf("%s{\"pairs\":%" PRIu64 ",\"changed_components\":%" PRIu64 ",\"saturated\":%" PRIu64
               ",\"out_of_range\":%" PRIu64 ",\"rms_native\":%.9g,\"peak_native\":%.9g,\"exponents\":[",
               k ? "," : "", t->pairs, t->changed, t->saturated, t->out_of_range,
               t->pairs ? sqrt(t->square_sum / (2 * t->pairs)) : 0, t->peak);
        for (unsigned e = 0; e < 16; ++e) printf("%s%" PRIu64, e ? "," : "", t->exponents[e]);
        printf("]}");
    }
    printf("]}\n");
    for (unsigned leg = 0; leg < 2; ++leg) NeAACDecClose(dec[leg]);
    free(data); return 0;
}
