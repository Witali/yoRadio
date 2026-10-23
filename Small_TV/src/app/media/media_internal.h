#pragma once
#include "esp_partition.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
extern const esp_partition_t *media_partition;
extern SemaphoreHandle_t media_mutex;
esp_err_t media_read_unlocked(uint32_t offset, void *data, size_t length);
esp_err_t media_validate_jpeg_unlocked(uint32_t offset, size_t length, unsigned width, unsigned height);
bool photo_upload_active_unlocked(void);
bool photo_upload_overlaps_unlocked(uint32_t offset,size_t bytes);
