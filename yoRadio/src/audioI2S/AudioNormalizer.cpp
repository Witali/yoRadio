#include "AudioNormalizer.h"

#include <stddef.h>

namespace {
constexpr uint32_t kUnityGainQ16 = 65536U;
constexpr uint32_t kMinimumGainQ16 = 6554U;  // -20 dB.
constexpr uint16_t kNoiseFloor = 128U;       // Do not amplify silence or decoder noise.
constexpr int32_t kSoftKnee = 28672;
constexpr int32_t kSampleMaximum = 32767;

// 10^(dB/20), Q16, for 0..20 dB. A table avoids powf() in the audio firmware.
constexpr uint32_t kGainQ16ByDb[] = {
    65536U, 73533U, 82505U, 92573U, 103867U, 116540U, 130762U,
    146718U, 164622U, 184714U, 207243U, 232529U, 260906U,
    292740U, 328458U, 368536U, 413510U, 463966U, 520567U,
    584078U, 655360U,
};

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
    m_maxGainQ16 = kGainQ16ByDb[m_maxBoostDb];
    setSampleRate(sampleRate);
    if(restart) reset();
    if(m_gainQ16 > m_maxGainQ16) m_gainQ16 = m_maxGainQ16;
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
    m_gainQ16 = kUnityGainQ16;
}

void AudioNormalizer::process(int16_t sample[2]) {
    if(!m_enabled) return;

    const uint32_t left = absoluteSample(sample[0]);
    const uint32_t right = absoluteSample(sample[1]);
    const uint32_t peak = left > right ? left : right;
    if(peak > m_blockPeak) m_blockPeak = static_cast<uint16_t>(peak);
    ++m_blockCount;

    const int32_t amplifiedLeft = static_cast<int32_t>(
        (static_cast<int64_t>(sample[0]) * m_gainQ16) >> 16);
    const int32_t amplifiedRight = static_cast<int32_t>(
        (static_cast<int64_t>(sample[1]) * m_gainQ16) >> 16);
    sample[0] = softLimit(amplifiedLeft);
    sample[1] = softLimit(amplifiedRight);

    if(m_blockCount >= m_blockFrames) updateGainTarget();
}

void AudioNormalizer::updateGainTarget() {
    uint32_t targetGain = kUnityGainQ16;
    if(m_blockPeak >= kNoiseFloor) {
        targetGain = static_cast<uint32_t>(
            (static_cast<uint64_t>(m_targetPeak) * kUnityGainQ16) / m_blockPeak);
        if(targetGain < kMinimumGainQ16) targetGain = kMinimumGainQ16;
        if(targetGain > m_maxGainQ16) targetGain = m_maxGainQ16;
    }

    // Use the same time constant in both directions. Transient overshoots are
    // handled by the soft limiter without abruptly changing the stream gain.
    const uint32_t blockDuration = static_cast<uint32_t>(m_blockFrames) * 1000U;
    uint32_t smoothingBlocks =
        (static_cast<uint32_t>(m_timeConstantMs) * m_sampleRate + blockDuration - 1U) /
        blockDuration;
    if(smoothingBlocks == 0U) smoothingBlocks = 1U;
    m_gainQ16 = moveTowards(m_gainQ16, targetGain, smoothingBlocks);
    m_blockPeak = 0;
    m_blockCount = 0;
}

int16_t AudioNormalizer::softLimit(int32_t value) {
    const bool negative = value < 0;
    int64_t magnitude = negative ? -static_cast<int64_t>(value)
                                 : static_cast<int64_t>(value);
    if(magnitude > kSoftKnee) {
        const int64_t over = magnitude - kSoftKnee;
        const int64_t remaining = kSampleMaximum - kSoftKnee;
        magnitude = kSoftKnee + (over * remaining) / (over + remaining);
    }
    if(magnitude > kSampleMaximum) magnitude = kSampleMaximum;
    return static_cast<int16_t>(negative ? -magnitude : magnitude);
}
