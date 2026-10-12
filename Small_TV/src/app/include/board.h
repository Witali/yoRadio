#pragma once
/* Verified in the factory firmware's GPIO/SPI/LEDC setup. */
#define LCD_WIDTH 240
#define LCD_HEIGHT 240
#define LCD_GPIO_SCK 4
#define LCD_GPIO_MOSI 6
#define LCD_GPIO_DC 5
#define LCD_GPIO_RESET 1
#define LCD_GPIO_BACKLIGHT 18
#define LCD_SPI_HZ 40000000
#define ASSETS_BASE 0x200000u
#define PHOTO_SLOT_BYTES 0x19000u
#define PHOTO_COUNT 5
#define ANIMATION_BASE 0x27d000u
#define ANIMATION_SLOT_BYTES 0x32000u
#define WEATHER_BASE 0x377000u
#define WEATHER_SLOT_BYTES 0x3c00u
#define PHOTO_CHUNK_BYTES 4096u
