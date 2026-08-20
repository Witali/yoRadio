#include <stdio.h>
#include <string.h>

#include "audio_service.h"
#include "board_config.h"
#include "driver/gpio.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_spiffs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_state.h"
#include "network_service.h"
#include "nvs_flash.h"
#include "oled_display.h"
#include "radio_control.h"
#include "web_service.h"

#define BUTTON_DEBOUNCE_MS 35
#define BUTTON_CLICK_WINDOW_MS 400
#define BUTTON_HOLD_MS 800

static const char *const TAG = "yoradio_c3";
static native_state_t s_state;
#ifndef YORADIO_CODEC_BENCHMARK
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

static size_t scroll_position(const char *text, uint32_t frame) {
    const size_t visible = OLED_DISPLAY_WIDTH / 6;
    size_t length = oled_display_large_text_length(text);
    if (length <= visible) return 0;
    // Hold the first frame, move at two pixels/second, and leave a short blank
    // tail before restarting from the beginning.
    return (frame / 2) % (length - visible + 4);
}

static void draw_status(const native_state_t *state, uint32_t frame) {
    char line[24] = {0};
    oled_display_clear(&s_display);
    oled_display_draw_large_text(
        &s_display, 0, 0, state->station,
        scroll_position(state->station, frame));
    oled_display_draw_large_text(
        &s_display, 0, 14, state->title,
        scroll_position(state->title, frame));

    if (state->network_mode == NATIVE_NETWORK_CLIENT && state->ipv4) {
        esp_ip4_addr_t address = {.addr = state->ipv4};
        snprintf(line, sizeof(line), IPSTR, IP2STR(&address));
    } else if (state->network_mode == NATIVE_NETWORK_ACCESS_POINT) {
        strcpy(line, "AP mode");
    } else if (state->network_mode == NATIVE_NETWORK_ERROR) {
        strcpy(line, "WiFi error");
    } else {
        strcpy(line, "WiFi start");
    }
    size_t width = strlen(line) * 5U;
    int left = width < OLED_DISPLAY_WIDTH
                   ? (OLED_DISPLAY_WIDTH - (int)width) / 2
                   : 0;
    oled_display_draw_compact_text(&s_display, left, 33, line);
    ESP_ERROR_CHECK_WITHOUT_ABORT(oled_display_present(&s_display));
}

static void display_task(void *argument) {
    (void)argument;
    native_state_t previous = {0};
    previous.network_mode = (native_network_mode_t)-1;
    uint32_t frame = 0;
    while (true) {
        native_state_t state;
        native_state_snapshot(&s_state, &state);
        if (memcmp(&state, &previous, sizeof(state)) != 0) {
            frame = 0;
            previous = state;
        }
        draw_status(&state, frame++);
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
    bool raw_pressed = gpio_get_level(BOARD_BOOT_BUTTON) == 0;
    bool stable_pressed = raw_pressed;
    TickType_t raw_changed_at = xTaskGetTickCount();
    TickType_t pressed_at = 0;
    TickType_t released_at = 0;
    uint8_t clicks = 0;
    bool hold_handled = false;
    while (true) {
        bool pressed = gpio_get_level(BOARD_BOOT_BUTTON) == 0;
        TickType_t now = xTaskGetTickCount();
        if (pressed != raw_pressed) {
            raw_pressed = pressed;
            raw_changed_at = now;
        }
        if (raw_pressed != stable_pressed &&
            now - raw_changed_at >= pdMS_TO_TICKS(BUTTON_DEBOUNCE_MS)) {
            stable_pressed = raw_pressed;
            if (stable_pressed) {
                pressed_at = now;
                hold_handled = false;
            } else if (!hold_handled) {
                if (clicks < UINT8_MAX) ++clicks;
                released_at = now;
            }
        }
        if (stable_pressed && !hold_handled &&
            now - pressed_at >= pdMS_TO_TICKS(BUTTON_HOLD_MS)) {
            ESP_ERROR_CHECK_WITHOUT_ABORT(radio_control_previous());
            hold_handled = true;
            clicks = 0;
        }
        if (!stable_pressed && clicks &&
            now - released_at >= pdMS_TO_TICKS(BUTTON_CLICK_WINDOW_MS)) {
            esp_err_t result = clicks >= 2 ? radio_control_next()
                                           : radio_control_toggle();
            ESP_ERROR_CHECK_WITHOUT_ABORT(result);
            clicks = 0;
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
    result = radio_control_init(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Radio control failed: %s", esp_err_to_name(result));
    }
    result = web_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Web server failed: %s", esp_err_to_name(result));
    }
    vTaskDelete(NULL);
}
#endif

void app_main(void) {
    ESP_LOGI(TAG, "Starting pure ESP-IDF ESP32-C3 OLED yoRadio");
    native_state_init(&s_state);

#ifdef YORADIO_CODEC_BENCHMARK
    ESP_LOGI(TAG, "Codec benchmark mode: network, WebUI and display disabled");
    ESP_ERROR_CHECK(audio_service_start(&s_state));
#else
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
    draw_status(&s_state, 0);

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
#endif
}
