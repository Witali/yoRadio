#include "native_audio_normalizer.h"

#include "AudioNormalizer.h"

namespace {
AudioNormalizer normalizer;
}

extern "C" void native_audio_normalizer_configure(
    bool enabled, uint8_t max_gain_db, int8_t target_dbfs,
    uint16_t time_ms, uint32_t sample_rate) {
    normalizer.configure(enabled, max_gain_db, target_dbfs, time_ms,
                         sample_rate);
}

extern "C" void native_audio_normalizer_set_sample_rate(
    uint32_t sample_rate) {
    normalizer.setSampleRate(sample_rate);
}

extern "C" void native_audio_normalizer_process(int16_t samples[2]) {
    normalizer.process(samples);
}

extern "C" void native_audio_normalizer_process_block(
    int16_t *samples, size_t frames, uint8_t channels) {
    normalizer.processBlock(samples, frames, channels);
}
