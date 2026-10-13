#include "display.h"
#include <string.h>
#include <stdlib.h>
#include "board.h"
#include "font6x12.h"
#include "factory_ui.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static spi_device_handle_t lcd_spi;
static DMA_ATTR uint8_t transfer_buffer[LCD_WIDTH * 2 * 4];

static void lcd_transfer(const void *data, size_t length, bool is_data)
{
    /* Send one command/data buffer through the configured hardware SPI device. */

    if (!length)
        return;
    gpio_set_level(LCD_GPIO_DC, is_data);
    spi_transaction_t transfer = {.length = length * 8, .tx_buffer = data};
    ESP_ERROR_CHECK(spi_device_polling_transmit(lcd_spi, &transfer));
}

static void lcd_command(uint8_t command, const uint8_t *data, size_t length)
{
    /* Send an ST7789 command followed by its optional argument bytes. */

    lcd_transfer(&command, 1, false);
    lcd_transfer(data, length, true);
}

static void lcd_window(int x, int y, int width, int height)
{
    /* Set the inclusive ST7789 address window and start its pixel stream. */

    uint8_t columns[4] = {x >> 8, x, (x + width - 1) >> 8, x + width - 1};
    uint8_t rows[4] = {y >> 8, y, (y + height - 1) >> 8, y + height - 1};
    lcd_command(0x2a, columns, 4);
    lcd_command(0x2b, rows, 4);
    lcd_command(0x2c, NULL, 0);
}

esp_err_t display_init(void)
{
    /* Initialize GPIO, SPI, reset sequence and the 240x240 RGB565 panel.
     * FIXED_FACTORY: 0x4200934a sends inclusive row/column end 240; the last
     * pixel is 239. lcd_window computes width/height minus one for both axes. */

    gpio_config_t pins = {.pin_bit_mask = (1ULL << LCD_GPIO_DC) | (1ULL << LCD_GPIO_RESET),
                          .mode = GPIO_MODE_OUTPUT};
    esp_err_t result = gpio_config(&pins);
    if (result != ESP_OK)
        return result;
    spi_bus_config_t bus = {.mosi_io_num = LCD_GPIO_MOSI,
                            .miso_io_num = -1,
                            .sclk_io_num = LCD_GPIO_SCK,
                            .quadwp_io_num = -1,
                            .quadhd_io_num = -1,
                            .max_transfer_sz = sizeof(transfer_buffer)};
    result = spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO);
    if (result != ESP_OK)
        return result;
    spi_device_interface_config_t device = {
        .clock_speed_hz = LCD_SPI_HZ, .mode = 3, .spics_io_num = -1, .queue_size = 7};
    result = spi_bus_add_device(SPI2_HOST, &device, &lcd_spi);
    if (result != ESP_OK)
        return result;
    gpio_set_level(LCD_GPIO_RESET, 0);
    vTaskDelay(pdMS_TO_TICKS(100));
    gpio_set_level(LCD_GPIO_RESET, 1);
    vTaskDelay(pdMS_TO_TICKS(250));
    lcd_command(0x11, NULL, 0);
    vTaskDelay(pdMS_TO_TICKS(150));
    uint8_t format = 0x55, orientation = 0;
    lcd_command(0x3a, &format, 1);
    lcd_command(0x36, &orientation, 1);
    lcd_window(0, 0, LCD_WIDTH, LCD_HEIGHT);
    lcd_command(0x21, NULL, 0);
    vTaskDelay(pdMS_TO_TICKS(20));
    lcd_command(0x13, NULL, 0);
    vTaskDelay(pdMS_TO_TICKS(20));
    lcd_command(0x29, NULL, 0);
    display_fill(0, 0, LCD_WIDTH, LCD_HEIGHT, 0);
    return ESP_OK;
}

void display_fill(int x, int y, int width, int height, uint16_t color)
{
    /* Clip and fill a display rectangle using the reusable DMA buffer. */

    if (x < 0)
    {
        width += x;
        x = 0;
    }
    if (y < 0)
    {
        height += y;
        y = 0;
    }
    if (x + width > LCD_WIDTH)
        width = LCD_WIDTH - x;
    if (y + height > LCD_HEIGHT)
        height = LCD_HEIGHT - y;
    if (width <= 0 || height <= 0)
        return;
    for (unsigned i = 0; i < sizeof(transfer_buffer); i += 2)
    {
        transfer_buffer[i] = color >> 8;
        transfer_buffer[i + 1] = color;
    }
    lcd_window(x, y, width, height);
    size_t bytes = width * height * 2;
    while (bytes)
    {
        size_t block = bytes < sizeof(transfer_buffer) ? bytes : sizeof(transfer_buffer);
        lcd_transfer(transfer_buffer, block, true);
        bytes -= block;
    }
}

void display_blit(int x, int y, int width, int height, const uint16_t *pixels)
{
    /* Clip and stream a host-endian RGB565 rectangle to the panel. */

    int stride = width, source_x = 0, source_y = 0;
    if (x < 0)
    {
        source_x = -x;
        width += x;
        x = 0;
    }
    if (y < 0)
    {
        source_y = -y;
        height += y;
        y = 0;
    }
    if (x + width > LCD_WIDTH)
        width = LCD_WIDTH - x;
    if (y + height > LCD_HEIGHT)
        height = LCD_HEIGHT - y;
    if (width <= 0 || height <= 0)
        return;
    lcd_window(x, y, width, height);
    for (int row = 0; row < height; ++row)
    {
        const uint16_t *source = pixels + (row + source_y) * stride + source_x;
        for (int column = 0; column < width; ++column)
        {
            transfer_buffer[column * 2] = source[column] >> 8;
            transfer_buffer[column * 2 + 1] = source[column];
        }
        lcd_transfer(transfer_buffer, width * 2, true);
    }
}

void display_text(int x, int y, const char *text, unsigned scale, uint16_t color,
                  uint16_t background)
{
    /* Render the retained small diagnostic ASCII font at an integer scale. */

    if (!scale || scale > 8)
        return;
    uint16_t row[6 * 8];
    for (; *text && x < LCD_WIDTH; ++text, x += 6 * scale)
    {
        unsigned glyph = (unsigned char)*text;
        if (glyph < 32 || glyph > 126)
            glyph = '?';
        for (unsigned r = 0; r < 12; ++r)
        {
            for (unsigned c = 0; c < 6 * scale; ++c)
                row[c] = (font6x12[glyph - 32][r] & (0x80 >> (c / scale))) ? color : background;
            for (unsigned sy = 0; sy < scale; ++sy)
                display_blit(x, y + r * scale + sy, 6 * scale, 1, row);
        }
    }
}

void display_line(int x0, int y0, int x1, int y1, uint16_t color)
{
    /* Draw a clipped one-pixel Bresenham line. */

    int dx = abs(x1 - x0), sx = x0 < x1 ? 1 : -1, dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1,
        error = dx + dy;
    for (;;)
    {
        display_fill(x0, y0, 1, 1, color);
        if (x0 == x1 && y0 == y1)
            break;
        int twice = 2 * error;
        if (twice >= dy)
        {
            error += dy;
            x0 += sx;
        }
        if (twice <= dx)
        {
            error += dx;
            y0 += sy;
        }
    }
}

void display_bitmap(int x, int y, const tv_bitmap_t *bitmap, uint16_t color, uint16_t background,
                    bool transparent)
{
    /* Render the factory LSB-first bitmap without allocating a framebuffer.
     * FIXED_FACTORY: 0x4200950e drops an entire glyph when its right/bottom edge
     * leaves the panel. Clip its visible columns/rows, preserving the source
     * stride; the final 'r' in Thunderstorm at x=236 must remain visible. */

    if (x < 0 || y < 0 || x >= LCD_WIDTH || y >= LCD_HEIGHT)
        return;
    /* Factory rows are byte-padded and LSB-first. Width-12 glyphs use only
     * four bits of their second byte; MSB-first Spleen rows cannot substitute. */
    unsigned width = bitmap->width, height = bitmap->height;
    if (x + (int)width > LCD_WIDTH)
        width = LCD_WIDTH - x;
    if (y + (int)height > LCD_HEIGHT)
        height = LCD_HEIGHT - y;
    if (!width || !height)
        return;
    if (transparent)
    {
        for (unsigned row = 0; row < height; ++row)
        {
            const uint8_t *bits = bitmap->pixels + row * bitmap->stride;
            for (unsigned column = 0; column < width; ++column)
                if (bits[column / 8] & (1u << (column & 7)))
                    display_fill(x + column, y + row, 1, 1, color);
        }
        return;
    }
    lcd_window(x, y, width, height);
    size_t used = 0;
    for (unsigned row = 0; row < height; ++row)
    {
        const uint8_t *bits = bitmap->pixels + row * bitmap->stride;
        for (unsigned column = 0; column < width; ++column)
        {
            uint16_t pixel = (bits[column / 8] & (1u << (column & 7))) ? color : background;
            transfer_buffer[used++] = pixel >> 8;
            transfer_buffer[used++] = pixel;
            if (used == sizeof(transfer_buffer))
            {
                lcd_transfer(transfer_buffer, used, true);
                used = 0;
            }
        }
    }
    lcd_transfer(transfer_buffer, used, true);
}
