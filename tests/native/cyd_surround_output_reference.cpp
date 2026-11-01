#include "AudioNormalizer.h"
#include "native_audio_normalizer.h"
#include <array>
#include <cassert>
#include <pthread.h>

namespace {
std::array<AudioNormalizer, 8> oracle;
pthread_t owner;
unsigned surround_calls;
uint32_t magnitude(int16_t value) {
    return value == INT16_MIN ? 32768u : static_cast<uint32_t>(value < 0 ? -value : value);
}
}
extern "C" void reference_owner(void) { owner = pthread_self(); }
extern "C" void surround_reference_configure(bool enabled, uint8_t gain, int8_t target,
                                              uint16_t time, uint32_t rate) {
    for (auto &item : oracle) { item.configure(enabled, gain, target, time, rate); item.reset(); }
}
extern "C" void surround_reference_process(int16_t *samples, uint8_t channels) {
    assert(channels && channels <= 8);
    int16_t peak = samples[0];
    for (uint8_t c = 1; c < channels; ++c)
        if (magnitude(samples[c]) > magnitude(peak)) peak = samples[c];
    for (uint8_t c = 0; c < channels; ++c) {
        int16_t pair[2] = {samples[c], peak};
        oracle[c].process(pair); samples[c] = pair[0];
    }
}
extern "C" unsigned surround_normalizer_calls(void) { return surround_calls; }
extern "C" void __real_native_audio_normalizer_configure(bool,uint8_t,int8_t,uint16_t,uint32_t);
extern "C" void __real_native_audio_normalizer_reset(void);
extern "C" void __real_native_audio_normalizer_process_block(int16_t *,size_t,uint8_t);
extern "C" void __real_native_audio_normalizer_process_multichannel_block(int16_t *,size_t,uint8_t);
extern "C" void __wrap_native_audio_normalizer_configure(bool a,uint8_t b,int8_t c,uint16_t d,uint32_t e) {
    assert(pthread_equal(owner,pthread_self())); __real_native_audio_normalizer_configure(a,b,c,d,e);
}
extern "C" void __wrap_native_audio_normalizer_reset(void) {
    assert(pthread_equal(owner,pthread_self())); __real_native_audio_normalizer_reset();
}
extern "C" void __wrap_native_audio_normalizer_process_block(int16_t *samples,size_t frames,uint8_t channels) {
    assert(pthread_equal(owner,pthread_self()) && frames && frames <= 128 && channels && channels <= 2);
    __real_native_audio_normalizer_process_block(samples,frames,channels);
}
extern "C" void __wrap_native_audio_normalizer_process_multichannel_block(int16_t *samples,size_t frames,uint8_t channels) {
    assert(pthread_equal(owner,pthread_self()) && frames && frames <= 128 && channels >= 3 && channels <= 8 && frames*channels <= 256);
    ++surround_calls; __real_native_audio_normalizer_process_multichannel_block(samples,frames,channels);
}
