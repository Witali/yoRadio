#pragma once
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
#define ESP_PARTITION_TYPE_DATA 1
typedef struct {uint32_t address,size;} esp_partition_t;
const esp_partition_t *esp_partition_find_first(unsigned type,unsigned subtype,const char *label);
esp_err_t esp_partition_read(const esp_partition_t *partition,size_t offset,void *data,size_t length);
esp_err_t esp_partition_write(const esp_partition_t *partition,size_t offset,const void *data,size_t length);
esp_err_t esp_partition_erase_range(const esp_partition_t *partition,size_t offset,size_t length);
