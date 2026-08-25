#include "AudioNormalizer.h"

#include <limits.h>
#include <stddef.h>
#include <utility>

namespace {
constexpr uint16_t kUnityGainQ12 = 4096U;
constexpr uint16_t kMinimumGainQ12 = 410U;   // -20 dB.
constexpr uint16_t kNoiseFloor = 128U;       // Do not amplify silence or decoder noise.
constexpr uint32_t kSoftKnee = 28672U;
constexpr uint32_t kSampleMaximum = 32767U;
constexpr int32_t kMaximumAmplifiedSample = 327680; // Full scale at +20 dB.

// 10^(dB/20), Q12, for 0..20 dB. Q12 keeps a full-scale sample multiplied
// by the maximum gain inside int32_t and avoids 64-bit work per sample.
constexpr uint16_t kGainQ12ByDb[] = {
    4096U, 4596U, 5157U, 5786U, 6492U, 7284U, 8173U,
    9170U, 10289U, 11545U, 12953U, 14533U, 16307U,
    18296U, 20529U, 23034U, 25844U, 28998U, 32535U,
    36505U, 40960U,
};

static_assert((kMaximumAmplifiedSample - kSoftKnee) *
                  (kSampleMaximum - kSoftKnee) <= INT32_MAX,
              "soft limiter numerator must fit in int32_t");

// Full-scale sample amplitude for 0..-20 dBFS. A table keeps the audio path
// deterministic and avoids pulling floating-point logarithms into firmware.
constexpr uint16_t kPeakByAttenuationDb[] = {
    32767U, 29204U, 26028U, 23198U, 20675U, 18426U, 16422U,
    14636U, 13045U, 11625U, 10362U, 9235U, 8231U, 7336U,
    6538U, 5827U, 5193U, 4628U, 4125U, 3676U, 3277U,
};

uint32_t moveTowards(uint32_t current, uint32_t target, uint32_t divisor) {
    if(current == target) return current;
    const uint32_t difference = current > target ? current - target : target - current;
    const uint32_t step = (difference + divisor - 1U) / divisor;
    return current > target ? current - step : current + step;
}
} // namespace

namespace audio_normalizer_detail {
namespace {
constexpr uint16_t softLimitLutValue(size_t index) {
    const uint32_t over = static_cast<uint32_t>(
        index << kSoftLimitLutStepShift);
    const uint32_t remaining = kSampleMaximum - kSoftKnee;
    return static_cast<uint16_t>(
        kSoftKnee + (over * remaining) / (over + remaining));
}

template<size_t... Index>
constexpr std::array<uint16_t, sizeof...(Index)> makeSoftLimitLut(
    std::index_sequence<Index...>) {
    return {{softLimitLutValue(Index)...}};
}
} // namespace

const std::array<uint16_t, kSoftLimitLutEntries> kSoftLimitLut =
    makeSoftLimitLut(std::make_index_sequence<kSoftLimitLutEntries>{});
} // namespace audio_normalizer_detail

void AudioNormalizer::configure(bool enabled, uint8_t maxBoostDb, int8_t targetDbfs,
                                uint16_t timeConstantMs, uint32_t sampleRate) {
    if(maxBoostDb > 20U) maxBoostDb = 20U;
    if(targetDbfs < -20) targetDbfs = -20;
    if(targetDbfs > 0) targetDbfs = 0;
    if(timeConstantMs < 100U) timeConstantMs = 100U;
    if(timeConstantMs > 10000U) timeConstantMs = 10000U;
    if(sampleRate < 8000U) sampleRate = 8000U;
    if(sampleRate > 96000U) sampleRate = 96000U;
    if(enabled == m_enabled && maxBoostDb == m_maxBoostDb &&
       targetDbfs == m_targetDbfs &&
       timeConstantMs == m_timeConstantMs && sampleRate == m_sampleRate) {
        return;
    }
    const bool restart = enabled != m_enabled;
    m_enabled = enabled;
    m_maxBoostDb = maxBoostDb;
    m_targetDbfs = targetDbfs;
    m_targetPeak = kPeakByAttenuationDb[static_cast<uint8_t>(-targetDbfs)];
    m_timeConstantMs = timeConstantMs;
    m_maxGainQ12 = kGainQ12ByDb[m_maxBoostDb];
    setSampleRate(sampleRate);
    if(restart) reset();
    if(m_gainQ12 > m_maxGainQ12) m_gainQ12 = m_maxGainQ12;
}

void AudioNormalizer::setSampleRate(uint32_t sampleRate) {
    if(sampleRate < 8000U) sampleRate = 8000U;
    if(sampleRate > 96000U) sampleRate = 96000U;
    m_sampleRate = sampleRate;
    m_blockFrames = static_cast<uint16_t>((sampleRate + 50U) / 100U); // 10 ms
    const uint32_t blockDuration = static_cast<uint32_t>(m_blockFrames) * 1000U;
    const uint32_t smoothingNumerator =
        static_cast<uint32_t>(m_timeConstantMs) * m_sampleRate;
    m_smoothingBlocks = static_cast<uint16_t>(
        (smoothingNumerator + blockDuration - 1U) / blockDuration);
    if(m_smoothingBlocks == 0U) m_smoothingBlocks = 1U;
}

void AudioNormalizer::reset() {
    m_blockPeak = 0;
    m_blockCount = 0;
    m_gainQ12 = kUnityGainQ12;
}

void AudioNormalizer::processBlock(int16_t *samples, size_t frames,
                                   uint8_t channels) {
    if(!m_enabled || !samples || !frames || !channels) return;
    for(size_t frame = 0; frame < frames; ++frame) {
        int16_t *input = samples + frame * channels;
        int16_t stereo[2] = {input[0], channels > 1 ? input[1] : input[0]};
        processEnabled(stereo);
        input[0] = stereo[0];
        if(channels > 1) input[1] = stereo[1];
    }
}

void AudioNormalizer::updateGainTarget() {
    uint32_t targetGain = kUnityGainQ12;
    if(m_blockPeak >= kNoiseFloor) {
        targetGain =
            (static_cast<uint32_t>(m_targetPeak) * kUnityGainQ12) / m_blockPeak;
        if(targetGain < kMinimumGainQ12) targetGain = kMinimumGainQ12;
        if(targetGain > m_maxGainQ12) targetGain = m_maxGainQ12;
    }

    // Use the same time constant in both directions. Transient overshoots are
    // handled by the soft limiter without abruptly changing the stream gain.
    m_gainQ12 = static_cast<uint16_t>(
        moveTowards(m_gainQ12, targetGain, m_smoothingBlocks));
    m_blockPeak = 0;
    m_blockCount = 0;
}
