#pragma once
#include <stdint.h>
#include "esp_err.h"
esp_err_t esp_ipc_call_blocking(uint32_t,void (*)(void *),void *);
