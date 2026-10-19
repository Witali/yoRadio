#pragma once
#include <stddef.h>
#include <stdint.h>
#include <assert.h>
#include <pthread.h>
#include <stdlib.h>
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef int BaseType_t;
typedef unsigned TickType_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
static inline SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    SemaphoreHandle_t p=malloc(sizeof(*p)); assert(p);
    assert(!pthread_mutex_init(p,NULL)); return p;
}
static inline int xSemaphoreTake(SemaphoreHandle_t p, unsigned t) {
    (void)t; assert(!pthread_mutex_lock(p)); return 1;
}
static inline void xSemaphoreGive(SemaphoreHandle_t p) { assert(!pthread_mutex_unlock(p)); }
size_t strlcpy(char *, const char *, size_t);
