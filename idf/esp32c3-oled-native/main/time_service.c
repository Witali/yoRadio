#include "time_service.h"

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "esp_log.h"
#include "esp_sntp.h"
#include "runtime_settings.h"

static const char *const TAG = "time_service";

esp_err_t time_service_apply(void) {
    int hour = runtime_settings_get_timezone_hour();
    unsigned minute = runtime_settings_get_timezone_minute();
    int offset_minutes = hour * 60;
    offset_minutes += hour < 0 ? -(int)minute : (int)minute;
    // POSIX TZ offsets have the opposite sign: UTC+2 is written as UTC-2.
    int posix_minutes = -offset_minutes;
    char timezone[24];
    snprintf(timezone, sizeof(timezone), "UTC%c%d:%02d",
             posix_minutes < 0 ? '-' : '+',
             abs(posix_minutes) / 60, abs(posix_minutes) % 60);
    if (setenv("TZ", timezone, 1) != 0) return ESP_FAIL;
    tzset();

    char server1[35];
    char server2[35];
    runtime_settings_get_sntp1(server1, sizeof(server1));
    runtime_settings_get_sntp2(server2, sizeof(server2));
    if (esp_sntp_enabled()) esp_sntp_stop();
    esp_sntp_setoperatingmode(SNTP_OPMODE_POLL);
    esp_sntp_setservername(0, server1);
    esp_sntp_setservername(1, server2);
    esp_sntp_set_sync_interval(
        (uint32_t)runtime_settings_get_time_sync_interval_min() * 60U * 1000U);
    esp_sntp_init();
    ESP_LOGI(TAG, "Timezone %s, SNTP %s / %s every %u min", timezone,
             server1, server2,
             runtime_settings_get_time_sync_interval_min());
    return ESP_OK;
}
