#pragma once

#include "sdkconfig.h"

// Wemos D1 mini HSPI PDM profile. GPIO13/D7 is the filtered audio output;
// GPIO14/D5 carries the SPI clock and is not part of the analogue path.
#define BOARD_SPI_PDM_DATA_GPIO 13
#define BOARD_SPI_PDM_CLOCK_GPIO 14
#define BOARD_SPI_PDM_SAMPLE_RATE 48000U

#if CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8
#define BOARD_SPI_PDM_OVERSAMPLE 8U
#define BOARD_SPI_PDM_BIT_RATE_HZ 384615U
#define BOARD_SPI_PDM_CLOCK_PREDIV 25U
#elif CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_16
#define BOARD_SPI_PDM_OVERSAMPLE 16U
#define BOARD_SPI_PDM_BIT_RATE_HZ 769231U
#define BOARD_SPI_PDM_CLOCK_PREDIV 12U
#else
#error "Select an ESP8266 SPI-PDM oversampling ratio"
#endif
