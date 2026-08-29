#include "storage_service.h"

#include "esp_log.h"
#include "esp_spiffs.h"

static const char *TAG = "storage";

esp_err_t storage_service_init(void) {
    const esp_vfs_spiffs_conf_t config = {
        .base_path = STORAGE_ROOT,
        .partition_label = "spiffs",
        .max_files = 10,
        .format_if_mount_failed = false,
    };
    esp_err_t result = esp_vfs_spiffs_register(&config);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "SPIFFS mount failed: %s", esp_err_to_name(result));
        return result;
    }
    size_t total = 0;
    size_t used = 0;
    result = esp_spiffs_info("spiffs", &total, &used);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "SPIFFS information failed: %s", esp_err_to_name(result));
        return result;
    }
    ESP_LOGI(TAG, "SPIFFS mounted: %u/%u bytes used", (unsigned)used,
             (unsigned)total);
    return ESP_OK;
}
