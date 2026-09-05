#include "time_service.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/apps/sntp.h"
#include "lwip/tcpip.h"
#include "persistent_settings.h"

static const char *TAG = "time";
static volatile bool s_connected;
static volatile bool s_dirty = true;
static volatile bool s_pending;
static struct tcpip_callback_msg *s_callback;
/* lwIP retains these pointers, so server names must outlive the init task. */
static char s_server1[SETTINGS_SNTP_CAPACITY];
static char s_server2[SETTINGS_SNTP_CAPACITY];

static void configure_sntp(void *argument) {
    (void)argument;
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    if (sntp_enabled()) sntp_stop();
    memcpy(s_server1, settings.sntp1, sizeof(s_server1));
    memcpy(s_server2, settings.sntp2, sizeof(s_server2));
    sntp_setoperatingmode(SNTP_OPMODE_POLL);
    sntp_setservername(0, s_server1);
    sntp_setservername(1, s_server2);
    sntp_set_sync_interval((uint32_t)settings.time_sync_interval_min * 60000U);
    sntp_init();
    s_pending = false;
}

void time_service_poll(void) {
    if (!s_connected || !s_dirty || s_pending) return;
    taskENTER_CRITICAL();
    s_dirty = false;
    taskEXIT_CRITICAL();
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    int offset_minutes = settings.timezone_hour * 60;
    offset_minutes += settings.timezone_hour < 0
                          ? -(int)settings.timezone_minute
                          : (int)settings.timezone_minute;
    int posix_minutes = -offset_minutes;
    char timezone[24];
    snprintf(timezone, sizeof(timezone), "UTC%c%d:%02d",
             posix_minutes < 0 ? '-' : '+', abs(posix_minutes) / 60,
             abs(posix_minutes) % 60);
    setenv("TZ", timezone, 1);
    tzset();
    /* Reusable message, nonblocking enqueue; all lwIP SNTP operations run on
     * its owning task. DNS/NTP remain asynchronous, never on the audio task. */
    if (!s_callback) s_callback = tcpip_callbackmsg_new(configure_sntp, NULL);
    s_pending = true;
    if (!s_callback || tcpip_callbackmsg_trycallback(s_callback) != ERR_OK) {
        s_pending = false;
        s_dirty = true;
        return;
    }
    ESP_LOGI(TAG, "Timezone %s; SNTP every %u minute(s)", timezone,
             settings.time_sync_interval_min);
}

esp_err_t time_service_start(void) {
    s_dirty = true;
    return ESP_OK;
}

void time_service_notify_connected(void) {
    s_connected = true;
    s_dirty = true;
}

void time_service_settings_changed(void) { s_dirty = true; }
