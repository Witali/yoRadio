#pragma once
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
typedef void esp_flash_t;
esp_err_t esp_flash_read(esp_flash_t *chip, void *data, uint32_t offset, uint32_t length);
esp_err_t esp_flash_write(esp_flash_t *chip, const void *data, uint32_t offset, uint32_t length);
esp_err_t esp_flash_erase_region(esp_flash_t *chip, uint32_t offset, uint32_t length);
