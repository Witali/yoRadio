#pragma once
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
typedef int esp_err_t;
enum {ESP_OK=0,ESP_FAIL=-1,ESP_ERR_INVALID_ARG=-2,ESP_ERR_INVALID_STATE=-3,
      ESP_ERR_TIMEOUT=-4,ESP_ERR_NO_MEM=-5,ESP_ERR_NVS_NOT_FOUND=-6};
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef uint32_t TickType_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define configTICK_RATE_HZ 1000U
#define portMAX_DELAY UINT32_MAX
#define NVS_READWRITE 1
typedef unsigned nvs_handle_t;
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_RETURN_ON_ERROR(expr,...) do {esp_err_t e=(expr);if(e!=ESP_OK)return e;} while(0)
#define ESP_RETURN_ON_FALSE(expr,error,...) do {if(!(expr))return(error);} while(0)
static SemaphoreHandle_t xSemaphoreCreateMutex(void);
static int xSemaphoreTake(SemaphoreHandle_t,TickType_t);
static void xSemaphoreGive(SemaphoreHandle_t);
static size_t strlcpy(char *,const char *,size_t);
static esp_err_t nvs_open(const char *,int,nvs_handle_t *);
static void nvs_close(nvs_handle_t);
static esp_err_t nvs_commit(nvs_handle_t);
static esp_err_t nvs_get_u8(nvs_handle_t,const char *,uint8_t *);
static esp_err_t nvs_get_i8(nvs_handle_t,const char *,int8_t *);
static esp_err_t nvs_get_u16(nvs_handle_t,const char *,uint16_t *);
static esp_err_t nvs_get_str(nvs_handle_t,const char *,char *,size_t *);
static esp_err_t nvs_set_u8(nvs_handle_t,const char *,uint8_t);
static esp_err_t nvs_set_i8(nvs_handle_t,const char *,int8_t);
static esp_err_t nvs_set_u16(nvs_handle_t,const char *,uint16_t);
static esp_err_t nvs_set_str(nvs_handle_t,const char *,const char *);
#include "runtime_settings.h"
