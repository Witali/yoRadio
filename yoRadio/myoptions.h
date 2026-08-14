#ifndef myoptions_h
#define myoptions_h

/*
 * Hardware profile for the two-USB ESP32-2432S028 CYD2USB board.
 * This revision uses an ST7789 display and the onboard mono amplifier on
 * ESP32 DAC2/GPIO26.
 */

#define L10N_LANGUAGE         RU

/* 320x240 ST7789 on the board's HSPI bus. */
#define DSP_MODEL             DSP_ST7789
#define DSP_HSPI              true
#define TFT_CS                15
#define TFT_DC                2
#define TFT_RST               -1
#define BRIGHTNESS_PIN        21

/* XPT2046 has dedicated, non-default SPI pins on this board. */
#define TS_MODEL              TS_MODEL_XPT2046
#define TS_CS                 33
#define TS_SPIPINS            25, 39, 32  /* SCK, MISO, MOSI */
#define TS_SPI_HOST           VSPI

/* Feed only DAC2/GPIO26; DAC1/GPIO25 is the touch clock. */
#define I2S_DOUT              255
#define I2S_INTERNAL          true
#define I2S_INTERNAL_CHANNEL  2
#define PLAYER_FORCE_MONO     true

/* No external VS1053. The microSD bus is intentionally disabled; see docs. */
#define VS1053_CS             255
#define SDC_CS                255

#define LED_BUILTIN           255

#endif
