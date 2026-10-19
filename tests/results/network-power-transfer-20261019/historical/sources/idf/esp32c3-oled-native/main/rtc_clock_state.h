#pragma once

#include <stdbool.h>
#include <stdint.h>

#define RTC_CLOCK_MAGIC 0x4333434cU
#define RTC_CLOCK_HALF_SECOND_US 500000U
#define RTC_CLOCK_DIGIT_WIDTH 13U
#define RTC_CLOCK_PAGES 5U

typedef struct {
    uint32_t magic;
    uint64_t ticks;
    uint32_t calibration;
    uint32_t fractional_us;
    uint32_t second_of_day;
    uint32_t microsecond;
    uint32_t displayed_minute;
    bool colon_on;
    bool user_wake;
    uint8_t encoder_phase;
    uint8_t digits[10][RTC_CLOCK_PAGES * RTC_CLOCK_DIGIT_WIDTH];
    uint8_t colon[RTC_CLOCK_PAGES * 3U];
    uint8_t framebuffer[72U * RTC_CLOCK_PAGES];
} rtc_clock_state_t;

extern rtc_clock_state_t g_rtc_clock;
void rtc_clock_wake_stub(void);

// Fixed-point RTC accounting retains sub-microsecond fractions. Advancing
// from elapsed ticks (including I2C work) avoids accumulating wake overhead.
static inline void rtc_clock_advance(rtc_clock_state_t *clock, uint64_t ticks) {
    uint64_t scaled = (ticks - clock->ticks) * clock->calibration +
                      clock->fractional_us;
    clock->ticks = ticks;
    clock->fractional_us = (uint32_t)(scaled & ((1U << 19) - 1U));
    uint64_t us = (scaled >> 19) + clock->microsecond;
    clock->second_of_day =
        (clock->second_of_day + (uint32_t)(us / 1000000U)) % 86400U;
    clock->microsecond = (uint32_t)(us % 1000000U);
}

static inline uint32_t rtc_clock_next_tick_us(const rtc_clock_state_t *clock) {
    return RTC_CLOCK_HALF_SECOND_US -
           clock->microsecond % RTC_CLOCK_HALF_SECOND_US;
}
