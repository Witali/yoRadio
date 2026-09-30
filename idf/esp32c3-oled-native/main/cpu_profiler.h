#pragma once

#include "esp_err.h"
#include "sdkconfig.h"

// Starts a low-priority interval profiler when FreeRTOS run-time statistics
// are enabled. In normal production builds this is a zero-cost no-op.
esp_err_t cpu_profiler_start(void);

#if CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS
void cpu_profiler_memory(const char *stage);
#else
static inline void cpu_profiler_memory(const char *stage) { (void)stage; }
#endif
