#include "oled_display.h"

#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "board_config.h"
#include "driver/i2c_master.h"
#include "esp_check.h"
#include "esp_log.h"
#include "font5x7.h"
#include "font8x15.h"

#define OLED_PAGES (OLED_DISPLAY_HEIGHT / 8)
#define OLED_COLUMN_OFFSET 28
#define OLED_TRANSFER_CHUNK 24

static const char *const TAG = "oled";

static i2c_master_dev_handle_t display_device(oled_display_t *display) {
    return (i2c_master_dev_handle_t)display->device;
}

static esp_err_t send_commands(oled_display_t *display,
                               const uint8_t *commands, size_t count) {
    uint8_t transfer[OLED_TRANSFER_CHUNK + 1];
    transfer[0] = 0x00;
    while (count) {
        size_t chunk = count > OLED_TRANSFER_CHUNK ? OLED_TRANSFER_CHUNK
                                                   : count;
        memcpy(transfer + 1, commands, chunk);
        ESP_RETURN_ON_ERROR(
            i2c_master_transmit(display_device(display), transfer, chunk + 1,
                                100),
            TAG, "OLED command transfer failed");
        commands += chunk;
        count -= chunk;
    }
    return ESP_OK;
}

static void draw_pixel(oled_display_t *display, int x, int y, bool on) {
    if (!display || x < 0 || x >= OLED_DISPLAY_WIDTH || y < 0 ||
        y >= OLED_DISPLAY_HEIGHT) return;
    uint8_t *value = &display->framebuffer[x + (y / 8) * OLED_DISPLAY_WIDTH];
    uint8_t mask = (uint8_t)(1U << (y & 7));
    if (on) {
        *value |= mask;
    } else {
        *value &= (uint8_t)~mask;
    }
}

esp_err_t oled_display_init(oled_display_t *display) {
    ESP_RETURN_ON_FALSE(display, ESP_ERR_INVALID_ARG, TAG,
                        "Display object is required");
    memset(display, 0, sizeof(*display));

    i2c_master_bus_config_t bus_config = {
        .i2c_port = -1,
        .sda_io_num = BOARD_OLED_SDA,
        .scl_io_num = BOARD_OLED_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags = {
            .enable_internal_pullup = true,
        },
    };
    i2c_master_bus_handle_t bus = NULL;
    ESP_RETURN_ON_ERROR(i2c_new_master_bus(&bus_config, &bus), TAG,
                        "I2C bus initialization failed");

    i2c_device_config_t device_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = BOARD_OLED_ADDRESS,
        .scl_speed_hz = BOARD_OLED_CLOCK_HZ,
    };
    i2c_master_dev_handle_t device = NULL;
    esp_err_t result = i2c_master_bus_add_device(bus, &device_config, &device);
    if (result != ESP_OK) {
        i2c_del_master_bus(bus);
        return result;
    }
    display->bus = bus;
    display->device = device;

    // EastRising 72x40 sequence used by U8g2 and the proven Arduino profile.
    const uint8_t init[] = {
        0xae, 0xd5, 0x80, 0xa8, 0x27, 0xd3, 0x00, 0xad, 0x30,
        0x8d, 0x14, 0x40, 0xa6, 0xa4, 0x20, 0x00, 0xa1, 0xc8,
        0xda, 0x12, 0x81, BOARD_OLED_CONTRAST, 0xd9, 0x22, 0xdb, 0x20,
        0x2e, 0xaf,
    };
    ESP_RETURN_ON_ERROR(send_commands(display, init, sizeof(init)), TAG,
                        "OLED initialization failed");
    oled_display_clear(display);
    ESP_RETURN_ON_ERROR(oled_display_present(display), TAG,
                        "OLED clear failed");
    ESP_LOGI(TAG, "SSD1306 72x40 ready at I2C 0x%02x", BOARD_OLED_ADDRESS);
    return ESP_OK;
}

esp_err_t oled_display_set_brightness(oled_display_t *display,
                                      uint8_t brightness) {
    ESP_RETURN_ON_FALSE(display && display->device, ESP_ERR_INVALID_STATE, TAG,
                        "OLED is not initialized");
    ESP_RETURN_ON_FALSE(brightness <= 100, ESP_ERR_INVALID_ARG, TAG,
                        "Brightness must be between 0 and 100");
    uint8_t controller_contrast =
        (uint8_t)(((unsigned)brightness * 255U + 50U) / 100U);
    const uint8_t commands[] = {0x81, controller_contrast};
    return send_commands(display, commands, sizeof(commands));
}

void oled_display_clear(oled_display_t *display) {
    if (display) memset(display->framebuffer, 0, sizeof(display->framebuffer));
}

void oled_display_draw_text(oled_display_t *display, int x, int y,
                            const char *text) {
    if (!display || !text) return;
    while (*text && x < OLED_DISPLAY_WIDTH) {
        uint8_t character = (uint8_t)*text++;
        for (int column = 0; column < 5; ++column) {
            uint8_t bits = font[(size_t)character * 5U + (size_t)column];
            for (int row = 0; row < 7; ++row) {
                draw_pixel(display, x + column, y + row,
                           (bits & (1U << row)) != 0);
            }
        }
        x += 6;
    }
}

void oled_display_draw_compact_text(oled_display_t *display, int x, int y,
                                    const char *text) {
    if (!display || !text) return;
    while (*text && x < OLED_DISPLAY_WIDTH) {
        uint8_t character = (uint8_t)*text++;
        for (int column = 0; column < 5; ++column) {
            uint8_t bits = font[(size_t)character * 5U + (size_t)column];
            for (int row = 0; row < 7; ++row) {
                draw_pixel(display, x + column, y + row,
                           (bits & (1U << row)) != 0);
            }
        }
        x += 5;
    }
}

static bool is_ascii_dash_equivalent(uint32_t codepoint) {
    switch (codepoint) {
        case 0x2010:  // hyphen
        case 0x2011:  // non-breaking hyphen
        case 0x2012:  // figure dash
        case 0x2013:  // en dash
        case 0x2014:  // em dash
        case 0x2015:  // horizontal bar
        case 0x2212:  // minus sign
            return true;
        default:
            return false;
    }
}

static const char *next_large_glyph(const char *text, uint8_t *glyph,
                                    bool uppercase) {
    const uint8_t *bytes = (const uint8_t *)text;
    uint32_t codepoint = 0;
    size_t length = 1;
    if (bytes[0] < 0x80) {
        codepoint = bytes[0];
    } else if ((bytes[0] & 0xe0) == 0xc0 &&
               (bytes[1] & 0xc0) == 0x80) {
        codepoint = ((uint32_t)(bytes[0] & 0x1f) << 6) |
                    (uint32_t)(bytes[1] & 0x3f);
        length = codepoint >= 0x80 ? 2 : 1;
    } else if ((bytes[0] & 0xf0) == 0xe0 && bytes[1] && bytes[2] &&
               (bytes[1] & 0xc0) == 0x80 &&
               (bytes[2] & 0xc0) == 0x80) {
        codepoint = ((uint32_t)(bytes[0] & 0x0f) << 12) |
                    ((uint32_t)(bytes[1] & 0x3f) << 6) |
                    (uint32_t)(bytes[2] & 0x3f);
        length = codepoint >= 0x800 ? 3 : 1;
    } else if ((bytes[0] & 0xf8) == 0xf0 && bytes[1] && bytes[2] &&
               bytes[3] && (bytes[1] & 0xc0) == 0x80 &&
               (bytes[2] & 0xc0) == 0x80 &&
               (bytes[3] & 0xc0) == 0x80) {
        codepoint = ((uint32_t)(bytes[0] & 0x07) << 18) |
                    ((uint32_t)(bytes[1] & 0x3f) << 12) |
                    ((uint32_t)(bytes[2] & 0x3f) << 6) |
                    (uint32_t)(bytes[3] & 0x3f);
        length = codepoint >= 0x10000 && codepoint <= 0x10ffff ? 4 : 1;
    } else {
        codepoint = 0xffffffff;
    }

    if (uppercase) {
        if (codepoint >= 'a' && codepoint <= 'z') {
            codepoint -= 'a' - 'A';
        } else if (codepoint >= 0x0430 && codepoint <= 0x044f) {
            codepoint -= 0x20;
        } else if (codepoint == 0x0451) {
            codepoint = 0x0401;
        }
    }

    // Normalize typography before consulting the font's Unicode table. Only
    // genuinely unsupported characters reach the boxed-question fallback.
    if (is_ascii_dash_equivalent(codepoint)) {
        *glyph = '-';
    } else if (codepoint < 0x7f) {
        *glyph = (uint8_t)codepoint;
    } else if (codepoint == 0x0401) {
        *glyph = 0xa8;
    } else if (codepoint == 0x0451) {
        *glyph = 0xb8;
    } else if (codepoint >= 0x0410 && codepoint <= 0x044f) {
        *glyph = (uint8_t)(0xc0 + codepoint - 0x0410);
    } else {
        for (size_t index = 0; index < 64; ++index) {
            if (font8x15_unicode_80_bf[index] == codepoint) {
                *glyph = (uint8_t)(0x80 + index);
                return text + length;
            }
        }
        // 0x7f is a dedicated question mark inside a rectangular border.
        *glyph = 0x7f;
    }
    return text + length;
}

size_t oled_display_large_text_length(const char *text) {
    size_t length = 0;
    if (!text) return 0;
    while (*text) {
        uint8_t glyph;
        text = next_large_glyph(text, &glyph, false);
        ++length;
    }
    return length;
}

void oled_display_draw_large_text(oled_display_t *display, int x, int y,
                                  const char *text, size_t pixel_offset,
                                  bool wrap, bool inverted, bool uppercase) {
    if (!display || !text) return;
    for (int row = 0; row < OLED_LARGE_GLYPH_HEIGHT; ++row) {
        for (int column = 0; column < OLED_DISPLAY_WIDTH; ++column) {
            draw_pixel(display, column, y + row, inverted);
        }
    }

    uint8_t glyphs[256];
    size_t glyph_count = 0;
    while (*text && glyph_count < sizeof(glyphs)) {
        uint8_t glyph;
        text = next_large_glyph(text, &glyph, uppercase);
        glyphs[glyph_count++] = glyph;
    }
    if (!glyph_count) return;

    size_t cycle_glyphs = glyph_count + (wrap ? 3U : 0U);
    size_t cycle_pixels = cycle_glyphs * OLED_LARGE_GLYPH_WIDTH;
    if (wrap && cycle_pixels) pixel_offset %= cycle_pixels;
    size_t glyph_index = pixel_offset / OLED_LARGE_GLYPH_WIDTH;
    x -= (int)(pixel_offset % OLED_LARGE_GLYPH_WIDTH);

    while (x < OLED_DISPLAY_WIDTH) {
        uint8_t glyph;
        if (glyph_index < glyph_count) {
            glyph = glyphs[glyph_index];
        } else if (wrap && glyph_index == glyph_count + 1U) {
            glyph = '*';
        } else if (wrap && glyph_index < cycle_glyphs) {
            glyph = ' ';
        } else {
            break;
        }
        const uint8_t *bitmap =
            font8x15 + (size_t)glyph * OLED_LARGE_GLYPH_HEIGHT;
        for (int row = 0; row < OLED_LARGE_GLYPH_HEIGHT; ++row) {
            for (int column = 0; column < OLED_LARGE_GLYPH_WIDTH; ++column) {
                unsigned bit =
                    (unsigned)(row * OLED_LARGE_GLYPH_WIDTH + column);
                bool set = (bitmap[bit >> 3] &
                            (uint8_t)(0x80U >> (bit & 7U))) != 0;
                draw_pixel(display, x + column, y + row,
                           inverted ? !set : set);
            }
        }
        x += OLED_LARGE_GLYPH_WIDTH;
        ++glyph_index;
        if (wrap && glyph_index == cycle_glyphs) glyph_index = 0;
    }
}

esp_err_t oled_display_present(oled_display_t *display) {
    ESP_RETURN_ON_FALSE(display && display->device, ESP_ERR_INVALID_STATE, TAG,
                        "OLED is not initialized");
    uint8_t transfer[OLED_TRANSFER_CHUNK + 1];
    transfer[0] = 0x40;
    for (uint8_t page = 0; page < OLED_PAGES; ++page) {
        const uint8_t commands[] = {
            (uint8_t)(0x10 | (OLED_COLUMN_OFFSET >> 4)),
            (uint8_t)(OLED_COLUMN_OFFSET & 0x0f),
            (uint8_t)(0xb0 | page),
        };
        ESP_RETURN_ON_ERROR(send_commands(display, commands, sizeof(commands)),
                            TAG, "OLED page selection failed");
        const uint8_t *data =
            display->framebuffer + page * OLED_DISPLAY_WIDTH;
        for (size_t sent = 0; sent < OLED_DISPLAY_WIDTH;
             sent += OLED_TRANSFER_CHUNK) {
            size_t chunk = OLED_DISPLAY_WIDTH - sent;
            if (chunk > OLED_TRANSFER_CHUNK) chunk = OLED_TRANSFER_CHUNK;
            memcpy(transfer + 1, data + sent, chunk);
            ESP_RETURN_ON_ERROR(
                i2c_master_transmit(display_device(display), transfer,
                                    chunk + 1, 100),
                TAG, "OLED data transfer failed");
        }
    }
    return ESP_OK;
}
