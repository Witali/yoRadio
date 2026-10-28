#pragma once
#include <assert.h>
#include <stdint.h>
#define portMAX_DELAY UINT32_MAX
#define pdPASS 1
#define pdTRUE 1
#define configUSE_TIME_SLICING 1
#define tskIDLE_PRIORITY 0
#define DMA_ATTR
#define pdMS_TO_TICKS(ms) (ms)
#define configASSERT(value) assert(value)
typedef volatile long portMUX_TYPE;
void native_port_enter(portMUX_TYPE *lock);
void native_port_exit(portMUX_TYPE *lock);
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(lock)                                                                   \
    do                                                                                             \
    {                                                                                              \
        native_port_enter(lock);                                                                   \
    } while (0)
#define portEXIT_CRITICAL(lock)                                                                    \
    do                                                                                             \
    {                                                                                              \
        native_port_exit(lock);                                                                    \
    } while (0)
#define portENTER_CRITICAL_ISR(lock) portENTER_CRITICAL(lock)
#define portEXIT_CRITICAL_ISR(lock) portEXIT_CRITICAL(lock)
