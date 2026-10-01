// Independent division oracle and storage checks for the 16+16+4 experiment.
#include "packed_complex16.h"
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

static uint64_t pairs_checked, codes_checked, stores_checked, blocks_checked;
static unsigned seen_shifts;

static int64_t rounded(int32_t x, unsigned shift) {
    int64_t magnitude = x < 0 ? -(int64_t)x : x;
    int64_t scale = (int64_t)1 << shift;
    int64_t m = (magnitude + scale / 2) / scale;
    return x < 0 ? -m : m;
}

static void check_pair(int32_t real, int32_t imag) {
    int32_t input[2] = {real, imag}, output[2];
    unsigned shift = 1;
    for (; shift < 16; ++shift) {
        int64_t r = rounded(real, shift), i = rounded(imag, shift);
        if (r >= INT16_MIN && r <= INT16_MAX && i >= INT16_MIN && i <= INT16_MAX) break;
    }
    unsigned exponent, clipped;
    uint32_t word = pc16_pack(real, imag, &exponent, &clipped);
    assert(exponent + 1 == shift);
    seen_shifts |= 1u << exponent;
    pc16_unpack(word, exponent, output, output + 1);
    unsigned expected_clips = 0;
    for (unsigned k = 0; k < 2; ++k) {
        int64_t scale = (int64_t)1 << shift, m = rounded(input[k], shift);
        unsigned clip = m > INT16_MAX;
        expected_clips += clip;
        if (clip) m = INT16_MAX;
        assert(m >= INT16_MIN && output[k] == m * scale);
        int64_t error = (int64_t)output[k] - input[k];
        if (error < 0) error = -error;
        assert(error <= (clip ? scale - 1 : scale / 2));
        if (!input[k]) assert(!output[k]);
    }
    assert(clipped == expected_clips);
    ++pairs_checked;
}

static void check_codes(void) {
    for (unsigned e = 0; e < 16; ++e) {
        for (int32_t m = INT16_MIN; m <= INT16_MAX; ++m) {
            uint32_t bits = (uint32_t)m & 0xffffu;
            int32_t r, i;
            pc16_unpack(bits, e, &r, &i);
            assert(r == (int64_t)m * ((int64_t)1 << (e + 1)) && i == 0);
            pc16_unpack(bits << 16, e, &r, &i);
            assert(i == (int64_t)m * ((int64_t)1 << (e + 1)) && r == 0);
            codes_checked += 2;
        }
    }
}

static void check_storage(void) {
    enum { N = 1197, E = (N + 7) / 8 };
    uint32_t mantissas[N + 2], exponents[E + 2];
    memset(mantissas, 0, sizeof(mantissas));
    memset(exponents, 0, sizeof(exponents));
    mantissas[0] = mantissas[N + 1] = exponents[0] = exponents[E + 1] = 0xaabbccddu;
    assert(pc16_exponent_words(N) == E && 4 * (N + E) == 5388);
    assert(pc16_exponent_words(0) == 0 && pc16_exponent_words(8) == 1);
    assert(pc16_exponent_words(9) == 2);
    // Rewrite every nibble with every exponent; verify adjacent words/nibbles.
    for (unsigned pass = 0; pass < 16; ++pass) for (size_t n = 0; n < N; ++n) {
        unsigned wanted = ((unsigned)n + pass) % 16;
        int32_t r = 20000 * (int32_t)(1u << (wanted + 1)), i = -r;
        uint32_t before[E + 2]; memcpy(before, exponents, sizeof(before));
        unsigned clipped, e;
        uint32_t expected = pc16_pack(r, i, &e, &clipped);
        assert(e == wanted && !clipped);
        pc16_store(mantissas + 1, exponents + 1, n, r, i, &clipped);
        assert(mantissas[n + 1] == expected && !clipped);
        for (unsigned w = 0; w < E + 2; ++w) {
            uint32_t mask = w == n / 8 + 1 ? 15u << ((n % 8) * 4) : 0;
            assert((before[w] & ~mask) == (exponents[w] & ~mask));
        }
        int32_t rr, ii; pc16_load(mantissas + 1, exponents + 1, n, &rr, &ii);
        assert(rr == r && ii == i);
        assert(mantissas[0] == 0xaabbccddu && mantissas[N + 1] == 0xaabbccddu);
        ++stores_checked;
    }
}

static void check_blocks(void) {
    uint32_t rng = 0x08041616u;
    for (unsigned block = 0; block < 65536; ++block) {
        int32_t real[8], imag[8], rr[10], ii[10];
        uint32_t words[10]; unsigned reference_clips = 0;
        uint32_t reference_words[8], reference_exponents = 0;
        for (unsigned n = 0; n < 8; ++n) {
            rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
            memcpy(real + n, &rng, 4);
            rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
            memcpy(imag + n, &rng, 4);
            // Include low exponents, zero and saturation in mixed-scale blocks.
            unsigned divisor_shift = (block + n) % 17;
            real[n] /= (int32_t)(1u << divisor_shift);
            imag[n] /= (int32_t)(1u << divisor_shift);
            if (!block) { real[n] = n ? INT32_MIN : 0; imag[n] = n ? INT32_MAX : 0; }
            unsigned e, clips;
            reference_words[n] = pc16_pack(real[n], imag[n], &e, &clips);
            reference_exponents |= e << (n * 4);
            reference_clips += clips;
            check_pair(real[n], imag[n]);
        }
        words[0] = words[9] = 0xfeedbacdu;
        rr[0] = rr[9] = ii[0] = ii[9] = 0x12345678;
        unsigned clipped;
        uint32_t exponents = pc16_pack8(real, imag, words + 1, &clipped);
        assert(exponents == reference_exponents && clipped == reference_clips);
        assert(memcmp(words + 1, reference_words, sizeof(reference_words)) == 0);
        pc16_unpack8(words + 1, exponents, rr + 1, ii + 1);
        for (unsigned n = 0; n < 8; ++n) {
            int32_t r, i;
            pc16_unpack(reference_words[n], (reference_exponents >> (4 * n)) & 15u, &r, &i);
            assert(rr[n + 1] == r && ii[n + 1] == i);
        }
        assert(words[0] == 0xfeedbacdu && words[9] == 0xfeedbacdu);
        assert(rr[0] == 0x12345678 && rr[9] == 0x12345678);
        assert(ii[0] == 0x12345678 && ii[9] == 0x12345678);
        ++blocks_checked;
    }
    // Integration example: one full block followed by a five-sample tail.
    int32_t real[13], imag[13], r[13], i[13]; uint32_t words[13], exponents[2] = {0};
    for (unsigned n = 0; n < 13; ++n) { real[n] = (int32_t)n * 54321; imag[n] = -real[n]; }
    exponents[0] = pc16_pack8(real, imag, words, NULL);
    for (unsigned n = 8; n < 13; ++n) pc16_store(words, exponents, n, real[n], imag[n], NULL);
    pc16_unpack8(words, exponents[0], r, i);
    for (unsigned n = 8; n < 13; ++n) pc16_load(words, exponents, n, r + n, i + n);
    assert(!(exponents[1] >> 20)); // Three unused nibbles are untouched.
    for (unsigned n = 0; n < 13; ++n) {
        unsigned e; int32_t rr, ii;
        uint32_t p = pc16_pack(real[n], imag[n], &e, NULL); pc16_unpack(p, e, &rr, &ii);
        assert(r[n] == rr && i[n] == ii);
    }
}

int main(void) {
    check_codes();
    const int32_t edges[] = {INT32_MIN, INT32_MIN + 1, INT32_MAX, INT32_MAX - 1,
        -1073741825, -1073741824, 1073741823, 1073741824,
        -65538, -65537, -65536, -65535, -32768, -32767, -3, -2, -1,
        0, 1, 2, 3, 32767, 32768, 65533, 65534, 65535, 65536};
    for (unsigned a = 0; a < sizeof(edges) / sizeof(edges[0]); ++a)
        for (unsigned b = 0; b < sizeof(edges) / sizeof(edges[0]); ++b) check_pair(edges[a], edges[b]);
    // Exponent carry, half-way rounding and both signed boundaries, on both axes.
    for (unsigned s = 1; s <= 16; ++s) {
        int64_t scale = (int64_t)1 << s;
        const int64_t centers[] = {32767 * scale, 32767 * scale + scale / 2,
            -32768 * scale, -32768 * scale - scale / 2, scale / 2, -scale / 2};
        for (unsigned c = 0; c < sizeof(centers) / sizeof(centers[0]); ++c)
            for (int delta = -2; delta <= 2; ++delta) {
                int64_t v = centers[c] + delta;
                if (v >= INT32_MIN && v <= INT32_MAX) {
                    check_pair((int32_t)v, 0); check_pair(0, (int32_t)v);
                }
            }
    }
    // Exercise small values as well as uniformly distributed int32 pairs.
    for (int32_t n = -131072; n <= 131072; ++n) check_pair(n, -n);
    uint32_t rng = 0x16160401u;
    for (unsigned n = 0; n < 1000000; ++n) {
        int32_t v[2];
        for (unsigned k = 0; k < 2; ++k) {
            rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
            memcpy(v + k, &rng, sizeof(rng));
        }
        check_pair(v[0], v[1]);
    }
    assert(seen_shifts == 0xffffu);
    unsigned e, clipped; int32_t r, i;
    uint32_t p = pc16_pack(INT32_MIN, INT32_MAX, &e, &clipped);
    pc16_unpack(p, e, &r, &i);
    assert(e == 15 && clipped == 1 && r == INT32_MIN && i == 2147418112);
    p = pc16_pack(1, -1, &e, &clipped); pc16_unpack(p, e, &r, &i);
    assert(e == 0 && p == 0xffff0001u && r == 2 && i == -2 && !clipped);
    check_storage();
    check_blocks();
    printf("{\"shift_min\":1,\"shift_max\":16,\"mantissa_codes_checked\":%" PRIu64
           ",\"input_pairs_checked\":%" PRIu64 ",\"nibble_stores_checked\":%" PRIu64
           ",\"eight_pair_blocks_checked\":%" PRIu64
           ",\"all_shifts_exercised\":true,\"int32_extrema_checked\":true,"
           "\"payload_bytes_1197_pairs\":5388,\"pcm_qualified\":false}\n",
           codes_checked, pairs_checked, stores_checked, blocks_checked);
    return 0;
}
