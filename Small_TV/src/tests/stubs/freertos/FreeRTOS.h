#pragma once
#include <assert.h>
#include <stdint.h>
#define portMAX_DELAY UINT32_MAX
#define pdPASS 1
#define pdMS_TO_TICKS(ms) (ms)
#define configASSERT(value) assert(value)
