#pragma once

#include <stdint.h>

class AudioNormalizer {
public:
    void configure(bool enabled, uint8_t maxBoostDb, uint32_t sampleRate);
    void setSampleRate(uint32_t sampleRate);
    void reset();
    void process(int16_t sample[2]);

private:
    static int16_t softLimit(int32_t value);
    void updateGainTarget();

    uint64_t m_levelSum = 0;
    uint32_t m_gainQ16 = 65536;
    uint32_t m_maxGainQ16 = 65536;
    uint32_t m_sampleRate = 16000;
    uint16_t m_blockFrames = 160;
    uint16_t m_blockPeak = 0;
    uint16_t m_blockCount = 0;
    uint8_t m_maxBoostDb = 0;
    bool m_enabled = false;
};
