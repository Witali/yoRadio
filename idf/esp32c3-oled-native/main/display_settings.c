#include "display_settings.h"

#include <stdatomic.h>

#include "board_config.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "nvs.h"

#define DISPLAY_NVS_NAMESPACE "display"
#define DISPLAY_NVS_BRIGHTNESS "brightness"
#define DISPLAY_NVS_STATION_UPPERCASE "station_upper"
#define DISPLAY_NVS_SCREEN_ON "screen_on"
#define DISPLAY_NVS_NUMBERED "numbered"
#define DISPLAY_NVS_SAVER_ENABLED "saver_en"
#define DISPLAY_NVS_SAVER_TIMEOUT "saver_timeout"
#define DISPLAY_NVS_SAVER_BLANK "saver_blank"
#define DISPLAY_NVS_PLAY_SAVER_ENABLED "play_saver_en"
#define DISPLAY_NVS_PLAY_SAVER_TIMEOUT "play_saver_t"
#define DISPLAY_NVS_PLAY_SAVER_BLANK "play_saver_b"

static const char *const TAG = "display_settings";
static oled_display_t *s_display;
static atomic_uchar s_brightness;
static atomic_bool s_station_uppercase;
static atomic_bool s_screen_on = true;
static atomic_bool s_numbered_playlist;
static atomic_bool s_screensaver_enabled;
static atomic_uint_least16_t s_screensaver_timeout = 20U;
static atomic_bool s_screensaver_blank;
static atomic_bool s_screensaver_playing_enabled;
static atomic_uint_least16_t s_screensaver_playing_timeout = 5U;
static atomic_bool s_screensaver_playing_blank;
static atomic_uint_least32_t s_last_activity_ms;

static uint8_t default_brightness(void) {
    return (uint8_t)(((unsigned)BOARD_OLED_CONTRAST * 100U + 127U) / 255U);
}

static void load_extended_settings(void) {
    nvs_handle_t handle;
    if (nvs_open(DISPLAY_NVS_NAMESPACE, NVS_READONLY, &handle) != ESP_OK) {
        return;
    }
    uint8_t u8;
    uint16_t u16;
    if (nvs_get_u8(handle, DISPLAY_NVS_SCREEN_ON, &u8) == ESP_OK && u8 <= 1U)
        atomic_store(&s_screen_on, u8 != 0U);
    if (nvs_get_u8(handle, DISPLAY_NVS_NUMBERED, &u8) == ESP_OK && u8 <= 1U)
        atomic_store(&s_numbered_playlist, u8 != 0U);
    if (nvs_get_u8(handle, DISPLAY_NVS_SAVER_ENABLED, &u8) == ESP_OK &&
        u8 <= 1U) atomic_store(&s_screensaver_enabled, u8 != 0U);
    if (nvs_get_u16(handle, DISPLAY_NVS_SAVER_TIMEOUT, &u16) == ESP_OK &&
        u16 >= 5U && u16 <= 65520U)
        atomic_store(&s_screensaver_timeout, u16);
    if (nvs_get_u8(handle, DISPLAY_NVS_SAVER_BLANK, &u8) == ESP_OK &&
        u8 <= 1U) atomic_store(&s_screensaver_blank, u8 != 0U);
    if (nvs_get_u8(handle, DISPLAY_NVS_PLAY_SAVER_ENABLED, &u8) == ESP_OK &&
        u8 <= 1U) atomic_store(&s_screensaver_playing_enabled, u8 != 0U);
    if (nvs_get_u16(handle, DISPLAY_NVS_PLAY_SAVER_TIMEOUT, &u16) == ESP_OK &&
        u16 >= 1U && u16 <= 1080U)
        atomic_store(&s_screensaver_playing_timeout, u16);
    if (nvs_get_u8(handle, DISPLAY_NVS_PLAY_SAVER_BLANK, &u8) == ESP_OK &&
        u8 <= 1U) atomic_store(&s_screensaver_playing_blank, u8 != 0U);
    nvs_close(handle);
}

static esp_err_t save_display_u8(const char *key, uint8_t value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(DISPLAY_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open display settings storage");
    esp_err_t result = nvs_set_u8(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static esp_err_t save_display_u16(const char *key, uint16_t value) {
    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(DISPLAY_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open display settings storage");
    esp_err_t result = nvs_set_u16(handle, key, value);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
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
    bool station_uppercase = false;
    result = nvs_open(DISPLAY_NVS_NAMESPACE, NVS_READONLY, &handle);
    if (result == ESP_OK) {
        uint8_t saved = 0;
        result = nvs_get_u8(handle, DISPLAY_NVS_STATION_UPPERCASE, &saved);
        nvs_close(handle);
        if (result == ESP_OK) station_uppercase = saved != 0;
    }
    atomic_init(&s_station_uppercase, station_uppercase);
    load_extended_settings();
    display_settings_note_activity();
    ESP_RETURN_ON_ERROR(oled_display_set_brightness(display, brightness), TAG,
                        "Apply display brightness");
    ESP_RETURN_ON_ERROR(oled_display_set_power(
                            display, display_settings_get_screen_on()), TAG,
                        "Apply display power");
    ESP_LOGI(TAG, "OLED brightness %u%%", brightness);
    ESP_LOGI(TAG, "Station uppercase %s",
             station_uppercase ? "enabled" : "disabled");
    return ESP_OK;
}

bool display_settings_get_station_uppercase(void) {
    return atomic_load(&s_station_uppercase);
}

esp_err_t display_settings_set_station_uppercase(bool enabled, bool persist) {
    atomic_store(&s_station_uppercase, enabled);
    if (!persist) return ESP_OK;

    nvs_handle_t handle;
    ESP_RETURN_ON_ERROR(
        nvs_open(DISPLAY_NVS_NAMESPACE, NVS_READWRITE, &handle), TAG,
        "Open display settings storage");
    esp_err_t result = nvs_set_u8(handle, DISPLAY_NVS_STATION_UPPERCASE,
                                  enabled ? 1U : 0U);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    ESP_RETURN_ON_ERROR(result, TAG, "Save station uppercase setting");
    ESP_LOGI(TAG, "Station uppercase saved: %s",
             enabled ? "enabled" : "disabled");
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

bool display_settings_get_screen_on(void) {
    return atomic_load(&s_screen_on);
}

esp_err_t display_settings_set_screen_on(bool enabled, bool persist) {
    ESP_RETURN_ON_FALSE(s_display, ESP_ERR_INVALID_STATE, TAG,
                        "Display settings are not initialized");
    ESP_RETURN_ON_ERROR(oled_display_set_power(s_display, enabled), TAG,
                        "Apply display power");
    atomic_store(&s_screen_on, enabled);
    if (enabled) display_settings_note_activity();
    if (!persist) return ESP_OK;
    return save_display_u8(DISPLAY_NVS_SCREEN_ON, enabled ? 1U : 0U);
}

bool display_settings_get_numbered_playlist(void) {
    return atomic_load(&s_numbered_playlist);
}

esp_err_t display_settings_set_numbered_playlist(bool enabled, bool persist) {
    atomic_store(&s_numbered_playlist, enabled);
    display_settings_note_activity();
    return persist ? save_display_u8(DISPLAY_NVS_NUMBERED, enabled ? 1U : 0U)
                   : ESP_OK;
}

bool display_settings_get_screensaver_enabled(void) {
    return atomic_load(&s_screensaver_enabled);
}
esp_err_t display_settings_set_screensaver_enabled(bool enabled) {
    ESP_RETURN_ON_ERROR(save_display_u8(DISPLAY_NVS_SAVER_ENABLED,
                                        enabled ? 1U : 0U), TAG,
                        "Save stopped screensaver state");
    atomic_store(&s_screensaver_enabled, enabled);
    display_settings_note_activity();
    return ESP_OK;
}
uint16_t display_settings_get_screensaver_timeout(void) {
    return atomic_load(&s_screensaver_timeout);
}
esp_err_t display_settings_set_screensaver_timeout(uint16_t seconds) {
    ESP_RETURN_ON_FALSE(seconds >= 5U && seconds <= 65520U,
                        ESP_ERR_INVALID_ARG, TAG, "Screensaver timeout range");
    ESP_RETURN_ON_ERROR(save_display_u16(DISPLAY_NVS_SAVER_TIMEOUT, seconds),
                        TAG, "Save stopped screensaver timeout");
    atomic_store(&s_screensaver_timeout, seconds);
    display_settings_note_activity();
    return ESP_OK;
}
bool display_settings_get_screensaver_blank(void) {
    return atomic_load(&s_screensaver_blank);
}
esp_err_t display_settings_set_screensaver_blank(bool blank) {
    ESP_RETURN_ON_ERROR(save_display_u8(DISPLAY_NVS_SAVER_BLANK,
                                        blank ? 1U : 0U), TAG,
                        "Save stopped screensaver blank mode");
    atomic_store(&s_screensaver_blank, blank);
    display_settings_note_activity();
    return ESP_OK;
}
bool display_settings_get_screensaver_playing_enabled(void) {
    return atomic_load(&s_screensaver_playing_enabled);
}
esp_err_t display_settings_set_screensaver_playing_enabled(bool enabled) {
    ESP_RETURN_ON_ERROR(save_display_u8(DISPLAY_NVS_PLAY_SAVER_ENABLED,
                                        enabled ? 1U : 0U), TAG,
                        "Save playing screensaver state");
    atomic_store(&s_screensaver_playing_enabled, enabled);
    display_settings_note_activity();
    return ESP_OK;
}
uint16_t display_settings_get_screensaver_playing_timeout(void) {
    return atomic_load(&s_screensaver_playing_timeout);
}
esp_err_t display_settings_set_screensaver_playing_timeout(uint16_t minutes) {
    ESP_RETURN_ON_FALSE(minutes >= 1U && minutes <= 1080U,
                        ESP_ERR_INVALID_ARG, TAG,
                        "Playing screensaver timeout range");
    ESP_RETURN_ON_ERROR(
        save_display_u16(DISPLAY_NVS_PLAY_SAVER_TIMEOUT, minutes), TAG,
        "Save playing screensaver timeout");
    atomic_store(&s_screensaver_playing_timeout, minutes);
    display_settings_note_activity();
    return ESP_OK;
}
bool display_settings_get_screensaver_playing_blank(void) {
    return atomic_load(&s_screensaver_playing_blank);
}
esp_err_t display_settings_set_screensaver_playing_blank(bool blank) {
    ESP_RETURN_ON_ERROR(save_display_u8(DISPLAY_NVS_PLAY_SAVER_BLANK,
                                        blank ? 1U : 0U), TAG,
                        "Save playing screensaver blank mode");
    atomic_store(&s_screensaver_playing_blank, blank);
    display_settings_note_activity();
    return ESP_OK;
}

void display_settings_note_activity(void) {
    atomic_store(&s_last_activity_ms,
                 (uint32_t)(esp_timer_get_time() / 1000U));
}

bool display_settings_screensaver_active(bool playing, uint32_t now_ms,
                                         bool *power_off) {
    if (!display_settings_get_screen_on()) {
        if (power_off) *power_off = true;
        return true;
    }
    bool enabled = playing
                       ? display_settings_get_screensaver_playing_enabled()
                       : display_settings_get_screensaver_enabled();
    if (!enabled) {
        if (power_off) *power_off = false;
        return false;
    }
    uint32_t timeout_ms =
        playing
            ? (uint32_t)display_settings_get_screensaver_playing_timeout() *
                  60U * 1000U
            : (uint32_t)display_settings_get_screensaver_timeout() * 1000U;
    bool active = now_ms - atomic_load(&s_last_activity_ms) >= timeout_ms;
    if (power_off) {
        *power_off = active &&
                     (playing
                          ? display_settings_get_screensaver_playing_blank()
                          : display_settings_get_screensaver_blank());
    }
    return active;
}
