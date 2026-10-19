#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

typedef enum {
    NATIVE_HEALTH_STREAM = 0,
    NATIVE_HEALTH_DECODE,
    NATIVE_HEALTH_OUTPUT,
    NATIVE_HEALTH_HTTP,
    NATIVE_HEALTH_TASKS,
} native_health_task_t;

typedef enum {
    NATIVE_HEALTH_OPEN = 1,
    NATIVE_HEALTH_PROCESS,
    NATIVE_HEALTH_PCM,
    NATIVE_HEALTH_INFO,
} native_health_decoder_stage_t;

typedef enum {
    NATIVE_HEALTH_OUTPUT_CONFIGURE = 1,
    NATIVE_HEALTH_OUTPUT_WRITE,
    NATIVE_HEALTH_OUTPUT_FLUSH,
} native_health_output_stage_t;

typedef struct {
    uint32_t allocation_failures, allocation_size, allocation_caps;
    uint32_t decoder_failures, decoder_generation, decoder_codec, decoder_stage;
    int32_t decoder_result;
    uint32_t decoder_completion, decoder_input_bytes, decoder_allocation_sequence;
    uint32_t stream_failures, stream_generation, stream_completion;
    int32_t stream_result;
    uint32_t output_failures, output_generation, output_stage;
    uint32_t output_write_errors, output_configure_errors, output_flush_errors;
    int32_t output_result;
} native_health_faults_t;

typedef struct {
    bool present;
    bool available;
    uint16_t percent_tenths; // Percentage of one core's capacity, 0..1000.
    uint32_t stack_free_min; // Bytes, copied by the SDK's task snapshot.
} native_health_task_cpu_t;

typedef struct {
    bool enabled, available;
    uint16_t overall_tenths, core_tenths[2];
    uint32_t snapshot_failures;
    uint64_t sampled_us;
    native_health_task_cpu_t task[NATIVE_HEALTH_TASKS];
} native_health_cpu_t;

typedef struct {
    native_health_faults_t faults;
    native_health_cpu_t cpu;
} native_health_snapshot_t;

typedef struct {
    bool available, leased;
    uint32_t resident, minimum, target, limit, ready, reading, writing, released;
    uint32_t ready_payload_bytes, reading_payload_bytes;
} native_input_health_t;

typedef struct {
    uint64_t boot_id, uptime_ms;
    uint32_t reset_reason, heap_free, heap_largest, heap_minimum, tasks, cores;
    uint32_t internal_free, internal_largest, dma_free, dma_largest;
    native_input_health_t input;
} native_health_runtime_t;

bool native_health_format_json(char *body, size_t capacity,
    const native_health_snapshot_t *snapshot, const native_health_runtime_t *runtime);

// Bootstrap once. Quiet builds register only the allocation-failure callback.
// Optional diagnostic sampling adds a task, RTOS stats and occasional IPC.
bool native_health_start(void);
void native_health_track_task(native_health_task_t role, void *handle);
void native_health_decoder_failure(uint32_t generation, uint32_t codec,
    native_health_decoder_stage_t stage, int32_t result, uint32_t completion,
    uint32_t input_bytes);
void native_health_stream_failure(uint32_t generation, uint32_t completion, int32_t result);
void native_health_output_failure(uint32_t generation, native_health_output_stage_t stage, int32_t result);
native_health_snapshot_t native_health_snapshot(void);
