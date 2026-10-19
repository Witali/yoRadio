#pragma once

#include "esp_err.h"

// Apply one checked saved-settings snapshot. Offline success applies TZ and
// defers SNTP until the first station GOT_IP; online success is checked backend
// configuration, not proof of clock synchronization. Snapshot failure changes
// neither TZ nor SNTP. SDK TCP/IP calls have no bounded-wait contract.
esp_err_t time_service_apply(void);
// Event-loop safe: latch TCP/IP readiness and notify; no DNS/NVS/control wait.
void time_service_notify_network_ready(void);
