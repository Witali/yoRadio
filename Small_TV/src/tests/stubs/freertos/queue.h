#pragma once
#include <stddef.h>
typedef void *QueueHandle_t;
QueueHandle_t xQueueCreate(unsigned count,unsigned bytes);
int xQueueSend(QueueHandle_t queue,const void *item,unsigned ticks);
int xQueueReceive(QueueHandle_t queue,void *item,unsigned ticks);
