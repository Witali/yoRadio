#pragma once

#include <stdbool.h>
#include "esp_err.h"

// Start during sequential web startup, before activating upload routes. The
// unpinned task and its 2048-byte stack are allocated before any file commit.
esp_err_t web_reboot_start(void);
bool web_reboot_ready(void);

// Requests need no allocation. The earliest pending deadline is retained;
// delays are capped at one minute and tolerate the 32-bit tick wrap.
void web_reboot_request(unsigned delay_ms);

// Startup rollback only, while upload routes are inactive. A pending reboot
// cannot be cancelled after credentials were committed.
esp_err_t web_reboot_abort(void);
