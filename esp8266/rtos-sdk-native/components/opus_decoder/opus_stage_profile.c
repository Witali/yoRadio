#define _POSIX_C_SOURCE 200809L
#include "opus_stage_profile.h"
#if YORADIO_OPUS_PROFILE_STAGE
static opus_stage_profile_t profile;
void opus_stage_profile_reset(void) { profile = (opus_stage_profile_t){0, 0, 0}; }
opus_stage_profile_t opus_stage_profile_snapshot(void) { return profile; }
void opus_stage_profile_record(uint32_t elapsed) {
    profile.cycles += elapsed;
    ++profile.calls;
    if (elapsed > profile.max_cycles) profile.max_cycles = elapsed;
}
#if !defined(__XTENSA__) && !defined(YORADIO_OPUS_PROFILE_TEST_CLOCK)
#include <time.h>
uint32_t opus_stage_profile_clock(void) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return (uint32_t)((uint64_t)now.tv_sec * 1000000000U + now.tv_nsec);
}
#endif
#endif
