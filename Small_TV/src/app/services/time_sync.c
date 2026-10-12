#include "services.h"
#include "network.h"
#include "settings.h"
#include "country_timezones.h"
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
    /* Apply the factory country timezone and manage the three SNTP servers. */

    (void)unused;
    char configured_ntp[65] = "", configured_country[3] = "", configured_city[65] = "";
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
        if (!timezone_ready)
        {
            /* Factory selects its country/POSIX table, not the weather UTC offset. */
            const char *zone = "GMT0BST";
            for (unsigned i = 0; i < sizeof(country_timezones) / sizeof(country_timezones[0]); ++i)
                if (!strcmp(s.country, country_timezones[i].country))
                {
                    zone = country_timezones[i].tz;
                    break;
                }
            setenv("TZ", zone, 1);
            tzset();
            timezone_ready = true;
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
