#pragma once
#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(value, marker) do { if (!(value)) { \
    fprintf(stderr, "SEMANTIC_FAILURE:%s:%u\n", marker, __LINE__); exit(80); \
} } while (0)
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_TIMEOUT 0x107
#define IRAM_ATTR
#define DRAM_ATTR
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
extern _Thread_local unsigned critical_depth;
extern _Thread_local bool in_isr;
static inline void enter(portMUX_TYPE *lock, bool isr) {
    CHECK(isr == in_isr && !critical_depth, "correct_critical_context");
    CHECK(!pthread_mutex_lock(lock), "lock_enter"); ++critical_depth;
}
static inline void leave(portMUX_TYPE *lock, bool isr) {
    CHECK(isr == in_isr && critical_depth == 1, "balanced_critical_context");
    --critical_depth; CHECK(!pthread_mutex_unlock(lock), "lock_leave");
}
#define portENTER_CRITICAL(lock) enter(lock, false)
#define portEXIT_CRITICAL(lock) leave(lock, false)
#define portENTER_CRITICAL_ISR(lock) enter(lock, true)
#define portEXIT_CRITICAL_ISR(lock) leave(lock, true)
int64_t esp_timer_get_time(void);
