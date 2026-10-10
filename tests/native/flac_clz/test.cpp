#include <cassert>
#include <cstdio>
#include "batches.h"

using namespace flac_clz;
uint64_t generic_checks = 0, byte_checks = 0, rice_checks = 0;

unsigned reference32(uint32_t value) {
    unsigned zeros = 0;
    for(uint32_t mask = UINT32_C(0x80000000); mask && !(value & mask); mask >>= 1) ++zeros;
    return zeros;
}

void generic(uint32_t value) {
    const unsigned expected = reference32(value);
    assert(intrinsic32(value) == expected);
    assert(staged32(value) == expected);
    ++generic_checks;
}

int main() {
    for(unsigned value = 0; value <= UINT8_MAX; ++value) {
        generic(value);
        const unsigned expected = reference32(value) - (kWordBits - kByteBits);
        assert(groups8(value) == expected);
        assert(nibble16(value) == expected);
        assert(byte256(value) == expected);
        assert(packed_nibble(value) == expected);
        ++byte_checks;
    }
    // Every possible cache is tested for every valid width, including zero.
    for(unsigned bits = 1; bits <= kByteBits; ++bits)
        for(unsigned value = 0; value < (1U << bits); ++value) {
            Sample sample{static_cast<uint8_t>(value), static_cast<uint8_t>(bits)};
            const unsigned expected = reference32(value) - (kWordBits - bits);
            assert(rice_intrinsic(sample) == expected);
            assert(rice_staged(sample) == expected);
            assert(rice_groups(sample) == expected);
            assert(rice_nibble(sample) == expected);
            assert(rice_table(sample) == expected);
            assert(rice_packed(sample) == expected);
            ++rice_checks;
        }
    for(unsigned bit = 0; bit < kWordBits; ++bit) {
        const uint32_t value = UINT32_C(1) << bit;
        generic(value-1); generic(value); generic(value+1);
        generic(~value); generic(UINT32_MAX >> bit);
    }
    generic(0); generic(UINT32_MAX);
    uint32_t random = UINT32_C(0xC351AC);
    for(unsigned i = 0; i < 1000000; ++i) {
        random ^= random << 13; random ^= random >> 17; random ^= random << 5;
        generic(random);
    }
    Sample cached[510];
    size_t count = 0;
    uint32_t expected = 0, identity = 0;
    for(unsigned bits = 1; bits <= kByteBits; ++bits)
        for(unsigned value = 0; value < (1U << bits); ++value) {
            cached[count++] = {static_cast<uint8_t>(value), static_cast<uint8_t>(bits)};
            expected += reference32(value) - (kWordBits - bits);
            identity += value + bits;
        }
    assert(count == 510);
    for(const auto& variant : kVariants) {
        assert(variant.batch(cached, count, 3) == 3 * (variant.identity ? identity : expected));
        assert(variant.batch(cached, 0, 3) == 0);
    }
    uint32_t words[2048];
    expected = identity = 0;
    for(auto& word : words) {
        random ^= random << 13; random ^= random >> 17; random ^= random << 5;
        word = random;
        expected += reference32(word); identity += word;
    }
    for(const auto& variant : kVariants32) {
        assert(variant.batch(words, 2048, 3) == 3 * (variant.identity ? identity : expected));
        assert(variant.batch(words, 0, 3) == 0);
    }
    std::printf("{\"passed\":true,\"generic32_checks\":%llu,\"all_byte_checks\":%llu,\"all_rice_checks\":%llu}\n",
        static_cast<unsigned long long>(generic_checks), static_cast<unsigned long long>(byte_checks),
        static_cast<unsigned long long>(rice_checks));
}
