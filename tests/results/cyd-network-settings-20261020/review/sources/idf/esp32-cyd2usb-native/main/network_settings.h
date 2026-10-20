#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

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
