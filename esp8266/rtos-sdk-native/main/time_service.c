#include "time_service.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"
#include "lwip/apps/sntp.h"
#include "persistent_settings.h"

#define NETWORK_READY_BIT BIT0

static const char *TAG = "time";
static EventGroupHandle_t s_events;
/* lwIP retains these pointers, so server names must outlive the init task. */
static char s_server1[SETTINGS_SNTP_CAPACITY];
static char s_server2[SETTINGS_SNTP_CAPACITY];

static void time_task(void *argument) {
    (void)argument;
    xEventGroupWaitBits(s_events, NETWORK_READY_BIT, pdFALSE, pdFALSE,
                        portMAX_DELAY);
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
    memcpy(s_server1, settings.sntp1, sizeof(s_server1));
    memcpy(s_server2, settings.sntp2, sizeof(s_server2));
    sntp_setoperatingmode(SNTP_OPMODE_POLL);
    sntp_setservername(0, s_server1);
    sntp_setservername(1, s_server2);
    sntp_set_sync_interval((uint32_t)settings.time_sync_interval_min * 60000U);
    sntp_init();
    ESP_LOGI(TAG, "Timezone %s; SNTP every %u minute(s)", timezone,
             settings.time_sync_interval_min);
    vTaskDelete(NULL);
}

esp_err_t time_service_start(void) {
    s_events = xEventGroupCreate();
    if (!s_events) return ESP_ERR_NO_MEM;
    if (xTaskCreate(time_task, "sntp_init", 1536, NULL, 1, NULL) != pdPASS)
        return ESP_ERR_NO_MEM;
    return ESP_OK;
}

void time_service_notify_connected(void) {
    if (s_events) xEventGroupSetBits(s_events, NETWORK_READY_BIT);
}
