#include "display_service.h"

#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#include "board_config.h"
#include "driver/i2c.h"
#include "esp_log.h"
#include "font5x7.h"
#include "font8x15.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_state.h"
#include "persistent_settings.h"

#define OLED_PAGE_COUNT (BOARD_OLED_HEIGHT / 8)
#define OLED_DATA_BYTES (BOARD_OLED_WIDTH + 1)
#define OLED_REFRESH_MS 100U
#define OLED_SCROLL_HOLD_MS 1000U

static const char *TAG = "display";
static i2c_cmd_handle_t s_page_select;
static i2c_cmd_handle_t s_page_data;
static uint8_t s_select_bytes[4] = {0x00, 0xb0, 0x00, 0x10};
/* Byte zero is the SSD1306 data control byte; the rest is the only page
 * buffer. A full 1024-byte framebuffer is intentionally not allocated. */
static uint8_t s_page_bytes[OLED_DATA_BYTES] = {0x40};
static uint8_t s_render_page;

static esp_err_t send_once(uint8_t *bytes, size_t count) {
    i2c_cmd_handle_t command = i2c_cmd_link_create();
    if (!command) return ESP_ERR_NO_MEM;
    i2c_master_start(command);
    i2c_master_write_byte(command, BOARD_OLED_ADDRESS << 1, true);
    i2c_master_write(command, bytes, count, true);
    i2c_master_stop(command);
    esp_err_t result = i2c_master_cmd_begin(I2C_NUM_0, command,
                                             pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(command);
    return result;
}

static esp_err_t build_reusable_commands(void) {
    s_page_select = i2c_cmd_link_create();
    s_page_data = i2c_cmd_link_create();
    if (!s_page_select || !s_page_data) return ESP_ERR_NO_MEM;
    i2c_master_start(s_page_select);
    i2c_master_write_byte(s_page_select, BOARD_OLED_ADDRESS << 1, true);
    i2c_master_write(s_page_select, s_select_bytes,
                     sizeof(s_select_bytes), true);
    i2c_master_stop(s_page_select);
    i2c_master_start(s_page_data);
    i2c_master_write_byte(s_page_data, BOARD_OLED_ADDRESS << 1, true);
    i2c_master_write(s_page_data, s_page_bytes, sizeof(s_page_bytes), true);
    i2c_master_stop(s_page_data);
    return ESP_OK;
}

static esp_err_t present_page(uint8_t page) {
    s_select_bytes[1] = (uint8_t)(0xb0U | page);
    esp_err_t result = i2c_master_cmd_begin(I2C_NUM_0, s_page_select,
                                             pdMS_TO_TICKS(100));
    if (result == ESP_OK)
        result = i2c_master_cmd_begin(I2C_NUM_0, s_page_data,
                                      pdMS_TO_TICKS(100));
    return result;
}

static void pixel(int x, int y, bool on) {
    if (x < 0 || x >= BOARD_OLED_WIDTH || y < 0 || y >= BOARD_OLED_HEIGHT ||
        (uint8_t)(y >> 3) != s_render_page) return;
    uint8_t mask = (uint8_t)(1U << (y & 7));
    if (on) s_page_bytes[x + 1] |= mask;
    else s_page_bytes[x + 1] &= (uint8_t)~mask;
}

static bool dash_equivalent(uint32_t codepoint) {
    return (codepoint >= 0x2010 && codepoint <= 0x2015) ||
           codepoint == 0x2212;
}

static const char *next_glyph(const char *text, uint8_t *glyph,
                              bool uppercase) {
    const uint8_t *b = (const uint8_t *)text;
    uint32_t cp = 0xffffffffU;
    size_t length = 1;
    if (b[0] < 0x80) cp = b[0];
    else if ((b[0] & 0xe0) == 0xc0 && (b[1] & 0xc0) == 0x80) {
        cp = ((uint32_t)(b[0] & 0x1f) << 6) | (b[1] & 0x3f);
        length = cp >= 0x80 ? 2 : 1;
    } else if ((b[0] & 0xf0) == 0xe0 && b[1] && b[2] &&
               (b[1] & 0xc0) == 0x80 && (b[2] & 0xc0) == 0x80) {
        cp = ((uint32_t)(b[0] & 0x0f) << 12) |
             ((uint32_t)(b[1] & 0x3f) << 6) | (b[2] & 0x3f);
        length = cp >= 0x800 ? 3 : 1;
    } else if ((b[0] & 0xf8) == 0xf0 && b[1] && b[2] && b[3] &&
               (b[1] & 0xc0) == 0x80 && (b[2] & 0xc0) == 0x80 &&
               (b[3] & 0xc0) == 0x80) {
        cp = ((uint32_t)(b[0] & 7) << 18) |
             ((uint32_t)(b[1] & 0x3f) << 12) |
             ((uint32_t)(b[2] & 0x3f) << 6) | (b[3] & 0x3f);
        length = cp <= 0x10ffff ? 4 : 1;
    }
    if (uppercase) {
        if (cp >= 'a' && cp <= 'z') cp -= 32;
        else if (cp >= 0x0430 && cp <= 0x044f) cp -= 0x20;
        else if (cp == 0x0451) cp = 0x0401;
    }
    if (dash_equivalent(cp)) *glyph = '-';
    else if (cp < 0x7f) *glyph = (uint8_t)cp;
    else if (cp == 0x0401) *glyph = 0xa8;
    else if (cp == 0x0451) *glyph = 0xb8;
    else if (cp >= 0x0410 && cp <= 0x044f)
        *glyph = (uint8_t)(0xc0 + cp - 0x0410);
    else {
        *glyph = 0x7f;
        for (size_t i = 0; i < 64; ++i) {
            if (font8x15_unicode_80_bf[i] == cp) {
                *glyph = (uint8_t)(0x80 + i);
                break;
            }
        }
    }
    return text + length;
}

static size_t glyph_count(const char *text) {
    size_t count = 0;
    while (text && *text) {
        uint8_t ignored;
        text = next_glyph(text, &ignored, false);
        ++count;
    }
    return count;
}

static void large_text(int y, const char *text, size_t offset,
                       bool inverted, bool uppercase) {
    for (int row = 0; row < 15; ++row)
        for (int x = 0; x < BOARD_OLED_WIDTH; ++x) pixel(x, y + row, inverted);
    size_t count = glyph_count(text);
    if (!count) return;
    bool wrap = count * 8U > BOARD_OLED_WIDTH;
    size_t cycle = (count + (wrap ? 3U : 0U)) * 8U;
    if (cycle) offset %= cycle;
    size_t skip = offset / 8U;
    int x = -(int)(offset & 7U);
    const char *cursor = text;
    size_t index = 0;
    while (index < skip) {
        uint8_t ignored;
        if (index < count) cursor = next_glyph(cursor, &ignored, uppercase);
        ++index;
        if (index == count + (wrap ? 3U : 0U)) {
            index = 0;
            cursor = text;
        }
    }
    while (x < BOARD_OLED_WIDTH) {
        uint8_t glyph = ' ';
        if (index < count) cursor = next_glyph(cursor, &glyph, uppercase);
        else if (wrap && index == count + 1U) glyph = '*';
        else if (!wrap) break;
        const uint8_t *bitmap = font8x15 + (size_t)glyph * 15U;
        for (int row = 0; row < 15; ++row) {
            uint8_t bits = bitmap[row];
            for (int column = 0; column < 8; ++column) {
                bool set = (bits & (uint8_t)(0x80U >> column)) != 0;
                pixel(x + column, y + row, inverted ? !set : set);
            }
        }
        x += 8;
        ++index;
        if (index == count + (wrap ? 3U : 0U)) {
            index = 0;
            cursor = text;
        }
    }
}

static void small_text(int x, int y, const char *text) {
    while (text && *text && x < BOARD_OLED_WIDTH) {
        uint8_t c = (uint8_t)*text++;
        for (int column = 0; column < 5; ++column) {
            uint8_t bits = font[(size_t)c * 5U + (size_t)column];
            for (int row = 0; row < 7; ++row)
                pixel(x + column, y + row, (bits & (1U << row)) != 0);
        }
        x += 6;
    }
}

static void rectangle(int x, int y, int width, int height) {
    for (int row = 0; row < height; ++row)
        for (int column = 0; column < width; ++column)
            pixel(x + column, y + row, true);
}

static void clock_digit(int x, int y, int digit) {
    static const uint8_t segments[10] = {
        0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f,
    };
    uint8_t on = digit >= 0 && digit <= 9 ? segments[digit] : 0x40;
    const int w = 22, h = 46, t = 4, vh = (h - 3 * t) / 2;
    if (on & 0x01) rectangle(x + t, y, w - 2 * t, t);
    if (on & 0x40) rectangle(x + t, y + t + vh, w - 2 * t, t);
    if (on & 0x08) rectangle(x + t, y + h - t, w - 2 * t, t);
    if (on & 0x20) rectangle(x, y + t, t, vh);
    if (on & 0x02) rectangle(x + w - t, y + t, t, vh);
    if (on & 0x10) rectangle(x, y + 2 * t + vh, t, vh);
    if (on & 0x04) rectangle(x + w - t, y + 2 * t + vh, t, vh);
}

static void render_clock(time_t now) {
    struct tm local;
    bool valid = now > 1600000000 && localtime_r(&now, &local) != NULL;
    int digits[4] = {-1, -1, -1, -1};
    if (valid) {
        digits[0] = local.tm_hour / 10;
        digits[1] = local.tm_hour % 10;
        digits[2] = local.tm_min / 10;
        digits[3] = local.tm_min % 10;
    }
    const int x[4] = {4, 30, 76, 102};
    for (int i = 0; i < 4; ++i) clock_digit(x[i], 9, digits[i]);
    if ((now & 1) == 0) {
        rectangle(62, 23, 4, 4);
        rectangle(62, 39, 4, 4);
    }
}

static void render_status(const native_state_t *state,
                          const persistent_settings_t *settings,
                          size_t station_offset, size_t title_offset,
                          bool screensaver) {
    if (screensaver) {
        if (!settings->screensaver_blank) render_clock(time(NULL));
        return;
    }
    TickType_t now = xTaskGetTickCount();
    const char *secondary = state->title;
    if ((int32_t)((TickType_t)state->message_until_tick - now) > 0 &&
        state->message[0]) secondary = state->message;
    else if (state->error[0]) secondary = state->error;
    else if (state->connecting) secondary = "connecting";
    else if (!state->playing) secondary = "stopped";
    large_text(0, state->station, station_offset, true,
               settings->station_uppercase);
    large_text(16, secondary, title_offset, false, false);
    char info[40];
    if (state->playing && state->codec != CODEC_NONE) {
        snprintf(info, sizeof(info), "%s %luk %luHz %s",
                 native_codec_name(state->codec),
                 (unsigned long)state->bitrate_kbps,
                 (unsigned long)state->sample_rate_hz,
                 state->channels == 2 ? "st" : "mo");
        small_text(0, 34, info);
    }
    if (state->ip[0]) small_text(0, 56, state->ip);
}

static esp_err_t present_scene(const native_state_t *state,
                               const persistent_settings_t *settings,
                               size_t station_offset, size_t title_offset,
                               bool screensaver) {
    for (uint8_t page = 0; page < OLED_PAGE_COUNT; ++page) {
        s_render_page = page;
        memset(s_page_bytes + 1, 0, BOARD_OLED_WIDTH);
        render_status(state, settings, station_offset, title_offset,
                      screensaver);
        esp_err_t result = present_page(page);
        if (result != ESP_OK) return result;
    }
    return ESP_OK;
}

static void display_task(void *argument) {
    (void)argument;
    vTaskDelay(pdMS_TO_TICKS(1200));
    native_state_t state;
    persistent_settings_t settings;
    char previous_station[sizeof(state.station)] = "";
    char previous_secondary[sizeof(state.title)] = "";
    size_t station_offset = 0, title_offset = 0;
    TickType_t station_hold = 0, title_hold = 0, idle_since = xTaskGetTickCount();
    bool was_active = false;
    while (true) {
        native_state_snapshot(&state);
        persistent_settings_get(&settings);
        TickType_t now = xTaskGetTickCount();
        const char *secondary = state.title;
        if ((int32_t)((TickType_t)state.message_until_tick - now) > 0 &&
            state.message[0]) secondary = state.message;
        else if (state.error[0]) secondary = state.error;
        else if (state.connecting) secondary = "connecting";
        else if (!state.playing) secondary = "stopped";
        if (strcmp(previous_station, state.station) != 0) {
            strncpy(previous_station, state.station,
                    sizeof(previous_station) - 1);
            previous_station[sizeof(previous_station) - 1] = '\0';
            station_offset = 0;
            station_hold = now + pdMS_TO_TICKS(OLED_SCROLL_HOLD_MS);
        }
        if (strcmp(previous_secondary, secondary) != 0) {
            strncpy(previous_secondary, secondary,
                    sizeof(previous_secondary) - 1);
            previous_secondary[sizeof(previous_secondary) - 1] = '\0';
            title_offset = 0;
            title_hold = now + pdMS_TO_TICKS(OLED_SCROLL_HOLD_MS);
        }
        bool active = state.playing || state.connecting;
        if (active || active != was_active ||
            (int32_t)((TickType_t)state.message_until_tick - now) > 0)
            idle_since = now;
        was_active = active;
        bool screensaver = !active && settings.screensaver_enabled &&
            now - idle_since >= pdMS_TO_TICKS(
                (uint32_t)settings.screensaver_timeout_s * 1000U);
        if (!screensaver) {
            if (glyph_count(state.station) * 8U > BOARD_OLED_WIDTH &&
                (int32_t)(now - station_hold) >= 0) ++station_offset;
            if (glyph_count(secondary) * 8U > BOARD_OLED_WIDTH &&
                (int32_t)(now - title_hold) >= 0) ++title_offset;
        }
        esp_err_t result = present_scene(&state, &settings, station_offset,
                                         title_offset, screensaver);
        if (result != ESP_OK) ESP_LOGW(TAG, "OLED update failed: %d", result);
        vTaskDelay(pdMS_TO_TICKS(OLED_REFRESH_MS));
    }
}

esp_err_t display_service_start(void) {
    i2c_config_t config = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = BOARD_OLED_SDA_GPIO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = BOARD_OLED_SCL_GPIO,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .clk_stretch_tick = 80,
    };
    esp_err_t result = i2c_driver_install(I2C_NUM_0, config.mode);
    if (result == ESP_OK) result = i2c_param_config(I2C_NUM_0, &config);
    if (result != ESP_OK) return result;
    const uint8_t init[] = {
        0x00, 0xae, 0xd5, 0x80, 0xa8, 0x3f, 0xd3, 0x00, 0x40,
        0x8d, 0x14, 0x20, 0x02, 0xa1, 0xc8, 0xda, 0x12, 0x81,
        0x61, 0xd9, 0xf1, 0xdb, 0x40, 0xa4, 0xa6, 0x2e, 0xaf,
    };
    if ((result = send_once((uint8_t *)init, sizeof(init))) != ESP_OK)
        return result;
    if ((result = build_reusable_commands()) != ESP_OK) return result;
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    uint8_t contrast[] = {0x00, 0x81,
        (uint8_t)(((unsigned)settings.brightness * 255U + 50U) / 100U)};
    send_once(contrast, sizeof(contrast));
    native_state_t logo;
    memset(&logo, 0, sizeof(logo));
    strcpy(logo.station, "\xd1\x91Radio");
    strcpy(logo.title, "ESP8266");
    present_scene(&logo, &settings, 0, 0, false);
    if (xTaskCreate(display_task, "display", BOARD_TASK_STACK_DISPLAY,
                    NULL, 2, NULL) != pdPASS) return ESP_ERR_NO_MEM;
    ESP_LOGI(TAG, "SSD1306 %dx%d: 128-byte page buffer", BOARD_OLED_WIDTH,
             BOARD_OLED_HEIGHT);
    return ESP_OK;
}
