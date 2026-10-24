/*
Portable floor1 curve application adapted from Xiph.Org Tremor revision
0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/{floor1.c,misc.h,floor_lookup.c}:
https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/
Source SHA256:
 floor1.c: 5dc87534496c039df8683b9d6149fc0c1ac6938c87a7e1b303d3a53b642330e4
 misc.h: f15d78fc4c49a95df854701aea3fd527ed35597767075d4eba48b80cab70ec66
 floor_lookup.c: dfc670f7648f94ae7beb25ca542380f42eba3dbf8e180e479648f20fb07bbaba

Vorbis I 7.2.4: extend the final floor in amplitude space to n, using the
same inverse-dB lookup and fixed multiply as the preceding line segments.
The original denominator is retained when a segment extends beyond n.

Copyright (c) 2002, Xiph.org Foundation

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

- Neither the name of the Xiph.org Foundation nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
#pragma once
#include <stdint.h>
#include <string.h>

static const int32_t repair_floor1_from_db[256] = {
    0x000000e5, 0x000000f4, 0x00000103, 0x00000114,
    0x00000126, 0x00000139, 0x0000014e, 0x00000163,
    0x0000017a, 0x00000193, 0x000001ad, 0x000001c9,
    0x000001e7, 0x00000206, 0x00000228, 0x0000024c,
    0x00000272, 0x0000029b, 0x000002c6, 0x000002f4,
    0x00000326, 0x0000035a, 0x00000392, 0x000003cd,
    0x0000040c, 0x00000450, 0x00000497, 0x000004e4,
    0x00000535, 0x0000058c, 0x000005e8, 0x0000064a,
    0x000006b3, 0x00000722, 0x00000799, 0x00000818,
    0x0000089e, 0x0000092e, 0x000009c6, 0x00000a69,
    0x00000b16, 0x00000bcf, 0x00000c93, 0x00000d64,
    0x00000e43, 0x00000f30, 0x0000102d, 0x0000113a,
    0x00001258, 0x0000138a, 0x000014cf, 0x00001629,
    0x0000179a, 0x00001922, 0x00001ac4, 0x00001c82,
    0x00001e5c, 0x00002055, 0x0000226f, 0x000024ac,
    0x0000270e, 0x00002997, 0x00002c4b, 0x00002f2c,
    0x0000323d, 0x00003581, 0x000038fb, 0x00003caf,
    0x000040a0, 0x000044d3, 0x0000494c, 0x00004e10,
    0x00005323, 0x0000588a, 0x00005e4b, 0x0000646b,
    0x00006af2, 0x000071e5, 0x0000794c, 0x0000812e,
    0x00008993, 0x00009283, 0x00009c09, 0x0000a62d,
    0x0000b0f9, 0x0000bc79, 0x0000c8b9, 0x0000d5c4,
    0x0000e3a9, 0x0000f274, 0x00010235, 0x000112fd,
    0x000124dc, 0x000137e4, 0x00014c29, 0x000161bf,
    0x000178bc, 0x00019137, 0x0001ab4a, 0x0001c70e,
    0x0001e4a1, 0x0002041f, 0x000225aa, 0x00024962,
    0x00026f6d, 0x000297f0, 0x0002c316, 0x0002f109,
    0x000321f9, 0x00035616, 0x00038d97, 0x0003c8b4,
    0x000407a7, 0x00044ab2, 0x00049218, 0x0004de23,
    0x00052f1e, 0x0005855c, 0x0005e135, 0x00064306,
    0x0006ab33, 0x00071a24, 0x0007904b, 0x00080e20,
    0x00089422, 0x000922da, 0x0009bad8, 0x000a5cb6,
    0x000b091a, 0x000bc0b1, 0x000c8436, 0x000d5471,
    0x000e3233, 0x000f1e5f, 0x001019e4, 0x001125c1,
    0x00124306, 0x001372d5, 0x0014b663, 0x00160ef7,
    0x00177df0, 0x001904c1, 0x001aa4f9, 0x001c603d,
    0x001e384f, 0x00202f0f, 0x0022467a, 0x002480b1,
    0x0026dff7, 0x002966b3, 0x002c1776, 0x002ef4fc,
    0x0032022d, 0x00354222, 0x0038b828, 0x003c67c2,
    0x004054ae, 0x004482e8, 0x0048f6af, 0x004db488,
    0x0052c142, 0x005821ff, 0x005ddc33, 0x0063f5b0,
    0x006a74a7, 0x00715faf, 0x0078bdce, 0x0080967f,
    0x0088f1ba, 0x0091d7f9, 0x009b5247, 0x00a56a41,
    0x00b02a27, 0x00bb9ce2, 0x00c7ce12, 0x00d4ca17,
    0x00e29e20, 0x00f15835, 0x0101074b, 0x0111bb4e,
    0x01238531, 0x01367704, 0x014aa402, 0x016020a7,
    0x017702c3, 0x018f6190, 0x01a955cb, 0x01c4f9cf,
    0x01e269a8, 0x0201c33b, 0x0223265a, 0x0246b4ea,
    0x026c9302, 0x0294e716, 0x02bfda13, 0x02ed9793,
    0x031e4e09, 0x03522ee4, 0x03896ed0, 0x03c445e2,
    0x0402efd6, 0x0445ac4b, 0x048cbefc, 0x04d87013,
    0x05290c67, 0x057ee5ca, 0x05da5364, 0x063bb204,
    0x06a36485, 0x0711d42b, 0x0787710e, 0x0804b299,
    0x088a17ef, 0x0918287e, 0x09af747c, 0x0a50957e,
    0x0afc2f19, 0x0bb2ef7f, 0x0c759034, 0x0d44d6ca,
    0x0e2195bc, 0x0f0cad0d, 0x10070b62, 0x1111aeea,
    0x122da66c, 0x135c120f, 0x149e24d9, 0x15f525b1,
    0x176270e3, 0x18e7794b, 0x1a85c9ae, 0x1c3f06d1,
    0x1e14f07d, 0x200963d7, 0x221e5ccd, 0x2455f870,
    0x26b2770b, 0x29363e2b, 0x2be3db5c, 0x2ebe06b6,
    0x31c7a55b, 0x3503ccd4, 0x3875c5aa, 0x3c210f44,
    0x4009632b, 0x4432b8cf, 0x48a149bc, 0x4d59959e,
    0x52606733, 0x57bad899, 0x5d6e593a, 0x6380b298,
    0x69f80e9a, 0x70dafda8, 0x78307d76, 0x7fffffff,
};

/* Exact bits15..46 of the signed wide product, including negative inputs.
 * Unsigned extraction and memcpy avoid signed shifts and narrowing overflow. */
static int32_t repair_floor1_multiply(int32_t x, int32_t y) {
    int64_t product = (int64_t)x * (int64_t)y;
    uint32_t bits = (uint32_t)((uint64_t)product >> 15);
    int32_t result;
    memcpy(&result, &bits, sizeof(result));
    return result;
}

static void repair_floor1_line(int n, int x0, int x1, int y0, int y1,
                               int32_t *out) {
    int dy = y1 - y0;
    int adx = x1 - x0;
    int ady = dy < 0 ? -dy : dy;
    int base = dy / adx;
    int sy = dy < 0 ? base - 1 : base + 1;
    int x = x0;
    int y = y0;
    int err = 0;
    if (n > x1) n = x1;
    int product = base * adx;
    ady -= product < 0 ? -product : product;
    if (x < n) out[x] = repair_floor1_multiply(out[x], repair_floor1_from_db[y]);
    while (++x < n) {
        err += ady;
        if (err >= adx) {
            err -= adx;
            y += sy;
        } else {
            y += base;
        }
        out[x] = repair_floor1_multiply(out[x], repair_floor1_from_db[y]);
    }
}

/* Caller supplies validated predecoded floor inputs: n>0; posts2..65;
 * multiplier1..4; xs[0]=0; forward is a sorted unique-X permutation;
 * both implicit endpoints are active; scaled active Y values are0..255.
 * Bit0x8000 marks inactive fit entries. out has n elements and does not alias
 * xs/forward/fit. No setup normalization, allocation or opaque state is used. */
static int repair_floor1_render(int n, int posts, int multiplier,
                                const uint16_t *xs, const char *forward,
                                const int32_t *fit, int32_t *out) {
    if (!fit) {
        memset(out, 0, (size_t)n * sizeof(*out));
        return 0;
    }
    int hx = 0;
    int lx = 0;
    int ly = fit[0] * multiplier;
    for (int j = 1; j < posts; ++j) {
        int current = (unsigned char)forward[j];
        int hy = fit[current] & 0x7fff;
        if (hy == fit[current]) {
            hy *= multiplier;
            hx = xs[current];
            repair_floor1_line(n, lx, hx, ly, hy, out);
            lx = hx;
            ly = hy;
        }
    }
    for (int j = hx; j < n; ++j)
        out[j] = repair_floor1_multiply(out[j], repair_floor1_from_db[ly]);
    return 1;
}
