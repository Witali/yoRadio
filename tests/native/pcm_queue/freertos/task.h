#pragma once
#include "FreeRTOS.h"
int xTaskCreate(void (*entry)(void *), const char *name, unsigned stack,
                void *arg, unsigned priority, TaskHandle_t *task);
void xTaskNotifyGive(TaskHandle_t task);
uint32_t ulTaskNotifyTake(int clear, TickType_t ticks);
TaskHandle_t xTaskGetCurrentTaskHandle(void);
unsigned uxTaskGetStackHighWaterMark(TaskHandle_t task);
void vTaskDelete(TaskHandle_t task);
