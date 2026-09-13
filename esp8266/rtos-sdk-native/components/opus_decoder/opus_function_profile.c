#include "opus_function_profile.h"
#if YORADIO_OPUS_FUNCTION_PROFILE
#include <string.h>
#include <limits.h>
static opus_function_row_t rows[OPUS_FUNCTION_COUNT];
static opus_function_scope_t *top;
static unsigned enabled, failure;
static uint32_t clock_min, clock_max;
static void add(uint32_t *total, uint32_t value) {
    if (value > UINT32_MAX - *total) { failure |= 1; return; }
    *total += value;
}
void opus_function_profile_reset(void) {
    memset(rows, 0, sizeof(rows)); top = 0; enabled = failure = 0;
    clock_min = UINT32_MAX; clock_max = 0;
    for (unsigned i = 0; i < 32; ++i) {
        uint32_t w0, c0, w1, c1;
        yoradio_opus_function_clock(&w0, &c0);
        yoradio_opus_function_clock(&w1, &c1);
        uint32_t cost = c1 - c0;
        if (cost < clock_min) clock_min = cost;
        if (cost > clock_max) clock_max = cost;
    }
}
void opus_function_profile_enable(int value) {
    if (top) { failure |= 2; top = 0; } /* Includes unwound OOM scopes. */
    enabled = !!value;
}
void opus_function_enter(opus_function_scope_t *s, unsigned id) {
    s->active = enabled && id < OPUS_FUNCTION_COUNT;
    if (!s->active) return;
    s->id = id; s->parent = top; s->child_wall = s->child_cpu = 0;
    top = s;
    yoradio_opus_function_clock(&s->wall, &s->cpu);
}
void opus_function_leave(opus_function_scope_t *s) {
    if (!s->active) return;
    uint32_t wall, cpu;
    yoradio_opus_function_clock(&wall, &cpu);
    /* A bounded decoder longjmp can skip inner wrappers. Never dereference
     * their expired stack scopes; invalidate the profile instead. */
    if (top != s) { failure |= 2; top = 0; return; }
    wall -= s->wall; cpu -= s->cpu; top = s->parent;
    if (s->child_wall > wall || s->child_cpu > cpu || cpu > wall + 2U) {
        failure |= 4; return;
    }
    opus_function_row_t *r = &rows[s->id];
    add(&r->calls, 1); add(&r->cpu_us, cpu); add(&r->wall_us, wall);
    add(&r->self_cpu_us, cpu - s->child_cpu);
    add(&r->self_wall_us, wall - s->child_wall);
    if (cpu > r->max_cpu_us) r->max_cpu_us = cpu;
    if (wall > r->max_wall_us) r->max_wall_us = wall;
    if (top) { add(&top->child_cpu, cpu); add(&top->child_wall, wall); }
}
opus_function_row_t opus_function_profile_row(unsigned id) {
    opus_function_row_t zero = {0}; return id < OPUS_FUNCTION_COUNT ? rows[id] : zero;
}
uint32_t opus_function_profile_error(void) { return failure; }
uint32_t opus_function_profile_clock_min(void) { return clock_min; }
uint32_t opus_function_profile_clock_max(void) { return clock_max; }
#endif
