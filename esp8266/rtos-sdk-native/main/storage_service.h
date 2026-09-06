#pragma once

#include "esp_err.h"

#define STORAGE_ROOT "/spiffs"
#define STORAGE_DATA_DIR STORAGE_ROOT "/data"
#define STORAGE_WEB_DIR STORAGE_ROOT "/www"

esp_err_t storage_service_init(void);
