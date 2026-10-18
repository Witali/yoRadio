#include "time_service.h"

#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "board_config.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "native_time_sntp.h"
#include "runtime_settings.h"

static const char *const TAG = "time_service";

#define TIME_SYNC_TASK_PRIORITY 1
#define TIME_SETTINGS_TIMEOUT_MS 100U
#define TIME_SYNC_EVENT_NETWORK_READY (1U << 0)
#define TIME_SYNC_EVENT_COMPLETED (1U << 1)

_Static_assert(RUNTIME_SNTP_NAME_CAPACITY == NATIVE_TIME_SNTP_NAME_CAPACITY,
               "SNTP settings and backend capacities must match");
static _Atomic(SemaphoreHandle_t) s_control_lock;
static _Atomic(TaskHandle_t) s_time_sync_task;
static atomic_bool s_network_ready_seen;
// Controller lock owns these flags. The shared backend owns immutable name
// storage and the complete managed/TCPIP lifecycle, with no runtime deinit.
static bool s_backend_applied;
static bool s_apply_pending = true;

static esp_err_t apply_time_locked(void);

static void time_sync_notification(void *context,
                                   const struct timeval *synced_time) {
    (void)context;
    (void)synced_time;
    // The callback runs in lwIP context. Only post a constant-time task
    // notification here; logging and SNTP control stay outside lwIP callbacks.
    TaskHandle_t task = atomic_load(&s_time_sync_task);
    if (task) {
        xTaskNotify(task, TIME_SYNC_EVENT_COMPLETED, eSetBits);
    }
}

static void time_sync_task(void *argument) {
    (void)argument;
    while (true) {
        uint32_t events = 0;
        xTaskNotifyWait(0, UINT32_MAX, &events, portMAX_DELAY);
        if ((events & TIME_SYNC_EVENT_NETWORK_READY) != 0U) {
            SemaphoreHandle_t lock = atomic_load(&s_control_lock);
            // The handle is published before task creation and remains alive
            // until reboot. Callbacks never wait for this lock.
            xSemaphoreTake(lock, portMAX_DELAY);
            esp_err_t result = s_apply_pending || !s_backend_applied
                ? apply_time_locked() : native_time_sntp_restart();
            if (result != ESP_OK) s_apply_pending = true;
            xSemaphoreGive(lock);
            if (result == ESP_OK) {
                ESP_LOGI(TAG, "Network ready; requested SNTP synchronization");
            } else {
                ESP_LOGW(TAG, "SNTP network update failed: %s",
                         esp_err_to_name(result));
            }
        }
        if ((events & TIME_SYNC_EVENT_COMPLETED) != 0U) {
            ESP_LOGI(TAG, "SNTP synchronized");
        }
    }
}

static esp_err_t ensure_time_sync_task(void) {
    if (atomic_load(&s_time_sync_task)) return ESP_OK;
    TaskHandle_t task = NULL;
    if (xTaskCreate(time_sync_task, "time_sync",
                       BOARD_TASK_STACK_TIME_SYNC, NULL,
                       TIME_SYNC_TASK_PRIORITY, &task) != pdPASS)
        return ESP_ERR_NO_MEM;
    atomic_store(&s_time_sync_task, task);
    return ESP_OK;
}

static esp_err_t apply_time_locked(void) {
    // Acquire settings only after the controller: an older caller cannot
    // capture values first and overwrite a later apply after waiting here.
    runtime_time_settings_t settings;
    s_apply_pending = true;
    esp_err_t result = runtime_settings_get_time_snapshot(
        &settings, TIME_SETTINGS_TIMEOUT_MS);
    if (result != ESP_OK) return result;
    result = native_time_sntp_init(time_sync_notification, NULL);
    if (result != ESP_OK) return result;
    int hour = settings.timezone_hour;
    unsigned minute = settings.timezone_minute;
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

    if (!atomic_load(&s_network_ready_seen)) {
        ESP_LOGI(TAG, "Timezone %s; SNTP deferred until station gets IP",
                 timezone);
        return ESP_OK;
    }
    native_time_sntp_config_t config = {
        .sync_interval_minutes = settings.sync_interval_min,
        .server_count = NATIVE_TIME_SNTP_SERVER_COUNT,
    };
    for (unsigned i = 0; i < NATIVE_TIME_SNTP_SERVER_COUNT; ++i)
        strlcpy(config.servers[i], settings.servers[i], sizeof(config.servers[i]));
    result = native_time_sntp_apply(&config);
    if (result != ESP_OK) return result;
    s_backend_applied = true;
    s_apply_pending = false;
    ESP_LOGI(TAG, "Timezone %s, SNTP %s / %s every %u min", timezone,
             settings.servers[0], settings.servers[1], settings.sync_interval_min);
    return ESP_OK;
}

esp_err_t time_service_apply(void) {
    SemaphoreHandle_t lock = atomic_load(&s_control_lock);
    if (!lock) {
        SemaphoreHandle_t created = xSemaphoreCreateMutex();
        if (!created) return ESP_ERR_NO_MEM;
        SemaphoreHandle_t expected = NULL;
        if (!atomic_compare_exchange_strong(&s_control_lock, &expected, created)) {
            vSemaphoreDelete(created);
            lock = expected;
        } else {
            lock = created;
        }
    }
    // SDK TCP/IP control itself has no bounded-wait public API. Keep the
    // existing synchronous apply contract; never abandon a borrowed IPC ctx.
    xSemaphoreTake(lock, portMAX_DELAY);
    esp_err_t result = ensure_time_sync_task();
    if (result == ESP_OK) result = apply_time_locked();
    xSemaphoreGive(lock);
    return result;
}

void time_service_notify_network_ready(void) {
    // Latch the initial GOT_IP even before the worker exists. This proves
    // TCP/IP initialization; it is deliberately not current link state.
    native_time_sntp_notify_network_ready();
    atomic_store(&s_network_ready_seen, true);
    TaskHandle_t task = atomic_load(&s_time_sync_task);
    if (task) {
        xTaskNotify(task, TIME_SYNC_EVENT_NETWORK_READY, eSetBits);
    }
}
