#include <string.h>

#include "cyd_display.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_spiffs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_state.h"
#include "network_service.h"
#include "nvs_flash.h"
#include "web_service.h"

static const char *const TAG = "yoradio_native";
static native_state_t s_state;
static cyd_display_t s_display;

static esp_err_t mount_spiffs(void) {
    esp_vfs_spiffs_conf_t config = {
        .base_path = "/spiffs",
        .partition_label = "spiffs",
        .max_files = 8,
        // Never format automatically: this preserves Wi-Fi, playlist and UI.
        .format_if_mount_failed = false,
    };
    return esp_vfs_spiffs_register(&config);
}

static void paint_status(uint16_t top, uint16_t center, uint16_t bottom) {
    for (int y = 0; y < CYD_DISPLAY_HEIGHT;
         y += cyd_display_rows_per_transfer(&s_display)) {
        int rows = cyd_display_rows_per_transfer(&s_display);
        if (rows > CYD_DISPLAY_HEIGHT - y) rows = CYD_DISPLAY_HEIGHT - y;
        uint16_t color = y < 48 ? top : (y < 208 ? center : bottom);
        uint16_t *pixels = cyd_display_acquire_buffer(&s_display);
        if (!pixels) return;
        for (size_t i = 0; i < (size_t)CYD_DISPLAY_WIDTH * rows; ++i) {
            pixels[i] = color;
        }
        if (cyd_display_draw_bitmap(&s_display, 0, y, CYD_DISPLAY_WIDTH, rows,
                                    pixels) != ESP_OK) {
            return;
        }
    }
    cyd_display_flush(&s_display);
}

static void display_task(void *argument) {
    (void)argument;
    native_network_mode_t previous = (native_network_mode_t)-1;
    while (true) {
        native_state_t state;
        native_state_snapshot(&s_state, &state);
        if (state.network_mode != previous) {
            previous = state.network_mode;
            if (previous == NATIVE_NETWORK_CLIENT) {
                paint_status(0xE007, 0x0000, 0xE007);  // yellow/black
            } else if (previous == NATIVE_NETWORK_ACCESS_POINT) {
                paint_status(0x1F00, 0x0000, 0x1F00);  // blue/black
            } else if (previous == NATIVE_NETWORK_ERROR) {
                paint_status(0x00F8, 0x0000, 0x00F8);  // red/black
            } else {
                paint_status(0xE007, 0x0000, 0x1F00);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(250));
    }
}

static void audio_task(void *argument) {
    (void)argument;
    // The decoder/output pipeline is kept on core 1. Until a station is
    // selected it sleeps and consumes no decoder heap or CPU time.
    while (true) vTaskDelay(pdMS_TO_TICKS(1000));
}

static void network_task(void *argument) {
    (void)argument;
    esp_err_t result = network_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Network failed: %s", esp_err_to_name(result));
        native_state_set_network(&s_state, NATIVE_NETWORK_ERROR, 0);
    }
    result = web_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Web server failed: %s", esp_err_to_name(result));
    }
    vTaskDelete(NULL);
}

void app_main(void) {
    ESP_LOGI(TAG, "Starting pure ESP-IDF yoRadio (Arduino-free)");
    native_state_init(&s_state);

    esp_err_t result = nvs_flash_init();
    if (result != ESP_OK) {
        // Do not erase NVS automatically. Existing settings have priority.
        ESP_LOGE(TAG, "NVS init failed without erase: %s",
                 esp_err_to_name(result));
    }
    result = mount_spiffs();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "SPIFFS mount failed without format: %s",
                 esp_err_to_name(result));
    }
    ESP_ERROR_CHECK(cyd_display_init(&s_display));

    xTaskCreatePinnedToCore(display_task, "display", 3072, NULL, 1, NULL, 0);
    xTaskCreatePinnedToCore(network_task, "network", 6144, NULL, 3, NULL, 0);
    xTaskCreatePinnedToCore(audio_task, "audio", 8192, NULL, 5, NULL, 1);
}

