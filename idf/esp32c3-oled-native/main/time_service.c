#include "time_service.h"

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "board_config.h"
#include "esp_log.h"
#include "esp_sntp.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "runtime_settings.h"

static const char *const TAG = "time_service";

#define SNTP_SERVER_NAME_CAPACITY 35
#define TIME_SYNC_TASK_PRIORITY 1
#define TIME_SYNC_EVENT_NETWORK_READY (1U << 0)
#define TIME_SYNC_EVENT_COMPLETED (1U << 1)

// lwIP stores the pointers passed to esp_sntp_setservername(); it does not
// copy the strings. Keep the backing storage alive for the entire SNTP
// service lifetime, including after the one-shot services task is deleted.
static char s_sntp_server1[SNTP_SERVER_NAME_CAPACITY] =
    RUNTIME_DEFAULT_SNTP1;
static char s_sntp_server2[SNTP_SERVER_NAME_CAPACITY] =
    RUNTIME_DEFAULT_SNTP2;
static TaskHandle_t s_time_sync_task;

static void time_sync_notification(struct timeval *synced_time) {
    (void)synced_time;
    // The callback runs in lwIP context. Only post a constant-time task
    // notification here; logging and all SNTP control stay at priority 1.
    if (s_time_sync_task) {
        xTaskNotify(s_time_sync_task, TIME_SYNC_EVENT_COMPLETED, eSetBits);
    }
}

static void time_sync_task(void *argument) {
    (void)argument;
    while (true) {
        uint32_t events = 0;
        xTaskNotifyWait(0, UINT32_MAX, &events, portMAX_DELAY);
        if ((events & TIME_SYNC_EVENT_NETWORK_READY) != 0U &&
            esp_sntp_enabled() && esp_sntp_restart()) {
            ESP_LOGI(TAG,
                     "Network ready; requested immediate SNTP synchronization");
        }
        if ((events & TIME_SYNC_EVENT_COMPLETED) != 0U) {
            ESP_LOGI(TAG, "SNTP synchronized");
        }
    }
}

static esp_err_t ensure_time_sync_task(void) {
    if (s_time_sync_task) return ESP_OK;
    return xTaskCreate(time_sync_task, "time_sync",
                       BOARD_TASK_STACK_TIME_SYNC, NULL,
                       TIME_SYNC_TASK_PRIORITY, &s_time_sync_task) == pdPASS
               ? ESP_OK
               : ESP_ERR_NO_MEM;
}

esp_err_t time_service_apply(void) {
    esp_err_t task_result = ensure_time_sync_task();
    if (task_result != ESP_OK) return task_result;
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

    if (esp_sntp_enabled()) esp_sntp_stop();
    // Stop first so the TCP/IP thread cannot resolve a name while its
    // persistent backing buffer is being updated from saved settings.
    runtime_settings_get_sntp1(s_sntp_server1, sizeof(s_sntp_server1));
    runtime_settings_get_sntp2(s_sntp_server2, sizeof(s_sntp_server2));
    esp_sntp_setoperatingmode(SNTP_OPMODE_POLL);
    esp_sntp_setservername(0, s_sntp_server1);
    esp_sntp_setservername(1, s_sntp_server2);
    esp_sntp_set_time_sync_notification_cb(time_sync_notification);
    esp_sntp_set_sync_interval(
        (uint32_t)runtime_settings_get_time_sync_interval_min() * 60U * 1000U);
    esp_sntp_init();
    ESP_LOGI(TAG, "Timezone %s, SNTP %s / %s every %u min", timezone,
             s_sntp_server1, s_sntp_server2,
             runtime_settings_get_time_sync_interval_min());
    return ESP_OK;
}

void time_service_notify_network_ready(void) {
    // Initial Wi-Fi connection completes before time_service_apply(), so
    // there is no worker to notify on that first event. time_service_apply()
    // starts the initial request. Subsequent reconnects wake this priority-1
    // worker instead of doing SNTP control work in the Wi-Fi event callback.
    if (s_time_sync_task) {
        xTaskNotify(s_time_sync_task, TIME_SYNC_EVENT_NETWORK_READY, eSetBits);
    }
}
