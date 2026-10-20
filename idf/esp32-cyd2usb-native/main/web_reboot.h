#pragma once

#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"

// Start during sequential web startup, before activating upload routes. The
// unpinned task and its 2048-byte stack are allocated before any file commit.
esp_err_t web_reboot_start(void);
bool web_reboot_ready(void);

// Requests need no allocation. The earliest pending deadline is retained;
// delays are capped at one minute and tolerate the 32-bit tick wrap.
void web_reboot_request(unsigned delay_ms);

// Zero-initialize a lease. Reservation atomically rejects an unavailable task,
// any pending reboot, or another owner. Ordinary requests during a lease are
// deferred; they cannot restart the board until cancel/commit consumes it.
typedef struct { uint64_t epoch; } web_reboot_lease_t;
esp_err_t web_reboot_reserve(web_reboot_lease_t *lease);
esp_err_t web_reboot_cancel(web_reboot_lease_t *lease);
// Call after OTA activation and the response attempt, even if sending failed.
// A valid reservation pins the preallocated reboot service; no allocation here.
esp_err_t web_reboot_commit(web_reboot_lease_t *lease, unsigned delay_ms);

// The exclusive lease owner may restart immediately after its final eligibility
// check. The lease must not be copied, cancelled or committed concurrently.
// The reservation stays active through esp_restart(), called outside the lock;
// ordinary pending requests and other reservations remain blocked. A successful
// real restart never returns. If a test restart double returns, return ESP_OK
// with the lease still reserved; the caller still owns that same lease.
esp_err_t web_reboot_restart_reserved_now(web_reboot_lease_t *lease);

// Startup rollback only, while upload routes are inactive. A pending reboot
// cannot be cancelled after credentials were committed.
esp_err_t web_reboot_abort(void);
