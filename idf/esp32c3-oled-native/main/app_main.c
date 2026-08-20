#include <stdio.h>
#include <string.h>

#include "audio_service.h"
#include "board_config.h"
#include "driver/gpio.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_spiffs.h"
#include "esp_timer.h"
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
#define DISPLAY_SCROLL_HOLD_MS 3500U
#define DISPLAY_SCROLL_STEP_MS 35U
#define DISPLAY_SCROLL_SEPARATOR_GLYPHS 3U

static const char *const TAG = "yoradio_c3";
static native_state_t s_state;
#ifndef YORADIO_CODEC_BENCHMARK
static oled_display_t s_display;

typedef struct {
    size_t glyph_count;
    size_t pixel_offset;
    uint32_t wait_started_ms;
    uint32_t last_step_ms;
    bool enabled;
} display_scroll_t;

typedef enum {
    DISPLAY_SCROLL_NONE,
    DISPLAY_SCROLL_STATION,
    DISPLAY_SCROLL_TITLE,
} display_scroll_owner_t;

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

static void reset_scroll(display_scroll_t *scroll, const char *text,
                         uint32_t now_ms) {
    scroll->glyph_count = oled_display_large_text_length(text);
    scroll->pixel_offset = 0;
    scroll->wait_started_ms = now_ms;
    scroll->last_step_ms = now_ms;
    scroll->enabled =
        scroll->glyph_count * OLED_LARGE_GLYPH_WIDTH > OLED_DISPLAY_WIDTH;
}

static bool advance_scroll(display_scroll_t *station,
                           display_scroll_t *title,
                           display_scroll_owner_t *owner,
                           uint32_t now_ms) {
    display_scroll_t *active = NULL;
    if (*owner == DISPLAY_SCROLL_STATION && station->enabled) active = station;
    if (*owner == DISPLAY_SCROLL_TITLE && title->enabled) active = title;
    if (!active) {
        *owner = DISPLAY_SCROLL_NONE;
        if (station->enabled &&
            now_ms - station->wait_started_ms >= DISPLAY_SCROLL_HOLD_MS) {
            *owner = DISPLAY_SCROLL_STATION;
            active = station;
        } else if (title->enabled &&
                   now_ms - title->wait_started_ms >= DISPLAY_SCROLL_HOLD_MS) {
            *owner = DISPLAY_SCROLL_TITLE;
            active = title;
        }
        if (!active) return false;
        active->last_step_ms = now_ms;
    }

    uint32_t elapsed = now_ms - active->last_step_ms;
    size_t steps = elapsed / DISPLAY_SCROLL_STEP_MS;
    if (!steps) return false;
    active->last_step_ms += (uint32_t)(steps * DISPLAY_SCROLL_STEP_MS);
    active->pixel_offset += steps;
    size_t cycle_pixels =
        (active->glyph_count + DISPLAY_SCROLL_SEPARATOR_GLYPHS) *
        OLED_LARGE_GLYPH_WIDTH;
    if (active->pixel_offset >= cycle_pixels) {
        active->pixel_offset = 0;
        active->wait_started_ms = now_ms;
        active->last_step_ms = now_ms;
        *owner = DISPLAY_SCROLL_NONE;
    }
    return true;
}

static void draw_status(const native_state_t *state,
                        const display_scroll_t *station_scroll,
                        const display_scroll_t *title_scroll) {
    char line[24] = {0};
    oled_display_clear(&s_display);
    oled_display_draw_large_text(
        &s_display, 0, 0, state->station,
        station_scroll->pixel_offset, station_scroll->enabled, true);
    oled_display_draw_large_text(
        &s_display, 0, 15, state->title,
        title_scroll->pixel_offset, title_scroll->enabled, false);

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
    display_scroll_t station_scroll = {0};
    display_scroll_t title_scroll = {0};
    display_scroll_owner_t scroll_owner = DISPLAY_SCROLL_NONE;
    while (true) {
        native_state_t state;
        native_state_snapshot(&s_state, &state);
        uint32_t now_ms = (uint32_t)(esp_timer_get_time() / 1000U);
        bool redraw = memcmp(&state, &previous, sizeof(state)) != 0;
        if (strcmp(state.station, previous.station) != 0) {
            reset_scroll(&station_scroll, state.station, now_ms);
            if (scroll_owner == DISPLAY_SCROLL_STATION) {
                scroll_owner = DISPLAY_SCROLL_NONE;
            }
        }
        if (strcmp(state.title, previous.title) != 0) {
            reset_scroll(&title_scroll, state.title, now_ms);
            if (scroll_owner == DISPLAY_SCROLL_TITLE) {
                scroll_owner = DISPLAY_SCROLL_NONE;
            }
        }
        if (advance_scroll(&station_scroll, &title_scroll, &scroll_owner,
                           now_ms)) {
            redraw = true;
        }
        if (redraw) {
            draw_status(&state, &station_scroll, &title_scroll);
            previous = state;
        }
        vTaskDelay(pdMS_TO_TICKS(10));
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
    const display_scroll_t initial_scroll = {0};
    draw_status(&s_state, &initial_scroll, &initial_scroll);

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
