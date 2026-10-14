#include "services.h"
#include "network.h"
#include "settings.h"
#include "timezones.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "esp_netif_sntp.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static void time_sync_task(void *unused)
{
    /* Apply country time rules and manage the three factory SNTP servers.
     * FIXED_FACTORY: derive the actual offset instead of implicit US DST rules
     * in 0x42010a06. Revisit the offset each second, including while offline. */

    (void)unused;
    char configured_ntp[65] = "", configured_country[3] = "", configured_city[65] = "";
    char configured_zone[32] = "";
    bool timezone_ready = false, sntp_started = false;
    for (;;)
    {
        tv_settings_t s;
        settings_snapshot(&s);
        bool location_changed =
            strcmp(s.country, configured_country) || strcmp(s.city, configured_city);
        if (location_changed)
        {
            strcpy(configured_country, s.country);
            strcpy(configured_city, s.city);
            timezone_ready = false;
        }
        int32_t offset;
        bool daylight;
        if (timezone_utc_offset(s.country, time(NULL), &offset, &daylight))
        {
            /* POSIX offsets have the opposite sign to UTC offsets. This fixed
             * TZ keeps libc consumers consistent, including irregular transitions;
             * the display computes its own calendar from the same immutable rules. */
            unsigned magnitude = (unsigned)(offset < 0 ? -offset : offset);
            char zone[32];
            snprintf(zone, sizeof(zone), "UTC%c%u:%02u:%02u", offset < 0 ? '+' : '-',
                     magnitude/3600, magnitude/60%60, magnitude%60);
            if ((!timezone_ready || strcmp(zone, configured_zone)) && !setenv("TZ", zone, 1))
            {
                tzset();
                strcpy(configured_zone, zone);
                timezone_ready = true;
            }
        }
        if (network_connected() && (!sntp_started || strcmp(configured_ntp, s.ntp)))
        {
            if (sntp_started)
                esp_netif_sntp_deinit();
            strcpy(configured_ntp, s.ntp);
            esp_sntp_config_t config = ESP_NETIF_SNTP_DEFAULT_CONFIG_MULTIPLE(
                3, ESP_SNTP_SERVER_LIST("ntp1.aliyun.com",
                                        configured_ntp[0] ? configured_ntp : "cn.pool.ntp.org",
                                        "pool.ntp.org"));
            config.wait_for_sync = false;
            sntp_started = esp_netif_sntp_init(&config) == ESP_OK;
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void services_start(void)
{
    /* Initialize the weather cache before starting the time-sync task. */

    weather_start(); /* Initialize the cache mutex before the time task reads it. */
    configASSERT(xTaskCreate(time_sync_task, "time_sync", 3072, NULL, 2, NULL) == pdPASS);
}
