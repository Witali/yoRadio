#pragma once
#include <stddef.h>
#include <stdint.h>
typedef void *RingbufHandle_t;
typedef uint32_t TickType_t;
typedef int BaseType_t;
#define pdTRUE 1
void *xRingbufferReceive(RingbufHandle_t, size_t *, TickType_t);
BaseType_t xRingbufferSendAcquire(RingbufHandle_t, void **, size_t, TickType_t);
