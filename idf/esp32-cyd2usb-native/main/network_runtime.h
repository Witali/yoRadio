#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"
#include "esp_netif.h"
#include "native_state.h"
#include "network_profiles.h"

#include "network_status.h"

// Driver/netif are initialized in STA/RAM mode, but Wi-Fi has not started.
// Copies the immutable active boot table. Does not read desired storage again.
esp_err_t network_runtime_start(native_state_t *state, esp_netif_t *station,
                                const network_profiles_t *profiles);
// Startup's UI budget only; the permanent owner continues after a timeout.
esp_err_t network_runtime_wait_initial(uint32_t timeout_ms);
// Admission only. One manual cycle, including its pending mailbox, at a time.
// Never calls a driver API or waits for association.
esp_err_t network_runtime_retry(void);
// Output is unchanged on failure. Pending link notices mask old IP/RSSI.
esp_err_t network_runtime_snapshot(network_snapshot_t *out, uint32_t timeout_ms);
// Startup rollback: caller has stopped the driver. On failure resources stay
// retained until a subsequent cleanup succeeds, never freed under a callback.
// timeout_ms bounds local reference/task waits. SDK unregister is synchronous
// and may wait on the event loop's own mutex before those waits can complete.
esp_err_t network_runtime_stop(uint32_t timeout_ms);
