#pragma once

#include "esp_err.h"

// Starts a low-priority interval profiler when FreeRTOS run-time statistics
// are enabled. In normal production builds this is a zero-cost no-op.
esp_err_t cpu_profiler_start(void);
