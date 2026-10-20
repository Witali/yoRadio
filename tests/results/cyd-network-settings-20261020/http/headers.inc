#include <inttypes.h>
#pragma once

#define NETWORK_SETTINGS_HOSTNAME_CAPACITY 24U
#define NETWORK_SETTINGS_AP_TIMEOUT_MAX_MINUTES 30U

typedef struct {
    char hostname[NETWORK_SETTINGS_HOSTNAME_CAPACITY];
    uint8_t ap_timeout_minutes;
} network_settings_t;

// Desired task-context settings only: these APIs do not change a netif, arm a
// timer or request reboot. Default hostname is yoradio and AP timeout is zero.
void network_settings_defaults(network_settings_t *settings);
// One nonempty ASCII hostname label, 1-23 bytes: letters/digits and internal
// hyphens. Case is preserved; dots, whitespace and non-ASCII are rejected.
bool network_settings_valid(const network_settings_t *settings);
esp_err_t network_settings_init(void);
// Coherent committed RAM copy. Before successful init, false leaves both
// outputs unchanged. Revision is optional, starts at one and is boot-local.
bool network_settings_snapshot(network_settings_t *settings, uint32_t *revision);
// Owns a canonical candidate before waiting for its 100 ms writer admission.
// Only successful NVS commit publishes settings/revision. No allocation or
// fallible lock acquisition remains between commit and RAM publication.
esp_err_t network_settings_save(const network_settings_t *settings);
#pragma once

typedef struct {
    uint32_t generation, desired_revision, applied_revision;
    bool desired_active, applied_active, applied_valid;
    uint8_t attempts;
    esp_err_t last_error;
} native_network_power_snapshot_t;

// Audio control establishes generations while holding its command lock.
// These intent APIs never call Wi-Fi, allocate, wait on a task or reject Play.
void native_network_power_accept(uint32_t generation, bool active);
// Receive attempts/backoff/EOF may update ONLY the current accepted generation.
// A delayed begin or finish cannot establish an old generation again.
void native_network_power_receive(uint32_t generation);
void native_network_power_finish(uint32_t generation);
// New driver lifetime: preserve desired audio intent, forget applied policy.
void native_network_power_invalidate(void);
void native_network_power_snapshot(native_network_power_snapshot_t *out);

typedef esp_err_t (*native_network_power_apply_t)(void *context, bool active);
// Exactly one permanent network task calls poll. Driver calls run outside the
// short intent critical section; the next poll reconciles a concurrent command.
// At most three attempts per desired revision, with 250 ms between failures.
void native_network_power_poll(int64_t now_us, native_network_power_apply_t apply,
                               void *context);
#pragma once

typedef enum {
    NETWORK_WAIT_START, NETWORK_WAIT_DISCONNECT, NETWORK_RETRY_WAIT,
    NETWORK_CONNECTING, NETWORK_ONLINE, NETWORK_AP_IDLE,
} network_phase_t;

#define NETWORK_NO_PROFILE UINT8_MAX

typedef struct {
    network_settings_t desired;
    uint32_t desired_revision;
    bool available;
    // Last successful netif configuration, not DHCP server acceptance or mDNS.
    char configured_hostname[NETWORK_SETTINGS_HOSTNAME_CAPACITY];
    bool hostname_valid;
    uint32_t hostname_revision;
    esp_err_t hostname_error;
    bool ap_timeout_armed;
    uint64_t ap_timeout_remaining_ms;
} network_settings_runtime_t;

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
    native_network_power_snapshot_t power;
    network_settings_runtime_t settings;
} network_snapshot_t;

// Authoritative bounded non-secret view; unchanged output on failure.
esp_err_t network_service_snapshot(network_snapshot_t *out, uint32_t timeout_ms);
