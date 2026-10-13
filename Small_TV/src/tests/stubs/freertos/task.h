#pragma once
#include <stdint.h>
typedef void *TaskHandle_t;
int xTaskCreate(void (*task)(void *), const char *name, unsigned stack, void *argument,
                unsigned priority, void *handle);
void vTaskDelay(unsigned ticks);
void vTaskDelete(TaskHandle_t task);
void xTaskNotifyGive(TaskHandle_t task);
uint32_t ulTaskNotifyTake(int clear, unsigned ticks);
