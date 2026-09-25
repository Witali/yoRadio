#pragma once

#include "driver/gpio.h"
#include "sdkconfig.h"

// The passive 32.768 kHz RTC crystal owns GPIO0/XTAL_32K_P and GPIO1/XTAL_32K_N.
// Reject conflicts even when using idf.py directly, before normal drivers or
// the deep-sleep wake stub can reconfigure those pins as digital GPIOs.
#if defined(CONFIG_RTC_CLK_SRC_EXT_CRYS)
#if CONFIG_YORADIO_ROTARY_ENCODER && \
    (CONFIG_YORADIO_ROTARY_ENCODER_GPIO_A <= 1 || \
     CONFIG_YORADIO_ROTARY_ENCODER_GPIO_B <= 1)
#error "RTC 32k crystal reserves GPIO0 and GPIO1: move encoder phases or disable the encoder"
#endif
#if CONFIG_YORADIO_ROTARY_ENCODER && CONFIG_YORADIO_ROTARY_ENCODER_BUTTON && \
    CONFIG_YORADIO_ROTARY_ENCODER_BUTTON_GPIO <= 1
#error "RTC 32k crystal reserves GPIO0 and GPIO1: move or disable the encoder button"
#endif
#if CONFIG_YORADIO_AUDIO_LEVEL_LED && CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO <= 1
#error "RTC 32k crystal reserves GPIO0 and GPIO1: move or disable the audio level LED"
#endif
#endif

// ESP32-C3 SuperMini OLED / 01Space-style 0.42-inch board.
#define BOARD_OLED_SDA GPIO_NUM_5
#define BOARD_OLED_SCL GPIO_NUM_6
#define BOARD_OLED_ADDRESS 0x3c
#define BOARD_OLED_CLOCK_HZ 400000
#define BOARD_OLED_CONTRAST 0x60

#define BOARD_AUDIO_LEFT_DATA GPIO_NUM_10
#define BOARD_AUDIO_RIGHT_DATA GPIO_NUM_3

#define BOARD_BOOT_BUTTON GPIO_NUM_9

// FreeRTOS stacks are board resources and are kept with the hardware profile.
// ESP-IDF stack sizes are expressed in bytes.
#define BOARD_TASK_STACK_DISPLAY 4096
#define BOARD_TASK_STACK_BOOT_BUTTON 4096
#define BOARD_TASK_STACK_ROTARY_ENCODER 4096
#define BOARD_TASK_STACK_SERVICES 6144
#define BOARD_TASK_STACK_RADIO_STREAM 6144
#define BOARD_TASK_STACK_AUDIO_DECODER 16384
#define BOARD_TASK_STACK_AUDIO_OUTPUT 4096
#define BOARD_TASK_STACK_WIFI_RSSI 2048
#define BOARD_TASK_STACK_WEBSOCKET_STATUS 8192
#define BOARD_TASK_STACK_WEB_STATIC 4096
#define BOARD_TASK_STACK_WIFI_REBOOT 2048
#define BOARD_TASK_STACK_TIME_SYNC 2048

