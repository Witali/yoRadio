#include "vq.c"
#include <assert.h>
#include <stdio.h>

#ifdef ROTATION_TEST_DISPATCH
/* Host-only stand-in checks C dispatch/arguments, not assembly execution.
 * The actual .S text is checked independently by the instruction model. */
static unsigned rotation_calls;
void yoradio_opus_exp_rotation1_stride1_lx106(celt_norm *X, int len,
                                             opus_val16 c, opus_val16 s)
{
    ++rotation_calls;
    const opus_val16 ms = NEG16(s);
    for (int i = 0; i < len - 1; ++i) {
        const celt_norm x1 = X[i], x2 = X[i+1];
        X[i+1] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2), s, x1), 15));
        X[i] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
    }
    for (int i = len - 3; i >= 0; --i) {
        const celt_norm x1 = X[i], x2 = X[i+1];
        X[i+1] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2), s, x1), 15));
        X[i] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
    }
}
#endif

int main(int argc, char **argv)
{
    assert(argc == 3);
    FILE *input = fopen(argv[1], "rb"), *output = fopen(argv[2], "wb");
    assert(input && output);
    int32_t header[4];
    int16_t data[968];
    while (fread(header, sizeof(header), 1, input) == 1) {
        const int n = header[0], stride = header[1];
        assert(n >= 1 && n <= 960 && stride >= 1 && stride <= n);
        for (int i = 0; i < n+8; ++i) data[i] = (int16_t)0x5aa5;
        assert(fread(data+4, sizeof(*data), n, input) == (size_t)n);
#ifdef ROTATION_TEST_DISPATCH
        const unsigned before = rotation_calls;
#endif
        exp_rotation1(data+4, n, stride, (opus_val16)header[2], (opus_val16)header[3]);
#ifdef ROTATION_TEST_DISPATCH
        assert(rotation_calls - before == (unsigned)(stride == 1));
#endif
        for (int i = 0; i < 4; ++i) assert(data[i] == (int16_t)0x5aa5 && data[n+4+i] == (int16_t)0x5aa5);
        assert(fwrite(data, sizeof(*data), n+8, output) == (size_t)n+8);
    }
    assert(feof(input) && !ferror(input));
    assert(fclose(input) == 0 && fclose(output) == 0);
    return 0;
}
