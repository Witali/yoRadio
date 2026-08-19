#ifndef yoradio_board_esp32c3_oled_042_h
#define yoradio_board_esp32c3_oled_042_h

/*
 * 01Space-style ESP32-C3 board with the onboard 0.42 inch 72x40 SSD1306 OLED.
 *
 * The ESP32-C3 has no internal analogue DAC. Its I2S peripheral converts the
 * decoded stereo PCM to two independent PDM bit streams for passive filtering:
 *   GPIO10 -> left PDM output
 *   GPIO3  -> right PDM output
 */

#define L10N_LANGUAGE         RU

#define DSP_MODEL             DSP_SSD1306_72X40
#define HIDE_WEATHER
#define I2C_SDA               5
#define I2C_SCL               6
#define I2C_RST               -1
#define I2CFREQ_HZ            400000UL

#define I2S_BCLK              255
#define I2S_LRC               255
#define I2S_DOUT              255
#define I2S_INTERNAL          true
#define I2S_INTERNAL_OUTPUT   AUDIO_OUTPUT_PDM
#define I2S_PDM_DOUT          10
#define I2S_PDM_DOUT2         3

/* The single-core C3 build bypasses the three software IIR tone filters. */
#define YORADIO_EQUALIZER_ENABLED 0

#define VS1053_CS             255
#define SDC_CS                255

/* BOOT is a normal active-low button after startup. Holding it while resetting
 * intentionally enters the ROM bootloader. */
#define BTN_CENTER            9
#define BTN_INTERNALPULLUP    true
/* Click: play/pause; double click: next station; long press: previous. */
#define BTN_CENTER_ONEBUTTON_RADIO 1

/* The board is single-core. Keep every explicitly pinned task on core 0. */
#define PLAYER_TASK_CORE_ID   0
#define DSP_TASK_CORE_ID      0
#define SEARCH_WIFI_CORE_ID   0
#define WATCHDOG_TASK_CORE_ID 0
#define SYNC_TASK_CORE        0
#define CONFIG_ASYNC_TCP_RUNNING_CORE 0

/* GPIO8 drives the onboard active-low blue LED through hardware PWM. */
#define AUDIO_LEVEL_LED_PIN   8
#define AUDIO_LEVEL_LED_MAX_BRIGHTNESS 255
#define USE_BUILTIN_LED       false
#define LED_BUILTIN_S3        255

#endif
