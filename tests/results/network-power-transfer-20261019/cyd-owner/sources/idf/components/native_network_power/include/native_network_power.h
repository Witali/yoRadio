#pragma once

#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"

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
