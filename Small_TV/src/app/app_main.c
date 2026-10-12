#include "settings.h"
#include "display.h"
#include "media.h"
#include "network.h"
#include "services.h"
#include "web.h"
#include "nvs_flash.h"
#include "esp_log.h"

void app_main(void)
{
    /* Initialize persistent settings, display, networking and the clock tasks. */
    /* Preserve the original dump and its calibration. No automatic NVS erase. */
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(settings_init());
    ESP_ERROR_CHECK(backlight_init());
    ESP_ERROR_CHECK(display_init());
    ESP_ERROR_CHECK(media_init());
    ESP_ERROR_CHECK(network_init());
    services_start();
    ESP_ERROR_CHECK(web_start());
    clock_ui_start();
    ESP_LOGI("small_tv", "Reconstructed ESP32-C2 clock started; 26 MHz crystal, 240x240 ST7789");
}
