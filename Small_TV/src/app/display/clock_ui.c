#include "display.h"
#include "factory_ui.h"
#include "media.h"
#include "network.h"
#include "services.h"
#include <time.h>
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static struct tm factory_local_time(time_t now, bool *valid)
{
    /* Return local time, retaining the original preset date until SNTP is valid. */

    struct tm local;
    localtime_r(&now, &local);
    *valid = local.tm_year >= 125;
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
    /* Run the startup/setup/theme state machine and factory animation/fade timers. */

    (void)unused;
    const int64_t started = esp_timer_get_time();
    uint32_t generation = 0, weather_generation = 0;
    unsigned animation = 0, photo = 0, description = 0, fade = 0;
    int64_t next_photo = 0, next_description = 0, next_colon = 0;
    time_t last_second = 0;
    unsigned phase = 0, progress = 0, previous_theme = 255;
    bool was_online = false, first_photo = true, previous_weather_valid = false;
    for (;;)
    {
        tv_settings_t settings;
        weather_snapshot_t weather;
        settings_snapshot(&settings);
        weather_snapshot(&weather);
        const int64_t elapsed = esp_timer_get_time() - started;
        bool online = network_connected(), valid;
        char address[20];
        network_address(address, sizeof(address));
        time_t now = time(NULL);
        struct tm local = factory_local_time(now, &valid);
        uint32_t current_generation = settings_generation();
        bool changed = current_generation != generation || weather.generation != weather_generation;
        if (media_upload_active() || (phase == 3 && weather_request_active()))
        {
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }
        /* The original 100-ms timer ends startup after 181 ticks. Its "second"
         * flags fire after eleven ticks: labels rotate every 3.3 seconds. */
        if (elapsed < 18100000 && settings.wifi_mode == 1 && settings.ssid[0])
        {
            unsigned current_progress = elapsed / 100000;
            if (phase != 1 || progress != current_progress || online != was_online)
                factory_draw_startup(online ? address : NULL, current_progress);
            phase = 1;
            progress = current_progress;
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
                animation = 0;
                description = 0;
                first_photo = true;
                next_description = (elapsed / 3300000 + 1) * 3300000;
                next_photo = elapsed;
            }
            phase = 3;
            if (!weather.valid || !previous_weather_valid)
                description = 0;
            if (elapsed >= next_description)
            {
                if (weather.valid && previous_weather_valid)
                    description = (description + 1) % 10;
                next_description = (elapsed / 3300000 + 1) * 3300000;
                /* The description flag belongs to the classic theme. It must
                 * not start a new photo fade or reset the simple clock timer. */
                changed = changed || settings.theme == 0;
            }
            if (settings.theme == 0)
            {
                if (changed || now != last_second)
                    factory_draw_classic(&settings, &local, &weather, description, animation,
                                         reset_theme);
                else
                {
                    unsigned frames = media_animation_frames(settings.animation);
                    if (frames)
                        media_draw_animation(settings.animation, animation % frames, 160, 160);
                }
                ++animation;
            }
            else if (settings.theme == 1)
            {
                if (changed || elapsed >= next_colon)
                {
                    factory_draw_simple(&settings, &local, address, reset_theme);
                    next_colon = (elapsed / 1100000 + 1) * 1100000;
                }
            }
            else if (settings.theme == 2)
            {
                if (!fade && (changed || elapsed >= next_photo))
                    fade = 1;
                if (fade)
                {
                    /* Higher duty dims this board. Change photos at duty 1000
                     * (backlight off), then restore full brightness in six steps. */
                    static const unsigned levels[] = {300, 600, 1000, 600, 300, 0};
                    backlight_set_level(levels[fade - 1]);
                    if (fade == 3)
                    {
                        if (!first_photo)
                            photo = (photo + 1) % PHOTO_COUNT;
                        unsigned tries = 0;
                        while (tries < PHOTO_COUNT && (!(settings.photo_mask & (1u << photo)) ||
                                                       !settings.photo_size[photo]))
                        {
                            photo = (photo + 1) % PHOTO_COUNT;
                            ++tries;
                        }
                        if (tries == PHOTO_COUNT)
                        {
                            display_fill(0, 0, 240, 240, 0);
                            display_factory_text(5, 225, address, 16, 0xffff, 0, true);
                        }
                        else
                            factory_draw_photo(photo, address);
                        first_photo = false;
                    }
                    if (++fade == 7)
                    {
                        fade = 0;
                        int64_t period = (int64_t)settings.photo_seconds * 1100000;
                        next_photo = (elapsed / period + 1) * period;
                    }
                }
            }
            else if (changed || elapsed >= next_colon)
            {
                factory_draw_dial(&local, address, reset_theme);
                next_colon = (elapsed / 1100000 + 1) * 1100000;
            }
            if (settings.theme != 2)
                backlight_update(&settings, local.tm_hour, local.tm_min, valid);
            previous_theme = settings.theme;
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
