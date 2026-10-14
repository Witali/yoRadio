#include "display.h"
#include "factory_ui.h"
#include "factory_timer.h"
#include "factory_photo.h"
#include "factory_animation.h"
#include "media.h"
#include "network.h"
#include "services.h"
#include "timezones.h"
#include <time.h>
#include "esp_attr.h"
#include "driver/gptimer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static factory_timer_t timer_state;
static uint32_t photo_interval;
static portMUX_TYPE timer_lock = portMUX_INITIALIZER_UNLOCKED;
static gptimer_handle_t clock_timer;

static bool IRAM_ATTR timer_alarm(gptimer_handle_t timer, const gptimer_alarm_event_data_t *event,
                                  void *context)
{
    /* Keep counting during blocking work; defer all SPI drawing to its owner task. */
    (void)timer;
    (void)event;
    (void)context;
    portENTER_CRITICAL_ISR(&timer_lock);
    factory_timer_tick(&timer_state, photo_interval);
    portEXIT_CRITICAL_ISR(&timer_lock);
    return false;
}

static factory_timer_t timer_snapshot(uint32_t consume, uint32_t interval)
{
    /* Atomically read counters and consume only the current renderer's events. */
    portENTER_CRITICAL(&timer_lock);
    photo_interval = interval;
    factory_timer_t result = timer_state;
    if (consume)
        result.pending = factory_timer_take(&timer_state, consume);
    portEXIT_CRITICAL(&timer_lock);
    return result;
}

static void timer_raise(uint32_t events)
{
    /* Restore the same update flags that a factory theme initializer sets. */
    portENTER_CRITICAL(&timer_lock);
    timer_state.pending |= events;
    portEXIT_CRITICAL(&timer_lock);
}

esp_err_t clock_ui_timer_init(void)
{
    /* Start the hardware timebase before network/services, as at 0x420083b6. */
    tv_settings_t settings;
    settings_snapshot(&settings);
    photo_interval = settings.photo_seconds;
    factory_timer_init(&timer_state, settings.wifi_mode == 1 && settings.ssid[0]);
    gptimer_config_t config = {
        .clk_src = GPTIMER_CLK_SRC_XTAL, .direction = GPTIMER_COUNT_UP, .resolution_hz = 1000000};
    esp_err_t result = gptimer_new_timer(&config, &clock_timer);
    if (result != ESP_OK)
        return result;
    gptimer_alarm_config_t alarm = {
        .alarm_count = 100000, .reload_count = 0, .flags.auto_reload_on_alarm = true};
    gptimer_event_callbacks_t callbacks = {.on_alarm = timer_alarm};
    result = gptimer_set_alarm_action(clock_timer, &alarm);
    if (result == ESP_OK)
        result = gptimer_register_event_callbacks(clock_timer, &callbacks, NULL);
    if (result == ESP_OK)
        result = gptimer_enable(clock_timer);
    if (result == ESP_OK)
        result = gptimer_start(clock_timer);
    return result;
}

static struct tm factory_local_time(const char *country, time_t now, bool *valid)
{
    /* Return the selected country's calendar, retaining the original year gate.
     * FIXED_FACTORY: use explicit IANA transitions instead of Newlib's implicit
     * US rules, and safely retain the preset if calendar conversion fails. */

    struct tm local;
    *valid = timezone_local_time(country, now, &local) && local.tm_year >= 125;
    if (!*valid)
        local = (struct tm){.tm_year = 125,
                            .tm_mon = 8,
                            .tm_mday = 19,
                            .tm_hour = 17,
                            .tm_min = 4,
                            .tm_sec = 40,
                            .tm_wday = 5};
    return local;
}

static void clock_task(void *unused)
{
    /* Run the startup/setup/theme state machine and factory animation/fade timers.
     * FIXED_RECONSTRUCTION: retain the GIF cursor across selection/theme changes
     * as in 0x4200b5cc and 0x42008e08; resetting it changes the next frame.
     * FIXED_FACTORY: repaint simple-clock digits at real minute rollover instead
     * of waiting for 0x4200bd8c's 66-second flag, and restore configured brightness
     * after the photo fade rather than 0x4200bc36's full-brightness ending.
     * REQUESTED_CHANGE: advance clipped text fields in the active display loop. */

    (void)unused;
    uint32_t generation = 0, weather_generation = 0;
    factory_animation_t animation = {0};
    unsigned description = 0;
    factory_photo_t slideshow = {0};
    time_t last_second = 0;
    unsigned phase = 0, progress = 0, previous_theme = 255;
    bool was_online = false, previous_weather_valid = false;
    unsigned weather_retry = 0;
    for (;;)
    {
        tv_settings_t settings;
        weather_snapshot_t weather;
        settings_snapshot(&settings);
        weather_snapshot(&weather);
        factory_timer_t ticks = timer_snapshot(0, settings.photo_seconds);
        bool online = network_connected(), valid;
        char address[20];
        network_address(address, sizeof(address));
        time_t now = time(NULL);
        struct tm local = factory_local_time(settings.country, now, &valid);
        uint32_t current_generation = settings_generation();
        bool changed = current_generation != generation || weather.generation != weather_generation;
        /* 0x42008e56 retries unsuccessful weather after 30 completed main-loop
         * delays. A blocking HTTP request does not spend these retry steps. */
        if (online && !weather.valid && !weather_request_active())
        {
            if (!weather_retry)
            {
                weather_retry = 30;
                weather_request_update();
            }
            else
                --weather_retry;
        }
        if (media_upload_active() || (!ticks.startup_active && weather_request_active()))
        {
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }
        /* The original 100-ms timer ends startup after 181 ticks. Its "second"
         * flags fire after eleven ticks: labels rotate every 3.3 seconds. */
        if (ticks.startup_active)
        {
            unsigned current_progress = ticks.startup_progress;
            if (phase != 1 || progress != current_progress || online != was_online)
                factory_draw_startup(online ? address : NULL, current_progress);
            phase = 1;
            progress = current_progress;
            timer_snapshot(TV_TIMER_STARTUP_DRAW, settings.photo_seconds);
        }
        else if (!online && network_ap_active())
        {
            if (phase != 2)
                factory_draw_setup();
            phase = 2;
        }
        else if (online)
        {
            bool reset_theme = phase != 3 || previous_theme != settings.theme;
            if (reset_theme)
            {
                display_fill(0, 0, 240, 240, 0);
                changed = true;
                /* 0x42008e08/0x4200aebe retain the animation cursor across
                 * theme switches; only initial boot starts it at zero. */
                description = 0;
                timer_raise(TV_TIMER_SECOND | TV_TIMER_DESCRIPTION | TV_TIMER_MINUTE |
                            (settings.theme == 2 ? TV_TIMER_PHOTO : 0));
            }
            phase = 3;
            if (!weather.valid || !previous_weather_valid)
                description = 0;
            if (settings.theme == 0 && (reset_theme || factory_scroll_description_ready()) &&
                timer_snapshot(TV_TIMER_DESCRIPTION, settings.photo_seconds).pending)
            {
                if (!reset_theme && weather.valid && previous_weather_valid)
                    description = (description + 1) % 10;
                /* A long label retains this event until its scroll completes.
                 * The description flag belongs to the classic theme. It must
                 * not start a new photo fade or reset the simple clock timer. */
                changed = changed || settings.theme == 0;
            }
            if (settings.theme == 0)
            {
                int frame = factory_animation_next(&animation,
                                                    media_animation_frames(settings.animation));
                bool periodic_status =
                    timer_snapshot(TV_TIMER_MINUTE, settings.photo_seconds).pending != 0;
                if (changed || now != last_second || periodic_status)
                    factory_draw_classic(&settings, &local, &weather, description,
                                         frame < 0 ? 0 : (unsigned)frame,
                                         reset_theme, periodic_status);
                else
                {
                    if (frame >= 0)
                        media_draw_animation(settings.animation, (unsigned)frame, 160, 160);
                }
                factory_scroll_tick();
            }
            else if (settings.theme == 1)
            {
                uint32_t events =
                    timer_snapshot(TV_TIMER_SECOND | TV_TIMER_MINUTE, settings.photo_seconds)
                        .pending;
                /* Correct the stock simple clock's stale-minute bug: its
                 * 0x4200bd8c only paints digits on a 66-second timer flag.
                 * Follow real minute/hour changes while retaining colon events. */
                factory_draw_simple(&settings, &local, address, reset_theme,
                                    events & TV_TIMER_SECOND, events & TV_TIMER_MINUTE);
            }
            else if (settings.theme == 2)
            {
                uint32_t present = 0;
                for (unsigned slot = 0; slot < PHOTO_COUNT; ++slot)
                    if (settings.photo_size[slot])
                        present |= 1u << slot;
                factory_photo_action_t action;
                factory_photo_step(&slideshow, settings.photo_mask, present,
                                   (ticks.pending & TV_TIMER_PHOTO) || reset_theme, false, &action);
                if (action.set_duty)
                    backlight_set_level(action.duty);
                if (action.photo >= -1)
                {
                    if (action.photo == -1)
                    {
                        display_fill(0, 0, 240, 240, 0);
                        display_factory_text(5, 225, address, 16, 0xffff, 0, true);
                    }
                    else
                        factory_draw_photo(action.photo, address);
                }
                if (action.finished)
                {
                    timer_snapshot(TV_TIMER_PHOTO, settings.photo_seconds);
                    /* Correct the stock fade's full-brightness ending when
                     * an explicit day/night brightness was requested. */
                    backlight_update(&settings, local.tm_hour, local.tm_min, valid);
                }
            }
            else if (timer_snapshot(TV_TIMER_SECOND, settings.photo_seconds).pending || reset_theme)
            {
                factory_draw_dial(&local, address, reset_theme);
            }
            if (settings.theme != 2)
                backlight_update(&settings, local.tm_hour, local.tm_min, valid);
            previous_theme = settings.theme;
            if (timer_snapshot(TV_TIMER_WEATHER, settings.photo_seconds).pending)
                weather_request_update();
        }
        generation = current_generation;
        weather_generation = weather.generation;
        was_online = online;
        last_second = now;
        previous_weather_valid = weather.valid;
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void clock_ui_start(void)
{
    /* Start the sole task that owns normal clock rendering. */

    configASSERT(xTaskCreate(clock_task, "clock_display", 4096, NULL, 2, NULL) == pdPASS);
}
