#include "esp_log.h"
#include "esp_system.h"
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "board_config.h"
#include "native_state.h"

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

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
