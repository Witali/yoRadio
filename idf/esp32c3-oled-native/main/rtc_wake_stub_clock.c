// ESP-IDF links rtc_wake_stub* code AND constants into retained RTC memory.
// This file must never call the normal GPIO/I2C drivers, libc or FreeRTOS.
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_DEEP_SLEEP_CLOCK

#include "board_config.h"
#include "esp_rom_gpio.h"
#include "esp_rom_sys.h"
#include "esp_sleep.h"
#include "esp_wake_stub.h"
#include "hal/gpio_ll.h"
#include "hal/rtc_timer_ll.h"
#include "rtc_clock_state.h"
#include "soc/gpio_sig_map.h"
#include "soc/io_mux_reg.h"

rtc_clock_state_t g_rtc_clock;

// Use computed IO_MUX addresses: GPIO_PIN_MUX_REG and GPIO_HOLD_MASK live in
// flash, so the GPIO LL helpers that index those tables are not stub-safe.
static void input_pin(unsigned pin) {
    esp_rom_gpio_pad_select_gpio(pin);
    REG_SET_BIT(IO_MUX_GPIO0_REG + pin * 4U, FUN_IE | FUN_PU);
    REG_CLR_BIT(IO_MUX_GPIO0_REG + pin * 4U, FUN_PD);
    gpio_ll_output_disable(&GPIO, pin);
}

static void i2c_pin(unsigned pin) {
    input_pin(pin);
    gpio_ll_set_level(&GPIO, pin, 1);
    esp_rom_gpio_connect_out_signal(pin, SIG_GPIO_OUT_IDX, false, false);
    gpio_ll_od_enable(&GPIO, pin);
    gpio_ll_output_enable(&GPIO, pin);
}

static void delay_half_bit(void) { esp_rom_delay_us(5); }
static void sda(unsigned level) {
    gpio_ll_set_level(&GPIO, BOARD_OLED_SDA, level);
}
static void scl_low(void) {
    gpio_ll_set_level(&GPIO, BOARD_OLED_SCL, 0);
    delay_half_bit();
}
static bool scl_high(void) {
    gpio_ll_set_level(&GPIO, BOARD_OLED_SCL, 1);
    // Bound clock stretching: a disconnected/stuck OLED must allow recovery.
    for (unsigned i = 0; i < 100; ++i) {
        if (gpio_ll_get_level(&GPIO, BOARD_OLED_SCL)) {
            delay_half_bit();
            return true;
        }
        esp_rom_delay_us(1);
    }
    return false;
}
static void stop(void) {
    scl_low();
    sda(0);
    scl_high();
    sda(1);
    delay_half_bit();
}
static bool byte(uint8_t value) {
    for (unsigned bit = 0; bit < 8; ++bit) {
        scl_low();
        sda((value & 0x80U) != 0);
        if (!scl_high()) return false;
        value <<= 1;
    }
    scl_low();
    sda(1);
    if (!scl_high()) return false;
    bool ack = gpio_ll_get_level(&GPIO, BOARD_OLED_SDA) == 0;
    scl_low();
    return ack;
}
static bool start(uint8_t control) {
    sda(1);
    if (!scl_high() || !gpio_ll_get_level(&GPIO, BOARD_OLED_SDA)) return false;
    sda(0);
    delay_half_bit();
    return byte(BOARD_OLED_ADDRESS << 1) && byte(control);
}

static void render_digits(unsigned minute_of_day) {
    unsigned digits[4] = {minute_of_day / 60U / 10U,
                          minute_of_day / 60U % 10U,
                          minute_of_day % 60U / 10U,
                          minute_of_day % 10U};
    static const unsigned left[4] = {2, 18, 40, 56};
    for (unsigned page = 0; page < RTC_CLOCK_PAGES; ++page) {
        for (unsigned digit = 0; digit < 4; ++digit) {
            for (unsigned x = 0; x < RTC_CLOCK_DIGIT_WIDTH; ++x) {
                g_rtc_clock.framebuffer[page * 72U + left[digit] + x] =
                    g_rtc_clock.digits[digits[digit]][page * 13U + x];
            }
        }
    }
}

static bool present(bool full, bool colon_on) {
    unsigned left = full ? 0 : 34;
    unsigned right = full ? 71 : 36;
    bool ok = start(0x00) && byte(0x21) && byte(28U + left) &&
              byte(28U + right) && byte(0x22) && byte(0) && byte(4);
    stop();
    if (!ok) return false;
    ok = start(0x40);
    for (unsigned page = 0; ok && page < RTC_CLOCK_PAGES; ++page) {
        for (unsigned x = left; ok && x <= right; ++x) {
            uint8_t value = x >= 34 && x <= 36
                ? (colon_on ? g_rtc_clock.colon[page * 3U + x - 34U] : 0)
                : g_rtc_clock.framebuffer[page * 72U + x];
            ok = byte(value);
        }
    }
    stop();
    return ok;
}

static bool user_pressed(void) {
    input_pin(BOARD_BOOT_BUTTON);
#ifdef CONFIG_YORADIO_ROTARY_ENCODER
    input_pin(CONFIG_YORADIO_ROTARY_ENCODER_GPIO_A);
    input_pin(CONFIG_YORADIO_ROTARY_ENCODER_GPIO_B);
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    input_pin(CONFIG_YORADIO_ROTARY_ENCODER_BUTTON_GPIO);
#endif
#endif
    esp_rom_delay_us(50);
    bool pressed = gpio_ll_get_level(&GPIO, BOARD_BOOT_BUTTON) == 0;
#ifdef CONFIG_YORADIO_ROTARY_ENCODER
    unsigned phase = gpio_ll_get_level(&GPIO, CONFIG_YORADIO_ROTARY_ENCODER_GPIO_A) |
        (gpio_ll_get_level(&GPIO, CONFIG_YORADIO_ROTARY_ENCODER_GPIO_B) << 1);
    pressed |= phase != g_rtc_clock.encoder_phase;
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    pressed |= gpio_ll_get_level(&GPIO, CONFIG_YORADIO_ROTARY_ENCODER_BUTTON_GPIO) == 0;
#endif
#endif
    return pressed;
}

void rtc_clock_wake_stub(void) {
    // Run IDF's required post-sleep workaround before accessing peripherals.
    esp_default_wake_deep_sleep();
    if (g_rtc_clock.magic != RTC_CLOCK_MAGIC) return;
    // Release the automatic digital pad latch before using SCL/BOOT.
    // Per-pin holds keep the audio outputs and level LED at their idle levels.
    REG_SET_BIT(RTC_CNTL_DIG_ISO_REG, RTC_CNTL_CLR_DG_PAD_AUTOHOLD);
    if (user_pressed()) {
        g_rtc_clock.user_wake = true;
        return; // Full boot restores services; this press only wakes the UI.
    }
    rtc_clock_advance(&g_rtc_clock, rtc_timer_ll_get_cycle_count(0));
    unsigned minute = g_rtc_clock.second_of_day / 60U;
    bool full = minute != g_rtc_clock.displayed_minute;
    bool colon_on = g_rtc_clock.microsecond < RTC_CLOCK_HALF_SECOND_US;
    i2c_pin(BOARD_OLED_SDA);
    i2c_pin(BOARD_OLED_SCL);
    if (full) render_digits(minute);
    if (!present(full, colon_on)) {
        // Leave the stub on an I2C fault. If normal OLED initialization
        // succeeds, sleep stays disarmed until the next ordinary reset.
        return;
    }
    g_rtc_clock.displayed_minute = minute;
    g_rtc_clock.colon_on = colon_on;
    rtc_clock_advance(&g_rtc_clock, rtc_timer_ll_get_cycle_count(0));
    esp_wake_stub_set_wakeup_time(rtc_clock_next_tick_us(&g_rtc_clock));
    esp_wake_stub_sleep(rtc_clock_wake_stub);
}
#endif
