#pragma once

// Generic ESP-12E / NodeMCU / Wemos D1 mini profile. The ESP8266 hardware
// I2S peripheral uses fixed signal routing in the RTOS SDK driver.
#define BOARD_I2S_DATA_GPIO 3
#define BOARD_I2S_BCLK_GPIO 15
#define BOARD_I2S_LRCLK_GPIO 2

#define BOARD_OLED_SDA_GPIO 4
#define BOARD_OLED_SCL_GPIO 5
#define BOARD_OLED_ADDRESS 0x3c
#define BOARD_OLED_WIDTH 128
#define BOARD_OLED_HEIGHT 64

#define BOARD_BOOT_BUTTON_GPIO 0
#define BOARD_STATUS_LED_GPIO 2
#define BOARD_STATUS_LED_ACTIVE_LOW 1
#define BOARD_ENCODER_A_GPIO (-1)
#define BOARD_ENCODER_B_GPIO (-1)
#define BOARD_ENCODER_BUTTON_GPIO (-1)

#define BOARD_TASK_STACK_APP 4096
#define BOARD_TASK_STACK_NETWORK 4096
#define BOARD_TASK_STACK_AUDIO 6144
/* Status formatting is bounded; playlist responses reuse the shared buffer. */
#define BOARD_TASK_STACK_WEB 4096
#define BOARD_TASK_STACK_DISPLAY 3072

#define BOARD_AUDIO_INPUT_BYTES 12288
#define BOARD_PCM_RING_FRAMES 2304

