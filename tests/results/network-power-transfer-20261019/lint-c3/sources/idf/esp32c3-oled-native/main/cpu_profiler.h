#pragma once

#include <stdint.h>

#include "esp_err.h"
#include "sdkconfig.h"

// Registers the allocation-failure counter in every build. Starts the optional
// profiler task or HTTP sampling only when runtime profiling is enabled.
esp_err_t cpu_profiler_start(void);

typedef struct {
    uint32_t allocation_failures;
    uint32_t task_watchdog_events;
    uint32_t allocation_size;
    uint32_t allocation_caps;
    uint32_t decoder_failures;
    uint32_t decoder_codec;
    uint32_t decoder_stage;
    int32_t decoder_result;
    uint32_t decoder_completion;
    uint32_t decoder_input_bytes;
    uint32_t decoder_allocation_sequence;
} cpu_profiler_faults_t;

typedef enum {
    DECODER_FAILURE_OPEN = 1,
    DECODER_FAILURE_PROCESS,
    DECODER_FAILURE_PCM,
} decoder_failure_stage_t;

// Retain only numbers, never input data or pointers. Call on fatal decoder
// errors before cleanup; completion is the original audio_completion marker.
void cpu_profiler_decoder_failure(uint32_t codec, decoder_failure_stage_t stage,
                                  int32_t result, uint32_t completion,
                                  uint32_t input_bytes);

// Lifetime counters, including quiet builds; no sampling or reset side effects.
cpu_profiler_faults_t cpu_profiler_faults(void);

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
