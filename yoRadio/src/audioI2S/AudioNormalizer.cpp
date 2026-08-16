#include "AudioNormalizer.h"

#include <stddef.h>

namespace {
constexpr uint32_t kUnityGainQ16 = 65536U;
constexpr uint16_t kTargetMeanLevel = 4096U; // About -18 dBFS for mean absolute level.
constexpr uint16_t kNoiseFloor = 128U;       // Do not amplify silence or decoder noise.
constexpr uint16_t kPeakTarget = 30000U;
constexpr int32_t kSoftKnee = 28672;
constexpr int32_t kSampleMaximum = 32767;

// 10^(dB/20), Q16, for 0..20 dB. A table avoids powf() in the audio firmware.
constexpr uint32_t kGainQ16ByDb[] = {
    65536U, 73533U, 82505U, 92573U, 103867U, 116540U, 130762U,
    146718U, 164622U, 184714U, 207243U, 232529U, 260906U,
    292740U, 328458U, 368536U, 413510U, 463966U, 520567U,
    584078U, 655360U,
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

void AudioNormalizer::configure(bool enabled, uint8_t maxBoostDb, uint32_t sampleRate) {
    if(maxBoostDb > 20U) maxBoostDb = 20U;
    const bool restart = enabled != m_enabled;
    m_enabled = enabled;
    m_maxBoostDb = maxBoostDb;
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
    m_levelSum = 0;
    m_blockPeak = 0;
    m_blockCount = 0;
    m_gainQ16 = kUnityGainQ16;
}

void AudioNormalizer::process(int16_t sample[2]) {
    if(!m_enabled) return;

    const uint32_t left = absoluteSample(sample[0]);
    const uint32_t right = absoluteSample(sample[1]);
    const uint32_t peak = left > right ? left : right;
    m_levelSum += peak;
    if(peak > m_blockPeak) m_blockPeak = static_cast<uint16_t>(peak);
    ++m_blockCount;

    // A newly arrived peak starts reducing boost immediately. The soft knee
    // below catches the transient while this linked stereo gain moves smoothly.
    if(peak > 0U && m_gainQ16 > kUnityGainQ16) {
        uint32_t safeGain = static_cast<uint32_t>(
            (static_cast<uint64_t>(kPeakTarget) * kUnityGainQ16) / peak);
        if(safeGain < kUnityGainQ16) safeGain = kUnityGainQ16;
        if(safeGain < m_gainQ16) {
            uint32_t attackSamples = m_sampleRate / 50U; // 20 ms
            if(attackSamples == 0U) attackSamples = 1U;
            m_gainQ16 = moveTowards(m_gainQ16, safeGain, attackSamples);
        }
    }

    const int32_t amplifiedLeft = static_cast<int32_t>(
        (static_cast<int64_t>(sample[0]) * m_gainQ16) >> 16);
    const int32_t amplifiedRight = static_cast<int32_t>(
        (static_cast<int64_t>(sample[1]) * m_gainQ16) >> 16);
    sample[0] = softLimit(amplifiedLeft);
    sample[1] = softLimit(amplifiedRight);

    if(m_blockCount >= m_blockFrames) updateGainTarget();
}

void AudioNormalizer::updateGainTarget() {
    const uint32_t meanLevel = static_cast<uint32_t>(m_levelSum / m_blockCount);
    uint32_t targetGain = kUnityGainQ16;
    if(meanLevel >= kNoiseFloor) {
        targetGain = static_cast<uint32_t>(
            (static_cast<uint64_t>(kTargetMeanLevel) * kUnityGainQ16) / meanLevel);
        if(targetGain < kUnityGainQ16) targetGain = kUnityGainQ16;
        if(targetGain > m_maxGainQ16) targetGain = m_maxGainQ16;

        if(m_blockPeak > 0U) {
            uint32_t peakGain = static_cast<uint32_t>(
                (static_cast<uint64_t>(kPeakTarget) * kUnityGainQ16) / m_blockPeak);
            if(peakGain < kUnityGainQ16) peakGain = kUnityGainQ16;
            if(targetGain > peakGain) targetGain = peakGain;
        }
    }

    // Reduce gain in roughly 40 ms, but restore it slowly over about 2 s.
    m_gainQ16 = moveTowards(m_gainQ16, targetGain,
                            targetGain < m_gainQ16 ? 4U : 200U);
    m_levelSum = 0;
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
