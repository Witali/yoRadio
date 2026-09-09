#pragma once
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
    uint32_t packets, samples, wall_us, task_us, max_wall_us, pcm_hash;
    uint32_t scratch_bytes, scratch_words, min_dram, stack_free;
    int error;
} opus_benchmark_case_t;
typedef struct {
    uint32_t run, state, current_case, round, cases, rounds;
    uint32_t dram_before, dram_after, state_bytes, empty_task_us;
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
