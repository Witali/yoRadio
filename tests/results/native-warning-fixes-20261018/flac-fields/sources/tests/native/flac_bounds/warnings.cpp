// Actual FLAC code: signed-field reconstruction, wasted-bit bounds and errors.
#include "flac_decoder.cpp"
#include <cassert>
#include <cstdio>
#include <vector>

namespace {
struct Bits {
    std::vector<uint8_t> bytes;
    size_t count = 0;
    void put(uint32_t value, unsigned width) {
        for(unsigned bit = width; bit; --bit) {
            if(count % 8 == 0) bytes.push_back(0);
            bytes.back() |= ((value >> (bit - 1)) & 1U) << (7 - count % 8);
            ++count;
        }
    }
};
void input(std::vector<uint8_t>& data) {
    FLACDecoderReset(); m_inptr = data.data();
    m_bytesAvail = static_cast<int32_t>(data.size()); m_rIndex = 0;
}
int32_t expectedSigned(uint32_t raw, unsigned width) {
    const uint64_t modulus = UINT64_C(1) << width;
    const uint64_t value = raw & (modulus - 1U);
    const int64_t expected = value >= modulus / 2
        ? static_cast<int64_t>(value) - static_cast<int64_t>(modulus)
        : static_cast<int64_t>(value);
    assert(expected >= INT32_MIN && expected <= INT32_MAX);
    return static_cast<int32_t>(expected);
}
unsigned signedCases, wastedCases, invalidCases;
void checkSigned(uint32_t raw, unsigned width, unsigned padding) {
    Bits bits; bits.put(0xA5, padding); bits.put(raw, width);
    input(bits.bytes);
    if(padding) readUint(static_cast<uint8_t>(padding));
    const int32_t actual = readSignedInt(static_cast<int>(width));
    assert(!m_readError && actual == expectedSigned(raw, width));
    ++signedCases;
}
void signedFields() {
    uint32_t random = 0x83b139e7U;
    for(unsigned width = 1; width <= 32; ++width) {
        const uint32_t sign = UINT32_C(1) << (width - 1);
        const uint32_t mask = sign | (sign - 1U);
        const uint32_t edge[] = {0, mask, sign, sign - 1U, sign + 1U,
                                 0xAAAAAAAAU & mask, 0x55555555U & mask};
        for(unsigned padding = 0; padding < 8; ++padding) {
            for(uint32_t raw : edge) checkSigned(raw, width, padding);
            for(unsigned i = 0; i < 1000; ++i) {
                random = random * 1664525U + 1013904223U;
                checkSigned(random, width, padding);
            }
        }
    }
    for(unsigned raw = 0; raw <= UINT16_MAX; ++raw) checkSigned(raw, 16, 0);
    for(unsigned raw = 0; raw <= UINT8_MAX; ++raw) checkSigned(raw, 8, 0);
    std::vector<uint8_t> empty;
    input(empty); assert(readSignedInt(0) == 0 && !m_readError);
    for(int invalid : {-1, 33, 255}) {
        input(empty); assert(readSignedInt(invalid) == 0 && m_readError == ERR_FLAC_INVALID_DATA);
        ++invalidCases;
    }
    for(int width = 1; width <= 32; ++width) {
        input(empty); assert(readSignedInt(width) == 0 && m_readError == ERR_FLAC_TRUNCATED_INPUT);
        ++invalidCases;
    }
}
void wastedBits() {
    assert(FLACDecoder_AllocateBuffers(16, 2)); m_blockSize = 16;
    for(unsigned depth = 1; depth <= FLAC_MAX_BITS_PER_SAMPLE + 1U; ++depth) {
        for(unsigned shift = 0; shift < depth; ++shift) {
            unsigned reduced = depth - shift;
            const int32_t limit = INT32_C(1) << (reduced - 1);
            const int32_t values[] = {-limit, -limit + 1, -1, 0, limit > 1 ? 1 : 0, limit - 1};
            for(uint8_t channel = 0; channel < 2; ++channel) {
                for(int32_t value : values) {
                    Bits bits; bits.put(shift ? 1 : 0, 8);
                    if(shift) bits.put(1, shift);
                    bits.put(static_cast<uint32_t>(value), reduced);
                    input(bits.bytes);
                    assert(decodeSubframe(static_cast<uint8_t>(depth), channel) == ERR_FLAC_NONE);
                    int64_t expected = static_cast<int64_t>(value) * (INT64_C(1) << shift);
                    for(unsigned i = 0; i < m_blockSize; ++i)
                        assert(samplesBuffer[channel][i] == expected);
                    ++wastedCases;
                }
            }
        }
        // Wasted count equal to the original depth would leave no sample bit.
        Bits invalid; invalid.put(1, 8); invalid.put(1, depth);
        input(invalid.bytes);
        assert(decodeSubframe(static_cast<uint8_t>(depth), 0) == ERR_FLAC_INVALID_DATA);
        ++invalidCases;
        // An unterminated wasted-bit run is bounded by depth or input extent.
        Bits truncated; truncated.put(1, 8); truncated.put(0, depth);
        input(truncated.bytes);
        assert(decodeSubframe(static_cast<uint8_t>(depth), 1) < 0);
        ++invalidCases;
    }
    for(uint8_t depth : {0, 26, 32, 255}) {
        std::vector<uint8_t> empty; input(empty);
        assert(decodeSubframe(depth, 0) == ERR_FLAC_INVALID_DATA);
        ++invalidCases;
    }
    FLACDecoder_FreeBuffers();
}
void errorCodes() {
    assert(FLACDecoder_AllocateBuffers(16, 2)); m_blockSize = 16;
    for(uint8_t channel = 0; channel < 2; ++channel) {
        for(unsigned method : {2U, 3U}) {
            Bits bits; bits.put(method, 2);
            input(bits.bytes);
            assert(decodeFixedPredictionSubframe(0, 16, channel) == ERR_FLAC_RESERVED_RESIDUAL_CODING);
            ++invalidCases;
        }
        std::vector<uint8_t> empty; input(empty);
        assert(decodeFixedPredictionSubframe(4, 16, channel) == ERR_FLAC_TRUNCATED_INPUT);
        ++invalidCases;
    }
    FLACDecoder_FreeBuffers();
}
}

int main(int argc, char **argv) {
    assert(argc == 2);
    if(!std::strcmp(argv[1], "signed")) signedFields();
    else if(!std::strcmp(argv[1], "wasted")) wastedBits();
    else if(!std::strcmp(argv[1], "errors")) errorCodes();
    else assert(false);
    std::printf("PASS signed_fields=%u wasted_cases=%u malformed_errors=%u\n",
                signedCases, wastedCases, invalidCases);
}
