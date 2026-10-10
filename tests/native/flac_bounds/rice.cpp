#include <cstdio>
#include <memory>
#include <random>
#include <vector>
#include "flac_decoder.cpp"

namespace {
constexpr unsigned kBitsPerByte = 8;
uint64_t cases = 0;
uint64_t reads = 0;

// Independent scalar extraction, with the old Rice loop as the behavioral
// reference. In particular, a truncated remainder returns the folded quotient
// while retaining the error and the partially refilled (unconsumed) cache.
struct ScalarReader {
    const uint8_t* input;
    uint32_t index;
    int32_t available;
    uint64_t cache;
    uint8_t cached;
    int8_t error;

    uint32_t read(uint8_t count) {
        if(error) return 0;
        if(count > 32) { error = ERR_FLAC_INVALID_DATA; return 0; }
        while(cached < count) {
            if(available <= 0) { error = ERR_FLAC_TRUNCATED_INPUT; return 0; }
            cache = (cache << kBitsPerByte) | input[index++];
            cached += kBitsPerByte;
            --available;
        }
        uint32_t result = 0;
        for(uint8_t i = 0; i < count; ++i) {
            --cached;
            result = (result << 1) | ((cache >> cached) & 1);
        }
        return result;
    }

    int64_t rice(uint8_t param) {
        if(param > 30) { error = ERR_FLAC_INVALID_DATA; return 0; }
        uint32_t value = 0;
        while(read(1) == 0) {
            if(error) return 0;
            if(value == (UINT32_MAX >> param)) { error = ERR_FLAC_INVALID_DATA; return 0; }
            ++value;
        }
        value = (value << param) | read(param);
        if(value == UINT32_MAX) { error = ERR_FLAC_INVALID_DATA; return 0; }
        return static_cast<int64_t>(value >> 1) ^ -static_cast<int64_t>(value & 1);
    }
};

void compare(ScalarReader& reference, uint8_t param, const char* label) {
    const int64_t expected = reference.rice(param);
    const int64_t actual = readRiceSignedInt(param);
    ++reads;
    if(expected != actual || reference.index != m_rIndex ||
       reference.available != m_bytesAvail || reference.cache != m_bitBuffer ||
       reference.cached != m_bitBufferLen || reference.error != m_readError) {
        std::fprintf(stderr,
            "%s param=%u case=%llu read=%llu: value=%lld/%lld index=%u/%u "
            "available=%d/%d cache=%llx/%llx bits=%u/%u error=%d/%d\n",
            label, param, static_cast<unsigned long long>(cases),
            static_cast<unsigned long long>(reads), static_cast<long long>(expected),
            static_cast<long long>(actual), reference.index, m_rIndex,
            reference.available, m_bytesAvail,
            static_cast<unsigned long long>(reference.cache),
            static_cast<unsigned long long>(m_bitBuffer), reference.cached,
            m_bitBufferLen, reference.error, m_readError);
        std::exit(1);
    }
}

void check(const std::vector<uint8_t>& input, uint64_t cache, uint8_t cached,
           uint8_t param, const char* label, int8_t error = ERR_FLAC_NONE,
           bool chained = false) {
    // Two already-consumed bytes exercise nonzero input indices. Allocate the
    // exact readable extent so ASan also detects any experimental lookahead.
    constexpr uint32_t kConsumedPrefixBytes = 2;
    std::unique_ptr<uint8_t[]> guarded(new uint8_t[input.size() + kConsumedPrefixBytes]);
    guarded[0] = 0xA5;
    guarded[1] = 0x5A;
    std::copy(input.begin(), input.end(), guarded.get() + kConsumedPrefixBytes);
    m_inptr = guarded.get();
    m_rIndex = kConsumedPrefixBytes;
    m_bytesAvail = static_cast<int32_t>(input.size());
    m_bitBuffer = cache;
    m_bitBufferLen = cached;
    m_readError = error;
    ScalarReader reference{m_inptr, m_rIndex, m_bytesAvail, cache, cached, error};
    ++cases;
    compare(reference, param, label);
    while(chained && !reference.error && (reference.available || reference.cached))
        compare(reference, param, label);
}

using Bits = std::vector<uint8_t>;

void appendRice(Bits& bits, uint32_t quotient, uint32_t remainder, uint8_t param) {
    bits.insert(bits.end(), quotient, 0);
    bits.push_back(1);
    for(int i = param - 1; i >= 0; --i) bits.push_back((remainder >> i) & 1);
}

void checkBits(Bits bits, uint8_t cached, uint8_t param, const char* label,
               bool cuts = false, bool chained = false) {
    while(bits.size() < cached) bits.push_back(0);
    uint64_t cache = UINT64_C(0xD6A54B73C918EF00);
    const uint64_t mask = (UINT64_C(1) << cached) - 1;
    cache &= ~mask;
    uint64_t initialBits = 0;
    for(unsigned i = 0; i < cached; ++i) initialBits = (initialBits << 1) | bits[i];
    cache |= initialBits;
    std::vector<uint8_t> bytes((bits.size() - cached + kBitsPerByte - 1) / kBitsPerByte, 0);
    for(size_t i = cached; i < bits.size(); ++i)
        bytes[(i - cached) / kBitsPerByte] |= bits[i] <<
            (kBitsPerByte - 1 - (i - cached) % kBitsPerByte);
    check(bytes, cache, cached, param, label, ERR_FLAC_NONE, chained);
    if(cuts) {
        // Every byte cut checks truncated unary/remainders and their cache state.
        for(size_t size = 0; size < bytes.size(); ++size)
            check(std::vector<uint8_t>(bytes.begin(), bytes.begin() + size),
                  cache, cached, param, "byte-cut");
    }
}
} // namespace

int main() {
    std::mt19937 random(0xC3F1AC);
    const uint32_t runs[] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,
                            23,24,31,32,63,64,127,128,255,256,1023,4095};
    for(uint8_t param = 0; param <= 30; ++param) {
        const uint32_t mask = (UINT32_C(1) << param) - 1;
        for(uint8_t cached = 0; cached < kBitsPerByte; ++cached) {
            for(uint32_t quotient : runs) {
                for(uint32_t remainder : {UINT32_C(0), mask, mask / 2,
                                          static_cast<uint32_t>(random()) & mask}) {
                    Bits bits;
                    appendRice(bits, quotient, remainder, param);
                    // Trailing nonzero bytes prove the decoder does not prefetch.
                    bits.insert(bits.end(), {1,0,1,0,1,1,0,1,1,1,1,1,0,0,0,0});
                    checkBits(bits, cached, param, "run", quotient <= 64);
                }
            }
            // Limit cases are practical to construct for the higher parameters.
            // Test success at the limit, forbidden folded UINT32_MAX, and the
            // first excessive unary zero at every possible cache alignment.
            if(param >= 18) {
                const uint32_t maximum = UINT32_MAX >> param;
                for(uint32_t quotient : {maximum - 1, maximum, maximum + 1, maximum + 7}) {
                    for(uint32_t remainder : {UINT32_C(0), mask - 1, mask}) {
                        Bits bits;
                        appendRice(bits, quotient, remainder, param);
                        checkBits(bits, cached, param, "quotient-limit");
                    }
                }
            }
            // Every unary truncation length through several byte boundaries.
            for(size_t size = 0; size <= 16; ++size)
                check(std::vector<uint8_t>(size, 0), UINT64_C(0xFEDCBA9876543200),
                      cached, param, "unterminated-unary");
            for(int8_t error : {ERR_FLAC_TRUNCATED_INPUT, ERR_FLAC_INVALID_DATA})
                check({0,255,0}, UINT64_C(0x89ABCDEF012345FF), cached, param,
                      "existing-error", error);
            // A stream of residues compares the state after every decoded item.
            Bits stream;
            for(unsigned i = 0; i < 100; ++i)
                appendRice(stream, random() % 32, random() & mask, param);
            checkBits(stream, cached, param, "stream", false, true);
        }
    }
    for(uint8_t param : {31, 255}) {
        for(uint8_t cached = 0; cached < kBitsPerByte; ++cached)
            for(int8_t error : {ERR_FLAC_NONE, ERR_FLAC_TRUNCATED_INPUT, ERR_FLAC_INVALID_DATA})
                check({0,255,0}, UINT64_C(0x89ABCDEF012345FF), cached, param,
                      "invalid-param", error);
    }
    // Exhaust all cached patterns and next bytes, varying the parameter. Stale
    // high cache bits deliberately contain ones; only the valid low bits count.
    for(uint8_t cached = 0; cached < kBitsPerByte; ++cached)
        for(unsigned pattern = 0; pattern < (1U << cached); ++pattern)
            for(unsigned byte = 0; byte <= UINT8_MAX; ++byte)
                check({static_cast<uint8_t>(byte)},
                      (UINT64_C(0xFEEDC0DE12345600) & ~((UINT64_C(1) << cached) - 1)) | pattern,
                      cached, (pattern + byte) % 31, "cache-pattern");
    for(unsigned trial = 0; trial < 50000; ++trial) {
        std::vector<uint8_t> bytes(random() % 33);
        for(auto& byte : bytes) byte = random();
        const uint64_t cache = (static_cast<uint64_t>(random()) << 32) | random();
        check(bytes, cache, random() % kBitsPerByte, random() % 31, "random", ERR_FLAC_NONE, true);
    }
    std::printf("{\"passed\":true,\"cases\":%llu,\"reads\":%llu}\n",
                static_cast<unsigned long long>(cases), static_cast<unsigned long long>(reads));
}
