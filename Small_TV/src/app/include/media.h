#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
esp_err_t media_init(void);
esp_err_t media_read(uint32_t flash_offset, void *data, size_t length);
esp_err_t media_draw_jpeg(uint32_t flash_offset, size_t length, int x, int y);
esp_err_t media_draw_photo(unsigned slot);
esp_err_t media_draw_animation(unsigned animation, unsigned frame, int x, int y);
unsigned media_animation_frames(unsigned animation);
esp_err_t media_draw_weather(const char *code, int x, int y);
bool media_upload_active(void);
esp_err_t photo_upload_start(unsigned slot, uint32_t length, unsigned chunks);
esp_err_t photo_upload_chunk(unsigned slot, unsigned index, unsigned total, const uint8_t *data, size_t length);
esp_err_t photo_upload_finish(unsigned slot);
