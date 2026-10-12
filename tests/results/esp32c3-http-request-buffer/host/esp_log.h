#pragma once
#include <stdio.h>
#include "esp_err.h"
#define unlikely(x) (x)
#define ESP_LOGD(tag,...) do { (void)(tag); if(0)printf(__VA_ARGS__); } while(0)
#define ESP_LOGE ESP_LOGD
#define ESP_LOGW ESP_LOGD
