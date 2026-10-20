#include "network_settings.h"

#include <stdatomic.h>
#include <stddef.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "nvs.h"

#define NETWORK_RECORD_SIZE 32U
#define NETWORK_RECORD_HOSTNAME 8U
#define SETTINGS_WAIT_MS 100U

static _Atomic(SemaphoreHandle_t) s_write_lock;
static portMUX_TYPE s_snapshot_lock = portMUX_INITIALIZER_UNLOCKED;
static bool s_initialized;
static network_settings_t s_settings;
static uint32_t s_revision;

void network_settings_defaults(network_settings_t *settings) {
    if (!settings) return;
    memset(settings, 0, sizeof(*settings));
    memcpy(settings->hostname, "yoradio", sizeof("yoradio"));
}

bool network_settings_valid(const network_settings_t *settings) {
    if (!settings || settings->ap_timeout_minutes > NETWORK_SETTINGS_AP_TIMEOUT_MAX_MINUTES)
        return false;
    const char *end = memchr(settings->hostname, '\0', sizeof(settings->hostname));
    if (!end || end == settings->hostname || settings->hostname[0] == '-' || end[-1] == '-')
        return false;
    for (const char *at = settings->hostname; at < end; ++at) {
        unsigned char value = (unsigned char)*at;
        if (!((value >= 'a' && value <= 'z') ||
              (value >= 'A' && value <= 'Z') ||
              (value >= '0' && value <= '9') || value == '-')) return false;
    }
    return true;
}

static void encode_record(const network_settings_t *settings,
                          uint8_t record[NETWORK_RECORD_SIZE]) {
    memset(record, 0, NETWORK_RECORD_SIZE);
    memcpy(record, "NNET", 4U);
    record[4] = 1U;
    record[6] = settings->ap_timeout_minutes;
    memcpy(record + NETWORK_RECORD_HOSTNAME, settings->hostname,
           strlen(settings->hostname));
}

static bool decode_record(const uint8_t record[NETWORK_RECORD_SIZE],
                           network_settings_t *settings) {
    if (memcmp(record, "NNET", 4U) || record[4] != 1U || record[5] || record[7])
        return false;
    network_settings_t candidate = {0};
    candidate.ap_timeout_minutes = record[6];
    memcpy(candidate.hostname, record + NETWORK_RECORD_HOSTNAME,
           sizeof(candidate.hostname));
    if (!network_settings_valid(&candidate)) return false;
    uint8_t canonical[NETWORK_RECORD_SIZE];
    encode_record(&candidate, canonical);
    if (memcmp(record, canonical, NETWORK_RECORD_SIZE)) return false;
    *settings = candidate;
    return true;
}

static SemaphoreHandle_t take_write_lock(void) {
    SemaphoreHandle_t lock = atomic_load(&s_write_lock);
    if (!lock) {
        SemaphoreHandle_t candidate = xSemaphoreCreateMutex();
        if (!candidate) return NULL;
        SemaphoreHandle_t empty = NULL;
        if (!atomic_compare_exchange_strong(&s_write_lock, &empty, candidate)) {
            vSemaphoreDelete(candidate);
            lock = empty;
        } else lock = candidate;
    }
    return xSemaphoreTake(lock, pdMS_TO_TICKS(SETTINGS_WAIT_MS)) == pdTRUE
               ? lock : NULL;
}

esp_err_t network_settings_init(void) {
    SemaphoreHandle_t lock = take_write_lock();
    if (!lock) return atomic_load(&s_write_lock) ? ESP_ERR_TIMEOUT : ESP_ERR_NO_MEM;
    portENTER_CRITICAL(&s_snapshot_lock);
    bool initialized = s_initialized;
    portEXIT_CRITICAL(&s_snapshot_lock);
    if (initialized) {
        xSemaphoreGive(lock);
        return ESP_OK;
    }
    network_settings_t candidate;
    network_settings_defaults(&candidate);
    nvs_handle_t handle;
    esp_err_t result = nvs_open("native_network", NVS_READONLY, &handle);
    if (result == ESP_OK) {
        size_t size = 0;
        result = nvs_get_blob(handle, "cfg", NULL, &size);
        if (result == ESP_OK && size == NETWORK_RECORD_SIZE) {
            uint8_t record[NETWORK_RECORD_SIZE];
            result = nvs_get_blob(handle, "cfg", record, &size);
            if (result == ESP_OK && size == NETWORK_RECORD_SIZE)
                (void)decode_record(record, &candidate);
        }
        nvs_close(handle);
    }
    if (result == ESP_ERR_NVS_NOT_FOUND || result == ESP_ERR_NVS_TYPE_MISMATCH)
        result = ESP_OK;
    if (result == ESP_OK) {
        portENTER_CRITICAL(&s_snapshot_lock);
        s_settings = candidate;
        s_revision = 1U;
        s_initialized = true;
        portEXIT_CRITICAL(&s_snapshot_lock);
    }
    xSemaphoreGive(lock);
    return result;
}

bool network_settings_snapshot(network_settings_t *settings, uint32_t *revision) {
    if (!settings) return false;
    portENTER_CRITICAL(&s_snapshot_lock);
    bool available = s_initialized;
    if (available) {
        *settings = s_settings;
        if (revision) *revision = s_revision;
    }
    portEXIT_CRITICAL(&s_snapshot_lock);
    return available;
}

esp_err_t network_settings_save(const network_settings_t *settings) {
    if (!network_settings_valid(settings)) return ESP_ERR_INVALID_ARG;
    network_settings_t candidate = *settings;
    uint8_t record[NETWORK_RECORD_SIZE];
    encode_record(&candidate, record);
    if (!decode_record(record, &candidate)) return ESP_ERR_INVALID_ARG;
    SemaphoreHandle_t lock = take_write_lock();
    if (!lock) return atomic_load(&s_write_lock) ? ESP_ERR_TIMEOUT : ESP_ERR_NO_MEM;
    portENTER_CRITICAL(&s_snapshot_lock);
    bool initialized = s_initialized;
    uint32_t revision = s_revision;
    portEXIT_CRITICAL(&s_snapshot_lock);
    esp_err_t result = ESP_ERR_INVALID_STATE;
    if (!initialized || revision == UINT32_MAX) goto done;
    nvs_handle_t handle;
    result = nvs_open("native_network", NVS_READWRITE, &handle);
    if (result != ESP_OK) goto done;
    result = nvs_set_blob(handle, "cfg", record, sizeof(record));
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    if (true) {
        portENTER_CRITICAL(&s_snapshot_lock);
        s_settings = candidate;
        s_revision = revision + 1U;
        portEXIT_CRITICAL(&s_snapshot_lock);
    }
done:
    xSemaphoreGive(lock);
    return result;
}
