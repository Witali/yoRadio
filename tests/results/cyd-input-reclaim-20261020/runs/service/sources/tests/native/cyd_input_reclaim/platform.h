#pragma once
#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#include <pthread.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define CHECK(condition,marker) do { if (!(condition)) { \
    fprintf(stderr,"SEMANTIC_FAILURE:%s:%u\n",marker,__LINE__); exit(80); \
} } while(0)
typedef int BaseType_t;
typedef uint32_t TickType_t;
typedef pthread_mutex_t portMUX_TYPE;
typedef struct test_semaphore *SemaphoreHandle_t;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(lock) test_enter_critical(lock)
#define portEXIT_CRITICAL(lock) test_exit_critical(lock)
#define pdTRUE 1
#define pdFALSE 0
#define portMAX_DELAY UINT32_MAX
void test_enter_critical(portMUX_TYPE *lock);
void test_exit_critical(portMUX_TYPE *lock);
BaseType_t xPortInIsrContext(void);
SemaphoreHandle_t xSemaphoreCreateBinary(void);
void vSemaphoreDelete(SemaphoreHandle_t semaphore);
BaseType_t xSemaphoreGive(SemaphoreHandle_t semaphore);
BaseType_t xSemaphoreTake(SemaphoreHandle_t semaphore,TickType_t timeout);
TickType_t xTaskGetTickCount(void);
void *cyd_test_malloc(size_t bytes);
void *cyd_test_calloc(size_t count,size_t size);
void cyd_test_free(void *pointer);
