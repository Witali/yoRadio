#pragma once
#include <pthread.h>
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
void host_enter_critical(portMUX_TYPE *, unsigned);
void host_exit_critical(portMUX_TYPE *, unsigned);
#define portENTER_CRITICAL_ISR(lock) host_enter_critical((lock), 1)
#define portEXIT_CRITICAL_ISR(lock) host_exit_critical((lock), 1)
#define portENTER_CRITICAL(lock) host_enter_critical((lock), 0)
#define portEXIT_CRITICAL(lock) host_exit_critical((lock), 0)
