/* Differential VQ capture only: no packet, DSP, floor or production path. */
#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "codebook.h"
#include "native_vorbis_quant.h"
#include "vorbis_xiph_alloc.h"

static void require(int condition) {
    assert(condition);
    if (!condition) abort();
}

static uint32_t read_u32(FILE *input) {
    unsigned char bytes[4];
    require(fread(bytes, 1, sizeof(bytes), input) == sizeof(bytes));
    return (uint32_t)bytes[0] | (uint32_t)bytes[1] << 8 |
        (uint32_t)bytes[2] << 16 | (uint32_t)bytes[3] << 24;
}

static void write_u32(FILE *output, uint32_t value) {
    unsigned char bytes[4] = {
        (unsigned char)value, (unsigned char)(value >> 8),
        (unsigned char)(value >> 16), (unsigned char)(value >> 24)
    };
    require(fwrite(bytes, 1, sizeof(bytes), output) == sizeof(bytes));
}

static uint32_t float_bits(float value) {
    uint32_t bits;
    require(sizeof(value) == sizeof(bits));
    require(isfinite(value));
    memcpy(&bits, &value, sizeof(bits));
    return bits;
}

static void *array_storage(size_t count, size_t width) {
    require(count && width && count <= SIZE_MAX / width);
    void *result = malloc(count * width);
    require(result != NULL);
    return result;
}

static long packed_word(uint32_t word) {
    /* Preserve all packed bits, including sign, on the qualified hosts. */
    return (long)(unsigned long)word;
}

static uint64_t capture_book(FILE *input, FILE *output, uint32_t index) {
    uint32_t maptype = read_u32(input), sequence = read_u32(input);
    uint32_t dimensions = read_u32(input), entries = read_u32(input);
    uint32_t minimum = read_u32(input), delta = read_u32(input);
    uint32_t quantcount = read_u32(input);
    require((maptype == 1 || maptype == 2) && sequence <= 1);
    require(dimensions && dimensions <= 65535 && entries && entries <= 0xffffff);
    require(entries <= INT_MAX);
    uint64_t expected_count = 0;
    require(native_vorbis_quantization_count(dimensions, entries, maptype,
        &expected_count) == NATIVE_VORBIS_NUMERIC_OK);
    require(expected_count == quantcount && quantcount);
    uint64_t value_count = (uint64_t)entries * dimensions;
    require(value_count <= UINT32_MAX && value_count <= SIZE_MAX / sizeof(float));

    uint32_t *original = array_storage(quantcount, sizeof(*original));
    uint16_t *multiplicands = array_storage(quantcount, sizeof(*multiplicands));
    long *quantlist = array_storage(quantcount, sizeof(*quantlist));
    char *lengthlist = array_storage(entries, sizeof(*lengthlist));
    memset(lengthlist, 1, entries);
    for (uint32_t i = 0; i < quantcount; ++i) {
        original[i] = read_u32(input);
        require(original[i] <= UINT16_MAX);
        multiplicands[i] = (uint16_t)original[i];
        quantlist[i] = (long)original[i];
    }

    static_codebook source = {0};
    source.dim = (long)dimensions;
    source.entries = (long)entries;
    source.lengthlist = lengthlist;
    source.maptype = (int)maptype;
    source.q_min = packed_word(minimum);
    source.q_delta = packed_word(delta);
    source.q_quant = 16;
    source.q_sequencep = (int)sequence;
    source.quantlist = quantlist;
    unsigned char source_snapshot[sizeof(source)];
    memcpy(source_snapshot, &source, sizeof(source));

    native_vorbis_quantization_t exact = {0};
    exact.layout.dimensions = dimensions;
    exact.layout.entries = entries;
    exact.layout.lookup_type = maptype;
    exact.layout.minimum_bits = minimum;
    exact.layout.delta_bits = delta;
    exact.layout.value_bits = 16;
    exact.layout.sequence_p = sequence;
    exact.layout.multiplicand_count = quantcount;
    exact.multiplicands = multiplicands;
    exact.storage_count = quantcount;
    unsigned char exact_snapshot[sizeof(exact)];
    memcpy(exact_snapshot, &exact, sizeof(exact));

    require(xiph_port_test_live() == 0 && xiph_port_test_bytes() == 0);
    xiph_port_test_reset(0);
    float *values = _book_unquantize(&source, (int)entries, NULL);
    require(values != NULL && xiph_port_test_failures() == 0);
    require(xiph_port_test_live() == 1);
    require(xiph_port_test_bytes() == (size_t)value_count * sizeof(*values));

    const uint64_t before = UINT64_C(0x13579bdf02468ace);
    const uint64_t after = UINT64_C(0xfdb97531eca86420);
    require(sizeof(native_vorbis_affine_t) <=
        (SIZE_MAX - 2 * sizeof(uint64_t)) / (size_t)dimensions);
    size_t row_bytes = (size_t)dimensions * sizeof(native_vorbis_affine_t);
    unsigned char *guarded = array_storage(1, row_bytes + 2 * sizeof(uint64_t));
    native_vorbis_affine_t *row = (void *)(guarded + sizeof(uint64_t));
    memcpy(guarded, &before, sizeof(before));
    memcpy(guarded + sizeof(uint64_t) + row_bytes, &after, sizeof(after));
    write_u32(output, index);
    write_u32(output, (uint32_t)value_count);
    for (uint32_t entry = 0; entry < entries; ++entry) {
        memset(row, 0xa5, row_bytes);
        require(native_vorbis_quantization_vector(&exact, entry, dimensions,
            row, dimensions) == NATIVE_VORBIS_NUMERIC_OK);
        require(memcmp(guarded, &before, sizeof(before)) == 0);
        require(memcmp(guarded + sizeof(uint64_t) + row_bytes,
            &after, sizeof(after)) == 0);
        for (uint32_t component = 0; component < dimensions; ++component) {
            size_t offset = (size_t)entry * dimensions + component;
            write_u32(output, float_bits(values[offset]));
            write_u32(output, row[component].minimum_bits);
            write_u32(output, row[component].delta_bits);
            write_u32(output, row[component].minimum_multiplier);
            write_u32(output, row[component].delta_multiplier);
        }
    }
    require(memcmp(&source, source_snapshot, sizeof(source)) == 0);
    require(memcmp(&exact, exact_snapshot, sizeof(exact)) == 0);
    for (uint32_t i = 0; i < quantcount; ++i) {
        require(quantlist[i] == (long)original[i]);
        require(multiplicands[i] == original[i]);
    }
    for (uint32_t i = 0; i < entries; ++i) require(lengthlist[i] == 1);
    xiph_port_test_free(values);
    require(xiph_port_test_live() == 0 && xiph_port_test_bytes() == 0);
    free(guarded);
    free(lengthlist);
    free(quantlist);
    free(multiplicands);
    free(original);
    return value_count;
}

int main(int argc, char **argv) {
    require(argc == 3);
    require(CHAR_BIT == 8 && FLT_RADIX == 2 && FLT_MANT_DIG == 24 &&
        FLT_MAX_EXP == 128 && sizeof(float) == 4);
    FILE *input = fopen(argv[1], "rb");
    require(input != NULL);
    FILE *output = fopen(argv[2], "wb");
    require(output != NULL);
    unsigned char magic[8];
    require(fread(magic, 1, sizeof(magic), input) == sizeof(magic));
    require(memcmp(magic, "XIPHVQ01", sizeof(magic)) == 0);
    require(fwrite("XIPHVQO1", 1, sizeof(magic), output) == sizeof(magic));
    uint32_t scalars = read_u32(input);
    write_u32(output, scalars);
    for (uint32_t i = 0; i < scalars; ++i) {
        uint32_t word = read_u32(input);
        write_u32(output, word);
        write_u32(output, float_bits(_float32_unpack(packed_word(word))));
    }
    uint32_t books = read_u32(input);
    write_u32(output, books);
    uint64_t values = 0;
    for (uint32_t i = 0; i < books; ++i) {
        uint64_t count = capture_book(input, output, i);
        require(values <= UINT64_MAX - count);
        values += count;
    }
    require(fgetc(input) == EOF && !ferror(input));
    require(fclose(input) == 0 && fclose(output) == 0);
    require(xiph_port_test_live() == 0 && xiph_port_test_bytes() == 0);
    printf("VQ_RANGE_CAPTURE scalars=%" PRIu32 " books=%" PRIu32
        " values=%" PRIu64 " live=0 bytes=0\n", scalars, books, values);
    return 0;
}
