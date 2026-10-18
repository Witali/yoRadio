#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#define NATIVE_TIME_SNTP_SERVER_COUNT 2U
#define NATIVE_TIME_SNTP_NAME_CAPACITY 35U

typedef struct {
    uint16_t sync_interval_minutes;
    uint8_t server_count;
    char servers[NATIVE_TIME_SNTP_SERVER_COUNT][NATIVE_TIME_SNTP_NAME_CAPACITY];
} native_time_sntp_config_t;

typedef void (*native_time_sntp_sync_cb_t)(
    void *context, const struct timeval *synced_time);

// Allocates the controller mutex only; TCP/IP need not exist yet. The callback
// and context remain valid until reboot. Repeated init must use the same pair.
esp_err_t native_time_sntp_init(native_time_sntp_sync_cb_t callback, void *context);

// A station GOT_IP proves TCP/IP is initialized. This atomic latch is safe
// before init and does not mean the station is still connected.
void native_time_sntp_notify_network_ready(void);

// No TCP/IP call occurs before the ready latch. Calls are serialized. Names
// are copied into permanent storage. Equal running configurations are a no-op.
// The caller must separately serialize obtaining and applying its settings.
esp_err_t native_time_sntp_apply(const native_time_sntp_config_t *config);
esp_err_t native_time_sntp_restart(void);

// There is deliberately no runtime deinit: pending lwIP DNS is not cancelled
// by stopping SNTP. Reconfiguration guarantees name-buffer lifetime, not DNS
// generation cancellation. Pinned assertion-enabled lwIP can abort on UDP PCB
// allocation failure; the public SDK does not expose recoverable start OOM.

#ifdef __cplusplus
}
#endif
#pragma once

typedef struct {
    int16_t utc_offset_minutes;
    uint16_t sync_interval_minutes;
    uint8_t server_count;
    char servers[NATIVE_TIME_SNTP_SERVER_COUNT][NATIVE_TIME_SNTP_NAME_CAPACITY];
} time_settings_t;

void time_settings_defaults(time_settings_t *settings);
bool time_settings_valid(const time_settings_t *settings);
esp_err_t time_settings_init(void);
bool time_settings_snapshot(time_settings_t *settings, uint32_t *revision);
esp_err_t time_settings_save(const time_settings_t *settings);
#pragma once

typedef struct {
    bool available;
    bool network_ready;
    bool clock_valid;
    bool synchronized_this_boot;
    time_t utc_epoch;
    struct tm local_time;
    time_t last_sync_epoch;
    int64_t last_sync_age_ms;
    uint32_t desired_revision;
    uint32_t applied_revision;
    esp_err_t last_apply_error;
    time_settings_t settings;
} time_snapshot_t;

esp_err_t time_service_start(void);
esp_err_t time_service_get_settings(time_settings_t *settings);
// Success means persisted desired settings; snapshot reports application.
esp_err_t time_service_save_settings(const time_settings_t *settings);
void time_service_notify_network(bool has_station_ip);
bool time_service_snapshot(time_snapshot_t *snapshot);
