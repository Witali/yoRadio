#include "vq.c"
#include <assert.h>
#include <stdio.h>

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
        exp_rotation1(data+4, n, stride, (opus_val16)header[2], (opus_val16)header[3]);
        for (int i = 0; i < 4; ++i) assert(data[i] == (int16_t)0x5aa5 && data[n+4+i] == (int16_t)0x5aa5);
        assert(fwrite(data, sizeof(*data), n+8, output) == (size_t)n+8);
    }
    assert(feof(input) && !ferror(input));
    assert(fclose(input) == 0 && fclose(output) == 0);
    return 0;
}
