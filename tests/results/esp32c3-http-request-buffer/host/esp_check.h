#pragma once
#include "esp_log.h"
#define ESP_RETURN_ON_FALSE(x,code,tag,...) do { (void)(tag);if(!(x))return(code); } while(0)
