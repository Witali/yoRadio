#pragma once
#include <stdbool.h>
#include <stdint.h>
#ifndef YORADIO_OPUS_PROFILE_STAGE
#define YORADIO_OPUS_PROFILE_STAGE 0
#endif
#ifndef YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
#define YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT 0
#endif

#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
    uint32_t packets, samples, wall_us, task_us, max_wall_us, pcm_hash;
    uint32_t scratch_bytes, scratch_words, min_dram, stack_free;
#if YORADIO_OPUS_PROFILE_STAGE
    uint64_t stage_ticks;
    uint32_t stage_calls, stage_max_ticks;
#endif
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
    uint32_t output_wall_us, max_output_us, output_samples;
    uint32_t pipeline_wall_us, pipeline_task_us, dma_eofs, dma_misses;
    uint32_t fifo_empty_seen;
#endif
    int error;
} opus_benchmark_case_t;
typedef struct {
    uint32_t run, state, current_case, round, cases, rounds;
    uint32_t dram_before, dram_after, state_bytes, empty_task_us;
#if YORADIO_OPUS_PROFILE_STAGE
    uint32_t clock_pair_ticks_min, clock_pair_ticks_max;
#endif
    int error;
} opus_benchmark_status_t;

#if YORADIO_ESP8266_OPUS_BENCHMARK
/* A POST queues a stop; only the audio owner executes the benchmark. */
bool opus_benchmark_request(void);
void opus_benchmark_cancel_pending(void);
void opus_benchmark_run_pending(uint32_t generation,
                               bool (*current)(uint32_t));
void opus_benchmark_snapshot(opus_benchmark_status_t *status);
void opus_benchmark_case_snapshot(unsigned index, opus_benchmark_case_t *result);
#else
static inline void opus_benchmark_cancel_pending(void) {}
static inline void opus_benchmark_run_pending(uint32_t generation,
                                             bool (*current)(uint32_t)) {
    (void)generation; (void)current;
}
#endif
#ifdef __cplusplus
}
#endif
