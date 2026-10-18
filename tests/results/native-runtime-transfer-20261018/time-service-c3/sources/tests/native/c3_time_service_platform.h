#pragma once
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
typedef int esp_err_t;
enum {ESP_OK=0,ESP_FAIL=-1,ESP_ERR_NO_MEM=-2,ESP_ERR_INVALID_ARG=-3,
      ESP_ERR_INVALID_STATE=-4,ESP_ERR_TIMEOUT=-5};
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef struct host_task *TaskHandle_t;
typedef unsigned TickType_t;
#define pdTRUE 1
#define pdPASS 1
#define eSetBits 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
#define BOARD_TASK_STACK_TIME_SYNC 2048U
static SemaphoreHandle_t xSemaphoreCreateMutex(void);
static int xSemaphoreTake(SemaphoreHandle_t,unsigned);
static void xSemaphoreGive(SemaphoreHandle_t);
static void vSemaphoreDelete(SemaphoreHandle_t);
static int xTaskCreate(void(*)(void*),const char *,unsigned,void *,unsigned,TaskHandle_t *);
static int xTaskNotify(TaskHandle_t,uint32_t,unsigned);
static int xTaskNotifyWait(uint32_t,uint32_t,uint32_t *,unsigned);
static size_t strlcpy(char *,const char *,size_t);
static const char *esp_err_to_name(int e){(void)e;return "host error";}
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#include "runtime_settings.h"
#include "native_time_sntp.h"
#include "time_service.h"
