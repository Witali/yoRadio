#include "native_time_sntp_internal.h"

#include <stdbool.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "esp_netif.h"
#include "esp_netif_sntp.h"
#include "esp_sntp.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

#define CONTROL_WAIT_MS 100U

static _Atomic(SemaphoreHandle_t) s_lock;
static atomic_bool s_tcpip_ready;
static bool s_initialized;
static bool s_managed;
static native_time_sntp_sync_cb_t s_callback;
static void *s_callback_context;

static bool valid_config(const native_time_sntp_config_t *config) {
    if (!config || config->server_count == 0U ||
        config->server_count > NATIVE_TIME_SNTP_SERVER_COUNT ||
        config->server_count > CONFIG_LWIP_SNTP_MAX_SERVERS ||
        config->sync_interval_minutes < 15U ||
        config->sync_interval_minutes > 1440U) return false;
    for (unsigned index = 0; index < config->server_count; ++index) {
        const char *name = config->servers[index];
        const char *end = memchr(name, '\0', NATIVE_TIME_SNTP_NAME_CAPACITY);
        if (!end || end == name) return false;
        for (const char *at = name; at < end; ++at) {
            unsigned char value = (unsigned char)*at;
            if (value <= 0x20U || value == 0x7fU || value == '"' ||
                value == '/' || value == '\\') return false;
        }
    }
    return true;
}

static void sync_notification(struct timeval *tv) {
    if (s_callback) s_callback(s_callback_context, tv);
}

static SemaphoreHandle_t take_control(void) {
    SemaphoreHandle_t lock = atomic_load(&s_lock);
    if (!lock || xSemaphoreTake(lock, pdMS_TO_TICKS(CONTROL_WAIT_MS)) != pdTRUE)
        return NULL;
    return lock;
}

esp_err_t native_time_sntp_init(native_time_sntp_sync_cb_t callback,
                                void *context) {
    SemaphoreHandle_t lock = atomic_load(&s_lock);
    if (!lock) {
        SemaphoreHandle_t candidate = xSemaphoreCreateMutex();
        if (!candidate) return ESP_ERR_NO_MEM;
        SemaphoreHandle_t empty = NULL;
        if (!atomic_compare_exchange_strong(&s_lock, &empty, candidate)) {
            vSemaphoreDelete(candidate);
            lock = empty;
        } else {
            lock = candidate;
        }
    }
    if (xSemaphoreTake(lock, pdMS_TO_TICKS(CONTROL_WAIT_MS)) != pdTRUE)
        return ESP_ERR_TIMEOUT;
    esp_err_t result = ESP_OK;
    if (s_initialized) {
        if (s_callback != callback || s_callback_context != context)
            result = ESP_ERR_INVALID_STATE;
    } else {
        s_callback = callback;
        s_callback_context = context;
        s_initialized = true;
    }
    xSemaphoreGive(lock);
    return result;
}

void native_time_sntp_notify_network_ready(void) {
    atomic_store(&s_tcpip_ready, true);
}

esp_err_t native_time_sntp_apply(const native_time_sntp_config_t *config) {
    if (!valid_config(config)) return ESP_ERR_INVALID_ARG;
    if (!atomic_load(&s_tcpip_ready)) return ESP_ERR_INVALID_STATE;
    SemaphoreHandle_t lock = take_control();
    if (!lock) return atomic_load(&s_lock) ? ESP_ERR_TIMEOUT : ESP_ERR_INVALID_STATE;
    esp_err_t result = ESP_ERR_INVALID_STATE;
    if (!s_initialized) goto done;
    if (!s_managed) {
        result = esp_netif_tcpip_exec(native_time_sntp_context_unused, NULL);
        if (result != ESP_OK) goto done;
        // No bank pointer is exposed during managed allocation/failure cleanup.
        // The actual pinned SDK accepts zero initial servers; the full list is
        // published by apply_in_tcpip only after managed storage is ready.
        esp_sntp_config_t initial = {0};
        initial.sync_cb = sync_notification;
        result = esp_netif_sntp_init(&initial);
        if (result != ESP_OK) goto done;
        s_managed = true;
    }
    result = esp_netif_tcpip_exec(native_time_sntp_context_apply, (void *)config);
done:
    xSemaphoreGive(lock);
    return result;
}

esp_err_t native_time_sntp_restart(void) {
    if (!atomic_load(&s_tcpip_ready)) return ESP_ERR_INVALID_STATE;
    SemaphoreHandle_t lock = take_control();
    if (!lock) return atomic_load(&s_lock) ? ESP_ERR_TIMEOUT : ESP_ERR_INVALID_STATE;
    esp_err_t result = s_initialized && s_managed
                           ? esp_netif_tcpip_exec(native_time_sntp_context_restart, NULL)
                           : ESP_ERR_INVALID_STATE;
    xSemaphoreGive(lock);
    return result;
}

void native_time_sntp_context_interval(uint32_t interval_ms) {
    sntp_set_sync_mode(SNTP_SYNC_MODE_IMMED);
    sntp_set_sync_interval(interval_ms);
}
