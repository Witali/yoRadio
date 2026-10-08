#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

/* Independent bit-serial multiplication: NIST SP 800-38D, Algorithm 1. */
static void reference_multiply(const uint8_t *x, const uint8_t *h, uint8_t *out)
{
    uint8_t v[16], z[16] = {0};
    memcpy(v, h, 16);
    for (unsigned bit = 0; bit < 128; ++bit) {
        if ((x[bit / 8] >> (7 - bit % 8)) & 1U)
            for (unsigned i = 0; i < 16; ++i) z[i] ^= v[i];
        unsigned reduce = v[15] & 1U;
        for (unsigned i = 15; i; --i) v[i] = (v[i] >> 1) | (v[i-1] << 7);
        v[0] = (v[0] >> 1) ^ (reduce ? 0xe1U : 0U);
    }
    memcpy(out, z, 16);
}

static uint32_t random_word(void)
{
    static uint32_t state = 0x74cb1859U;
    state ^= state << 13; state ^= state >> 17; state ^= state << 5;
    return state;
}

static void multiply(esp_gcm_context *ctx, const uint8_t *x, uint8_t *out)
{
#if CANDIDATE
    yoradio_gcm_shifted_table shifted;
    yoradio_gcm_prepare_shifted(ctx, &shifted);
    yoradio_gcm_mult_byte(ctx, &shifted, x, out);
    mbedtls_platform_zeroize(&shifted, sizeof(shifted));
#else
    gcm_mult(ctx, x, out);
#endif
}

static void reference_ghash(const uint8_t *h, const uint8_t *input, size_t length, uint8_t *z)
{
    while (length) {
        size_t count = length < 16 ? length : 16;
        for (size_t i=0; i<count; ++i) z[i] ^= input[i];
        reference_multiply(z, h, z);
        input += count; length -= count;
    }
}

static void test_fields(void)
{
    esp_gcm_context ctx = {0};
    uint8_t x[32], result[32], expected[16], alias[32];
    const uint8_t fills[]={0,0xff,0x55,0xaa};
    for (unsigned hi=0; hi<4; ++hi) for (unsigned xi=0; xi<4; ++xi) {
        memset(ctx.H,fills[hi],16); memset(x,fills[xi],16); gcm_gen_table(&ctx);
        reference_multiply(x,ctx.H,expected); multiply(&ctx,x,result);
        assert(memcmp(result,expected,16)==0);
    }
    for (unsigned hbit=0; hbit<128; ++hbit) {
        memset(ctx.H,0,16); ctx.H[hbit/8] = 1U << (hbit%8); gcm_gen_table(&ctx);
        for (unsigned xbit=0; xbit<128; ++xbit) {
            memset(x,0,16); x[xbit/8] = 1U << (xbit%8);
            reference_multiply(x,ctx.H,expected);
            multiply(&ctx,x,result);
            assert(memcmp(result,expected,16)==0);
        }
    }
    for (unsigned sample=0; sample<8192; ++sample) {
        unsigned offset = sample%16;
        for (unsigned i=0; i<16; ++i) {ctx.H[i]=random_word(); x[offset+i]=random_word();}
        gcm_gen_table(&ctx);
        reference_multiply(x+offset,ctx.H,expected);
        memset(result,0xab,sizeof(result));
        multiply(&ctx,x+offset,result+offset);
        assert(memcmp(result+offset,expected,16)==0);
        for (unsigned i=0; i<32; ++i)
            if (i<offset || i>=offset+16) assert(result[i]==0xab);
        memcpy(alias,x,sizeof(alias)); multiply(&ctx,alias+offset,alias+offset);
        assert(memcmp(alias+offset,expected,16)==0);
    }
    puts("PASS 16 zero/ones/alternating pairs; 16384 basis pairs; 8192 random products, in-place and all 16 alignments");
}

static void test_lengths(void)
{
    esp_gcm_context ctx = {0};
    for (unsigned sample=0; sample<640; ++sample) {
        size_t length = sample<512 ? sample : 16000+(sample-512)*3;
        unsigned offset=sample%16;
        uint8_t *allocation=malloc(length+offset);
        assert(allocation || length+offset==0);
        uint8_t *input=allocation ? allocation+offset : NULL;
        uint8_t initial[16], expected[16], guarded[48];
        for (unsigned i=0; i<16; ++i) {ctx.H[i]=random_word(); initial[i]=random_word();}
        for (size_t i=0; i<length; ++i) input[i]=random_word();
        gcm_gen_table(&ctx);
        memcpy(expected,initial,16); reference_ghash(ctx.H,input,length,expected);
        memset(guarded,0xab,sizeof(guarded)); memcpy(guarded+offset,initial,16);
        esp_gcm_ghash(&ctx,input,length,guarded+offset);
        assert(memcmp(guarded+offset,expected,16)==0);
        for (size_t i=0; i<sizeof(guarded); ++i)
            if (i<offset || i>=offset+16) assert(guarded[i]==0xab);
        free(allocation);
    }
    puts("PASS 640 lengths including every short tail, threshold and large unaligned input");
}

static uint32_t read_u32(FILE *f)
{
    uint8_t b[4]; assert(fread(b,1,4,f)==4);
    return b[0] | (uint32_t)b[1]<<8 | (uint32_t)b[2]<<16 | (uint32_t)b[3]<<24;
}

static void test_gcm_vectors(const char *path)
{
    FILE *f=fopen(path,"rb"); assert(f);
    uint32_t count=read_u32(f);
    for (uint32_t sample=0; sample<count; ++sample) {
        esp_gcm_context ctx={0}; uint8_t expected[16];
        uint32_t length=read_u32(f);
        assert(fread(ctx.H,1,16,f)==16); assert(fread(expected,1,16,f)==16);
        uint8_t *body=malloc(length); assert(body && length%16==0);
        assert(fread(body,1,length,f)==length); gcm_gen_table(&ctx);
        for (unsigned mode=0; mode<3; ++mode) {
            memset(ctx.ghash,0,16); ctx.ghash_buf_len=0;
            size_t at=0;
            while (at<length) {
                static const size_t chunks[]={1,7,15,16,17,127,128,129,1024};
                size_t n=mode==0 ? length : mode==1 ? 1 : chunks[(at+sample)%9];
                if (n>length-at) n=length-at;
                esp_gcm_ghash_buffered(&ctx,body+at,n); at+=n;
            }
            assert(ctx.ghash_buf_len==0);
            assert(memcmp(ctx.ghash,expected,16)==0);
        }
        free(body);
    }
    assert(fgetc(f)==EOF); fclose(f);
    printf("PASS %u independent AES-GCM tag equations in whole, byte and mixed chunks\n",count);
}

int main(int argc, char **argv)
{
    assert(argc==2);
    test_fields(); test_lengths(); test_gcm_vectors(argv[1]);
    puts("PASS GHASH: exact bits, guarded buffers, no sanitizer errors");
    return 0;
}
