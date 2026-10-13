#include "display.h"
#include "board.h"
#include "driver/ledc.h"
#include <limits.h>

static unsigned backlight_applied_level = UINT_MAX;

esp_err_t backlight_init(void)
{
    /* Configure the factory LEDC timer/channel and initial active-low brightness.
     * FIXED_RECONSTRUCTION: 0x42008d62 configures channel duty zero, then sets
     * and latches level 100 through 0x42008bd2. Preserve that call sequence. */

    ledc_timer_config_t timer = {.speed_mode = LEDC_LOW_SPEED_MODE,
                                 .timer_num = LEDC_TIMER_0,
                                 .duty_resolution = LEDC_TIMER_13_BIT,
                                 .freq_hz = 1000,
                                 .clk_cfg = LEDC_AUTO_CLK};
    esp_err_t result = ledc_timer_config(&timer);
    if (result != ESP_OK)
        return result;
    ledc_channel_config_t channel = {.gpio_num = LCD_GPIO_BACKLIGHT,
                                     .speed_mode = LEDC_LOW_SPEED_MODE,
                                     .channel = LEDC_CHANNEL_0,
                                     .timer_sel = LEDC_TIMER_0,
                                     .duty = 0,
                                     .hpoint = 0};
    result = ledc_channel_config(&channel);
    if (result == ESP_OK)
        backlight_set_level(100);
    return result;
}

void backlight_set_level(unsigned per_mille)
{
    /* Apply a bounded per-mille PWM duty to the display backlight.
     * FIXED_FACTORY: remember the actually applied level, including photo fades,
     * so the scheduled brightness can be restored after a forced duty change.
     * The factory cache at 0x3fcc39ec tracks only schedule changes. */

    if (per_mille > 1000)
        per_mille = 1000;
    ESP_ERROR_CHECK(ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, per_mille * 8191 / 1000));
    ESP_ERROR_CHECK(ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0));
    backlight_applied_level = per_mille;
}

void backlight_update(const tv_settings_t *s, int local_hour, int local_minute, bool clock_valid)
{
    /* Select day/night duty using the factory minute-of-day boundary rules.
     * FIXED_RECONSTRUCTION: 0x42008c4c skips LEDC writes when the requested level
     * is unchanged; rewriting it every main-loop pass adds needless driver work.
     * Compare with the actual applied level to retain the photo-fade correction. */

    unsigned minute = local_hour * 60 + local_minute;
    bool day = minute < (unsigned)s->night_start * 60 &&
               (minute > 720 || minute > (unsigned)s->night_stop * 60);
    /* 0x42008cd4..0x42008ce0 uses strict unsigned comparisons and no SNTP gate;
     * the factory preset local time also participates in the night schedule. */
    (void)clock_valid;
    bool night = s->night_mode && !day;
    unsigned level = night ? s->night_level : s->day_level;
    if (level != backlight_applied_level)
        backlight_set_level(level);
}
