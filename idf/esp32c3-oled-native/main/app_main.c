#include <stdio.h>
#include <string.h>

#include "audio_service.h"
#include "board_config.h"
#include "driver/gpio.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_spiffs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_state.h"
#include "network_service.h"
#include "nvs_flash.h"
#include "oled_display.h"
#include "web_service.h"

static const char *const TAG = "yoradio_c3";
static native_state_t s_state;
static oled_display_t s_display;

static esp_err_t mount_spiffs(void) {
    esp_vfs_spiffs_conf_t config = {
        .base_path = "/spiffs",
        .partition_label = "spiffs",
        .max_files = 8,
        // Never format automatically: preserve Wi-Fi, playlist and WebUI.
        .format_if_mount_failed = false,
    };
    return esp_vfs_spiffs_register(&config);
}

static void draw_status(const native_state_t *state) {
    // Keep formatting storage wider than the 12 visible columns so values such
    // as a three-digit negative RSSI are never truncated by snprintf itself.
    // The display driver performs the intentional clipping at the panel edge.
    char line[24];
    oled_display_clear(&s_display);
    oled_display_draw_text(&s_display, 0, 0, "yoRadio IDF");

    switch (state->network_mode) {
        case NATIVE_NETWORK_CLIENT:
            snprintf(line, sizeof(line), "WiFi %d dBm", state->wifi_rssi);
            break;
        case NATIVE_NETWORK_ACCESS_POINT:
            strcpy(line, "AP mode");
            break;
        case NATIVE_NETWORK_ERROR:
            strcpy(line, "WiFi error");
            break;
        default:
            strcpy(line, "WiFi start");
            break;
    }
    oled_display_draw_text(&s_display, 0, 8, line);

    snprintf(line, sizeof(line), "%.12s", state->stream_format);
    oled_display_draw_text(&s_display, 0, 16, line);
    oled_display_draw_text(&s_display, 0, 24,
                           state->audio_running ? "Playing" : "Stopped");

    const char *station = state->station;
    if (strncmp(station, "http://", 7) == 0) station += 7;
    if (strncmp(station, "https://", 8) == 0) station += 8;
    snprintf(line, sizeof(line), "%.12s", station);
    oled_display_draw_text(&s_display, 0, 32, line);
    ESP_ERROR_CHECK_WITHOUT_ABORT(oled_display_present(&s_display));
}

static void display_task(void *argument) {
    (void)argument;
    native_state_t previous = {0};
    previous.network_mode = (native_network_mode_t)-1;
    while (true) {
        native_state_t state;
        native_state_snapshot(&s_state, &state);
        if (memcmp(&state, &previous, sizeof(state)) != 0) {
            draw_status(&state);
            previous = state;
        }
        vTaskDelay(pdMS_TO_TICKS(250));
    }
}

static void button_task(void *argument) {
    (void)argument;
    gpio_config_t config = {
        .pin_bit_mask = 1ULL << BOARD_BOOT_BUTTON,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&config));
    bool previous = gpio_get_level(BOARD_BOOT_BUTTON) == 0;
    TickType_t changed_at = xTaskGetTickCount();
    while (true) {
        bool pressed = gpio_get_level(BOARD_BOOT_BUTTON) == 0;
        TickType_t now = xTaskGetTickCount();
        if (pressed != previous && now - changed_at >= pdMS_TO_TICKS(35)) {
            previous = pressed;
            changed_at = now;
            if (!pressed) {
                native_state_t state;
                native_state_snapshot(&s_state, &state);
                if (state.audio_running) {
                    audio_service_stop();
                } else if (strncmp(state.station, "http://", 7) == 0 ||
                           strncmp(state.station, "https://", 8) == 0) {
                    audio_service_play(state.station, NATIVE_CODEC_AUTO);
                }
            }
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

static void services_task(void *argument) {
    (void)argument;
    esp_err_t result = network_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Network failed: %s", esp_err_to_name(result));
        native_state_set_network(&s_state, NATIVE_NETWORK_ERROR, 0);
    }
    result = audio_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Audio service failed: %s", esp_err_to_name(result));
    }
    result = web_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Web server failed: %s", esp_err_to_name(result));
    }
    vTaskDelete(NULL);
}

void app_main(void) {
    ESP_LOGI(TAG, "Starting pure ESP-IDF ESP32-C3 OLED yoRadio");
    native_state_init(&s_state);

    esp_err_t result = nvs_flash_init();
    if (result != ESP_OK) {
        // Existing settings are more important than automatic recovery.
        ESP_LOGE(TAG, "NVS init failed without erase: %s",
                 esp_err_to_name(result));
    }
    result = mount_spiffs();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "SPIFFS mount failed without format: %s",
                 esp_err_to_name(result));
    }
    ESP_ERROR_CHECK(oled_display_init(&s_display));
    draw_status(&s_state);

    ESP_ERROR_CHECK(xTaskCreate(display_task, "display", 3072, NULL, 1, NULL) ==
                            pdPASS
                        ? ESP_OK
                        : ESP_ERR_NO_MEM);
    ESP_ERROR_CHECK(xTaskCreate(button_task, "boot_button", 2048, NULL, 2,
                                NULL) == pdPASS
                        ? ESP_OK
                        : ESP_ERR_NO_MEM);
    ESP_ERROR_CHECK(xTaskCreate(services_task, "services", 6144, NULL, 3,
                                NULL) == pdPASS
                        ? ESP_OK
                        : ESP_ERR_NO_MEM);
}
