#pragma once
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
typedef unsigned nvs_handle_t;
#define NVS_READWRITE 1
#define ESP_ERR_NVS_NOT_FOUND ESP_ERR_NOT_FOUND
esp_err_t nvs_open(const char *name, int mode, nvs_handle_t *handle);
esp_err_t nvs_get_blob(nvs_handle_t handle, const char *key, void *data, size_t *length);
esp_err_t nvs_set_blob(nvs_handle_t handle, const char *key, const void *data, size_t length);
esp_err_t nvs_commit(nvs_handle_t handle);
esp_err_t nvs_get_u32(nvs_handle_t handle,const char *key,uint32_t *value);
esp_err_t nvs_set_u32(nvs_handle_t handle,const char *key,uint32_t value);
