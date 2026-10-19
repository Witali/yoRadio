#pragma once

#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"

typedef enum {
    NETWORK_WAIT_START, NETWORK_WAIT_DISCONNECT, NETWORK_RETRY_WAIT,
    NETWORK_CONNECTING, NETWORK_ONLINE, NETWORK_AP_IDLE,
} network_phase_t;

#define NETWORK_NO_PROFILE UINT8_MAX

typedef struct {
    network_phase_t phase;
    uint32_t epoch, event_overflows;
    uint8_t profile_count, profile_index, target_profile, attempt, profiles_tried;
    bool online, ap_enabled, rssi_valid, reconciling;
    int8_t rssi;
    uint16_t disconnect_reason;
    uint32_t ipv4;
    esp_err_t last_error;
    uint64_t updated_us, rssi_updated_us, rssi_age_ms;
} network_snapshot_t;

// Authoritative bounded non-secret view; unchanged output on failure.
esp_err_t network_service_snapshot(network_snapshot_t *out, uint32_t timeout_ms);
