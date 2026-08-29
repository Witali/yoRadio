#pragma once

#include "esp_err.h"

esp_err_t audio_service_init(void);
esp_err_t audio_service_play(const char *url);
esp_err_t audio_service_stop(void);
