#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
#include "esp32c3_sleep_mock.h"
#include "rtc_wake_stub_clock.c"

// Execute the actual wake stub against an I2C wire model. The model decodes
// START/STOP, eight data bits and ACK; it does not call its private renderer.
gpio_dev_t GPIO;
static unsigned levels[22], bits, value, transactions, bytes[4];
static uint8_t wire[4][400];
static bool started, nack, stuck;
static uint64_t now_ticks, sleep_us;
static jmp_buf slept;
static unsigned default_wakes;

void esp_rom_gpio_pad_select_gpio(unsigned pin) { (void)pin; }
void esp_rom_gpio_connect_out_signal(unsigned pin, unsigned signal, bool inv, bool oen) {
    (void)pin; (void)signal; (void)inv; (void)oen;
}
void gpio_ll_output_disable(gpio_dev_t *gpio, unsigned pin) { (void)gpio; (void)pin; }
void gpio_ll_output_enable(gpio_dev_t *gpio, unsigned pin) { (void)gpio; (void)pin; }
void gpio_ll_od_enable(gpio_dev_t *gpio, unsigned pin) { (void)gpio; (void)pin; }
void gpio_ll_set_level(gpio_dev_t *gpio, unsigned pin, unsigned level) {
    (void)gpio;
    unsigned old = levels[pin];
    levels[pin] = level;
    if (pin == BOARD_OLED_SDA && levels[BOARD_OLED_SCL]) {
        if (old && !level) { started = true; bits = value = 0; }
        if (!old && level && started) {
            started = false;
            ++transactions;
            assert(transactions < 4);
        }
    }
    if (pin != BOARD_OLED_SCL || old == level || !started) return;
    if (!level) {
        if (bits == 9) bits = value = 0;
        return;
    }
    ++bits;
    if (bits <= 8) value = (value << 1) | levels[BOARD_OLED_SDA];
    if (bits == 8) {
        assert(bytes[transactions] < 400);
        wire[transactions][bytes[transactions]++] = (uint8_t)value;
    }
}
unsigned gpio_ll_get_level(gpio_dev_t *gpio, unsigned pin) {
    (void)gpio;
    if (pin == BOARD_OLED_SCL && stuck) return 0;
    if (pin == BOARD_OLED_SDA && started && bits == 9) return nack ? 1 : 0;
    return levels[pin];
}
void esp_rom_delay_us(unsigned us) { now_ticks += us; }
uint64_t rtc_timer_ll_get_cycle_count(unsigned id) { (void)id; return now_ticks; }
void esp_default_wake_deep_sleep(void) { ++default_wakes; }
void esp_wake_stub_set_wakeup_time(uint64_t us) { sleep_us = us; }
void esp_wake_stub_sleep(void (*stub)(void)) {
    assert(stub == rtc_clock_wake_stub);
    longjmp(slept, 1);
}
static void reset(void) {
    memset(&g_rtc_clock, 0, sizeof(g_rtc_clock));
    memset(wire, 0, sizeof(wire));
    memset(bytes, 0, sizeof(bytes));
    for (unsigned i = 0; i < 22; ++i) levels[i] = 1;
    bits = value = transactions = default_wakes = 0;
    started = nack = stuck = false;
    now_ticks = sleep_us = 0;
    g_rtc_clock.magic = RTC_CLOCK_MAGIC;
    g_rtc_clock.calibration = 1U << 19; // one microsecond per model tick
    for (unsigned d = 0; d < 10; ++d)
        for (unsigned i = 0; i < 65; ++i)
            g_rtc_clock.digits[d][i] = (uint8_t)(d * 17U + i);
    for (unsigned i = 0; i < 15; ++i) g_rtc_clock.colon[i] = (uint8_t)(i + 1);
}
static bool run_stub(void) {
    if (setjmp(slept)) return true;
    rtc_clock_wake_stub();
    return false;
}
static void check_address(unsigned left, unsigned right) {
    const uint8_t expected[] = {0x78, 0x00, 0x21, (uint8_t)(28 + left),
                                (uint8_t)(28 + right), 0x22, 0, 4};
    assert(transactions == 2);
    assert(bytes[0] == sizeof(expected));
    assert(memcmp(wire[0], expected, sizeof(expected)) == 0);
    assert(wire[1][0] == 0x78 && wire[1][1] == 0x40);
}
static void test_colon(void) {
    reset();
    g_rtc_clock.second_of_day = 12 * 3600 + 34 * 60;
    g_rtc_clock.displayed_minute = 12 * 60 + 34;
    g_rtc_clock.microsecond = 450000;
    now_ticks = 60000; // cross the OFF edge without a minute change
    assert(run_stub());
    check_address(34, 36);
    assert(bytes[1] == 17);
    for (unsigned i = 2; i < 17; ++i) assert(wire[1][i] == 0);
    assert(!g_rtc_clock.colon_on);
    assert(sleep_us == rtc_clock_next_tick_us(&g_rtc_clock));
    assert(sleep_us > 0 && sleep_us <= 500000);
    assert(default_wakes == 1);

    reset();
    now_ticks = 1000;
    assert(run_stub());
    check_address(34, 36);
    assert(memcmp(wire[1] + 2, g_rtc_clock.colon, 15) == 0);
}
static void test_minute(unsigned second, unsigned next_minute) {
    reset();
    g_rtc_clock.second_of_day = second;
    g_rtc_clock.displayed_minute = second / 60;
    g_rtc_clock.microsecond = 800000;
    now_ticks = 300000; // elapsed wake time, not a synthetic +500 ms
    assert(run_stub());
    check_address(0, 71);
    assert(bytes[1] == 362);
    assert(g_rtc_clock.displayed_minute == next_minute);
    unsigned digits[] = {next_minute / 600, next_minute / 60 % 10,
                          next_minute % 60 / 10, next_minute % 10};
    const unsigned left[] = {2, 18, 40, 56};
    for (unsigned page = 0; page < 5; ++page) {
        for (unsigned d = 0; d < 4; ++d) {
            assert(memcmp(wire[1] + 2 + page * 72 + left[d],
                          g_rtc_clock.digits[digits[d]] + page * 13, 13) == 0);
        }
    }
    assert(sleep_us == rtc_clock_next_tick_us(&g_rtc_clock));
}
static void test_recovery(void) {
    reset();
    levels[BOARD_BOOT_BUTTON] = 0;
    assert(!run_stub());
    assert(g_rtc_clock.user_wake && transactions == 0 && sleep_us == 0);
    reset();
    nack = true;
    assert(!run_stub());
    assert(!g_rtc_clock.user_wake && sleep_us == 0);
    reset();
    stuck = true;
    assert(!run_stub());
    assert(now_ticks < 1000); // clock stretching must be bounded
    reset();
    g_rtc_clock.magic = 0;
    assert(!run_stub());
    assert(transactions == 0);
}
static void test_elapsed_time(void) {
    rtc_clock_state_t clock = {.calibration = 3500001, .second_of_day = 86399,
                               .microsecond = 750000};
    uint64_t ticks = 0;
    // Two days of irregular samples include active I2C work and late wakes.
    for (unsigned i = 0; i < 400000; ++i) {
        ticks += 71000 + i % 2001;
        rtc_clock_advance(&clock, ticks);
        uint64_t elapsed = (ticks * clock.calibration) >> 19;
        uint64_t absolute = 86399750000ULL + elapsed;
        assert(clock.second_of_day == (absolute / 1000000) % 86400);
        assert(clock.microsecond == absolute % 1000000);
        assert(rtc_clock_next_tick_us(&clock) > 0);
        assert(rtc_clock_next_tick_us(&clock) <= 500000);
    }
    assert(clock.fractional_us == (ticks * clock.calibration) % (1U << 19));
}
int main(void) {
    test_colon();
    test_minute(12 * 3600 + 34 * 60 + 59, 12 * 60 + 35);
    test_minute(12 * 3600 + 59 * 60 + 59, 13 * 60);
    test_minute(86399, 0);
    test_recovery();
    test_elapsed_time();
    puts("PASS: actual RTC wake stub, I2C bytes, half-second edges, hour/day rollover, recovery and elapsed-time drift");
}
