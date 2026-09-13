#pragma once
#include <stdint.h>
#ifndef YORADIO_OPUS_FUNCTION_PROFILE
#define YORADIO_OPUS_FUNCTION_PROFILE 0
#endif
#define OPUS_FUNCTION_COUNT 14
#ifdef __cplusplus
extern "C" {
#endif
/* Bounded totals in microseconds; overflow rejects the measurement. Only the
 * raw benchmark audio owner writes. Read rows only after terminal state. */
typedef struct {
    uint32_t calls, cpu_us, self_cpu_us, max_cpu_us;
    uint32_t wall_us, self_wall_us, max_wall_us;
} opus_function_row_t;
typedef struct opus_function_scope {
    struct opus_function_scope *parent;
    uint32_t wall, cpu, child_wall, child_cpu;
    unsigned id, active;
} opus_function_scope_t;
#if YORADIO_OPUS_FUNCTION_PROFILE
void yoradio_opus_function_clock(uint32_t *wall, uint32_t *cpu);
void opus_function_profile_reset(void);
void opus_function_profile_enable(int enabled);
void opus_function_enter(opus_function_scope_t *scope, unsigned id);
void opus_function_leave(opus_function_scope_t *scope);
opus_function_row_t opus_function_profile_row(unsigned id);
uint32_t opus_function_profile_error(void);
uint32_t opus_function_profile_clock_min(void);
uint32_t opus_function_profile_clock_max(void);
#endif
#ifdef __cplusplus
}
#endif
