#pragma once
#include <assert.h>
#include <stdint.h>
#define portMAX_DELAY UINT32_MAX
#define pdPASS 1
#define pdTRUE 1
#define DMA_ATTR
#define pdMS_TO_TICKS(ms) (ms)
#define configASSERT(value) assert(value)
typedef unsigned portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(lock)                                                                   \
    do                                                                                             \
    {                                                                                              \
        assert(*(lock) == 0);                                                                      \
        *(lock) = 1;                                                                               \
    } while (0)
#define portEXIT_CRITICAL(lock)                                                                    \
    do                                                                                             \
    {                                                                                              \
        assert(*(lock) == 1);                                                                      \
        *(lock) = 0;                                                                               \
    } while (0)
#define portENTER_CRITICAL_ISR(lock) portENTER_CRITICAL(lock)
#define portEXIT_CRITICAL_ISR(lock) portEXIT_CRITICAL(lock)
