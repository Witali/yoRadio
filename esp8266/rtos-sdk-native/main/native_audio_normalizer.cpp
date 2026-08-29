#include "native_audio_normalizer.h"

#include "AudioNormalizer.h"

namespace {
AudioNormalizer s_normalizer;
}

extern "C" void native_audio_normalizer_configure(
    bool enabled, uint8_t max_gain_db, int8_t target_dbfs, uint16_t time_ms,
    uint32_t sample_rate) {
    s_normalizer.configure(enabled, max_gain_db, target_dbfs, time_ms,
                           sample_rate);
}

extern "C" void native_audio_normalizer_reset(void) {
    s_normalizer.reset();
}

extern "C" void native_audio_normalizer_process(int16_t *samples,
                                                  size_t frames,
                                                  uint8_t channels) {
    s_normalizer.processBlock(samples, frames, channels);
}
