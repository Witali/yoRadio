#include "opus_memory.h"
#include <assert.h>
#include <stdio.h>

/* Also compiled as a target snippet. Inspect these functions even where a
 * caller consumes only one halfword, and inspect the real copy/clear objects. */
__attribute__((noinline)) int16_t opus_word_load_low(const int32_t *p) {
    return (int16_t)yoradio_opus_load32(p);
}
__attribute__((noinline)) int16_t opus_word_load_high(const int32_t *p) {
    return (int16_t)(yoradio_opus_load32(p) >> 16);
}
__attribute__((noinline)) int16_t opus_word_table_first(const int32_t *p) {
    return yoradio_opus_table_read16((const int16_t *)p);
}
__attribute__((noinline)) int16_t opus_word_table_second(const int32_t *p) {
    return yoradio_opus_table_read16((const int16_t *)p + 1);
}
__attribute__((noinline)) int32_t opus_word_write_read(int32_t *p, int32_t value) {
    yoradio_opus_store32(p, value);
    return yoradio_opus_load32(p);
}
__attribute__((noinline)) int32_t opus_word_alias_order(int32_t *p, int32_t value) {
    *p = value;
    int32_t observed = yoradio_opus_load32(p);
    yoradio_opus_store32(p, observed ^ 0x13579bdf);
    return *p;
}

#ifndef OPUS_WORD_TARGET_SNIPPET
int main(void) {
    uint32_t random = 0x82435371;
    for (unsigned i = 0; i < 100000; i++) {
        random ^= random << 13; random ^= random >> 17; random ^= random << 5;
        int32_t value = (int32_t)random, storage = 0;
        assert(opus_word_write_read(&storage, value) == value);
        assert(opus_word_load_low(&storage) == (int16_t)value);
        assert(opus_word_load_high(&storage) == (int16_t)(value >> 16));
        assert(opus_word_alias_order(&storage, value) == (value ^ 0x13579bdf));
    }
    for (unsigned value = 0; value < 65536; value++) {
        yoradio_opus_table_pair table;
        table.half[0] = (int16_t)value;
        table.half[1] = (int16_t)(65535 - value);
        assert(opus_word_table_first((const int32_t *)&table) == table.half[0]);
        assert(opus_word_table_second((const int32_t *)&table) == table.half[1]);
    }
    for (size_t size = 1; size <= 8; size *= 2) {
        for (size_t count = 0; count <= 32; count++) {
            for (size_t source = 0; source <= 8; source++) {
                for (size_t target = 0; target <= 8; target++) {
                    uint32_t expected[96], actual[96];
                    for (size_t i = 0; i < 96; i++) expected[i] = actual[i] = (uint32_t)i * 0x135798U;
                    memmove(expected + target, expected + source, count * size);
                    yoradio_opus_copy(actual + target, actual + source, count, size);
                    assert(memcmp(actual, expected, sizeof(actual)) == 0);
                    memset(expected + target, 0, count * size);
                    yoradio_opus_clear(actual + target, count, size);
                    assert(memcmp(actual, expected, sizeof(actual)) == 0);
                }
            }
        }
    }
    printf("Opus private word helpers PASS: macro=%d; overlaps, tails, signed halves, alias ordering\n", YORADIO_OPUS_WORD_ASM);
    return 0;
}
#endif
