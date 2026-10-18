#pragma once

#include <stdint.h>
#include <sys/time.h>

#include "esp_err.h"

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
// This backend exclusively owns the singleton after binding. The first apply
// rejects an enabled client or any preset name/nonzero IP without changing it.
// External raw/managed SNTP reconfiguration must not run concurrently with or
// after this backend; the initial state check is not an atomic external lease.
esp_err_t native_time_sntp_apply(const native_time_sntp_config_t *config);
esp_err_t native_time_sntp_restart(void);

// There is deliberately no runtime deinit: pending lwIP DNS is not cancelled
// by stopping SNTP. Reconfiguration guarantees name-buffer lifetime, not DNS
// generation cancellation. Pinned assertion-enabled lwIP can abort on UDP PCB
// allocation failure; the public SDK does not expose recoverable start OOM.

#ifdef __cplusplus
}
#endif
