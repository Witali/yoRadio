#pragma once
#ifndef NATIVE_OTA_TEST_HOST_H
#define NATIVE_OTA_TEST_HOST_H
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_NOT_SUPPORTED 0x106
#define ESP_ERR_NOT_FOUND 0x105
#define ESP_ERR_OTA_VALIDATE_FAILED 0x1503
#define ESP_ERR_IMAGE_INVALID 0x2002
#define ESP_ERR_IMAGE_FLASH_FAIL 0x2001
#define ESP_IMAGE_HASH_LEN 32
#define OTA_WITH_SEQUENTIAL_WRITES 0xfffffffeU
#define ESP_STATIC_ASSERT _Static_assert
#define FORCE_INLINE_ATTR static inline
typedef int esp_err_t;
typedef unsigned esp_ota_handle_t;
typedef struct {
    uint32_t address, size;
    int type, subtype;
    void *flash_chip;
} esp_partition_t;
#define ESP_PARTITION_TYPE_APP 0
#define ESP_PARTITION_TYPE_DATA 1
#define ESP_PARTITION_SUBTYPE_APP_OTA_MIN 0x10
#define ESP_PARTITION_SUBTYPE_APP_OTA_MAX 0x20
typedef struct {uint32_t offset,size;} esp_partition_pos_t;
#include "sdk-app-format.h"
#include "sdk-app-desc.h"
#include "sdk-image-types.inc"
const esp_partition_t *esp_ota_get_running_partition(void);
const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *);
esp_err_t esp_ota_begin(const esp_partition_t *,size_t,esp_ota_handle_t *);
esp_err_t esp_ota_write(esp_ota_handle_t,const void *,size_t);
esp_err_t esp_ota_end(esp_ota_handle_t);
esp_err_t esp_ota_abort(esp_ota_handle_t);
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *);
esp_err_t esp_image_verify(esp_image_load_mode_t,const esp_partition_pos_t *,esp_image_metadata_t *);
#endif
