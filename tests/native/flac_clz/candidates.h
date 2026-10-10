#pragma once
#include <cstdint>

namespace flac_clz {
#define FLAC_CLZ_INLINE inline __attribute__((always_inline))
constexpr unsigned kWordBits = 32;
constexpr unsigned kByteBits = 8;
static_assert(sizeof(unsigned) * kByteBits == kWordBits, "CLZ intrinsic requires 32-bit unsigned");

// These two functions support the complete uint32_t domain, including zero.
FLAC_CLZ_INLINE unsigned intrinsic32(uint32_t value) {
    return value ? static_cast<unsigned>(__builtin_clz(static_cast<unsigned>(value))) : kWordBits;
}

FLAC_CLZ_INLINE unsigned staged32(uint32_t value) {
    if(!value) return kWordBits;
    unsigned zeros = 0;
    if(value < UINT32_C(0x00010000)) { zeros += 16; value <<= 16; }
    if(value < UINT32_C(0x01000000)) { zeros += 8; value <<= 8; }
    if(value < UINT32_C(0x10000000)) { zeros += 4; value <<= 4; }
    if(value < UINT32_C(0x40000000)) { zeros += 2; value <<= 2; }
    return zeros + (value < UINT32_C(0x80000000));
}

// Byte functions support all 256 inputs, returning eight for zero.
FLAC_CLZ_INLINE unsigned groups8(uint8_t byte) {
    if(!byte) return kByteBits;
    unsigned value = byte, zeros = 0;
    if(value < 16) { zeros += 4; value <<= 4; }
    if(value < 64) { zeros += 2; value <<= 2; }
    return zeros + (value < 128);
}

// Ordinary const data: on ESP-IDF these tables must be audited in Flash rodata,
// rather than moved into DRAM to give an unreported lookup advantage.
static const uint8_t kNibbleZeros[16] = {4,3,2,2,1,1,1,1,0,0,0,0,0,0,0,0};
FLAC_CLZ_INLINE unsigned nibble16(uint8_t value) {
    const unsigned high = value >> 4;
    return high ? kNibbleZeros[high] : 4 + kNibbleZeros[value];
}

static const uint8_t kByteZeros[256] = {
    8,7,6,6,5,5,5,5,4,4,4,4,4,4,4,4,
    3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,
    2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
};
FLAC_CLZ_INLINE unsigned byte256(uint8_t value) { return kByteZeros[value]; }

// Entry n occupies bits 2*n..2*n+1. Nonzero nibble leading-zero counts are
// 3,2,2,1,1,1,1,0..0, which pack into 0x55AC. Zero needs the separate guard
// because its count (four) cannot fit in two bits. The largest shift is 30.
constexpr uint32_t kPackedNibbleZeros = UINT32_C(0x000055AC);
FLAC_CLZ_INLINE unsigned packed_nibble(uint8_t value) {
    if(!value) return kByteBits;
    const unsigned high = value >> 4;
    const unsigned nibble = high ? high : value;
    return (high ? 0 : 4) + ((kPackedNibbleZeros >> (2 * nibble)) & 3);
}

struct Sample { uint8_t cached; uint8_t valid_bits; };

// Rice inputs contain only their valid low 1..8 bits. The common zero guard
// mirrors production's separate all-zero unary-chunk handling.
FLAC_CLZ_INLINE unsigned rice_intrinsic(Sample sample) {
    return sample.cached ? intrinsic32(sample.cached) - (kWordBits - sample.valid_bits)
                         : sample.valid_bits;
}
FLAC_CLZ_INLINE unsigned rice_staged(Sample sample) {
    return sample.cached ? staged32(sample.cached) - (kWordBits - sample.valid_bits)
                         : sample.valid_bits;
}
#define FLAC_CLZ_RICE_BYTE(name, function) \
    FLAC_CLZ_INLINE unsigned name(Sample sample) { \
        return sample.cached ? function(sample.cached) - (kByteBits - sample.valid_bits) \
                             : sample.valid_bits; \
    }
FLAC_CLZ_RICE_BYTE(rice_groups, groups8)
FLAC_CLZ_RICE_BYTE(rice_nibble, nibble16)
FLAC_CLZ_RICE_BYTE(rice_table, byte256)
FLAC_CLZ_RICE_BYTE(rice_packed, packed_nibble)
#undef FLAC_CLZ_RICE_BYTE
#undef FLAC_CLZ_INLINE
} // namespace flac_clz
