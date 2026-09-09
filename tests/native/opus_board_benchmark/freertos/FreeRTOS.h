#pragma once
#include <stdint.h>
#define configGENERATE_RUN_TIME_STATS 1
#define configUSE_TRACE_FACILITY 1
#define CONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER 1
#define pdFALSE 0
typedef unsigned UBaseType_t;
void test_enter_critical(void);
void test_exit_critical(void);
#define taskENTER_CRITICAL() test_enter_critical()
#define taskEXIT_CRITICAL() test_exit_critical()
