#include "display_settings.h"

#include <stdatomic.h>

#include "board_config.h"
#include "esp_check.h"
#include "esp_log.h"
#include "nvs.h"

#define DISPLAY_NVS_NAMESPACE "display"
#define DISPLAY_NVS_BRIGHTNESS "brightness"

static const char *const TAG = "display_settings";
static oled_display_t *s_display;
static atomic_uchar s_brightness;

static uint8_t default_brightness(void) {
    return (uint8_t)(((unsigned)BOARD_OLED_CONTRAST * 100U + 127U) / 255U);
}

esp_err_t display_settings_init(oled_display_t *display) {
    ESP_RETURN_ON_FALSE(display, ESP_ERR_INVALID_ARG, TAG,
                        "Display object is required");
    s_display = display;
    uint8_t brightness = default_brightness();
    nvs_handle_t handle;
    esp_err_t result = nvs_open(DISPLAY_NVS_NAMESPACE, NVS_READONLY, &handle);
    if (result == ESP_OK) {
        uint8_t saved = brightness;
        result = nvs_get_u8(handle, DISPLAY_NVS_BRIGHTNESS, &saved);
        nvs_close(handle);
        if (result == ESP_OK && saved <= 100) {
            brightness = saved;
        } else if (result != ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGW(TAG, "Stored brightness is invalid: %s",
                     esp_err_to_name(result));
        }
    } else if (result != ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGW(TAG, "Brightness storage unavailable: %s",
                 esp_err_to_name(result));
    }
    atomic_init(&s_brightness, brightness);
    ESP_RETURN_ON_ERROR(oled_display_set_brightness(display, brightness), TAG,
                        "Apply display brightness");
    ESP_LOGI(TAG, "OLED brightness %u%%", brightness);
    return ESP_OK;
}

uint8_t display_settings_get_brightness(void) {
    return atomic_load(&s_brightness);
}

esp_err_t display_settings_set_brightness(uint8_t brightness, bool persist) {
    ESP_RETURN_ON_FALSE(s_display, ESP_ERR_INVALID_STATE, TAG,
                        "Display settings are not initialized");
    ESP_RETURN_ON_FALSE(brightness <= 100, ESP_ERR_INVALID_ARG, TAG,
                        "Brightness must be between 0 and 100");
    ESP_RETURN_ON_ERROR(oled_display_set_brightness(s_display, brightness), TAG,
                        "Apply display brightness");
    atomic_store(&s_brightness, brightness);
    if (!persist) return ESP_OK;

    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(DISPLAY_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open display settings storage");
    esp_err_t result = nvs_set_u8(handle, DISPLAY_NVS_BRIGHTNESS, brightness);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    ESP_RETURN_ON_ERROR(result, TAG, "Save display brightness");
    ESP_LOGI(TAG, "OLED brightness saved: %u%%", brightness);
    return ESP_OK;
}
