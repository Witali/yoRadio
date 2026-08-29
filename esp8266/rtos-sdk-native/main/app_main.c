#include "esp_log.h"
#include "esp_system.h"
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "board_config.h"
#include "native_state.h"
#include "network_service.h"
#include "nvs_flash.h"
#include "persistent_settings.h"
#include "playlist_service.h"
#include "storage_service.h"
#include "time_service.h"

static const char *TAG = "yoradio8266";

void app_main(void) {
    native_state_init();
    ESP_LOGI(TAG, "yoRadio ESP8266 RTOS SDK native starting");
    ESP_LOGI(TAG, "CPU: %u MHz; free heap: %u",
             CONFIG_ESP8266_DEFAULT_CPU_FREQ_MHZ,
             esp_get_free_heap_size());
    ESP_LOGI(TAG, "profile: HTTP only, Helix MP3/AAC, I2S GPIO %d/%d/%d",
             BOARD_I2S_DATA_GPIO, BOARD_I2S_BCLK_GPIO,
             BOARD_I2S_LRCLK_GPIO);

    esp_err_t result = nvs_flash_init();
    if (result == ESP_ERR_NVS_NO_FREE_PAGES) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        result = nvs_flash_init();
    }
    ESP_ERROR_CHECK(result);
    ESP_ERROR_CHECK(persistent_settings_init());
    result = storage_service_init();
    if (result == ESP_OK) {
        result = playlist_service_init();
        if (result != ESP_OK && result != ESP_ERR_NOT_FOUND)
            ESP_LOGE(TAG, "Playlist initialization failed: %s",
                     esp_err_to_name(result));
        native_state_set_station_count(playlist_service_count());
    }
    ESP_ERROR_CHECK(time_service_start());
    ESP_ERROR_CHECK(network_service_start());

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
