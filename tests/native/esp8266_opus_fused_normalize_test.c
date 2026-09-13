/* Host-only prototype for the next ASM experiment. NOT selected by firmware.
 * Reference functions are the actual pinned vq.c, with Xiph's original license.
 * Fusion must test RAW iy before MUL16 truncation or output rounding.
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "vq.c"

static unsigned fused(int *iy, celt_norm *X, int N, opus_val32 Ryy,
                      opus_val16 gain, int B)
{
    /* Keep unsupported/custom shape behavior unchanged, not rounded down. */
    if (B <= 1 || N % B) {
        normalise_residual(iy, X, N, Ryy, gain);
        return extract_collapse_mask(iy, N, B);
    }
    int k = celt_ilog2(Ryy) >> 1;
    opus_val32 t = VSHR32(Ryy, 2*(k-7));
    opus_val16 g = MULT16_16_P15(celt_rsqrt_norm(t), gain);
    int N0 = N / B, pos = 0;
    unsigned mask = 0;
    for (int b = 0; b < B; b++) {
        unsigned bits = 0;
        for (int j = 0; j < N0; j++, pos++) {
            int value = iy[pos]; /* One aligned word read in the future ASM. */
            bits |= (unsigned)value;
            X[pos] = EXTRACT16(PSHR32(MULT16_16(g, value), k+1));
        }
        mask |= (bits != 0) << b;
    }
    return mask;
}
int main(void)
{
    const int sizes[] = {2,3,4,6,8,12,16,24,32,44,64,88,128,176};
    const int blocks[] = {1,2,4,8};
    const int gains[] = {0,1,8192,16384,32767};
    uint32_t state = 0x927115a3;
    unsigned cases = 0, fallback = 0, zero_pcm_nonzero_mask = 0;
    for (unsigned n = 0; n < sizeof(sizes)/sizeof(sizes[0]); n++)
    for (unsigned b = 0; b < sizeof(blocks)/sizeof(blocks[0]); b++)
    for (unsigned g = 0; g < sizeof(gains)/sizeof(gains[0]); g++)
    for (unsigned pattern = 0; pattern < 32; pattern++) {
        int N = sizes[n], B = blocks[b], iy[176], saved[176];
        if (B > N) continue;
        celt_norm ref[178], out[178];
        memset(ref, 0x65, sizeof(ref)); memcpy(out, ref, sizeof(out));
        opus_val32 Ryy = 0;
        for (int i = 0; i < N; i++) {
            state = state*1664525u + 1013904223u;
            iy[i] = pattern == 0 ? (i == N-1 ? 32767 : 0) :
                pattern == 1 ? (i == 0 ? -128 : 0) :
                pattern == 2 ? (i == N/2 ? 1 : 0) :
                (int)(state % 17u)-8;
            Ryy += iy[i]*iy[i];
        }
        if (!Ryy) { iy[0] = 1; Ryy = 1; }
        memcpy(saved, iy, sizeof(int)*N);
        normalise_residual(iy, ref+1, N, Ryy, gains[g]);
        unsigned expected = extract_collapse_mask(iy, N, B);
        unsigned actual = fused(iy, out+1, N, Ryy, gains[g], B);
        assert(expected == actual);
        assert(!memcmp(ref, out, sizeof(out))); /* Includes untouched guards. */
        assert(!memcmp(saved, iy, sizeof(int)*N));
        if (gains[g] == 0 && actual) {
            for (int i = 1; i <= N; i++) assert(out[i] == 0);
            zero_pcm_nonzero_mask++;
        }
        if (B <= 1 || N % B) fallback++;
        cases++;
    }
    printf("{\"passed\":true,\"cases\":%u,\"fallback_cases\":%u,"
           "\"zero_pcm_nonzero_mask\":%u,\"pcm_exact\":true,"
           "\"physical_speed_measured\":false}\n",
           cases, fallback, zero_pcm_nonzero_mask);
    return 0;
}
