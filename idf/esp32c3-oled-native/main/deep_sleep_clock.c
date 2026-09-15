#include "deep_sleep_clock.h"
#include "sdkconfig.h"

#ifndef CONFIG_YORADIO_DEEP_SLEEP_CLOCK
bool deep_sleep_clock_begin_activity(void) { return true; }
void deep_sleep_clock_end_activity(void) {}
void deep_sleep_clock_set_ready(void) {}
bool deep_sleep_clock_boot(void) { return false; }
void deep_sleep_clock_wait_for_release(int pin) { (void)pin; }
void deep_sleep_clock_try_enter(native_state_t *state, oled_display_t *display) {
    (void)state;
    (void)display;
}
#else
#include <stdatomic.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include "audio_service.h"
#include "board_config.h"
#include "display_settings.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_private/esp_clk.h"
#include "esp_sleep.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "hal/rtc_timer_ll.h"
#include "native_audio_settings.h"
#include "network_service.h"
#include "freertos/task.h"
#include "rtc_clock_state.h"

static const char *const TAG = "sleep_clock";
static atomic_int s_activity; // -1: sleep owns the board; >= 0: active users
static atomic_bool s_ready;
static bool s_faulted;
static bool s_user_wake;

bool deep_sleep_clock_begin_activity(void) {
    int users = atomic_load(&s_activity);
    while (users >= 0) {
        if (atomic_compare_exchange_weak(&s_activity, &users, users + 1))
            return true;
    }
    return false;
}
void deep_sleep_clock_end_activity(void) { atomic_fetch_sub(&s_activity, 1); }
void deep_sleep_clock_set_ready(void) { atomic_store(&s_ready, true); }

bool deep_sleep_clock_boot(void) {
    bool retained = esp_reset_reason() == ESP_RST_DEEPSLEEP &&
                    g_rtc_clock.magic == RTC_CLOCK_MAGIC;
    bool user_wake = retained && g_rtc_clock.user_wake;
    s_user_wake = user_wake;
    s_faulted = retained && !user_wake;
    g_rtc_clock.magic = 0;
    gpio_deep_sleep_hold_dis();
    gpio_hold_dis(BOARD_AUDIO_LEFT_DATA);
    gpio_hold_dis(BOARD_AUDIO_RIGHT_DATA);
#ifdef CONFIG_YORADIO_AUDIO_LEVEL_LED
    gpio_hold_dis(CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO);
#endif
    if (s_faulted) ESP_LOGW(TAG, "OLED wake failed; sleep disabled until reset");
    return user_wake;
}

void deep_sleep_clock_wait_for_release(int pin) {
    if (!s_user_wake) return;
    unsigned released_ms = 0;
    while (released_ms < 40U) {
        released_ms = gpio_get_level(pin) ? released_ms + 10U : 0;
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    display_settings_note_activity();
}

static bool idle_clock(native_state_t *state) {
    native_state_t current;
    native_state_snapshot(state, &current);
    bool power_off = false;
    return !current.audio_running && current.web_ready &&
        current.network_mode == NATIVE_NETWORK_CLIENT &&
        (strcmp(current.stream_format, "stopped") == 0 ||
         strcmp(current.stream_format, "idle") == 0) &&
        display_settings_screensaver_active(false,
            (uint32_t)(esp_timer_get_time() / 1000U), &power_off) && !power_off &&
        gpio_get_level(BOARD_BOOT_BUTTON) != 0;
}

static bool controls_released(void) {
    if (gpio_get_level(BOARD_BOOT_BUTTON) == 0) return false;
#ifdef CONFIG_YORADIO_ROTARY_ENCODER
    uint8_t phase = gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_GPIO_A) |
        (gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_GPIO_B) << 1);
    if (phase != g_rtc_clock.encoder_phase) return false;
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    if (gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_BUTTON_GPIO) == 0)
        return false;
#endif
#endif
    return true;
}

static bool prepare_clock(oled_display_t *display) {
    struct timeval now;
    gettimeofday(&now, NULL);
    if ((int64_t)now.tv_sec < 1704067200LL) return false;
    struct tm local;
    if (!localtime_r(&now.tv_sec, &local)) return false;
    g_rtc_clock.ticks = rtc_timer_ll_get_cycle_count(0);
    g_rtc_clock.calibration = esp_clk_slowclk_cal_get();
    if (!g_rtc_clock.calibration) return false;
    g_rtc_clock.second_of_day = local.tm_hour * 3600U +
                                local.tm_min * 60U + local.tm_sec;
    g_rtc_clock.microsecond = (uint32_t)now.tv_usec;
    g_rtc_clock.fractional_us = 0;
    g_rtc_clock.user_wake = false;
    // Cache the existing renderer's glyphs once. No font, libc, timezone or
    // framebuffer allocation is needed while flash is powered down.
    for (unsigned digit = 0; digit < 10; ++digit) {
        oled_display_draw_clock(display, 0, digit, true, true);
        for (unsigned page = 0; page < RTC_CLOCK_PAGES; ++page) {
            memcpy(&g_rtc_clock.digits[digit][page * 13U],
                   &display->framebuffer[page * 72U + 56U], 13);
            memcpy(&g_rtc_clock.colon[page * 3U],
                   &display->framebuffer[page * 72U + 34U], 3);
        }
    }
    rtc_clock_advance(&g_rtc_clock, rtc_timer_ll_get_cycle_count(0));
    unsigned minute = g_rtc_clock.second_of_day / 60U;
    g_rtc_clock.displayed_minute = minute;
    g_rtc_clock.colon_on = g_rtc_clock.microsecond < RTC_CLOCK_HALF_SECOND_US;
    oled_display_draw_clock(display, minute / 60U, minute % 60U,
                            g_rtc_clock.colon_on, true);
    memcpy(g_rtc_clock.framebuffer, display->framebuffer,
           sizeof(g_rtc_clock.framebuffer));
    return oled_display_present(display) == ESP_OK;
}

void deep_sleep_clock_try_enter(native_state_t *state, oled_display_t *display) {
    if (s_faulted || !atomic_load(&s_ready) || !idle_clock(state)) return;
    int expected = 0;
    if (!atomic_compare_exchange_strong(&s_activity, &expected, -1)) return;
    bool output_suspended = false;
#ifdef CONFIG_YORADIO_ROTARY_ENCODER
    g_rtc_clock.encoder_phase = gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_GPIO_A) |
        (gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_GPIO_B) << 1);
#endif
    if (!idle_clock(state) || !controls_released() || !prepare_clock(display))
        goto cancel;
    if (native_audio_settings_flush() != ESP_OK) goto cancel;
    // Only the output task may disable I2S: wait for its acknowledgement.
    if (audio_service_suspend_output() != ESP_OK) {
        s_faulted = true;
        ESP_LOGW(TAG, "I2S shutdown failed; sleep disabled until reset");
        goto cancel;
    }
    output_suspended = true;
    if (!idle_clock(state) || !controls_released()) goto cancel;
    if (esp_sleep_enable_timer_wakeup(RTC_CLOCK_HALF_SECOND_US) != ESP_OK)
        goto cancel;
    if (network_service_prepare_sleep() != ESP_OK) goto cancel;

    gpio_hold_en(BOARD_AUDIO_LEFT_DATA);
    gpio_hold_en(BOARD_AUDIO_RIGHT_DATA);
#ifdef CONFIG_YORADIO_AUDIO_LEVEL_LED
    gpio_reset_pin(CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO);
    gpio_set_direction(CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO, GPIO_MODE_OUTPUT);
#ifdef CONFIG_YORADIO_AUDIO_LEVEL_LED_ACTIVE_LOW
    gpio_set_level(CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO, 1);
#else
    gpio_set_level(CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO, 0);
#endif
    gpio_hold_en(CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO);
#endif
    gpio_deep_sleep_hold_en();
    g_rtc_clock.magic = RTC_CLOCK_MAGIC;
    esp_set_deep_sleep_wake_stub(rtc_clock_wake_stub);
    ESP_LOGI(TAG, "Deep-sleep clock: 500 ms RTC ticks; hold BOOT to wake");
    rtc_clock_advance(&g_rtc_clock, rtc_timer_ll_get_cycle_count(0));
    ESP_ERROR_CHECK(esp_sleep_enable_timer_wakeup(
        rtc_clock_next_tick_us(&g_rtc_clock)));
    esp_deep_sleep_start();
cancel:
    if (output_suspended && audio_service_resume_output() != ESP_OK) {
        s_faulted = true;
        ESP_LOGW(TAG, "I2S restore failed; sleep disabled until reset");
    }
    atomic_store(&s_activity, 0);
}
#endif
