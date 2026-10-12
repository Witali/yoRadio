#pragma once
#include <pthread.h>
#include <stdbool.h>
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) pthread_mutex_lock(p)
#define portEXIT_CRITICAL(p) pthread_mutex_unlock(p)
extern _Thread_local bool test_isr;
static inline bool xPortInIsrContext(void) { return test_isr; }
