#pragma once
#include <stdbool.h>
#include <stdint.h>
#ifdef AUDIO_POWER_INTEGRATION
#include <stdatomic.h>
#include "native_network_power.h"
#include "native_network_power.c"
static atomic_uint audio_power_accepted_generation;
static atomic_bool audio_power_accepted_active;
static inline void network_service_audio_accept(uint32_t generation, bool active) {
    native_network_power_accept(generation, active);
    atomic_store(&audio_power_accepted_generation, generation);
    atomic_store(&audio_power_accepted_active, active);
}
static inline void network_service_audio_receive(uint32_t generation) {
    native_network_power_receive(generation);
}
static inline void network_service_audio_finish(uint32_t generation) {
    native_network_power_finish(generation);
}
static inline void audio_power_assert_quiet(uint32_t generation) {
    native_network_power_snapshot_t state;
    native_network_power_snapshot(&state);
    assert(state.generation == generation && !state.desired_active);
}
static inline void audio_power_assert_accepted(uint32_t generation, bool active) {
    assert(atomic_load(&audio_power_accepted_generation) == generation);
    assert(atomic_load(&audio_power_accepted_active) == active);
}
#else
// Default existing fixtures isolate the network boundary and make no power
// claim. --network-power links the actual shared policy and enables checks.
static inline void network_service_audio_accept(uint32_t generation, bool active) {
    (void)generation; (void)active;
}
static inline void network_service_audio_receive(uint32_t generation) {(void)generation;}
static inline void network_service_audio_finish(uint32_t generation) {(void)generation;}
static inline void audio_power_assert_quiet(uint32_t generation) {(void)generation;}
static inline void audio_power_assert_accepted(uint32_t generation, bool active) {(void)generation;(void)active;}
#endif
