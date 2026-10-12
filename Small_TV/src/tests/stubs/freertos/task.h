#pragma once
int xTaskCreate(void (*task)(void *),const char *name,unsigned stack,void *argument,unsigned priority,void *handle);
void vTaskDelay(unsigned ticks);
