// Compare the actual predictor with independent scalar arithmetic, including
// histories crossing every segmented allocation boundary and dense order 32.
#include "flac_decoder.cpp"
#include <cassert>
#include <cstdio>
#include <vector>

int main() {
    assert(FLACDecoder_AllocateBuffers(MAX_BLOCKSIZE, MAX_CHANNELS));
    m_blockSize = MAX_BLOCKSIZE;
    unsigned cases = 0;
    for(unsigned channel = 0; channel < MAX_CHANNELS; ++channel) {
        for(unsigned order = 0; order <= kMaximumLpcOrder; ++order) {
            for(unsigned pattern = 0; pattern < 6; ++pattern) {
                coefficientCount = order;
                for(unsigned j = 0; j < order; ++j)
                    coefs[j] = pattern == 0 ? 0 :
                        pattern == 1 && j + 1 < order ? 0 :
                        (j & 1 ? -16383 : 16383);
                if(pattern >= 3)
                    for(unsigned j = 0; j < order; ++j) {
                        const int32_t magnitude = pattern == 3 ? 16383 :
                            j < order / 3 ? 16383 : j < 2 * order / 3 ? (pattern == 5 ? 16382 : -16384) : 7891;
                        coefs[j] = pattern == 5 && (j & 1) ? -magnitude : magnitude;
                    }
                constexpr uint8_t kPredictionShift = 14;
                std::vector<int32_t> expected(m_blockSize);
                for(unsigned i = 0; i < m_blockSize; ++i) {
                    // Wide, deterministic values require a >32-bit accumulator.
                    expected[i] = (static_cast<int32_t>((i * 9173U + channel * 101U)
                                                       % 100003U) - 50001) * 128;
                    int64_t prediction = 0;
                    if(i >= order)
                        for(unsigned j = 0; j < order; ++j)
                            prediction += static_cast<int64_t>(expected[i - 1 - j]) * coefs[j];
                    int64_t residual = expected[i] - (prediction >> kPredictionShift);
                    assert(residual >= INT32_MIN && residual <= INT32_MAX);
                    samplesBuffer[channel][i] = static_cast<int32_t>(residual);
                }
                m_readError = ERR_FLAC_NONE;
                restoreLinearPrediction(channel, kPredictionShift);
                assert(!m_readError);
                for(unsigned i = 0; i < m_blockSize; ++i)
                    assert(samplesBuffer[channel][i] == expected[i]);
                ++cases;
            }
        }
    }
    FLACDecoder_FreeBuffers();
    // Exercise every legal prediction shift with asymmetric coefficients,
    // all group remainders, and a partly allocated final workspace segment.
    constexpr unsigned kPartialBlock = 1057;
    assert(FLACDecoder_AllocateBuffers(kPartialBlock, MAX_CHANNELS));
    m_blockSize = kPartialBlock;
    uint32_t random = 0x192a45b7U;
    auto next = [&random]() { random = random * 1664525U + 1013904223U; return random; };
    for(unsigned channel = 0; channel < MAX_CHANNELS; ++channel) {
        for(unsigned order = 1; order <= kMaximumLpcOrder; ++order) {
            for(unsigned shift = 0; shift <= 15; ++shift) {
              for(unsigned pattern = 0; pattern < 4; ++pattern) {
                coefficientCount = order;
                for(unsigned j = 0; j < order; ++j)
                    coefs[j] = static_cast<int32_t>(next() % 32768) - 16384;
                // Include both extremes of the signed 15-bit coefficient range.
                coefs[0] = (shift & 1) ? -16384 : 16383;
                if(pattern)
                    for(unsigned j = 0; j < order; ++j) {
                        if(pattern == 1) coefs[j] = (shift & 1) ? -16384 : 16383;
                        if(pattern == 2) coefs[j] = (j & 1) ? -16383 : 16383;
                        if(pattern == 3) coefs[j] = j < order / 3 ? 8911 : j < 2 * order / 3 ? -16384 : 13271;
                    }
                std::vector<int32_t> expected(m_blockSize);
                const int32_t scale = INT32_C(1) << std::min(shift, 14U);
                for(unsigned i = 0; i < m_blockSize; ++i) {
                    expected[i] = (static_cast<int32_t>(next() % 2047) - 1023) * scale;
                    int64_t prediction = 0;
                    if(i >= order)
                        for(unsigned j = 0; j < order; ++j)
                            prediction += static_cast<int64_t>(expected[i - 1 - j]) * coefs[j];
                    int64_t residual = expected[i] - (prediction >> shift);
                    assert(residual >= INT32_MIN && residual <= INT32_MAX);
                    samplesBuffer[channel][i] = static_cast<int32_t>(residual);
                }
                m_readError = ERR_FLAC_NONE;
                restoreLinearPrediction(channel, shift);
                assert(!m_readError);
                for(unsigned i = 0; i < m_blockSize; ++i)
                    assert(samplesBuffer[channel][i] == expected[i]);
                ++cases;
              }
            }
        }
    }
    FLACDecoder_FreeBuffers();
    printf("PASS predictor_cases=%u orders=0..32 shifts=0..15 dense/sparse/zero/random/repeated/alternating/runs all-segment-boundaries/partial-segment\n", cases);
}
