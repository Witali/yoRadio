#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_IMAGE_HEADER_MAGIC 0xe9
#define ESP_CHIP_ID_ESP32C3 5
#define ESP_APP_DESC_MAGIC_WORD 0xabcd5432
#define OTA_WITH_SEQUENTIAL_WRITES 0xfffffffe
typedef int esp_err_t;
typedef unsigned esp_ota_handle_t;
typedef struct { uint32_t address, size; char label[17]; } esp_partition_t;
typedef struct __attribute__((packed)) {
    uint8_t magic, reserved1[11];
    uint16_t chip_id;
    uint8_t reserved2[10];
} esp_image_header_t;
typedef struct { uint32_t load_addr, data_len; } esp_image_segment_header_t;
typedef struct {
    uint32_t magic_word;
    uint8_t reserved1[12];
    char version[32], project_name[32];
    uint8_t reserved2[64], app_elf_sha256[32], reserved3[80];
} esp_app_desc_t;
typedef struct { uint32_t offset, size; } esp_partition_pos_t;
typedef struct { uint32_t image_len; } esp_image_metadata_t;
const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *);
const esp_partition_t *esp_ota_get_running_partition(void);
const esp_app_desc_t *esp_app_get_description(void);
esp_err_t esp_ota_begin(const esp_partition_t *, size_t, esp_ota_handle_t *);
esp_err_t esp_ota_write(esp_ota_handle_t, const void *, size_t);
esp_err_t esp_ota_end(esp_ota_handle_t);
esp_err_t esp_ota_abort(esp_ota_handle_t);
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *);
esp_err_t esp_image_get_metadata(const esp_partition_pos_t *, esp_image_metadata_t *);
