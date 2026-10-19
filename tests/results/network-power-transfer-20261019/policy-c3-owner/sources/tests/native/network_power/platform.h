#pragma once
#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <limits.h>

#define CHECK(condition, marker) do { if (!(condition)) { \
    fprintf(stderr, "SEMANTIC_FAILURE:%s:%u\n", marker, __LINE__); exit(80); \
} } while (0)
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(lock) CHECK(!pthread_mutex_lock(lock), "critical_enter")
#define portEXIT_CRITICAL(lock) CHECK(!pthread_mutex_unlock(lock), "critical_leave")
#define pdMS_TO_TICKS(ms) (ms)
