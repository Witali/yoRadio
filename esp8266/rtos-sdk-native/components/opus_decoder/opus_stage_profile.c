#define _POSIX_C_SOURCE 200809L
#include "opus_stage_profile.h"
#if YORADIO_OPUS_PROFILE_STAGE
static opus_stage_profile_t profile;
void opus_stage_profile_reset(void) { profile = (opus_stage_profile_t){0, 0, 0}; }
opus_stage_profile_t opus_stage_profile_snapshot(void) { return profile; }
void opus_stage_profile_record(uint32_t elapsed) {
    profile.ticks += elapsed;
    ++profile.calls;
    if (elapsed > profile.max_ticks) profile.max_ticks = elapsed;
}
#if defined(__XTENSA__) && !defined(YORADIO_OPUS_PROFILE_TEST_CLOCK)
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
uint32_t opus_stage_profile_clock(void) {
    /* SDK reads a 64-bit accumulated epoch plus current CCOUNT. Prevent the
     * tick ISR from updating/resetting them halfway through this snapshot.
     * Interrupts are masked ONLY for the clock read, never for decode. */
    taskENTER_CRITICAL();
    uint32_t now = (uint32_t)esp_timer_get_time();
    taskEXIT_CRITICAL();
    return now;
}
#elif !defined(YORADIO_OPUS_PROFILE_TEST_CLOCK)
#include <time.h>
uint32_t opus_stage_profile_clock(void) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return (uint32_t)((uint64_t)now.tv_sec * 1000000U + now.tv_nsec / 1000U);
}
#endif
#endif
