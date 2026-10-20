#pragma once
#include <stddef.h>
#include <stdint.h>
typedef void *SemaphoreHandle_t;
typedef int BaseType_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
static inline void *xSemaphoreCreateMutex(void) { return (void *)1; }
static inline int xSemaphoreTake(void *p, unsigned t) { (void)t; return !!p; }
static inline void xSemaphoreGive(void *p) { (void)p; }
size_t strlcpy(char *, const char *, size_t);
