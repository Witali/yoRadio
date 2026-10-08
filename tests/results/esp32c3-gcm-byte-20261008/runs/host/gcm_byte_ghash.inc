/*
 * SPDX-License-Identifier: Apache-2.0
 * Based on the Mbed TLS / Espressif four-bit GHASH recurrence.
 * Included only by the source-hash-guarded esp_aes_gcm.c build-local copy.
 */

enum {
    YORADIO_GHASH_NIBBLE_VALUES = 16,
    YORADIO_GHASH_BYTE_VALUES = 256,
    /* Amortize key-table preparation over at least eight AES blocks. */
    YORADIO_GHASH_LARGE_MIN_BYTES = 8 * AES_BLOCK_BYTES,
};

/* Generated from last4: R8[b] = (R4[b & 15] >> 4) ^ R4[b >> 4].
 * The generator verifies every entry against eight polynomial shifts. */
#include "gcm_reduction8.inc"

typedef struct {
    uint64_t high[YORADIO_GHASH_NIBBLE_VALUES];
    uint64_t low[YORADIO_GHASH_NIBBLE_VALUES];
} yoradio_gcm_shifted_table;

_Static_assert(sizeof(yoradio_gcm_shifted_table) == 256,
               "GHASH scratch-table stack budget changed");

/* M(X) = S4(S4(Z) xor H[lo]) xor H[hi]
 *      = S8(Z) xor S4(H[lo]) xor H[hi].
 * S is the exact reduction shift in GF(2^128), not an integer truncation.
 * Input and output may be identical, as in the SDK's original gcm_mult.
 */
static void yoradio_gcm_mult_byte(const esp_gcm_context *ctx,
                                const yoradio_gcm_shifted_table *shifted,
                                const uint8_t x[AES_BLOCK_BYTES],
                                uint8_t output[AES_BLOCK_BYTES])
{
    unsigned low = x[AES_BLOCK_BYTES - 1] & 15U;
    unsigned high = x[AES_BLOCK_BYTES - 1] >> 4;
    uint64_t zh = shifted->high[low] ^ ctx->HH[high];
    uint64_t zl = shifted->low[low] ^ ctx->HL[high];
    for (int i = AES_BLOCK_BYTES - 2; i >= 0; --i) {
        low = x[i] & 15U;
        high = x[i] >> 4;
        unsigned remainder = (uint8_t)zl;
        zl = (zh << 56) | (zl >> 8);
        zh = (zh >> 8) ^ ((uint64_t)yoradio_gcm_reduction8[remainder] << 32);
        zh ^= shifted->high[low] ^ ctx->HH[high];
        zl ^= shifted->low[low] ^ ctx->HL[high];
    }
    PUT_UINT32_BE(zh >> 32, output, 0);
    PUT_UINT32_BE(zh, output, 4);
    PUT_UINT32_BE(zl >> 32, output, 8);
    PUT_UINT32_BE(zl, output, 12);
}

/* Keep the extra stack frame out of short AAD/tag/IV calls. No context ABI,
 * heap allocation, static mutable state or borrowed scratch lifetime changes.
 */
static void yoradio_gcm_prepare_shifted(const esp_gcm_context *ctx,
                                      yoradio_gcm_shifted_table *shifted)
{
    for (unsigned i = 0; i < YORADIO_GHASH_NIBBLE_VALUES; ++i) {
        uint64_t high = ctx->HH[i];
        uint64_t low = ctx->HL[i];
        shifted->low[i] = (high << 60) | (low >> 4);
        shifted->high[i] = (high >> 4) ^ ((uint64_t)last4[low & 15U] << 32);
    }
}

static __attribute__((noinline)) void yoradio_gcm_ghash_large(
        esp_gcm_context *ctx, const uint8_t *input, size_t length, uint8_t *z)
{
    yoradio_gcm_shifted_table shifted;
    yoradio_gcm_prepare_shifted(ctx, &shifted);
    while (length >= AES_BLOCK_BYTES) {
        xor_data(z, input);
        yoradio_gcm_mult_byte(ctx, &shifted, z, z);
        input += AES_BLOCK_BYTES;
        length -= AES_BLOCK_BYTES;
    }
    if (length) {
        /* XOR only real bytes: the remaining block bytes are zero padding. */
        for (size_t i = 0; i < length; ++i) z[i] ^= input[i];
        yoradio_gcm_mult_byte(ctx, &shifted, z, z);
    }
    mbedtls_platform_zeroize(&shifted, sizeof(shifted));
}
