#pragma once
#include "FreeRTOS.h"
typedef void *TaskHandle_t;
typedef enum { eRunning } eTaskState;
typedef struct { uint32_t ulRunTimeCounter; } TaskStatus_t;
void vTaskGetInfo(TaskHandle_t task, TaskStatus_t *status, int stack, eTaskState state);
void vTaskDelay(unsigned ticks);
UBaseType_t uxTaskGetStackHighWaterMark(TaskHandle_t task);
