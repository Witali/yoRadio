#include "AudioNormalizer.h"
#include "native_audio_normalizer.h"

#include <cassert>
#include <pthread.h>

namespace {
AudioNormalizer reference;
pthread_t owner;
unsigned configure_calls, reset_calls, process_calls;
}

extern "C" void reference_owner(void) { owner = pthread_self(); }
extern "C" void reference_configure(bool enabled, uint8_t gain, int8_t target,
                                     uint16_t time, uint32_t rate) {
    reference.configure(enabled, gain, target, time, rate);
}
extern "C" void reference_reset(void) { reference.reset(); }
extern "C" void reference_process(int16_t stereo[2]) { reference.process(stereo); }
extern "C" unsigned normalizer_configure_calls(void) { return configure_calls; }
extern "C" unsigned normalizer_reset_calls(void) { return reset_calls; }
extern "C" unsigned normalizer_process_calls(void) { return process_calls; }

extern "C" void __real_native_audio_normalizer_configure(
    bool, uint8_t, int8_t, uint16_t, uint32_t);
extern "C" void __real_native_audio_normalizer_reset(void);
extern "C" void __real_native_audio_normalizer_process_block(int16_t *, size_t,
                                                              uint8_t);
extern "C" void __wrap_native_audio_normalizer_configure(
    bool enabled, uint8_t gain, int8_t target, uint16_t time, uint32_t rate) {
    assert(pthread_equal(owner, pthread_self()));
    ++configure_calls;
    __real_native_audio_normalizer_configure(enabled, gain, target, time, rate);
}
extern "C" void __wrap_native_audio_normalizer_reset(void) {
    assert(pthread_equal(owner, pthread_self()));
    ++reset_calls;
    __real_native_audio_normalizer_reset();
}
extern "C" void __wrap_native_audio_normalizer_process_block(
    int16_t *samples, size_t frames, uint8_t channels) {
    assert(pthread_equal(owner, pthread_self()));
    assert(frames && frames <= 128 && channels && channels <= 2);
    ++process_calls;
    __real_native_audio_normalizer_process_block(samples, frames, channels);
}
