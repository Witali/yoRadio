#include <stdint.h>
#include <stddef.h>
#include <string.h>
#define AES_BLOCK_BYTES 16
typedef struct {
    uint8_t H[16],ghash[16]; uint64_t HL[16],HH[16];
    uint8_t ghash_buf[16]; size_t ghash_buf_len;
} esp_gcm_context;
static void mbedtls_platform_zeroize(void *p, size_t n) {
    volatile uint8_t *v=p; while(n--) *v++=0;
}

#define CANDIDATE 1
/* Function to xor two data blocks */
static void xor_data(uint8_t *d, const uint8_t *s)
{
    for (int i = 0; i < AES_BLOCK_BYTES; i++) {
        d[i] ^= s[i];
    }
}


/*
 * 32-bit integer manipulation macros (big endian)
 */
#ifndef GET_UINT32_BE
#define GET_UINT32_BE(n,b,i)                            \
{                                                       \
    (n) = ( (uint32_t) (b)[(i)    ] << 24 )             \
        | ( (uint32_t) (b)[(i) + 1] << 16 )             \
        | ( (uint32_t) (b)[(i) + 2] <<  8 )             \
        | ( (uint32_t) (b)[(i) + 3]       );            \
}
#endif

#ifndef PUT_UINT32_BE
#define PUT_UINT32_BE(n,b,i)                            \
{                                                       \
    (b)[(i)    ] = (unsigned char) ( (n) >> 24 );       \
    (b)[(i) + 1] = (unsigned char) ( (n) >> 16 );       \
    (b)[(i) + 2] = (unsigned char) ( (n) >>  8 );       \
    (b)[(i) + 3] = (unsigned char) ( (n)       );       \
}
#endif

/* Based on MbedTLS's implementation
 *
 * Precompute small multiples of H, that is set
 *      HH[i] || HL[i] = H times i,
 * where i is seen as a field element as in [MGV], ie high-order bits
 * correspond to low powers of P. The result is stored in the same way, that
 * is the high-order bit of HH corresponds to P^0 and the low-order bit of HL
 * corresponds to P^127.
 */
static int gcm_gen_table( esp_gcm_context *ctx )
{
    int i, j;
    uint64_t hi, lo;
    uint64_t vl, vh;
    unsigned char *h;

    h = ctx->H;

    /* pack h as two 64-bits ints, big-endian */
    GET_UINT32_BE( hi, h,  0  );
    GET_UINT32_BE( lo, h,  4  );
    vh = (uint64_t) hi << 32 | lo;

    GET_UINT32_BE( hi, h,  8  );
    GET_UINT32_BE( lo, h,  12 );
    vl = (uint64_t) hi << 32 | lo;

    /* 8 = 1000 corresponds to 1 in GF(2^128) */
    ctx->HL[8] = vl;
    ctx->HH[8] = vh;

    /* 0 corresponds to 0 in GF(2^128) */
    ctx->HH[0] = 0;
    ctx->HL[0] = 0;

    for ( i = 4; i > 0; i >>= 1 ) {
        uint32_t T = ( vl & 1 ) * 0xe1000000U;
        vl  = ( vh << 63 ) | ( vl >> 1 );
        vh  = ( vh >> 1 ) ^ ( (uint64_t) T << 32);

        ctx->HL[i] = vl;
        ctx->HH[i] = vh;
    }

    for ( i = 2; i <= 8; i *= 2 ) {
        uint64_t *HiL = ctx->HL + i, *HiH = ctx->HH + i;
        vh = *HiH;
        vl = *HiL;
        for ( j = 1; j < i; j++ ) {
            HiH[j] = vh ^ ctx->HH[j];
            HiL[j] = vl ^ ctx->HL[j];
        }
    }

    return ( 0 );
}
/*
 * Shoup's method for multiplication use this table with
 *      last4[x] = x times P^128
 * where x and last4[x] are seen as elements of GF(2^128) as in [MGV]
 */
static const uint32_t last4[16] = {
    0x00000000, 0x1c200000, 0x38400000, 0x24600000,
    0x70800000, 0x6ca00000, 0x48c00000, 0x54e00000,
    0xe1000000, 0xfd200000, 0xd9400000, 0xc5600000,
    0x91800000, 0x8da00000, 0xa9c00000, 0xb5e00000
};
/* Based on MbedTLS's implementation
 *
 * Sets output to x times H using the precomputed tables.
 * x and output are seen as elements of GF(2^128) as in [MGV].
 */
static void gcm_mult( esp_gcm_context *ctx, const unsigned char x[16],
                      unsigned char output[16] )
{
    int i = 0;
    unsigned char lo, hi, rem;
    uint64_t zh, zl;

    lo = x[15] & 0xf;
    hi = x[15] >> 4;

    zh = ctx->HH[lo];
    zl = ctx->HL[lo];

    rem = (unsigned char) zl & 0xf;
    zl = ( zh << 60 ) | ( zl >> 4 );
    zh = ( zh >> 4 );
    zh ^= (uint64_t) last4[rem] << 32;
    zh ^= ctx->HH[hi];
    zl ^= ctx->HL[hi];

    for ( i = 14; i >= 0; i-- ) {
        lo = x[i] & 0xf;
        hi = x[i] >> 4;

        rem = (unsigned char) zl & 0xf;
        zl = ( zh << 60 ) | ( zl >> 4 );
        zh = ( zh >> 4 );
        zh ^= (uint64_t) last4[rem] << 32;
        zh ^= ctx->HH[lo];
        zl ^= ctx->HL[lo];

        rem = (unsigned char) zl & 0xf;
        zl = ( zh << 60 ) | ( zl >> 4 );
        zh = ( zh >> 4 );
        zh ^= (uint64_t) last4[rem] << 32;
        zh ^= ctx->HH[hi];
        zl ^= ctx->HL[hi];
    }

    PUT_UINT32_BE( zh >> 32, output, 0 );
    PUT_UINT32_BE( zh, output, 4 );
    PUT_UINT32_BE( zl >> 32, output, 8 );
    PUT_UINT32_BE( zl, output, 12 );
}



#include "gcm_byte_ghash.inc"

static void esp_gcm_ghash(esp_gcm_context *ctx, const unsigned char *x, size_t x_len, uint8_t *z)
{
    if (x_len >= YORADIO_GHASH_LARGE_MIN_BYTES) {
        yoradio_gcm_ghash_large(ctx, x, x_len, z);
        return;
    }


    uint8_t tmp[AES_BLOCK_BYTES];

    memset(tmp, 0, AES_BLOCK_BYTES);
    /* GHASH(X) is calculated on input string which is multiple of 128 bits
     * If input string bit length is not multiple of 128 bits it needs to
     * be padded by 0
     *
     * Steps:
     * 1. Let X1, X2, ... , Xm-1, Xm denote the unique sequence of blocks such
     * that X = X1 || X2 || ... || Xm-1 || Xm.
     * 2. Let Y0 be the “zero block,” 0128.
     * 3. Fori=1,...,m,letYi =(Yi-1 ^ Xi)•H.
     * 4. Return Ym
     */

    /* If input bit string is >= 128 bits, process full 128 bit blocks */
    while (x_len >= AES_BLOCK_BYTES) {

        xor_data(z, x);
        gcm_mult(ctx, z, z);

        x += AES_BLOCK_BYTES;
        x_len -= AES_BLOCK_BYTES;
    }

    /* If input bit string is not multiple of 128 create last 128 bit
     * block by padding necessary 0s
     */
    if (x_len) {
        memcpy(tmp, x, x_len);
        xor_data(z, tmp);
        gcm_mult(ctx, z, z);
    }
}

/* Feed data into the running GHASH one full 16-byte block at a time, carrying
 * any sub-block remainder across calls in ctx->ghash_buf.
 */
static void esp_gcm_ghash_buffered(esp_gcm_context *ctx, const unsigned char *data, size_t len)
{
    size_t buffered = ctx->ghash_buf_len;

    if (len == 0) {
        return;
    }

    if (buffered) {
        size_t fill = AES_BLOCK_BYTES - buffered;
        if (fill > len) {
            fill = len;
        }
        memcpy(ctx->ghash_buf + buffered, data, fill);
        buffered += fill;
        data += fill;
        len -= fill;
        if (buffered == AES_BLOCK_BYTES) {
            esp_gcm_ghash(ctx, ctx->ghash_buf, AES_BLOCK_BYTES, ctx->ghash);
            buffered = 0;
        }
        ctx->ghash_buf_len = buffered;
    }

    size_t full = len - (len % AES_BLOCK_BYTES);
    if (full) {
        esp_gcm_ghash(ctx, data, full, ctx->ghash);
        data += full;
        len -= full;
    }

    if (len) {
        memcpy(ctx->ghash_buf, data, len);
        ctx->ghash_buf_len = len;
    }
}



#include "gcm_ghash_test.c"
