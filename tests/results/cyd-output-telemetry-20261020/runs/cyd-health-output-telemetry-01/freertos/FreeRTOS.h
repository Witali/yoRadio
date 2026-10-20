#pragma once
#include <assert.h>
#include <stdint.h>
#include <pthread.h>
typedef pthread_mutex_t portMUX_TYPE;
typedef int BaseType_t;
typedef unsigned UBaseType_t,TickType_t;
#ifdef TEST_COUNTER64
typedef uint64_t configRUN_TIME_COUNTER_TYPE;
#else
typedef uint32_t configRUN_TIME_COUNTER_TYPE;
#endif
#define configNUMBER_OF_CORES 2
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
#define portENTER_CRITICAL_ISR(p) portENTER_CRITICAL(p)
#define portEXIT_CRITICAL_ISR(p) portEXIT_CRITICAL(p)
#define pdPASS 1
#define pdMS_TO_TICKS(x) (x)
BaseType_t xPortGetCoreID(void);
