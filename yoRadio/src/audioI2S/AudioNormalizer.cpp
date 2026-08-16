#include "AudioNormalizer.h"

#include <limits.h>
#include <stddef.h>

namespace {
constexpr uint16_t kUnityGainQ12 = 4096U;
constexpr uint16_t kMinimumGainQ12 = 410U;   // -20 dB.
constexpr uint16_t kNoiseFloor = 128U;       // Do not amplify silence or decoder noise.
constexpr int32_t kSoftKnee = 28672;
constexpr int32_t kSampleMaximum = 32767;
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

uint32_t absoluteSample(int16_t value) {
    return value == INT16_MIN ? 32768U
                              : static_cast<uint32_t>(value < 0 ? -value : value);
}

uint32_t moveTowards(uint32_t current, uint32_t target, uint32_t divisor) {
    if(current == target) return current;
    const uint32_t difference = current > target ? current - target : target - current;
    const uint32_t step = (difference + divisor - 1U) / divisor;
    return current > target ? current - step : current + step;
}
} // namespace

void AudioNormalizer::configure(bool enabled, uint8_t maxBoostDb, int8_t targetDbfs,
                                uint16_t timeConstantMs, uint32_t sampleRate) {
    if(maxBoostDb > 20U) maxBoostDb = 20U;
    if(targetDbfs < -20) targetDbfs = -20;
    if(targetDbfs > 0) targetDbfs = 0;
    if(timeConstantMs < 100U) timeConstantMs = 100U;
    if(timeConstantMs > 10000U) timeConstantMs = 10000U;
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
}

void AudioNormalizer::reset() {
    m_blockPeak = 0;
    m_blockCount = 0;
    m_gainQ12 = kUnityGainQ12;
}

void AudioNormalizer::process(int16_t sample[2]) {
    if(!m_enabled) return;

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

void AudioNormalizer::updateGainTarget() {
    uint32_t targetGain = kUnityGainQ12;
    if(m_blockPeak >= kNoiseFloor) {
        targetGain = static_cast<uint32_t>(
            (static_cast<uint64_t>(m_targetPeak) * kUnityGainQ12) / m_blockPeak);
        if(targetGain < kMinimumGainQ12) targetGain = kMinimumGainQ12;
        if(targetGain > m_maxGainQ12) targetGain = m_maxGainQ12;
    }

    // Use the same time constant in both directions. Transient overshoots are
    // handled by the soft limiter without abruptly changing the stream gain.
    const uint32_t blockDuration = static_cast<uint32_t>(m_blockFrames) * 1000U;
    uint32_t smoothingBlocks =
        (static_cast<uint32_t>(m_timeConstantMs) * m_sampleRate + blockDuration - 1U) /
        blockDuration;
    if(smoothingBlocks == 0U) smoothingBlocks = 1U;
    m_gainQ12 = static_cast<uint16_t>(moveTowards(m_gainQ12, targetGain, smoothingBlocks));
    m_blockPeak = 0;
    m_blockCount = 0;
}

int16_t AudioNormalizer::softLimit(int32_t value) {
    const bool negative = value < 0;
    int32_t magnitude = negative ? -value : value;
    if(magnitude > kSoftKnee) {
        const int32_t over = magnitude - kSoftKnee;
        const int32_t remaining = kSampleMaximum - kSoftKnee;
        magnitude = kSoftKnee + (over * remaining) / (over + remaining);
    }
    if(magnitude > kSampleMaximum) magnitude = kSampleMaximum;
    return static_cast<int16_t>(negative ? -magnitude : magnitude);
}
