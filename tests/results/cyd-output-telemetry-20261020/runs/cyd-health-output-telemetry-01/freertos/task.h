#pragma once
#include "FreeRTOS.h"
typedef void *TaskHandle_t;
typedef struct { TaskHandle_t xHandle;const char *pcTaskName;UBaseType_t xTaskNumber;
    configRUN_TIME_COUNTER_TYPE ulRunTimeCounter;uint32_t usStackHighWaterMark; } TaskStatus_t;
UBaseType_t uxTaskGetSystemState(TaskStatus_t *,UBaseType_t,configRUN_TIME_COUNTER_TYPE *);
TaskHandle_t xTaskGetIdleTaskHandleForCore(BaseType_t);
BaseType_t xTaskCreatePinnedToCore(void (*)(void *),const char *,unsigned,void *,unsigned,TaskHandle_t *,BaseType_t);
void vTaskDelay(TickType_t);
