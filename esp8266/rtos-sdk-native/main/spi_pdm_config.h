#pragma once

// Wemos D1 mini HSPI PDM profile. GPIO13/D7 is the filtered audio output;
// GPIO14/D5 carries the SPI clock and is not part of the analogue path.
#define BOARD_SPI_PDM_DATA_GPIO 13
#define BOARD_SPI_PDM_CLOCK_GPIO 14
#define BOARD_SPI_PDM_SAMPLE_RATE 48000U
#define BOARD_SPI_PDM_OVERSAMPLE 16U
#define BOARD_SPI_PDM_BIT_RATE_HZ 769231U
