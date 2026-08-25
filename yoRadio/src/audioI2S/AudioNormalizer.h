#pragma once

#include <array>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>

namespace audio_normalizer_detail {
constexpr size_t kSoftLimitLutStepShift = 9U;
constexpr size_t kSoftLimitLutEntries = 585U;
extern const std::array<uint16_t, kSoftLimitLutEntries> kSoftLimitLut;
} // namespace audio_normalizer_detail

#if defined(__GNUC__)
#define YORADIO_AUDIO_ALWAYS_INLINE inline __attribute__((always_inline))
#else
#define YORADIO_AUDIO_ALWAYS_INLINE inline
#endif

class AudioNormalizer {
public:
    void configure(bool enabled, uint8_t maxBoostDb, int8_t targetDbfs,
                   uint16_t timeConstantMs, uint32_t sampleRate);
    void setSampleRate(uint32_t sampleRate);
    void reset();
    YORADIO_AUDIO_ALWAYS_INLINE void process(int16_t sample[2]) {
        if(!m_enabled) return;
        processEnabled(sample);
    }
    void processBlock(int16_t *samples, size_t frames, uint8_t channels);

private:
    static constexpr uint16_t kUnityGainQ12 = 4096U;
    static constexpr int32_t kSoftKnee = 28672;
    static constexpr int32_t kSampleMaximum = 32767;

    YORADIO_AUDIO_ALWAYS_INLINE static uint32_t absoluteSample(int16_t value) {
        return value == INT16_MIN
            ? 32768U
            : static_cast<uint32_t>(value < 0 ? -value : value);
    }

    YORADIO_AUDIO_ALWAYS_INLINE static int16_t softLimit(int32_t value) {
        const bool negative = value < 0;
        int32_t magnitude = negative ? -value : value;
        if(magnitude > kSoftKnee) {
            const uint32_t over = static_cast<uint32_t>(magnitude - kSoftKnee);
            const uint32_t index =
                over >> audio_normalizer_detail::kSoftLimitLutStepShift;
            if(index >= audio_normalizer_detail::kSoftLimitLutEntries - 1U) {
                magnitude = audio_normalizer_detail::kSoftLimitLut.back();
            } else {
                constexpr uint32_t fractionMask =
                    (1U << audio_normalizer_detail::kSoftLimitLutStepShift) - 1U;
                constexpr uint32_t rounding =
                    1U << (audio_normalizer_detail::kSoftLimitLutStepShift - 1U);
                const uint32_t fraction = over & fractionMask;
                const uint32_t low = audio_normalizer_detail::kSoftLimitLut[index];
                const uint32_t high =
                    audio_normalizer_detail::kSoftLimitLut[index + 1U];
                magnitude = static_cast<int32_t>(
                    low + (((high - low) * fraction + rounding) >>
                           audio_normalizer_detail::kSoftLimitLutStepShift));
            }
        }
        if(magnitude > kSampleMaximum) magnitude = kSampleMaximum;
        return static_cast<int16_t>(negative ? -magnitude : magnitude);
    }

    YORADIO_AUDIO_ALWAYS_INLINE void processEnabled(int16_t sample[2]) {
        const uint32_t left = absoluteSample(sample[0]);
        const uint32_t right = absoluteSample(sample[1]);
        const uint32_t peak = left > right ? left : right;
        if(peak > m_blockPeak) m_blockPeak = static_cast<uint16_t>(peak);
        ++m_blockCount;

        const int32_t amplifiedLeft =
            (static_cast<int32_t>(sample[0]) * m_gainQ12) >> 12;
        const int32_t amplifiedRight =
            (static_cast<int32_t>(sample[1]) * m_gainQ12) >> 12;
        sample[0] = softLimit(amplifiedLeft);
        sample[1] = softLimit(amplifiedRight);

        if(m_blockCount >= m_blockFrames) updateGainTarget();
    }

    void updateGainTarget();

    uint16_t m_gainQ12 = kUnityGainQ12;
    uint16_t m_maxGainQ12 = kUnityGainQ12;
    uint32_t m_sampleRate = 16000;
    uint16_t m_targetPeak = 23198;
    uint16_t m_timeConstantMs = 5000;
    uint16_t m_blockFrames = 160;
    uint16_t m_smoothingBlocks = 500;
    uint16_t m_blockPeak = 0;
    uint16_t m_blockCount = 0;
    uint8_t m_maxBoostDb = 0;
    int8_t m_targetDbfs = -3;
    bool m_enabled = false;
};

#undef YORADIO_AUDIO_ALWAYS_INLINE
