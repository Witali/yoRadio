#include "services.h"
#include "network.h"
#include "settings.h"
#include "timezones.h"
#include <limits.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "esp_netif_sntp.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static atomic_bool time_synced;

static void time_sync_notify(struct timeval *event)
{
    /* Latch an actual SNTP synchronization; keep it across disconnects and client restarts.
     * FIXED_FACTORY: 0x420109de records this notification, but 0x42010b96 ignores
     * it and rejects every year before 2025 instead of tracking successful sync. */
    (void)event;
    atomic_store_explicit(&time_synced, true, memory_order_release);
}

bool services_time_synced(void)
{
    /* Read the successful-sync latch without racing the TCP/IP callback task. */
    return atomic_load_explicit(&time_synced, memory_order_acquire);
}

bool services_local_time(const char *country, time_t utc, struct tm *local)
{
    /* Convert only a synchronized clock; retain the caller's calendar on failure.
     * FIXED_FACTORY: successful notification, rather than 0x42010b96's year >= 2025,
     * determines validity. Country conversion still validates libc/epoch overflow. */
    return services_time_synced() && timezone_local_time(country, utc, local);
}

static void time_sync_task(void *unused)
{
    /* Apply country time rules and manage the three factory SNTP servers.
     * FIXED_FACTORY: derive the actual offset instead of implicit US DST rules
     * in 0x42010a06. Revisit the offset each second, including while offline.
     * FIXED_FACTORY: let an active client finish its retry/fallback sequence;
     * 0x42010c3e restarts it every 21 invalid-year updates and starves server 3. */

    (void)unused;
    char configured_ntp[65] = "", configured_country[TV_COUNTRY_BYTES] = "", configured_city[65] = "";
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
            config.sync_cb = time_sync_notify;
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
