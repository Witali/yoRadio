#pragma once

#include "sdkconfig.h"

// Wemos D1 mini HSPI PDM profile. GPIO13/D7 is the filtered audio output;
// GPIO14/D5 carries the SPI clock and is not part of the analogue path.
#define BOARD_SPI_PDM_DATA_GPIO 13
#define BOARD_SPI_PDM_CLOCK_GPIO 14
#define BOARD_PDM_SAMPLE_RATE 48000U

#if CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8
#define BOARD_PDM_OVERSAMPLE 8U
#define BOARD_PDM_BIT_RATE_HZ 384615U
#define BOARD_SPI_PDM_CLOCK_PREDIV 25U
#elif CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_16
#define BOARD_PDM_OVERSAMPLE 16U
#define BOARD_PDM_BIT_RATE_HZ 769231U
#define BOARD_SPI_PDM_CLOCK_PREDIV 12U
#else
#error "Select an ESP8266 PDM oversampling ratio"
#endif

// The stable ESP8266 I2S/SLC path consumes one 32-bit DMA word per PCM sample.
// Preserve the low-cost 8x/16x sigma-delta kernel by stretching each logical
// PDM bit to fill that word. The physical carrier is therefore ~1.538 MHz,
// while the effective PDM transition rate remains 384.615/769.231 kHz.
#if (32U % BOARD_PDM_OVERSAMPLE) != 0
#error "ESP8266 I2S-PDM oversampling must divide one 32-bit DMA word"
#endif
#define BOARD_I2S_PDM_FRAME_RATE BOARD_PDM_SAMPLE_RATE
#define BOARD_I2S_PDM_BIT_REPEAT (32U / BOARD_PDM_OVERSAMPLE)
#define BOARD_I2S_PDM_CARRIER_HZ (BOARD_I2S_PDM_FRAME_RATE * 32U)

// Backward-compatible names used by the legacy SPI backend.
#define BOARD_SPI_PDM_SAMPLE_RATE BOARD_PDM_SAMPLE_RATE
#define BOARD_SPI_PDM_OVERSAMPLE BOARD_PDM_OVERSAMPLE
#define BOARD_SPI_PDM_BIT_RATE_HZ BOARD_PDM_BIT_RATE_HZ
