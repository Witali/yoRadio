#pragma once

#include "esp_err.h"
#include "sdkconfig.h"

// Starts runtime diagnostics when enabled; the default profiler uses a task,
// while HTTP sampling mode relies on status requests. Production is a no-op.
esp_err_t cpu_profiler_start(void);

// Diagnostic mode: sample from the existing HTTP task, without a profiler stack.
// Only the single HTTP server task may call this entry point.
#ifdef CONFIG_YORADIO_CPU_PROFILE_HTTP
void cpu_profiler_poll(void);
#else
static inline void cpu_profiler_poll(void) {}
#endif

#if CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS
void cpu_profiler_memory(const char *stage);
#else
static inline void cpu_profiler_memory(const char *stage) { (void)stage; }
#endif
