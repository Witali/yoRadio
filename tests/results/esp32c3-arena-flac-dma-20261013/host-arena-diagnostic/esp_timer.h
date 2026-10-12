#pragma once
#include <stdint.h>
// Synthetic increments verify bookkeeping only, not target latency.
static inline int64_t esp_timer_get_time(void) { static int64_t tick; return ++tick; }
