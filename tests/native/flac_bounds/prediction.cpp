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
            for(unsigned pattern = 0; pattern < 3; ++pattern) {
                coefficientCount = order;
                for(unsigned j = 0; j < order; ++j)
                    coefs[j] = pattern == 0 ? 0 :
                        pattern == 1 && j + 1 < order ? 0 :
                        (j & 1 ? -16383 : 16383);
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
    printf("PASS predictor_cases=%u orders=0..32 dense/sparse/zero all-segment-boundaries\n", cases);
}
