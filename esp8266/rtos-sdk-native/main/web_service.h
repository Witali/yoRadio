#pragma once

#include "esp_err.h"

esp_err_t web_service_start(void);
void web_service_poll(void);
void web_service_notify_playlist_changed(void);
